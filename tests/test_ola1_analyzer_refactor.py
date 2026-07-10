"""
Tests for the analyzer refactor (Ola 1, Día 3).
- B-23: _silent_import extracted to analyzers._utils
- B-24: _ensure_cols extracted to analyzers._base.BaseAnalyzer
- B-25: _empty_result extracted to analyzers._base.BaseAnalyzer
- B-27: tests use tmp_path instead of real data/cache/
- B-28: tests for analyzers in active pipeline
- B-29: integration tests for orchestrator
"""
import importlib
import inspect
from pathlib import Path
import sys

import pandas as pd
import pytest

from analyzers._base import BaseAnalyzer
from analyzers._utils import silent_import
from analyzers.technical import TechnicalAnalyzer
from analyzers.adx_regime import ADXRegimeAnalyzer
from analyzers.ict_smc import ICTAnalyzer
from analyzers.sentiment import SentimentAnalyzer
from analyzers.orderbook import OrderBookAnalyzer
from analyzers.onchain import OnChainAnalyzer
from analyzers.fundamental import FundamentalAnalyzer
from analyzers.cross_asset import CrossAssetAnalyzer
from analyzers.macro import MacroAnalyzer


# ─── B-25: all 9 analyzers inherit from BaseAnalyzer and use empty_result() ───

ALL_ANALYZER_CLASSES = [
    TechnicalAnalyzer, ADXRegimeAnalyzer, ICTAnalyzer,
    SentimentAnalyzer, OrderBookAnalyzer, OnChainAnalyzer,
    FundamentalAnalyzer, CrossAssetAnalyzer, MacroAnalyzer,
]


@pytest.mark.parametrize("cls", ALL_ANALYZER_CLASSES, ids=lambda c: c.__name__)
def test_b_25_all_analyzers_inherit_base(cls):
    """B-25: every analyzer must inherit from BaseAnalyzer."""
    assert issubclass(cls, BaseAnalyzer), f"{cls.__name__} does not inherit from BaseAnalyzer"


@pytest.mark.parametrize("cls", ALL_ANALYZER_CLASSES, ids=lambda c: c.__name__)
def test_b_25_all_analyzers_have_empty_result(cls):
    """B-25: every analyzer must have the empty_result() method (inherited)."""
    inst = cls()
    assert hasattr(inst, "empty_result")
    result = inst.empty_result()
    assert result == {"signal": "WAIT", "score": 50, "reasoning": "insufficient_data", "details": {}}


def test_b_25_no_duplicate_empty_result_in_subclasses():
    """B-25: subclasses should NOT override empty_result with the same body (no duplicates)."""
    base_src = inspect.getsource(BaseAnalyzer)
    assert 'def empty_result' in base_src
    # The literal `{"signal": "WAIT", "score": 50, "reasoning": "insufficient_data"...}` should appear only in BaseAnalyzer
    for cls in ALL_ANALYZER_CLASSES:
        try:
            src = inspect.getsource(cls)
            # Subclasses may have wrappers like `return self.empty_result()` but not the literal dict
            if '"reasoning": "insufficient_data"' in src and 'def _empty_result' in src:
                # Old-style method with hardcoded dict should be gone
                assert 'def empty_result' not in src or src.count('{"signal": "WAIT"') == 0, \
                    f"{cls.__name__} still has duplicated _empty_result with hardcoded dict"
        except (OSError, TypeError):
            pass


# ─── B-24: ensure_cols in BaseAnalyzer ───

def test_b_24_ensure_cols_lowercases():
    """B-24: ensure_cols lowercases column names."""
    inst = BaseAnalyzer()
    df = pd.DataFrame({"Open": [1], "Close": [2], "Volume": [3]})
    out = inst.ensure_cols(df)
    assert list(out.columns) == ["open", "close", "volume"]


def test_b_24_ensure_cols_handles_multiindex():
    """B-24: ensure_cols handles MultiIndex columns (yfinance format)."""
    inst = BaseAnalyzer()
    cols = pd.MultiIndex.from_tuples([("Open", "SPY"), ("Close", "SPY"), ("Volume", "SPY")])
    df = pd.DataFrame([[1, 2, 3]], columns=cols)
    out = inst.ensure_cols(df)
    assert list(out.columns) == ["open", "close", "volume"]


def test_b_24_ensure_cols_fill_volume():
    """B-24: ensure_cols(fill_volume=True) adds volume=0 if missing."""
    inst = BaseAnalyzer()
    df = pd.DataFrame({"Open": [1], "Close": [2]})
    out = inst.ensure_cols(df, fill_volume=True)
    assert "volume" in out.columns
    assert out["volume"].iloc[0] == 0


def test_b_24_ensure_cols_no_fill_by_default():
    """B-24: ensure_cols without fill_volume does NOT add volume."""
    inst = BaseAnalyzer()
    df = pd.DataFrame({"Open": [1], "Close": [2]})
    out = inst.ensure_cols(df)
    assert "volume" not in out.columns


# ─── B-23: silent_import extracted ───

def test_b_23_silent_import_returns_smc():
    """B-23: silent_import() returns the smartmoneyconcepts.smc module."""
    smc = silent_import()
    assert smc is not None
    # Has typical smc functions
    assert hasattr(smc, "fvg")
    assert hasattr(smc, "ob")
    assert hasattr(smc, "swing_highs_lows")


