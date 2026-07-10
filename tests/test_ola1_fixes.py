"""
Tests for the 3 new bugs (Ola 1) and the auto-recovery on boot.
Covers B-N1 (crash recovery), B-N2 (lost_recovery reconciliation), B-N3 (current_prices for all brokers).
"""
import json
import sqlite3
import tempfile
import pytest
from datetime import datetime, timezone
from pathlib import Path

from data.database import Database
from execution.paper_broker import PaperBroker


@pytest.fixture
def tmp_db_path(tmp_path):
    """Returns path to a fresh SQLite DB in tmp."""
    return str(tmp_path / "test_market.db")


@pytest.fixture
def fresh_db(tmp_db_path):
    return Database(db_path=tmp_db_path)


def test_b_n2_mark_lost_recovery_method(fresh_db):
    """B-N2: mark_lost_recovery should close a trade with exit_reason='lost_recovery' and NULL PnL."""
    trade_id = fresh_db.insert_trade({
        "market": "normal_stocks", "ticker": "SPY", "signal": "LONG",
        "entry_price": 500.0, "position_size_usd": 30.0,
        "stop_loss": 2.0, "take_profit": 5.0,
        "confidence": 50, "strategy_used": "test",
        "position_id": "stocks_SPY_1234567890",
    })
    assert trade_id > 0
    open_trades = fresh_db.get_open_trades()
    assert len(open_trades) == 1
    assert open_trades[0]["status"] == "open"

    ts = datetime.now(timezone.utc).isoformat()
    fresh_db.mark_lost_recovery(trade_id, ts)

    open_after = fresh_db.get_open_trades()
    assert len(open_after) == 0
    history = fresh_db.get_trade_history(limit=10)
    assert len(history) == 1
    assert history[0]["status"] == "closed"
    assert history[0]["exit_reason"] == "lost_recovery"
    assert history[0]["pnl_usd"] is None
    assert history[0]["pnl_pct"] is None
    assert history[0]["exit_time"] == ts


def test_b_n2_reconcile_closes_orphan_open_trades(fresh_db, tmp_path):
    """B-N2: when a trade is open in DB but no broker has it in JSON, reconcile marks it as lost_recovery."""
    trade_id = fresh_db.insert_trade({
        "market": "normal_stocks", "ticker": "QQQ", "signal": "LONG",
        "entry_price": 700.0, "position_size_usd": 30.0,
        "stop_loss": 2.0, "take_profit": 5.0,
        "confidence": 50, "strategy_used": "test",
        "position_id": "stocks_QQQ_orphaned",
    })
    open_trades = fresh_db.get_open_trades()
    assert len(open_trades) == 1
    assert open_trades[0]["position_id"] == "stocks_QQQ_orphaned"

    # Simulate empty broker state (no JSON has 'stocks_QQQ_orphaned')
    empty_pb_normal = PaperBroker(initial_balance=1000, state_path=str(tmp_path / "pb_normal.json"))
    empty_pb_fast = PaperBroker(initial_balance=1000, state_path=str(tmp_path / "pb_fast.json"))

    # Simulate reconcile logic
    known_position_ids = set()
    for pb in [empty_pb_normal, empty_pb_fast]:
        known_position_ids.update(pb.positions.keys())

    lost = [t for t in open_trades if t.get("position_id") not in known_position_ids]
    assert len(lost) == 1
    assert lost[0]["position_id"] == "stocks_QQQ_orphaned"

    ts = datetime.now(timezone.utc).isoformat()
    for t in lost:
        fresh_db.mark_lost_recovery(t["id"], ts)

    assert len(fresh_db.get_open_trades()) == 0
    history = fresh_db.get_trade_history(limit=10)
    assert history[0]["exit_reason"] == "lost_recovery"


