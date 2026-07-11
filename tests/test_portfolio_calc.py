"""
test_portfolio_calc.py — Regression test for Issue 7 (CRITICAL):
  `portfolio.total_pnl` reports fictional inflated PnL when PaperBroker's
  in-memory self.balance is corrupted (typically by Issue 6: duplicate
  orchestrators or state-file race conditions on the server).

The fix introduces Database.compute_total_pnl_from_db() which derives the
total_pnl directly from the trades table using live prices, ignoring the
in-memory broker state. This file verifies that the new function:
  1. Sums closed-trade pnl_usd correctly (realized)
  2. Marks-to-market open positions using the provided price source
  3. Excludes exit_reason='lost_recovery' trades from realized PnL
  4. Returns gracefully (unrealized=0) when no price is available
  5. Detects the exact pattern that produced the bug (+$10k on $1k account)
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.database import Database


def _fresh_db():
    """Create a fresh test DB in temp. Returns (Database, path)."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    return Database(db_path=path), path


def _insert_trade(db, *, market, ticker, signal, entry_price, size_usd,
                  status="open", pnl_usd=None, exit_reason=None):
    """Helper: insert one trade and return its id."""
    tid = db.insert_trade({
        "market": market,
        "ticker": ticker,
        "signal": signal,
        "entry_price": entry_price,
        "position_size_usd": size_usd,
        "stop_loss": entry_price * 0.95,
        "take_profit": entry_price * 1.10,
        "confidence": 50,
        "strategy_used": "test",
    })
    if status == "closed" and pnl_usd is not None:
        db.close_trade(tid, entry_price * 1.05, exit_reason or "tp", pnl_usd, 5.0)
    elif status == "closed" and exit_reason == "lost_recovery":
        db.mark_lost_recovery(tid, "2026-07-10T12:00:00+00:00")
    return tid


