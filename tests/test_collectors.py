import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestYFinanceCollector:
    def test_import(self):
        from data.collector_yfinance import YFinanceCollector
        c = YFinanceCollector()
        assert c is not None

    def test_get_current_price_spy(self):
        from data.collector_yfinance import YFinanceCollector
        c = YFinanceCollector()
        price = c.get_current_price("SPY")
        if price is not None:
            assert isinstance(price, (int, float))
            assert price > 0

    def test_get_forex_pairs(self):
        from data.collector_yfinance import YFinanceCollector
        c = YFinanceCollector()
        result = c.get_forex_pairs()
        assert isinstance(result, dict)
        for pair, data in result.items():
            assert "price" in data
            assert "change_24h_pct" in data

    def test_get_stocks(self):
        from data.collector_yfinance import YFinanceCollector
        c = YFinanceCollector()
        result = c.get_stocks(["SPY"])
        assert isinstance(result, dict)

    def test_get_dxy(self):
        from data.collector_yfinance import YFinanceCollector
        c = YFinanceCollector()
        dxy = c.get_dxy()
        if dxy is not None:
            assert isinstance(dxy, (int, float))

    def test_get_vix(self):
        from data.collector_yfinance import YFinanceCollector
        c = YFinanceCollector()
        vix = c.get_vix()
        if vix is not None:
            assert isinstance(vix, (int, float))


class TestPolymarketCollector:
    def test_import(self):
        from data.collector_polymarket import PolymarketCollector
        c = PolymarketCollector()
        assert c is not None

    def test_get_active_markets(self):
        from data.collector_polymarket import PolymarketCollector
        c = PolymarketCollector()
        markets = c.get_active_markets(limit=5)
        assert isinstance(markets, list)


class TestNewsCollector:
    def test_import(self):
        from data.collector_news import NewsCollector
        c = NewsCollector()
        assert c is not None

    def test_get_sentiment_summary_empty(self):
        from data.collector_news import NewsCollector
        c = NewsCollector()
        result = c.get_sentiment_summary("all", 24)
        assert isinstance(result, dict)
        assert "count" in result
        assert "bullish" in result


class TestDatabase:
    @pytest.fixture
    def db(self, tmp_path):
        from data.database import Database
        return Database(str(tmp_path / "test.db"))

    def test_import(self):
        from data.database import Database
        assert Database is not None

    def test_insert_and_query_trade(self, db):
        tid = db.insert_trade({
            "market": "forex",
            "ticker": "EURUSD=X",
            "signal": "LONG",
            "entry_price": 1.10,
            "position_size_usd": 100,
        })
        assert tid > 0
        open_trades = db.get_open_trades()
        assert len(open_trades) >= 1

    def test_insert_signal(self, db):
        db.insert_signal({
            "market": "stocks",
            "ticker": "SPY",
            "decision": "WAIT",
            "confidence": 50,
            "layer_scores": {"technical": 50},
            "reasoning": "test",
        })
        signals = db.get_recent_signals(5)
        assert len(signals) >= 1

    def test_portfolio_summary(self, db):
        summary = db.get_portfolio_summary()
        assert "open_positions" in summary
        assert "total_pnl_usd" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
