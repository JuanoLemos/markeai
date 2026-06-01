import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_stock_data():
    dates = pd.date_range("2026-01-01", periods=200, freq="h")
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(200) * 0.5)
    return pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.005,
        "low": close * 0.995,
        "close": close,
        "volume": np.random.randint(1000000, 5000000, 200),
    }, index=dates)


@pytest.fixture
def sample_order_book():
    return {
        "bids": [
            {"price": "0.55", "size": "5000"},
            {"price": "0.54", "size": "3000"},
            {"price": "0.53", "size": "2000"},
            {"price": "0.52", "size": "1000"},
            {"price": "0.51", "size": "500"},
        ],
        "asks": [
            {"price": "0.56", "size": "2000"},
            {"price": "0.57", "size": "1500"},
            {"price": "0.58", "size": "1000"},
            {"price": "0.59", "size": "500"},
            {"price": "0.60", "size": "200"},
        ],
    }


@pytest.fixture
def sample_news_data():
    return {
        "count": 20,
        "bullish": 10,
        "bearish": 5,
        "neutral": 5,
        "bullish_pct": 50.0,
        "bearish_pct": 25.0,
        "top_headlines": ["BTC rally", "Fed holds rates", "Market up"],
    }


class TestTechnicalAnalyzer:
    def test_import(self):
        from analyzers.technical import TechnicalAnalyzer
        assert TechnicalAnalyzer is not None

    def test_analyze_with_data(self, sample_stock_data):
        from analyzers.technical import TechnicalAnalyzer
        a = TechnicalAnalyzer()
        result = a.analyze(sample_stock_data)
        assert isinstance(result, dict)
        assert "signal" in result
        assert "score" in result
        assert result["signal"] in ("LONG", "SHORT", "WAIT")
        assert 0 <= result["score"] <= 100

    def test_analyze_empty(self):
        from analyzers.technical import TechnicalAnalyzer
        a = TechnicalAnalyzer()
        result = a.analyze(pd.DataFrame())
        assert result["signal"] == "WAIT"

    def test_analyze_insufficient_data(self):
        from analyzers.technical import TechnicalAnalyzer
        a = TechnicalAnalyzer()
        small = pd.DataFrame({"close": [100, 101]}, index=pd.date_range("2026-01-01", periods=2, freq="h"))
        result = a.analyze(small)
        assert result["signal"] == "WAIT"


class TestOrderBookAnalyzer:
    def test_analyze(self, sample_order_book):
        from analyzers.orderbook import OrderBookAnalyzer
        a = OrderBookAnalyzer()
        result = a.analyze(sample_order_book)
        assert result["signal"] in ("LONG", "SHORT", "WAIT")
        assert "imbalance" in str(result.get("details", {}))
        assert result["details"]["imbalance"] > 1.0

    def test_analyze_empty(self):
        from analyzers.orderbook import OrderBookAnalyzer
        a = OrderBookAnalyzer()
        result = a.analyze({})
        assert result["signal"] == "WAIT"

    def test_analyze_error(self):
        from analyzers.orderbook import OrderBookAnalyzer
        a = OrderBookAnalyzer()
        result = a.analyze({"error": "no data"})
        assert result["signal"] == "WAIT"


class TestSentimentAnalyzer:
    def test_analyze_bullish(self, sample_news_data):
        from analyzers.sentiment import SentimentAnalyzer
        a = SentimentAnalyzer()
        result = a.analyze(sample_news_data)
        assert result["signal"] in ("LONG", "SHORT", "WAIT")

    def test_analyze_empty(self):
        from analyzers.sentiment import SentimentAnalyzer
        a = SentimentAnalyzer()
        result = a.analyze({})
        assert result["signal"] == "WAIT"

    def test_analyze_neutral(self):
        from analyzers.sentiment import SentimentAnalyzer
        a = SentimentAnalyzer()
        neutral = {"count": 10, "bullish_pct": 30, "bearish_pct": 30, "neutral_pct": 40, "top_headlines": []}
        result = a.analyze(neutral)
        assert result["signal"] in ("LONG", "SHORT", "WAIT")