def test_b_n2_reconcile_keeps_valid_open_trades(fresh_db, tmp_path):
    """B-N2: trades that ARE in broker JSON must NOT be marked as lost_recovery."""
    trade_id = fresh_db.insert_trade({
        "market": "normal_stocks", "ticker": "SPY", "signal": "LONG",
        "entry_price": 500.0, "position_size_usd": 30.0,
        "stop_loss": 2.0, "take_profit": 5.0,
        "confidence": 50, "strategy_used": "test",
        "position_id": "stocks_SPY_live",
    })
    # Create a broker that has this position in memory
    pb_path = str(tmp_path / "pb_normal.json")
    pb = PaperBroker(initial_balance=1000, state_path=pb_path)
    pb.open_position(
        market="stocks", ticker="SPY", signal="LONG", entry_price=500.0,
        size_usd=30.0, stop_loss_pct=2.0, take_profit_pct=5.0,
        strategy_used="test",
    )
    # The position_id format in PB is "{market}_{ticker}_{timestamp}"
    pb_position_ids = list(pb.positions.keys())
    assert len(pb_position_ids) == 1
    live_position_id = pb_position_ids[0]

    # Update DB to use the actual PB position_id
    conn = fresh_db._get_conn()
    conn.execute("UPDATE trades SET position_id=? WHERE id=?", (live_position_id, trade_id))
    conn.commit()
    conn.close()

    # Now reconcile
    open_trades = fresh_db.get_open_trades()
    known_position_ids = set(pb_position_ids)
    lost = [t for t in open_trades if t.get("position_id") not in known_position_ids]
    assert len(lost) == 0  # Nothing should be lost


def test_b_n2_column_alter_for_existing_db(tmp_db_path):
    """B-N2: the defensive ALTER TABLE for position_id must work on DBs created before the column existed."""
    # Manually create a DB without the position_id column
    conn = sqlite3.connect(tmp_db_path)
    conn.executescript("""
        CREATE TABLE trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market TEXT NOT NULL,
            ticker TEXT NOT NULL,
            signal TEXT NOT NULL CHECK(signal IN ('LONG','SHORT')),
            entry_price REAL NOT NULL,
            position_size_usd REAL NOT NULL,
            stop_loss REAL,
            take_profit REAL,
            take_profit2 REAL,
            entry_time TEXT NOT NULL DEFAULT (datetime('now')),
            exit_time TEXT,
            exit_price REAL,
            exit_reason TEXT,
            pnl_usd REAL,
            pnl_pct REAL,
            status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','closed','cancelled')),
            confidence INTEGER,
            strategy_used TEXT
        );
    """)
    conn.commit()
    conn.close()

    # Open the DB via Database() — should add the column
    db = Database(db_path=tmp_db_path)
    cols = [r[1] for r in db._get_conn().execute("PRAGMA table_info(trades)").fetchall()]
    assert "position_id" in cols
    # Inserting a trade with position_id should work
    tid = db.insert_trade({
        "market": "stocks", "ticker": "SPY", "signal": "LONG",
        "entry_price": 500.0, "position_size_usd": 30.0,
        "position_id": "stocks_SPY_999",
    })
    assert tid > 0
    history = db.get_trade_history(limit=10)
    assert history[0]["position_id"] == "stocks_SPY_999"


