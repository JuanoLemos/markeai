import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent / "market.db")
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self):
        conn = self._get_conn()
        # B-N2: defensive ALTER for existing DBs that predate position_id column
        cols = [r[1] for r in conn.execute("PRAGMA table_info(trades)").fetchall()]
        if "position_id" not in cols:
            try:
                conn.execute("ALTER TABLE trades ADD COLUMN position_id TEXT")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_trades_position_id ON trades(position_id)")
            except Exception:
                pass
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS trades (
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
                strategy_used TEXT,
                position_id TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_trades_position_id ON trades(position_id);

            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                market TEXT NOT NULL,
                ticker TEXT NOT NULL,
                decision TEXT NOT NULL CHECK(decision IN ('LONG','SHORT','WAIT')),
                confidence INTEGER NOT NULL,
                layer_scores TEXT NOT NULL,
                reasoning TEXT
            );

            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                market TEXT NOT NULL,
                ticker TEXT NOT NULL,
                price REAL,
                volume REAL,
                high_24h REAL,
                low_24h REAL,
                change_24h_pct REAL,
                extra_data TEXT
            );

            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL UNIQUE,
                total_trades INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                profit_factor REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                total_pnl REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS prompt_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                ticker TEXT NOT NULL,
                signal TEXT NOT NULL,
                confidence REAL DEFAULT 0,
                outcome TEXT NOT NULL CHECK(outcome IN ('win','loss')),
                pnl_pct REAL DEFAULT 0,
                lesson TEXT NOT NULL,
                critique TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                market TEXT NOT NULL,
                balance_usd REAL NOT NULL,
                open_positions INTEGER DEFAULT 0,
                daily_pnl REAL DEFAULT 0.0,
                total_pnl REAL DEFAULT 0.0
            );

            CREATE TABLE IF NOT EXISTS motor_heartbeat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                motor TEXT NOT NULL,
                status TEXT DEFAULT 'ok',
                message TEXT DEFAULT '',
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS ghost_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                ticker TEXT NOT NULL,
                signal TEXT NOT NULL,
                confidence REAL DEFAULT 0,
                version TEXT DEFAULT 'ghost',
                live_signal TEXT DEFAULT '',
                live_confidence REAL DEFAULT 0,
                live_outcome TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS backtest_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created TEXT NOT NULL DEFAULT (datetime('now')),
                market TEXT NOT NULL,
                config_snapshot TEXT NOT NULL,
                results TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_trades_market ON trades(market);
            CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
            CREATE INDEX IF NOT EXISTS idx_trades_entry ON trades(entry_time);
            CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
            CREATE INDEX IF NOT EXISTS idx_market_data_ticker ON market_data(ticker);
            CREATE INDEX IF NOT EXISTS idx_motor_ts ON motor_heartbeat(motor, timestamp);
        """)
        conn.commit()
        conn.close()

    def insert_trade(self, trade: dict) -> int:
        conn = self._get_conn()
        cursor = conn.execute("""
            INSERT INTO trades (market, ticker, signal, entry_price, position_size_usd,
                                stop_loss, take_profit, take_profit2, confidence, strategy_used, position_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade["market"], trade["ticker"], trade["signal"], trade["entry_price"],
            trade["position_size_usd"], trade.get("stop_loss"), trade.get("take_profit"),
            trade.get("take_profit2"), trade.get("confidence"), trade.get("strategy_used"),
            trade.get("position_id"),
        ))
        conn.commit()
        trade_id = cursor.lastrowid
        conn.close()
        return trade_id

    def mark_lost_recovery(self, trade_id: int, exit_time_iso: str):
        """B-N2: mark a trade as 'lost_recovery' (closed but PnL unknown)."""
        conn = self._get_conn()
        conn.execute("""
            UPDATE trades SET status='closed', exit_time=?, exit_reason='lost_recovery',
                              pnl_usd=NULL, pnl_pct=NULL
            WHERE id=?
        """, (exit_time_iso, trade_id))
        conn.commit()
        conn.close()

    def close_trade(self, trade_id: int, exit_price: float, exit_reason: str, pnl_usd: float, pnl_pct: float):
        conn = self._get_conn()
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            UPDATE trades SET exit_time=?, exit_price=?, exit_reason=?,
                              pnl_usd=?, pnl_pct=?, status='closed'
            WHERE id=?
        """, (now, exit_price, exit_reason, pnl_usd, pnl_pct, trade_id))
        conn.commit()
        conn.close()

    def get_open_trades(self) -> list:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM trades WHERE status='open'").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_trade_history(self, limit: int = 50) -> list:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM trades ORDER BY entry_time DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def insert_signal(self, signal: dict):
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO signals (market, ticker, decision, confidence, layer_scores, reasoning)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            signal["market"], signal["ticker"], signal["decision"],
            signal["confidence"], json.dumps(signal.get("layer_scores", {})),
            signal.get("reasoning", ""),
        ))
        conn.commit()
        conn.close()

    def get_recent_signals(self, limit: int = 10) -> list:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def insert_market_data(self, data: dict):
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO market_data (market, ticker, price, volume, high_24h, low_24h, change_24h_pct, extra_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["market"], data["ticker"], data.get("price"),
            data.get("volume"), data.get("high_24h"), data.get("low_24h"),
            data.get("change_24h_pct"), json.dumps(data.get("extra", {})),
        ))
        conn.commit()
        conn.close()

    def get_portfolio_summary(self) -> dict:
        conn = self._get_conn()
        open_trades = conn.execute("SELECT COUNT(*) as count, COALESCE(SUM(position_size_usd), 0) as exposure FROM trades WHERE status='open'").fetchone()
        closed_trades = conn.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(pnl_usd), 0) as total_pnl,
                   COALESCE(AVG(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END), 0) as win_rate
            FROM trades WHERE status='closed'
        """).fetchone()
        conn.close()
        return {
            "open_positions": open_trades["count"],
            "exposure_usd": open_trades["exposure"],
            "total_closed_trades": closed_trades["count"],
            "total_pnl_usd": closed_trades["total_pnl"],
            "win_rate": round(closed_trades["win_rate"] * 100, 1),
        }

    def update_strategy_performance(self, name: str, metrics: dict):
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO strategy_performance (strategy_name, total_trades, wins, losses, win_rate,
                                              sharpe_ratio, profit_factor, max_drawdown, total_pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(strategy_name) DO UPDATE SET
                total_trades=excluded.total_trades, wins=excluded.wins, losses=excluded.losses,
                win_rate=excluded.win_rate, sharpe_ratio=excluded.sharpe_ratio,
                profit_factor=excluded.profit_factor, max_drawdown=excluded.max_drawdown,
                total_pnl=excluded.total_pnl, last_updated=datetime('now')
        """, (
            name, metrics.get("total_trades", 0), metrics.get("wins", 0),
            metrics.get("losses", 0), metrics.get("win_rate", 0.0),
            metrics.get("sharpe_ratio", 0.0), metrics.get("profit_factor", 0.0),
            metrics.get("max_drawdown", 0.0), metrics.get("total_pnl", 0.0),
        ))
        conn.commit()
        conn.close()

    def insert_portfolio_snapshot(self, balance: float, open_positions: int, daily_pnl: float, total_pnl: float):
        conn = self._get_conn()
        conn.execute("""
            INSERT INTO portfolio (market, balance_usd, open_positions, daily_pnl, total_pnl)
            VALUES ('all', ?, ?, ?, ?)
        """, (balance, open_positions, daily_pnl, total_pnl))
        conn.commit()
        conn.close()

    def insert_ghost_signal(self, ticker: str, signal: str, confidence: float,
                            version: str = "ghost", live_signal: str = "",
                            live_confidence: float = 0, live_outcome: str = ""):
        conn = self._get_conn()
        conn.execute(
            """INSERT INTO ghost_signals (ticker, signal, confidence, version,
               live_signal, live_confidence, live_outcome)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (ticker, signal, confidence, version, live_signal, live_confidence, live_outcome),
        )
        conn.commit()
        conn.close()

    def get_portfolio_history(self, limit: int = 200) -> list:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM portfolio ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return reversed([dict(r) for r in rows])

    def compute_total_pnl_from_db(self, get_current_price=None) -> dict:
        """
        Issue 7 fix: compute total_pnl from DB (source of truth) instead of
        trusting the in-memory state of PaperBroker (which can be corrupted by
        duplicate orchestrators or state-file race conditions on the server).

        Formula:
            realized_pnl   = SUM(pnl_usd) for status='closed' AND exit_reason != 'lost_recovery'
            unrealized_pnl = SUM( (current - entry)/entry * size * sign ) for status='open'
            total_pnl      = realized_pnl + unrealized_pnl

        Args:
            get_current_price: callable(ticker: str) -> float | None.
                If None or returns None for a ticker, that trade's unrealized
                PnL contributes 0 (graceful degradation, not an error).

        Returns:
            dict with keys: total_pnl, realized_pnl, unrealized_pnl, n_open, n_closed
        """
        conn = self._get_conn()
        try:
            realized_row = conn.execute("""
                SELECT COALESCE(SUM(pnl_usd), 0) FROM trades
                WHERE status='closed' AND exit_reason != 'lost_recovery'
            """).fetchone()
            realized = float(realized_row[0] or 0.0)

            n_closed = int(conn.execute(
                "SELECT COUNT(*) FROM trades WHERE status='closed' AND exit_reason != 'lost_recovery'"
            ).fetchone()[0])

            open_rows = conn.execute("""
                SELECT ticker, signal, entry_price, position_size_usd
                FROM trades WHERE status='open'
            """).fetchall()

            unrealized = 0.0
            for r in open_rows:
                entry_price = float(r["entry_price"]) or 0.0
                size_usd = float(r["position_size_usd"]) or 0.0
                if entry_price <= 0 or size_usd <= 0:
                    continue
                current = None
                if get_current_price is not None:
                    try:
                        current = get_current_price(r["ticker"])
                    except Exception:
                        current = None
                if current is None or current <= 0:
                    # No live price → can't mark to market → 0 contribution.
                    # Better to under-report than fabricate a number.
                    continue
                sign = 1 if r["signal"] == "LONG" else -1
                pnl = (current - entry_price) / entry_price * size_usd * sign
                unrealized += pnl

            return {
                "total_pnl": round(realized + unrealized, 2),
                "realized_pnl": round(realized, 2),
                "unrealized_pnl": round(unrealized, 2),
                "n_open": len(open_rows),
                "n_closed": n_closed,
            }
        finally:
            conn.close()

    def record_heartbeat(self, motor: str, status: str = "ok", message: str = ""):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO motor_heartbeat (motor, status, message) VALUES (?, ?, ?)",
            (motor, status, message),
        )
        conn.commit()
        conn.close()

    def get_heartbeats(self, motors: list = None, minutes: int = 60) -> list:
        conn = self._get_conn()
        if motors:
            placeholders = ",".join("?" for _ in motors)
            rows = conn.execute(
                f"SELECT motor, status, message, timestamp FROM motor_heartbeat "
                f"WHERE motor IN ({placeholders}) AND timestamp >= datetime('now', '-' || ? || ' minutes') "
                f"ORDER BY motor, timestamp DESC",
                [*motors, minutes],
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT motor, status, message, timestamp FROM motor_heartbeat "
                "WHERE timestamp >= datetime('now', '-' || ? || ' minutes') "
                "ORDER BY motor, timestamp DESC",
                (minutes,),
            ).fetchall()
        conn.close()
        result = {}
        for r in rows:
            m = r["motor"]
            if m not in result:
                result[m] = {"motor": m, "last_status": r["status"], "last_message": r["message"], "last_run": r["timestamp"]}
        return list(result.values())

    def prune_signals(self, days: int = 90):
        conn = self._get_conn()
        conn.execute("DELETE FROM signals WHERE timestamp < datetime('now', '-' || ? || ' days')", (days,))
        conn.execute("DELETE FROM motor_heartbeat WHERE timestamp < datetime('now', '-' || ? || ' days')", (days,))
        conn.commit()
        conn.close()