class TestOnChainAnalyzer:
    def test_analyze_empty(self):
        from analyzers.onchain import OnChainAnalyzer
        a = OnChainAnalyzer()
        result = a.analyze()
        assert result["signal"] == "WAIT"

    def test_analyze_with_data(self):
        from analyzers.onchain import OnChainAnalyzer
        a = OnChainAnalyzer()
        result = a.analyze({"trade_history": [], "market_details": {"volume24hr": "50000"}})
        assert result["signal"] in ("LONG", "SHORT", "WAIT")


class TestFundamentalAnalyzer:
    def test_analyze_empty(self):
        from analyzers.fundamental import FundamentalAnalyzer
        a = FundamentalAnalyzer()
        result = a.analyze("SPY")
        assert result["signal"] == "WAIT"

    def test_analyze_with_price_data(self):
        from analyzers.fundamental import FundamentalAnalyzer
        a = FundamentalAnalyzer()
        result = a.analyze("SPY", {"volume_24h": 1000000, "avg_volume_20d": 500000, "change_24h_pct": 2.5})
        assert result["signal"] in ("LONG", "SHORT", "WAIT")

    def test_etf_bullish(self):
        from analyzers.fundamental import FundamentalAnalyzer
        a = FundamentalAnalyzer()
        fund_data = {
            "quoteType": "ETF",
            "totalAssets": 50e9,
            "expenseRatio": 0.0003,
            "ytdReturn": 0.15,
            "averageVolume": 10e6,
        }
        price_data = {"price": 450, "volume_24h": 25e6, "change_24h_pct": 2.5}
        result = a.analyze("SPY", price_data, fund_data)
        assert result["score"] > 50
        assert result["signal"] in ("LONG", "WAIT")

    def test_etf_bearish(self):
        from analyzers.fundamental import FundamentalAnalyzer
        a = FundamentalAnalyzer()
        fund_data = {
            "quoteType": "ETF",
            "totalAssets": 50e6,
            "expenseRatio": 0.015,
            "ytdReturn": -0.12,
            "averageVolume": 500_000,
        }
        price_data = {"price": 50, "volume_24h": 100_000, "change_24h_pct": -4.0}
        result = a.analyze("QQQ", price_data, fund_data)
        assert result["score"] < 50
        assert result["signal"] in ("SHORT", "WAIT")

    def test_etf_detected_by_heuristic(self):
        from analyzers.fundamental import FundamentalAnalyzer
        a = FundamentalAnalyzer()
        fund_data = {
            "averageVolume": 5e6,
            "sector": "Technology",
        }
        price_data = {"price": 200, "volume_24h": 50e6, "change_24h_pct": 1.0}
        result = a.analyze("XLK", price_data, fund_data)
        assert "details" in result
        assert result["score"] != 50 or result["signal"] == "WAIT"


class TestMacroAnalyzer:
    def test_analyze_forex(self):
        from analyzers.macro import MacroAnalyzer
        a = MacroAnalyzer()
        result = a.analyze(dxy=105, vix=12, market_type="forex")
        assert result["signal"] in ("LONG", "SHORT", "WAIT")
        assert "dxy" in result.get("details", {})

    def test_analyze_stocks(self):
        from analyzers.macro import MacroAnalyzer
        a = MacroAnalyzer()
        result = a.analyze(vix=15, market_type="stocks")
        assert result["signal"] in ("LONG", "SHORT", "WAIT")


class TestCrossAssetAnalyzer:
    def test_analyze_empty(self):
        from analyzers.cross_asset import CrossAssetAnalyzer
        a = CrossAssetAnalyzer()
        result = a.analyze()
        assert result["signal"] == "WAIT"

    def test_analyze_with_data(self):
        from analyzers.cross_asset import CrossAssetAnalyzer
        a = CrossAssetAnalyzer()
        result = a.analyze({
            "stocks": {
                "SPY": {"change_24h_pct": 1.0},
                "QQQ": {"change_24h_pct": 3.5},
            },
            "forex": {
                "EURUSD=X": {"change_24h_pct": 0.2},
                "USDJPY=X": {"change_24h_pct": -0.1},
            },
        })
        assert result["signal"] in ("LONG", "SHORT", "WAIT")