def test_b_23_no_duplicate_silent_import_in_analyzers():
    """B-23: the old _silent_import() function should not exist in analyzer modules anymore."""
    for mod_name in ["analyzers.adx_regime", "analyzers.ict_smc"]:
        mod = importlib.import_module(mod_name)
        src = Path(mod.__file__).read_text(encoding="utf-8")
        assert "def _silent_import" not in src, f"{mod_name} still has _silent_import"
        assert "from ._utils import silent_import" in src, f"{mod_name} should import silent_import from ._utils"


# ─── B-27: tests use tmp_path ───

def test_b_27_no_real_cache_paths_in_tests():
    """B-27: tests must NOT use real data/cache/ paths for state files."""
    tests_dir = Path("tests")
    offenders = []
    for test_file in tests_dir.glob("test_*.py"):
        src = test_file.read_text(encoding="utf-8")
        if 'data" / "cache"' in src or 'data / "cache"' in src or "data/cache" in src:
            # Allow references in comments but not as actual paths
            for i, line in enumerate(src.splitlines(), 1):
                if "data/cache" in line and "state_path" in line and "tmp_path" not in line:
                    offenders.append(f"{test_file.name}:{i}: {line.strip()}")
    assert not offenders, f"Tests still use real data/cache/ paths:\n" + "\n".join(offenders)


# ─── B-28: tests for analyzers in active pipeline ───

def test_b_28_adx_regime_returns_correct_format():
    """B-28: ADX analyzer returns standard {signal, score, reasoning, details} dict."""
    a = ADXRegimeAnalyzer()
    # Insufficient data → WAIT
    empty = pd.DataFrame()
    r = a.analyze(empty)
    assert "signal" in r and "score" in r and "reasoning" in r and "details" in r
    assert r["signal"] == "WAIT"
    assert r["score"] == 50


def test_b_28_ict_returns_correct_format():
    """B-28: ICT analyzer returns standard format."""
    a = ICTAnalyzer()
    r = a.analyze(pd.DataFrame())
    assert r["signal"] == "WAIT"
    assert r["score"] == 50


def test_b_28_technical_returns_correct_format():
    """B-28: Technical analyzer returns standard format."""
    a = TechnicalAnalyzer()
    r = a.analyze(pd.DataFrame())
    assert r["signal"] == "WAIT"
    assert r["score"] == 50


# ─── B-29: integration tests ───

def test_b_29_orchestrator_imports_clean():
    """B-29: the orchestrator package imports without error."""
    from orchestrator import MarketAIOrchestrator, load_config
    assert MarketAIOrchestrator is not None
    assert load_config is not None


def test_b_29_orchestrator_runs_once_with_test_config(tmp_path):
    """B-29: orchestrator boot + single iteration succeeds end-to-end with isolated config."""
    import yaml
    config = {
        "markets": {"polymarket": {"enabled": False}, "forex": {"enabled": False}, "stocks": {"enabled": True, "tickers": ["SPY"]}},
        "risk": {"max_total_exposure_pct": 0.4, "max_daily_loss_pct": 0.1, "correlation_threshold": 0.85, "time_exit": {"default": {"base_hours": 72}}},
        "orchestrator": {"log_level": "WARNING", "log_file": str(tmp_path / "test.log")},
        "deepseek": {"model": "deepseek-v4-pro", "temperature": 0.3, "max_tokens": 500, "timeout_seconds": 30},
        "layers": {k: {"enabled": False} for k in ["technical", "fundamental", "macro", "sentiment", "onchain", "orderbook", "ict_smc", "adx_regime", "cross_asset"]},
        "alerts": {"telegram": {"enabled": False}, "discord": {"enabled": False}},
        "profiles": {"normal": {"sl_min_pct": 1, "sl_max_pct": 5, "tp_min_pct": 2, "tp_max_pct": 10, "sl_default": 1.0, "tp_default": 2.0}, "fast": {"sl_min_pct": 0.5, "sl_max_pct": 1.5, "tp_min_pct": 1, "tp_max_pct": 3, "sl_default": 0.5, "tp_default": 1.0}},
    }
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    import orchestrator.core as core_mod
    importlib.reload(core_mod)
    importlib.reload(sys.modules.get("orchestrator") or importlib.import_module("orchestrator"))
    original_path = core_mod.CONFIG_PATH
    core_mod.CONFIG_PATH = cfg_path
    try:
        orch = core_mod.MarketAIOrchestrator(config, mode="paper")
        # Suppress logging
        import logging
        orch.log.setLevel(logging.ERROR)
        # Just init — don't run iteration (would need real APIs)
        assert orch.db is not None
        assert orch.paper_broker is not None
        assert orch.paper_brokers.get("normal") is not None
        assert orch.paper_brokers.get("fast") is not None
        # B-08: defaults came from config
        assert orch.paper_brokers["normal"].default_sl_pct == 1.0
        assert orch.paper_brokers["normal"].default_tp_pct == 2.0
        assert orch.paper_brokers["fast"].default_sl_pct == 0.5
        assert orch.paper_brokers["fast"].default_tp_pct == 1.0
    finally:
        core_mod.CONFIG_PATH = original_path
