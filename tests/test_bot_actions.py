import sys
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import numpy as np


# ═══════════════════════════════════════════════════════════════════
# PAPER BROKER — APERTURA Y CIERRE
# ═══════════════════════════════════════════════════════════════════

class TestPaperBrokerOpenClose:
    def test_open_long_position(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        trade = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        assert trade is not None
        assert "error" not in trade
        assert trade["signal"] == "LONG"
        assert trade["size_usd"] == 50
        assert trade["stop_loss_pct"] == 2
        assert trade["take_profit_pct"] == 5
        assert trade["entry_price"] > 0
        assert len(pb.positions) == 1

    def test_open_short_position(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        trade = pb.open_position("forex", "EURUSD=X", "SHORT", 1.10, 50, 2, 5)
        assert trade is not None
        assert trade["signal"] == "SHORT"

    def test_close_position_tp_long(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        trade = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        result = pb.close_position(trade["id"], 1.12, "take_profit")
        assert result is not None
        assert result["reason"] == "take_profit"
        assert result["pnl_usd"] > 0

    def test_close_position_sl_short(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        trade = pb.open_position("forex", "EURUSD=X", "SHORT", 1.10, 50, 2, 5)
        result = pb.close_position(trade["id"], 1.15, "stop_loss")
        assert result is not None
        assert result["reason"] == "stop_loss"
        assert result["pnl_usd"] < 0

    def test_close_position_not_found(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        result = pb.close_position("inexistente", 1.10, "manual")
        assert result is None

    def test_insufficient_balance(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(10, state_path=str(tmp_path / "pb.json"))
        trade = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 999, 2, 5)
        assert "error" not in trade
        assert trade["size_usd"] <= 10 * 0.95

    def test_max_total_exposure(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.max_total_exposure_pct = 0.10
        trade1 = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        assert "error" not in trade1
        trade2 = pb.open_position("forex", "GBPUSD=X", "LONG", 1.30, 50, 2, 5)
        assert "error" not in trade2
        trade3 = pb.open_position("forex", "USDJPY=X", "LONG", 110, 50, 2, 5)
        assert trade3.get("error") == "max_total_exposure"


# ═══════════════════════════════════════════════════════════════════
# STOP-LOSS / TAKE-PROFIT (SL/TP automático)
# ═══════════════════════════════════════════════════════════════════

class TestStopLossTakeProfit:
    def test_sl_long_triggered(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        closed = pb.check_stops({"EURUSD=X": 1.07})
        assert len(closed) == 1
        assert closed[0]["reason"] == "stop_loss"

    def test_sl_short_triggered(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.open_position("forex", "EURUSD=X", "SHORT", 1.10, 50, 2, 5)
        closed = pb.check_stops({"EURUSD=X": 1.13})
        assert len(closed) == 1
        assert closed[0]["reason"] == "stop_loss"

    def test_tp_long_triggered(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 5, 10)
        closed = pb.check_stops({"EURUSD=X": 1.22})
        assert len(closed) == 1
        assert closed[0]["reason"] == "take_profit"

    def test_tp_short_triggered(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.open_position("forex", "EURUSD=X", "SHORT", 1.10, 50, 5, 10)
        closed = pb.check_stops({"EURUSD=X": 0.98})
        assert len(closed) == 1
        assert closed[0]["reason"] == "take_profit"

    def test_no_sl_no_tp_when_price_stable(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        closed = pb.check_stops({"EURUSD=X": 1.09})
        assert len(closed) == 0

    def test_multiple_positions_one_triggered(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        pb.open_position("forex", "GBPUSD=X", "LONG", 1.30, 50, 2, 5)
        closed = pb.check_stops({"EURUSD=X": 1.07, "GBPUSD=X": 1.29})
        assert len(closed) == 1


# ═══════════════════════════════════════════════════════════════════
# TIME-BASED EXIT (cierre por tiempo)
# ═══════════════════════════════════════════════════════════════════

class TestTimeExit:
    def test_time_exit_forex_old(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.set_time_exit_config({
            "forex": {"base_hours": 72, "profit_hours": 168, "loss_hours": 48, "stagnant_hours": 36}
        })
        pb.max_total_exposure_pct = 1.0
        pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        pb.positions[next(iter(pb.positions))]["entry_time"] = (
            datetime.now(timezone.utc) - timedelta(hours=200)
        ).isoformat()
        closed = pb.check_stops({"EURUSD=X": 1.10})
        assert len(closed) >= 1

    def test_time_exit_stocks_profit(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.set_time_exit_config({
            "stocks": {"base_hours": 72, "profit_hours": 120, "loss_hours": 36, "stagnant_hours": 24}
        })
        pb.max_total_exposure_pct = 1.0
        pb.open_position("stocks", "AAPL", "LONG", 100, 50, 2, 5)
        pid = next(iter(pb.positions))
        pb.positions[pid]["entry_time"] = (datetime.now(timezone.utc) - timedelta(hours=200)).isoformat()
        closed = pb.check_stops({"AAPL": 105})
        assert len(closed) == 1

    def test_time_exit_not_triggered_recent(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.set_time_exit_config({"default": {"base_hours": 72, "profit_hours": 120, "loss_hours": 48, "stagnant_hours": 36}})
        pb.max_total_exposure_pct = 1.0
        pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        pid = next(iter(pb.positions))
        pb.positions[pid]["entry_time"] = (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
        closed = pb.check_stops({"EURUSD=X": 1.10})
        assert len(closed) == 0


# ═══════════════════════════════════════════════════════════════════
# ENTRY FILTERS — SESIÓN, DÍA, CORRELACIÓN
# ═══════════════════════════════════════════════════════════════════

class TestEntryFilters:
    def test_session_forex_london(self):
        from execution import entry_filters
        result = entry_filters.session_hours("forex", 10)
        assert result is True

    def test_session_forex_sydney_blocked(self):
        from execution import entry_filters
        result = entry_filters.session_hours("forex", 4)
        assert result is False

    def test_session_stocks_market(self):
        from execution import entry_filters
        result = entry_filters.session_hours("stocks", 16)
        assert result is True

    def test_session_stocks_premarket(self):
        from execution import entry_filters
        result = entry_filters.session_hours("stocks", 12)
        assert result is False

    def test_session_polymarket_always(self):
        from execution import entry_filters
        result = entry_filters.session_hours("polymarket", 3)
        assert result is True

    def test_correlation_same_direction(self):
        from execution import entry_filters
        open_positions = [
            {"market": "forex", "ticker": "EURUSD=X", "signal": "LONG"},
        ]
        result = entry_filters.correlation_check(open_positions, "forex", "GBPUSD=X", "LONG")
        assert result is False

    def test_correlation_diff_direction(self):
        from execution import entry_filters
        open_positions = [{"market": "forex", "ticker": "EURUSD=X", "signal": "LONG"}]
        result = entry_filters.correlation_check(open_positions, "forex", "GBPUSD=X", "SHORT")
        assert result is True

    def test_correlation_diff_market(self):
        from execution import entry_filters
        open_positions = [{"market": "forex", "ticker": "EURUSD=X", "signal": "LONG"}]
        result = entry_filters.correlation_check(open_positions, "stocks", "SPY", "LONG")
        assert result is True


# ═══════════════════════════════════════════════════════════════════
# RISK ENGINE — KELLY, POSITION SIZING, CIRCUIT BREAKERS
# ═══════════════════════════════════════════════════════════════════

class TestRiskEngine:
    def test_kelly_fraction(self):
        from execution.risk_engine import RiskEngine
        re = RiskEngine()
        k = re.kelly_fraction(win_rate=0.6, avg_win=100, avg_loss=50)
        assert k > 0
        assert k < 0.5

    def test_kelly_negative(self):
        from execution.risk_engine import RiskEngine
        re = RiskEngine()
        k = re.kelly_fraction(win_rate=0.3, avg_win=50, avg_loss=100)
        assert k == 0

    def test_position_size(self):
        from execution.risk_engine import RiskEngine
        re = RiskEngine()
        re.balance = 1000
        size = re.position_size(entry_price=100, stop_price=95, kelly_f=0.02)
        assert size > 0
        assert size <= 50  # 5% max

    def test_daily_loss_breached(self):
        from execution.risk_engine import RiskEngine
        re = RiskEngine(initial_balance=1000)
        re.daily_pnl = -150
        assert re.check_daily_loss() is False

    def test_daily_loss_ok(self):
        from execution.risk_engine import RiskEngine
        re = RiskEngine(initial_balance=1000)
        re.daily_pnl = -30
        assert re.check_daily_loss() is True

    def test_drawdown_breached(self):
        from execution.risk_engine import RiskEngine
        re = RiskEngine(initial_balance=1000)
        re.peak_balance = 1000
        re.balance = 800
        assert re.check_drawdown() is False

    def test_drawdown_ok(self):
        from execution.risk_engine import RiskEngine
        re = RiskEngine(initial_balance=1000)
        re.peak_balance = 1000
        re.balance = 950
        assert re.check_drawdown() is True

    def test_circuit_breakers_daily_loss(self):
        from execution.risk_engine import RiskEngine
        re = RiskEngine(initial_balance=1000)
        re.daily_pnl = -200
        can, reason = re.circuit_breakers()
        assert can is False
        assert "daily_loss" in reason

    def test_circuit_breakers_all_ok(self):
        from execution.risk_engine import RiskEngine
        re = RiskEngine(initial_balance=1000)
        can, reason = re.circuit_breakers()
        assert can is True


# ═══════════════════════════════════════════════════════════════════
# FUSION ENGINE — SEÑALES COMPUESTAS
# ═══════════════════════════════════════════════════════════════════

class TestFusionEngine:
    def test_fusion_long(self):
        from engine.fusion import FusionEngine
        cfg = {"layers": {"technical": {"enabled": True, "weight_stocks": 1.0}}}
        fe = FusionEngine(cfg)
        result = fe.fuse({"technical": {"signal": "LONG", "score": 70}}, "stocks")
        assert result["signal"] == "LONG"
        assert result["confidence"] > 0

    def test_fusion_short(self):
        from engine.fusion import FusionEngine
        cfg = {"layers": {"technical": {"enabled": True, "weight_stocks": 1.0}}}
        fe = FusionEngine(cfg)
        result = fe.fuse({"technical": {"signal": "SHORT", "score": 30}}, "stocks")
        assert result["signal"] == "SHORT"

    def test_fusion_wait_neutral(self):
        from engine.fusion import FusionEngine
        cfg = {"layers": {"technical": {"enabled": True, "weight_stocks": 1.0}}}
        fe = FusionEngine(cfg)
        result = fe.fuse({"technical": {"signal": "WAIT", "score": 50}}, "stocks")
        assert result["signal"] == "WAIT"

    def test_fusion_no_layers(self):
        from engine.fusion import FusionEngine
        cfg = {"layers": {}}
        fe = FusionEngine(cfg)
        result = fe.fuse({}, "stocks")
        assert result["signal"] == "WAIT"

    def test_fusion_no_weights(self):
        from engine.fusion import FusionEngine
        cfg = {"layers": {"technical": {"enabled": True, "weight_stocks": 0.0}}}
        fe = FusionEngine(cfg)
        result = fe.fuse({"technical": {"signal": "LONG", "score": 80}}, "stocks")
        assert result["signal"] == "WAIT"


# ═══════════════════════════════════════════════════════════════════
# DEEPSEEK DECIDER — SIN API KEY (FALLBACK)
# ═══════════════════════════════════════════════════════════════════

class TestDeepSeekFallback:
    def test_decide_without_api_key_returns_wait(self):
        from engine.decider import DeepSeekDecider
        d = DeepSeekDecider(api_key="")
        result = d.decide("forex", "EURUSD=X",
                          {"signal": "LONG", "score": 65, "confidence": 70},
                          {"EURUSD=X": {"price": 1.10}},
                          {"technical": {"signal": "LONG", "score": 70}})
        assert result["signal"] == "WAIT"


# ═══════════════════════════════════════════════════════════════════
# PERFILES NORMAL vs FAST
# ═══════════════════════════════════════════════════════════════════

class TestProfiles:
    def test_normal_profile_sl_tp(self):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(Path(__file__).parent.parent / "data" / "cache" / "pb_test.json"))
        pb.max_total_exposure_pct = 1.0
        trade = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        assert "error" not in trade
        assert trade["stop_loss_pct"] == 2
        assert trade["take_profit_pct"] == 5

    def test_fast_profile_sl_tp(self):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(Path(__file__).parent.parent / "data" / "cache" / "pb_fast_test.json"))
        pb.max_total_exposure_pct = 1.0
        trade = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 0.5, 1.5)
        assert "error" not in trade
        assert trade["stop_loss_pct"] == 0.5
        assert trade["take_profit_pct"] == 1.5


# ═══════════════════════════════════════════════════════════════════
# GET SUMMARY — RESULTADOS DEL PAPER BROKER
# ═══════════════════════════════════════════════════════════════════

class TestGetSummary:
    def test_summary_empty(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        s = pb.get_summary()
        assert s["balance"] == 1000
        assert s["open_positions"] == 0
        assert s["total_trades"] == 0

    def test_summary_after_open(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        s = pb.get_summary()
        assert s["open_positions"] == 1
        assert s["exposure_usd"] > 0

    def test_summary_after_close(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        t = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        pb.close_position(t["id"], 1.13, "take_profit")
        s = pb.get_summary()
        assert s["total_trades"] == 1
        assert s["winning_trades"] == 1
        assert s["win_rate"] == 100.0


# ═══════════════════════════════════════════════════════════════════
# STATE PERSISTENCE — GUARDAR Y CARGAR
# ═══════════════════════════════════════════════════════════════════

class TestStatePersistence:
    def test_state_persistence(self, tmp_path):
        from execution.paper_broker import PaperBroker
        path = str(tmp_path / "state.json")
        pb1 = PaperBroker(1000, state_path=path)
        pb1.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        pb2 = PaperBroker(1000, state_path=path)
        assert pb2.balance < 1000  # deduct commission
        assert len(pb2.positions) == 1


# ═══════════════════════════════════════════════════════════════════
# EDGE CASES
# ═══════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_open_with_zero_balance(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(0, state_path=str(tmp_path / "pb.json"))
        trade = pb.open_position("forex", "EURUSD=X", "LONG", 1.10, 50, 2, 5)
        assert trade.get("error") == "sin_balance"

    def test_close_already_closed(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        result = pb.close_position("no_existe", 1.10, "manual")
        assert result is None

    def test_check_stops_empty(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "pb.json"))
        closed = pb.check_stops({"EURUSD=X": 1.10})
        assert len(closed) == 0

    def test_load_state_nonexistent(self, tmp_path):
        from execution.paper_broker import PaperBroker
        pb = PaperBroker(1000, state_path=str(tmp_path / "no_existe.json"))
        assert pb.balance == 1000
        assert len(pb.positions) == 0