class TestFusionEngine:
    def test_import(self):
        from engine.fusion import FusionEngine
        config = {
            "layers": {
                "technical": {"enabled": True, "weight_polymarket": 0.5},
                "sentiment": {"enabled": True, "weight_polymarket": 0.5},
            }
        }
        fe = FusionEngine(config)
        assert fe is not None

    def test_fuse(self):
        from engine.fusion import FusionEngine
        config = {
            "layers": {
                "technical": {"enabled": True, "weight_polymarket": 0.5},
                "sentiment": {"enabled": True, "weight_polymarket": 0.5},
            }
        }
        fe = FusionEngine(config)
        result = fe.fuse({
            "technical": {"signal": "LONG", "score": 70, "reasoning": "bullish"},
            "sentiment": {"signal": "LONG", "score": 60, "reasoning": "positive"},
        }, "polymarket")
        assert result["signal"] in ("LONG", "SHORT", "WAIT")
        assert "confidence" in result


class TestPaperBroker:
    def test_import(self):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker()
        assert pb is not None

    def test_open_and_close(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(initial_balance=1000, state_path=str(tmp_path / "pb.json"))
        trade = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        assert trade is not None
        assert "error" not in trade
        result = pb.close_position(trade["id"], 1.12, "take_profit")
        assert result is not None
        assert "pnl_usd" in result

    def test_size_capped_to_max_position(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(initial_balance=10, state_path=str(tmp_path / "pb.json"))
        trade = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 500, 2, 5)
        assert trade is not None
        expected = 10 * 0.05  # 5% of balance
        assert trade["size_usd"] == pytest.approx(expected, rel=0.1)


class TestDeepSeekDecider:
    def test_import(self):
        from engine.decider import DeepSeekDecider
        d = DeepSeekDecider(api_key="test")
        assert d is not None

    def test_decide_without_api_key(self, monkeypatch):
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        from engine.decider import DeepSeekDecider
        d = DeepSeekDecider(api_key="")
        result = d.decide("forex", "EURUSD=X",
                          {"signal": "LONG", "score": 65, "confidence": 70},
                          {"EURUSD=X": {"price": 1.10}},
                          {"technical": {"signal": "LONG", "score": 70, "reasoning": "trend"}})
        assert result["signal"] == "WAIT"
        assert "no_api_key" in result.get("reasoning", "")


class TestBacktester:
    def test_import(self):
        from learning.backtest import Backtester
        bt = Backtester()
        assert bt is not None

    def test_run_insufficient_data(self):
        from learning.backtest import Backtester
        bt = Backtester()
        result = bt.run("forex", "EURUSD=X", pd.DataFrame())
        assert "error" in result

    def test_run_with_data(self, sample_stock_data):
        from learning.backtest import Backtester
        bt = Backtester()
        result = bt.run("stocks", "SPY", sample_stock_data)
        assert isinstance(result, dict)
        assert "trades" in result


class TestStrategyEvolver:
    def test_import(self):
        from learning.strategy_evolver import StrategyEvolver
        se = StrategyEvolver()
        assert se is not None

    def test_evolve_not_enough(self):
        from learning.strategy_evolver import StrategyEvolver
        se = StrategyEvolver()
        result = se.evolve([], {})
        assert "not_enough_trades" in result


class TestTradeJournal:
    def test_import(self):
        from learning.journal import TradeJournal
        assert TradeJournal is not None

    def test_record_trade(self, tmp_path):
        from learning.journal import TradeJournal
        path = str(tmp_path / "journal.md")
        tj = TradeJournal(path)
        tj.record_trade({
            "market": "forex", "ticker": "EURUSD=X", "signal": "LONG",
            "entry_price": 1.10, "exit_price": 1.12, "pnl_pct": 1.8,
            "reason": "take_profit", "entry_time": "2026-01-01T00:00:00",
            "exit_time": "2026-01-01T12:00:00",
        })
        summary = tj.generate_summary()
        assert "EURUSD" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