class TestComputeTotalPnlFromDB:
    def test_empty_db_returns_zero(self):
        db, path = _fresh_db()
        try:
            result = db.compute_total_pnl_from_db(get_current_price=lambda t: 100.0)
            assert result["total_pnl"] == 0.0
            assert result["realized_pnl"] == 0.0
            assert result["unrealized_pnl"] == 0.0
            assert result["n_open"] == 0
            assert result["n_closed"] == 0
        finally:
            os.unlink(path)

    def test_realized_pnl_only(self):
        """3 closed trades with valid pnl_usd. Total = sum of those pnls."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="AAPL",
                          signal="LONG", entry_price=100.0, size_usd=50.0,
                          status="closed", pnl_usd=10.0, exit_reason="tp")
            _insert_trade(db, market="normal_stocks", ticker="MSFT",
                          signal="LONG", entry_price=200.0, size_usd=50.0,
                          status="closed", pnl_usd=-5.0, exit_reason="sl")
            _insert_trade(db, market="normal_forex", ticker="EURUSD=X",
                          signal="SHORT", entry_price=1.10, size_usd=100.0,
                          status="closed", pnl_usd=20.0, exit_reason="tp")
            result = db.compute_total_pnl_from_db(get_current_price=lambda t: None)
            assert result["realized_pnl"] == 25.0
            assert result["total_pnl"] == 25.0
            assert result["n_closed"] == 3
            assert result["n_open"] == 0
        finally:
            os.unlink(path)

    def test_lost_recovery_excluded(self):
        """Closed trades with exit_reason='lost_recovery' MUST NOT contribute to realized PnL."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="AAPL",
                          signal="LONG", entry_price=100.0, size_usd=50.0,
                          status="closed", pnl_usd=10.0, exit_reason="tp")
            _insert_trade(db, market="normal_stocks", ticker="MSFT",
                          signal="LONG", entry_price=200.0, size_usd=50.0,
                          status="closed", exit_reason="lost_recovery")
            result = db.compute_total_pnl_from_db(get_current_price=lambda t: None)
            # Only the first trade's pnl counts (10.0), lost_recovery is excluded
            assert result["realized_pnl"] == 10.0
            assert result["n_closed"] == 1
        finally:
            os.unlink(path)

    def test_unrealized_long_with_profit(self):
        """1 open LONG. current > entry → profit."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="AAPL",
                          signal="LONG", entry_price=100.0, size_usd=50.0)
            result = db.compute_total_pnl_from_db(
                get_current_price=lambda t: 110.0 if t == "AAPL" else None
            )
            # (110-100)/100 * 50 = 5.0
            assert result["unrealized_pnl"] == 5.0
            assert result["total_pnl"] == 5.0
            assert result["n_open"] == 1
        finally:
            os.unlink(path)

    def test_unrealized_long_with_loss(self):
        """1 open LONG. current < entry → loss."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="AAPL",
                          signal="LONG", entry_price=100.0, size_usd=50.0)
            result = db.compute_total_pnl_from_db(
                get_current_price=lambda t: 90.0 if t == "AAPL" else None
            )
            # (90-100)/100 * 50 = -5.0
            assert result["unrealized_pnl"] == -5.0
        finally:
            os.unlink(path)

    def test_unrealized_short_with_profit(self):
        """1 open SHORT. current < entry → profit (sign=-1)."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="TSLA",
                          signal="SHORT", entry_price=200.0, size_usd=100.0)
            result = db.compute_total_pnl_from_db(
                get_current_price=lambda t: 190.0 if t == "TSLA" else None
            )
            # (190-200)/200 * 100 * -1 = +5.0
            assert result["unrealized_pnl"] == 5.0
        finally:
            os.unlink(path)

    def test_unrealized_short_with_loss(self):
        """1 open SHORT. current > entry → loss (sign=-1)."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="TSLA",
                          signal="SHORT", entry_price=200.0, size_usd=100.0)
            result = db.compute_total_pnl_from_db(
                get_current_price=lambda t: 220.0 if t == "TSLA" else None
            )
            # (220-200)/200 * 100 * -1 = -10.0
            assert result["unrealized_pnl"] == -10.0
        finally:
            os.unlink(path)

    def test_no_price_falls_back_to_zero(self):
        """If get_current_price returns None for a ticker, that trade contributes 0."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="AAPL",
                          signal="LONG", entry_price=100.0, size_usd=50.0)
            _insert_trade(db, market="normal_stocks", ticker="MSFT",
                          signal="LONG", entry_price=200.0, size_usd=50.0)
            # Only AAPL has a price; MSFT returns None
            result = db.compute_total_pnl_from_db(
                get_current_price=lambda t: 110.0 if t == "AAPL" else None
            )
            # Only AAPL contributes: (110-100)/100 * 50 = 5.0
            assert result["unrealized_pnl"] == 5.0
        finally:
            os.unlink(path)

    def test_price_source_can_raise(self):
        """If get_current_price raises, the function must NOT crash the snapshot."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="AAPL",
                          signal="LONG", entry_price=100.0, size_usd=50.0)
            def bad_price(t):
                raise RuntimeError("yfinance timeout")
            result = db.compute_total_pnl_from_db(get_current_price=bad_price)
            # Raised → caught → trade skipped → unrealized=0
            assert result["unrealized_pnl"] == 0.0
        finally:
            os.unlink(path)

    def test_no_price_source_means_zero_unrealized(self):
        """If get_current_price is None, all open trades have unrealized_pnl=0 (graceful)."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="AAPL",
                          signal="LONG", entry_price=100.0, size_usd=50.0)
            result = db.compute_total_pnl_from_db(get_current_price=None)
            assert result["unrealized_pnl"] == 0.0
            assert result["total_pnl"] == 0.0
        finally:
            os.unlink(path)

    def test_combined_realized_plus_unrealized(self):
        """Mixed portfolio: 1 closed winner, 1 closed loser, 1 open LONG profit."""
        db, path = _fresh_db()
        try:
            _insert_trade(db, market="normal_stocks", ticker="AAPL",
                          signal="LONG", entry_price=100.0, size_usd=50.0,
                          status="closed", pnl_usd=10.0, exit_reason="tp")
            _insert_trade(db, market="normal_stocks", ticker="MSFT",
                          signal="LONG", entry_price=200.0, size_usd=50.0,
                          status="closed", pnl_usd=-5.0, exit_reason="sl")
            _insert_trade(db, market="normal_stocks", ticker="GOOGL",
                          signal="LONG", entry_price=150.0, size_usd=75.0)
            result = db.compute_total_pnl_from_db(
                get_current_price=lambda t: 165.0 if t == "GOOGL" else None
            )
            # realized = 10 + (-5) = 5
            # unrealized = (165-150)/150 * 75 = 7.5
            # total = 5 + 7.5 = 12.5
            assert result["realized_pnl"] == 5.0
            assert result["unrealized_pnl"] == 7.5
            assert result["total_pnl"] == 12.5
            assert result["n_closed"] == 2
            assert result["n_open"] == 1
        finally:
            os.unlink(path)

    def test_regression_fictional_pnl_pattern(self):
        """
        REGRESSION for the actual Issue 7 observed on the server:
          - Account $1000, 11 open positions, all stuck with pnl_usd=0
          - Old code (in-memory self.balance) reported total_pnl = +$10,736.92
          - New code (DB-derived) must report something close to the real MTM,
            NOT the fictional inflated value.

        We simulate the conditions and assert the new function does NOT
        return the corrupted value. Real PnL will be ~0 because open trades
        have no live-price delta from their entry.
        """
        db, path = _fresh_db()
        try:
            for i, ticker in enumerate(["SPY", "QQQ", "AAPL", "MSFT", "GOOGL",
                                         "AMZN", "IVV", "EEM", "IWM", "XLK", "TSLA"]):
                _insert_trade(db, market="normal_stocks", ticker=ticker,
                              signal="LONG", entry_price=100.0, size_usd=36.0)
            # If prices are at entry (no live movement), unrealized = 0
            result = db.compute_total_pnl_from_db(
                get_current_price=lambda t: 100.0
            )
            # The bug: old code reported +10736.92. New code must NOT match that.
            assert result["total_pnl"] != 10736.92, (
                "REGRESSION: new compute_total_pnl_from_db returned the "
                "fictional Issue 7 value — fix did not take effect."
            )
            # And with no movement, total should be ~0
            assert abs(result["total_pnl"]) < 1.0
            assert result["n_open"] == 11
            assert result["n_closed"] == 0
        finally:
            os.unlink(path)
