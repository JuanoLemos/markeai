"""
Fase 1 — Tests para /api/overview/pnl
Refactoriza el P&L en 3 partes honestas:
  - hoy          : P&L cerrado HOY
  - realizado    : P&L acumulado de TODOS los trades cerrados
  - no_realizado : mark-to-market de posiciones abiertas
  - desde        : fecha del primer trade/señal

Issue relacionado: PnL ficticio (Issue 7) — el endpoint debe usar SOLO
datos de la DB / paper broker, nunca valores inventados.
"""
import sys
import json
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


@pytest.fixture
def tmp_market(monkeypatch, tmp_path):
    """
    Crea un mini MarketAI en tmp_path con:
    - data/market.db con señales y trades controladas
    - data/cache/pb_normal.json y pb_fast.json
    Redirige BASE_DIR / DB_PATH / STATE_PATH de dashboard al tmp_path.
    """
    import dashboard as d
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "cache").mkdir()
    db_path = data_dir / "market.db"
    log_path = tmp_path / "orchestrator.log"
    log_path.write_text("")
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("version: '1.3.0'\n", encoding="utf-8")

    # DB schema mínima
    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
        CREATE TABLE signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            market TEXT,
            ticker TEXT,
            decision TEXT,
            confidence INTEGER,
            layer_scores TEXT,
            reasoning TEXT
        );
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            market TEXT,
            signal TEXT,
            entry_time TEXT,
            exit_time TEXT,
            entry_price REAL,
            exit_price REAL,
            exit_reason TEXT,
            pnl_usd REAL,
            status TEXT
        );
        CREATE TABLE portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            balance_usd REAL
        );
        CREATE TABLE market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ticker TEXT,
            price REAL
        );
    """)
    conn.commit()
    conn.close()

    # Redirigir constantes de dashboard
    monkeypatch.setattr(d, "BASE_DIR", tmp_path)
    monkeypatch.setattr(d, "DB_PATH", db_path)
    monkeypatch.setattr(d, "CONFIG_PATH", cfg_path)
    monkeypatch.setattr(d, "LOG_PATH", log_path)
    monkeypatch.setattr(d, "STATE_PATH", data_dir / "cache" / "paper_broker_state.json")

    # Inicializar paper broker states vacíos
    for name in ("normal", "fast"):
        (data_dir / "cache" / f"pb_{name}.json").write_text(
            json.dumps({"balance": 1000, "positions": {}, "trade_log": [], "daily_pnl": 0})
        )

    return tmp_path, db_path


def _insert_trade(db_path, ticker, pnl, exit_time, market="forex", signal="LONG"):
    """Inserta un trade CERRADO. Usamos exit_time (esquema real de la DB)."""
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO trades (ticker, market, signal, entry_time, exit_time, entry_price, pnl_usd, status) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (ticker, market, signal, exit_time, exit_time, 1.0, pnl, "closed"),
    )
    conn.commit()
    conn.close()


def _insert_signal(db_path, ticker, ts, market="forex", decision="LONG"):
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO signals (timestamp, market, ticker, decision, confidence, layer_scores, reasoning) "
        "VALUES (?, ?, ?, ?, 50, '{}', '')",
        (ts, market, ticker, decision),
    )
    conn.commit()
    conn.close()


def _insert_market_data(db_path, ticker, price):
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO market_data (timestamp, ticker, price) VALUES (?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), ticker, price),
    )
    conn.commit()
    conn.close()


def _write_pb(path, balance, positions):
    """Escribe un paper broker state con balance y posiciones."""
    Path(path).write_text(json.dumps({
        "balance": balance, "positions": positions, "trade_log": [], "daily_pnl": 0,
    }))


# ═════════════════════════════════════════════════════════════
# Tests del endpoint /api/overview/pnl
# ═════════════════════════════════════════════════════════════

class TestOverviewPnlEndpoint:
    """El endpoint existe, devuelve 200 y los campos esperados."""

    def test_endpoint_returns_200_and_all_fields(self, tmp_market):
        import dashboard as d
        app = d.create_app()
        client = app.test_client()
        r = client.get("/api/overview/pnl")
        assert r.status_code == 200
        body = r.get_json()
        for key in ("hoy", "realizado", "no_realizado", "balance", "equity", "since", "open_positions", "total_trades"):
            assert key in body, f"falta campo {key}"
        assert isinstance(body["hoy"], (int, float))
        assert isinstance(body["realizado"], (int, float))
        assert isinstance(body["no_realizado"], (int, float))
        assert isinstance(body["balance"], (int, float))
        assert isinstance(body["equity"], (int, float))
        assert isinstance(body["open_positions"], int)
        assert isinstance(body["total_trades"], int)

    def test_no_data_returns_zeros(self, tmp_market):
        """Sin trades, sin posiciones → P&L todo 0, since None.
        Balance = $1000 (normal) + $1000 (fast) = $2000 (capital inicial paper)."""
        import dashboard as d
        app = d.create_app()
        r = app.test_client().get("/api/overview/pnl")
        body = r.get_json()
        assert body["hoy"] == 0
        assert body["realizado"] == 0
        assert body["no_realizado"] == 0
        assert body["balance"] == 2000  # 2 profiles × $1000 seed
        assert body["equity"] == 2000
        assert body["total_trades"] == 0
        assert body["open_positions"] == 0
        assert body["since"] is None


class TestOverviewPnlHoy:
    """El campo 'hoy' suma SOLO los trades cerrados HOY (UTC)."""

    def test_trades_today_counted_in_hoy(self, tmp_market):
        tmpdir, db = tmp_market
        now = datetime.now(timezone.utc)
        today_iso = now.isoformat()
        _insert_trade(db, "EURUSD=X", 12.50, today_iso)
        _insert_trade(db, "GBPUSD=X", -3.20, today_iso)
        import dashboard as d
        r = d.create_app().test_client().get("/api/overview/pnl")
        body = r.get_json()
        assert body["hoy"] == pytest.approx(9.30, abs=0.01)

    def test_trades_other_days_NOT_in_hoy(self, tmp_market):
        tmpdir, db = tmp_market
        old = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        _insert_trade(db, "EURUSD=X", 100.0, old)  # trade viejo: NO va en "hoy"
        import dashboard as d
        r = d.create_app().test_client().get("/api/overview/pnl")
        body = r.get_json()
        assert body["hoy"] == 0
        assert body["realizado"] == pytest.approx(100.0, abs=0.01)

    def test_hoy_count_field(self, tmp_market):
        """El endpoint también devuelve 'hoy_count' (cuántos trades cerraron hoy)."""
        tmpdir, db = tmp_market
        today_iso = datetime.now(timezone.utc).isoformat()
        _insert_trade(db, "EURUSD=X", 5.0, today_iso)
        _insert_trade(db, "GBPUSD=X", 7.0, today_iso)
        _insert_trade(db, "USDJPY=X", -2.0, today_iso)
        import dashboard as d
        r = d.create_app().test_client().get("/api/overview/pnl")
        body = r.get_json()
        assert body["hoy"] == pytest.approx(10.0, abs=0.01)
        assert body["hoy_count"] == 3


class TestOverviewPnlRealizado:
    """El campo 'realizado' suma TODOS los trades cerrados (acumulado)."""

    def test_realizado_is_cumulative(self, tmp_market):
        tmpdir, db = tmp_market
        old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        _insert_trade(db, "AAPL", 50.0, old)
        _insert_trade(db, "MSFT", -20.0, old)
        recent = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        _insert_trade(db, "TSLA", 15.0, recent)
        import dashboard as d
        r = d.create_app().test_client().get("/api/overview/pnl")
        body = r.get_json()
        assert body["realizado"] == pytest.approx(45.0, abs=0.01)
        assert body["total_trades"] == 3

    def test_open_trades_dont_count_in_realizado(self, tmp_market):
        """Trades con status='open' o sin pnl_usd NO se cuentan en realizado."""
        tmpdir, db = tmp_market
        old = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        # trade cerrado
        _insert_trade(db, "AAPL", 30.0, old, signal="LONG")
        # trade abierto (no tiene exit_time)
        conn = sqlite3.connect(str(db))
        conn.execute(
            "INSERT INTO trades (ticker, signal, entry_time, pnl_usd, status) "
            "VALUES ('MSFT', 'LONG', ?, NULL, 'open')",
            (old,),
        )
        conn.commit()
        conn.close()
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        assert body["realizado"] == pytest.approx(30.0, abs=0.01)
        assert body["total_trades"] == 1


class TestOverviewPnlNoRealizado:
    """El campo 'no_realizado' = mark-to-market de posiciones abiertas."""

    def test_long_profit(self, tmp_market):
        """LONG, current > entry → no_realizado positivo."""
        tmpdir, db = tmp_market
        # Posición LONG abierta: entry=1.10, current=1.15 (+4.55%), size=$100
        _write_pb(
            tmpdir / "data" / "cache" / "pb_normal.json",
            balance=900,  # 1000 - 100 invertidos
            positions={
                "p1": {
                    "market": "forex", "ticker": "EURUSD=X", "signal": "LONG",
                    "entry_price": 1.10, "size_usd": 100,
                }
            },
        )
        # pb_fast queda con el default del fixture (balance=1000, sin posiciones)
        _insert_market_data(db, "EURUSD=X", 1.15)
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        # pct = (1.15 - 1.10) / 1.10 = 0.0455 → 100 * 0.0455 = 4.55
        assert body["no_realizado"] == pytest.approx(4.55, abs=0.01)
        # equity = (900 normal) + (1000 fast default) + 4.55 unrealized = 1904.55
        assert body["equity"] == pytest.approx(1904.55, abs=0.01)

    def test_long_loss(self, tmp_market):
        """LONG, current < entry → no_realizado negativo."""
        tmpdir, db = tmp_market
        _write_pb(
            tmpdir / "data" / "cache" / "pb_normal.json",
            balance=900,
            positions={
                "p1": {
                    "market": "forex", "ticker": "EURUSD=X", "signal": "LONG",
                    "entry_price": 1.10, "size_usd": 100,
                }
            },
        )
        _insert_market_data(db, "EURUSD=X", 1.05)  # -4.55%
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        assert body["no_realizado"] == pytest.approx(-4.55, abs=0.01)

    def test_short_direction_flips(self, tmp_market):
        """SHORT: cae → ganancia (no_realizado positivo)."""
        tmpdir, db = tmp_market
        _write_pb(
            tmpdir / "data" / "cache" / "pb_normal.json",
            balance=900,
            positions={
                "p1": {
                    "market": "forex", "ticker": "EURUSD=X", "signal": "SHORT",
                    "entry_price": 1.10, "size_usd": 100,
                }
            },
        )
        _insert_market_data(db, "EURUSD=X", 1.05)  # cayó 4.55% → SHORT gana
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        assert body["no_realizado"] == pytest.approx(4.55, abs=0.01)

    def test_no_current_price_no_unrealized(self, tmp_market):
        """Si no hay precio actual para el ticker, no cuenta (no se inventa)."""
        tmpdir, db = tmp_market
        _write_pb(
            tmpdir / "data" / "cache" / "pb_normal.json",
            balance=900,
            positions={
                "p1": {
                    "market": "forex", "ticker": "EURUSD=X", "signal": "LONG",
                    "entry_price": 1.10, "size_usd": 100,
                }
            },
        )
        # NO insertamos market_data → no hay precio actual
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        assert body["no_realizado"] == 0

    def test_aggregates_across_profiles(self, tmp_market):
        """Suma no_realizado de NORMAL + FAST."""
        tmpdir, db = tmp_market
        _write_pb(
            tmpdir / "data" / "cache" / "pb_normal.json",
            balance=900,
            positions={"p1": {
                "market": "forex", "ticker": "EURUSD=X", "signal": "LONG",
                "entry_price": 1.0, "size_usd": 100,
            }},
        )
        _write_pb(
            tmpdir / "data" / "cache" / "pb_fast.json",
            balance=900,
            positions={"p2": {
                "market": "forex", "ticker": "GBPUSD=X", "signal": "LONG",
                "entry_price": 1.0, "size_usd": 100,
            }},
        )
        _insert_market_data(db, "EURUSD=X", 1.10)  # +10 → 10
        _insert_market_data(db, "GBPUSD=X", 0.95)  # -5  → -5
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        assert body["no_realizado"] == pytest.approx(5.0, abs=0.01)
        assert body["open_positions"] == 2


class TestOverviewPnlSince:
    """El campo 'since' = fecha más antigua entre (primer trade, primera señal)."""

    def test_since_uses_oldest_event(self, tmp_market):
        tmpdir, db = tmp_market
        # trade hace 10 días
        old_trade = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        _insert_trade(db, "AAPL", 5.0, old_trade)
        # signal hace 3 días
        recent_signal = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        _insert_signal(db, "TSLA", recent_signal)
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        assert body["since"] is not None
        # El "since" debe ser la fecha del trade (10 días atrás)
        # La comparación exacta es frágil por formato, así que validamos que está en el pasado
        since_dt = datetime.fromisoformat(body["since"].rstrip("Z"))
        diff = (datetime.now(timezone.utc) - since_dt).total_seconds() / 86400
        assert 9 < diff < 11  # ~10 días atrás

    def test_since_none_with_no_data(self, tmp_market):
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        assert body["since"] is None


class TestOverviewPnlEquityVsBalance:
    """equity = balance + no_realizado (lo que tendrías cerrando todo ahora)."""

    def test_equity_includes_unrealized(self, tmp_market):
        tmpdir, db = tmp_market
        _write_pb(
            tmpdir / "data" / "cache" / "pb_normal.json",
            balance=950,  # 1000 - 50 invertidos
            positions={"p1": {
                "market": "forex", "ticker": "EURUSD=X", "signal": "LONG",
                "entry_price": 1.0, "size_usd": 50,
            }},
        )
        _write_pb(
            tmpdir / "data" / "cache" / "pb_fast.json",
            balance=1000,  # sin posiciones
            positions={},
        )
        _insert_market_data(db, "EURUSD=X", 1.10)  # +10% sobre $50 = +$5
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        assert body["balance"] == pytest.approx(1950, abs=0.01)
        assert body["no_realizado"] == pytest.approx(5.0, abs=0.01)
        assert body["equity"] == pytest.approx(1955, abs=0.01)


class TestNoFictionalDataRegression:
    """Regresión para Issue 7 (PnL ficticio)."""

    def test_endpoint_never_invents_values(self, tmp_market):
        """Con DB completamente vacía, TODOS los valores numéricos son 0 o None."""
        import dashboard as d
        body = d.create_app().test_client().get("/api/overview/pnl").get_json()
        # ningún valor puede ser algo != 0 sin que haya datos
        assert body["hoy"] == 0
        assert body["realizado"] == 0
        assert body["no_realizado"] == 0
        assert body["total_trades"] == 0
        assert body["open_positions"] == 0
        assert body["since"] is None
