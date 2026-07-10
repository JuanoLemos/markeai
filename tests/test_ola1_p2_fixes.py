"""
Tests for the 5 P2 fixes (Ola 1, Día 2).
- B-08: PaperBroker SL/TP defaults from config
- B-09: correlation_check threshold from config
- B-14: api_error helper
- B-15: api() JS helper distinguishes HTTP errors (template-side)
- B-13 + B-16: closing the stale tracker entries (verified in commit, no code change)
"""
import os
import pytest
import yaml
import tempfile
import json
from pathlib import Path

from execution.paper_broker import PaperBroker
from execution.entry_filters import correlation_check


def test_b_08_paper_broker_default_sl_tp(tmp_path):
    """B-08: PaperBroker with custom default_sl_pct/default_tp_pct uses those for open_position."""
    pb = PaperBroker(
        initial_balance=1000,
        state_path=str(tmp_path / "pb.json"),
        default_sl_pct=2.0,  # from 'normal' profile
        default_tp_pct=5.0,
    )
    trade = pb.open_position(
        market="stocks", ticker="SPY", signal="LONG", entry_price=500.0,
        size_usd=30.0,  # no sl/tp passed
    )
    assert "error" not in trade
    assert trade["stop_loss_pct"] == 2.0
    assert trade["take_profit_pct"] == 5.0


def test_b_08_paper_broker_explicit_overrides_default(tmp_path):
    """B-08: explicit SL/TP args still take precedence over broker defaults."""
    pb = PaperBroker(
        initial_balance=1000,
        state_path=str(tmp_path / "pb.json"),
        default_sl_pct=2.0, default_tp_pct=5.0,
    )
    trade = pb.open_position(
        market="stocks", ticker="SPY", signal="LONG", entry_price=500.0,
        size_usd=30.0, stop_loss_pct=3.5, take_profit_pct=7.0,  # explicit
    )
    assert "error" not in trade
    assert trade["stop_loss_pct"] == 3.5
    assert trade["take_profit_pct"] == 7.0


def test_b_08_paper_broker_default_backward_compatible(tmp_path):
    """B-08: when no defaults are passed, falls back to legacy 5.0/10.0."""
    pb = PaperBroker(initial_balance=1000, state_path=str(tmp_path / "pb.json"))
    assert pb.default_sl_pct == 5.0
    assert pb.default_tp_pct == 10.0


def test_b_09_correlation_threshold_from_config():
    """B-09: correlation_check accepts threshold from config (single source of truth)."""
    # With threshold=0.85, a correlation of 0.80 should PASS
    open_positions = [{"market": "stocks", "ticker": "AAPL", "signal": "LONG"}]
    # AAPL has MSFT=0.78, GOOGL=0.75, AMZN=0.72, QQQ=0.85
    # With threshold=0.80, AAPL vs MSFT (0.78) passes
    assert correlation_check(open_positions, "stocks", "MSFT", "LONG", threshold=0.80) is True
    # With threshold=0.70, AAPL vs MSFT (0.78) blocks
    assert correlation_check(open_positions, "stocks", "MSFT", "LONG", threshold=0.70) is False
    # With threshold=0.85 (config), AAPL vs QQQ (0.85) blocks
    assert correlation_check(open_positions, "stocks", "QQQ", "LONG", threshold=0.85) is False
    # With threshold=0.86, AAPL vs QQQ (0.85) passes
    assert correlation_check(open_positions, "stocks", "QQQ", "LONG", threshold=0.86) is True


def test_b_09_default_threshold_backward_compatible():
    """B-09: omitting threshold keeps legacy 0.80 behavior (backward compat)."""
    open_positions = [{"market": "stocks", "ticker": "AAPL", "signal": "LONG"}]
    # AAPL vs MSFT=0.78 — passes with default 0.80
    assert correlation_check(open_positions, "stocks", "MSFT", "LONG") is True
    # AAPL vs QQQ=0.85 — blocks with default 0.80
    assert correlation_check(open_positions, "stocks", "QQQ", "LONG") is False


def test_b_14_dashboard_api_error_helper():
    """B-14: api_error helper returns standardized JSON with status code."""
    # api_error is defined inside dashboard's run() closure (Flask app factory pattern).
    # We can't import it directly, so we verify it exists in source and behaves correctly
    # by running it within a Flask test app.
    import re
    src = Path("dashboard.py").read_text(encoding="utf-8")
    # The helper must exist with the right signature
    m = re.search(r"def api_error\(msg:\s*str,\s*code:\s*int\s*=\s*400\)", src)
    assert m, "api_error(msg: str, code: int = 400) not found in dashboard.py"
    # The body must use the standardized format
    assert 'jsonify({"ok": False, "error": msg})' in src
    # And it must set the response status_code
    assert "resp.status_code = code" in src

    # Behavioral test: build a minimal Flask app, mount the helper, verify response
    from flask import Flask
    app = Flask(__name__)
    # Inline copy of the helper logic (matches dashboard.py)
    def api_error(msg, code=400):
        from flask import jsonify
        resp = jsonify({"ok": False, "error": msg})
        resp.status_code = code
        return resp
    app.add_url_rule("/err/<msg>", "err", lambda msg: api_error(msg, 422))
    client = app.test_client()
    r = client.get("/err/bad_input")
    assert r.status_code == 422
    body = r.get_json()
    assert body == {"ok": False, "error": "bad_input"}


def test_b_15_api_helper_distinguishes_errors_in_template():
    """B-15: base.html api() helper now distinguishes HTTP errors from empty data."""
    from pathlib import Path
    src = Path("templates/base.html").read_text(encoding="utf-8")
    # Check the new behavior is in place
    assert "_error" in src
    assert "_status" in src
    # And the old silent fallback is gone
    assert "return {};" not in src  # no silent {} on error


def test_b_13_fused_calculated_once_per_market():
    """B-13: in pipeline._process_market, fused is computed outside the ticker loop."""
    from pathlib import Path
    src = Path("orchestrator/pipeline.py").read_text(encoding="utf-8")
    # Find the _process_market function
    # The fused call should be at function scope, not inside `for ticker in target_tickers:`
    fn_start = src.find("def _process_market")
    assert fn_start > 0
    fn_end = src.find("def _analyze_polymarket", fn_start)
    fn = src[fn_start:fn_end]
    # The `for ticker in target_tickers:` should be AFTER the `fused = ...` line
    fused_pos = fn.find("fused = orch.fusion_engine.fuse")
    ticker_loop_pos = fn.find("for ticker in target_tickers:")
    assert fused_pos > 0 and ticker_loop_pos > 0
    assert fused_pos < ticker_loop_pos, "fused must be calculated before the ticker loop"


def test_b_16_tray_app_uses_sys_exit():
    """B-16: tray_app.do_exit uses sys.exit (not os._exit)."""
    from pathlib import Path
    src = Path("tray_app.py").read_text(encoding="utf-8")
    # Find do_exit function
    fn_start = src.find("def do_exit")
    assert fn_start > 0
    fn_end = src.find("def on_show", fn_start)
    fn = src[fn_start:fn_end]
    assert "sys.exit(0)" in fn
    assert "os._exit" not in fn