def test_b_n3_check_stops_uses_all_brokers(monkeypatch, tmp_path):
    """B-N3: check_stops_and_evolve must collect prices for ALL brokers' positions, not just the 'normal' one."""
    from orchestrator import MarketAIOrchestrator
    from execution import paper_broker as pb_module

    # Create two brokers with positions in DIFFERENT tickers
    pb_normal = PaperBroker(initial_balance=1000, state_path=str(tmp_path / "pb_normal.json"))
    pb_fast = PaperBroker(initial_balance=1000, state_path=str(tmp_path / "pb_fast.json"))

    t1 = pb_normal.open_position(
        market="stocks", ticker="SPY", signal="LONG", entry_price=500.0,
        size_usd=30.0, stop_loss_pct=2.0, take_profit_pct=5.0,
    )
    t2 = pb_fast.open_position(
        market="stocks", ticker="QQQ", signal="LONG", entry_price=700.0,
        size_usd=30.0, stop_loss_pct=2.0, take_profit_pct=5.0,
    )

    assert t1 and "id" in t1
    assert t2 and "id" in t2
    assert "SPY" in str(pb_normal.positions)
    assert "QQQ" in str(pb_fast.positions)
    # The fast broker does NOT have SPY
    assert "SPY" not in str(pb_fast.positions)
    # The normal broker does NOT have QQQ
    assert "QQQ" not in str(pb_normal.positions)

    # Build minimal config and orch
    config = {
        "markets": {"polymarket": {"enabled": False}, "forex": {"enabled": False}, "stocks": {"enabled": True}},
        "risk": {"max_total_exposure_pct": 0.4, "max_daily_loss_pct": 0.1, "correlation_threshold": 0.85, "time_exit": {"default": {"base_hours": 72}}},
        "orchestrator": {"log_level": "WARNING", "log_file": "test_orch.log"},
        "deepseek": {"model": "deepseek-v4-pro", "temperature": 0.3, "max_tokens": 500, "timeout_seconds": 30},
        "layers": {k: {"enabled": False} for k in ["technical", "fundamental", "macro", "sentiment", "onchain", "orderbook", "ict_smc", "adx_regime", "cross_asset"]},
        "alerts": {"telegram": {"enabled": False}, "discord": {"enabled": False}},
        "profiles": {"normal": {"sl_min_pct": 1, "sl_max_pct": 5, "tp_min_pct": 2, "tp_max_pct": 10}, "fast": {"sl_min_pct": 0.5, "sl_max_pct": 1.5, "tp_min_pct": 1, "tp_max_pct": 3}},
    }

    # Build orch with monkeypatched init
    import yaml
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    import importlib
    import orchestrator.core as core_mod
    importlib.reload(core_mod)
    # Patch CONFIG_PATH
    monkeypatch.setattr(core_mod, "CONFIG_PATH", cfg_path)

    # Patch the PaperBroker ctor in core to use our pre-populated brokers
    original_init = core_mod.MarketAIOrchestrator.init_components
    def patched_init(self):
        self.db = Database(db_path=str(tmp_path / "test.db"))
        # Mock the rest
        from data.collector_news import NewsCollector
        from data.collector_yfinance import YFinanceCollector
        from data.collector_polymarket import PolymarketCollector
        from analyzers.technical import TechnicalAnalyzer
        from analyzers.onchain import OnChainAnalyzer
        from analyzers.sentiment import SentimentAnalyzer
        from analyzers.orderbook import OrderBookAnalyzer
        from analyzers.fundamental import FundamentalAnalyzer
        from analyzers.macro import MacroAnalyzer
        from analyzers.cross_asset import CrossAssetAnalyzer
        from analyzers.ict_smc import ICTAnalyzer
        from analyzers.adx_regime import ADXRegimeAnalyzer
        from engine.fusion import FusionEngine
        from engine.decider import DeepSeekDecider
        from execution.executor_polymarket import PolymarketExecutor
        from execution.executor_traditional import TraditionalExecutor
        from learning.journal import TradeJournal
        from learning.strategy_evolver import StrategyEvolver
        from alerts.notifier import Notifier
        from execution.risk_engine import RiskEngine
        self.news_collector = NewsCollector()
        self.yf_collector = YFinanceCollector()
        self.pm_collector = PolymarketCollector()
        self.tech_analyzer = TechnicalAnalyzer()
        self.onchain_analyzer = OnChainAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.ob_analyzer = OrderBookAnalyzer()
        self.fund_analyzer = FundamentalAnalyzer()
        self.macro_analyzer = MacroAnalyzer()
        self.cross_analyzer = CrossAssetAnalyzer()
        self.ict_analyzer = ICTAnalyzer()
        self.adx_analyzer = ADXRegimeAnalyzer()
        self.fusion_engine = FusionEngine(self.config)
        self.decider = DeepSeekDecider(api_key="", model="deepseek-v4-pro")
        # Inject our pre-populated brokers
        self.paper_brokers = {"normal": pb_normal, "fast": pb_fast}
        self.paper_broker = pb_normal
        self.profiles_config = self.config.get("profiles", {})
        self.pm_executor = PolymarketExecutor()
        self.trad_executor = TraditionalExecutor()
        self.journal = TradeJournal()
        self.evolver = StrategyEvolver()
        self.notifier = Notifier()
        self.risk_engine = RiskEngine(initial_balance=1000)
        self._news_cache = {}
        self._reconcile_db_with_brokers()

    core_mod.MarketAIOrchestrator.init_components = patched_init

    # Capture which tickers get price requests
    requested_tickers = []

    def fake_get_current_price(self, tk):
        requested_tickers.append(tk)
        return 500.0  # arbitrary non-None

    monkeypatch.setattr("data.collector_yfinance.YFinanceCollector.get_current_price", fake_get_current_price)

    # Build orch
    orch = core_mod.MarketAIOrchestrator(config, mode="paper")
    # Suppress noise
    import logging
    orch.log.setLevel(logging.ERROR)

    # Run check_stops
    orch.check_stops_and_evolve()

    # B-N3: both tickers (SPY from normal, QQQ from fast) must be requested
    assert "SPY" in requested_tickers, f"SPY not requested. Got: {requested_tickers}"
    assert "QQQ" in requested_tickers, f"QQQ not requested. Got: {requested_tickers}"
    # Both tickers should be in current_prices internally
    # (we test the union via the requested_tickers list)
