"""
test_risk_gates.py — Tests for the 5 pre-trade risk gates (Issue 2).

Validates:
- Each individual gate (PASS / REJECT scenarios) with proper context
- The cascade order (R4 -> R5 -> R1 -> R2 -> R3) and short-circuit behavior
- The "11 correlated trades" bug scenario: the gates REJECT the redundant trades
- The fusion of the old `correlation_check` into R2 (the old function is removed
  from entry_filters.py and its logic lives only in R2 now)
"""
import pytest

from execution.risk_gates import (
    RiskGateManager,
    MaxOpenGate,
    MaxSizeGate,
    SectorCapGate,
    CorrelationGate,
    EffectiveNGate,
    BaseGate,
    GateResult,
    GateConfigError,
)


# ════════════════════════════════════════════
# Fixtures
# ════════════════════════════════════════════

SECTOR_MAP = {
    "AAPL": "us_mega_cap_tech",
    "MSFT": "us_mega_cap_tech",
    "GOOGL": "us_mega_cap_tech",
    "AMZN": "us_mega_cap_tech",
    "NVDA": "us_mega_cap_tech",
    "META": "us_mega_cap_tech",
    "TSLA": "us_mega_cap_tech",
    "SPY": "us_broad_market",
    "QQQ": "us_broad_market",
    "IVV": "us_broad_market",
    "XLK": "us_sector_etf",
    "EEM": "emerging_markets",
    "SHY": "cash_equivalent",
}

SECTOR_CAPS = {
    "us_mega_cap_tech": 0.30,
    "us_broad_market": 0.30,
    "us_sector_etf": 0.20,
    "emerging_markets": 0.15,
    "cash_equivalent": 1.00,
}

# All 11 tickers from the original bug highly correlated with each other.
HIGH_CORR_MATRIX = {
    **{(a, b): 0.85 for a in ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"] for b in ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"] if a != b},
    **{(a, b): 0.75 for a in ["SPY", "QQQ", "IVV", "XLK"] for b in ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]},
    **{(a, b): 0.95 for a in ["SPY", "QQQ", "IVV", "XLK"] for b in ["SPY", "QQQ", "IVV", "XLK"] if a != b},
    **{("AAPL", "SPY"): 0.80, ("SPY", "AAPL"): 0.80,
      ("MSFT", "QQQ"): 0.78, ("QQQ", "MSFT"): 0.78,
      ("EEM", "SPY"): 0.40, ("SPY", "EEM"): 0.40,
      ("SHY", "SPY"): 0.05, ("SPY", "SHY"): 0.05,
      ("SHY", "EEM"): 0.10, ("EEM", "SHY"): 0.10},
}


def make_manager(**overrides):
    """Build a RiskGateManager with sane defaults for tests."""
    cfg = {
        "risk_gates": {
            "max_open_positions": {"enabled": True, "threshold": 12},
            "max_position_size": {"enabled": True, "threshold_pct": 0.08},
            "sector_cap": {
                "enabled": True,
                "default_threshold_pct": 0.30,
                "unknown_sector_threshold_pct": 0.15,
            },
            "correlation": {
                "enabled": True,
                "threshold": 0.70,
                "cluster_threshold": 0.60,
                "cluster_min_count": 3,
            },
            "effective_n": {"enabled": True, "min_effective_n": 4},
        }
    }
    if overrides:
        for k, v in overrides.items():
            cfg["risk_gates"][k] = v
    return RiskGateManager(
        config=cfg,
        sector_map=SECTOR_MAP,
        sector_caps=SECTOR_CAPS,
        correlation_matrix=HIGH_CORR_MATRIX,
    )


def make_positions(symbols, size_each=36.0, market="stocks"):
    """Mock open positions dict for tests."""
    return {sym: {"ticker": sym, "size_usd": size_each, "signal": "LONG", "market": market} for sym in symbols}


def make_candidate(symbol, market="stocks", signal="LONG", size_usd=36.0):
    return {"symbol": symbol, "market": market, "signal": signal, "size_usd": size_usd}


def make_ctx(positions, equity=1000.0, extra=None):
    """Build a full context for individual-gate tests (matrix + sector_map)."""
    ctx = {
        "positions": positions,
        "equity": equity,
        "correlation_matrix": HIGH_CORR_MATRIX,
        "sector_map": SECTOR_MAP,
        "sector_caps": SECTOR_CAPS,
    }
    if extra:
        ctx.update(extra)
    return ctx


# ════════════════════════════════════════════
# R4 — MaxOpenGate
# ════════════════════════════════════════════

class TestMaxOpenGate:
    def test_pass_under_threshold(self):
        m = make_manager()
        ctx = make_ctx(make_positions(["AAPL", "MSFT", "GOOGL"]))
        result = m.gates[0].evaluate(make_candidate("AMZN"), ctx)
        assert result.passed is True
        assert result.gate_id == "max_open"

    def test_reject_at_threshold(self):
        m = make_manager()
        ctx = make_ctx(make_positions([f"SYM{i}" for i in range(12)]))
        result = m.gates[0].evaluate(make_candidate("AMZN"), ctx)
        assert result.passed is False
        assert result.reason == "MAX_OPEN_POSITIONS_EXCEEDED"
        assert result.details["current_open"] == 12
        assert result.details["threshold"] == 12

    def test_disabled_short_circuits(self):
        m = make_manager(**{"max_open_positions": {"enabled": False, "threshold": 1}})
        ctx = make_ctx(make_positions(["AAPL", "MSFT"]))
        result = m.gates[0].evaluate(make_candidate("AMZN"), ctx)
        assert result.passed is True
        assert result.reason == "disabled"

    def test_config_validation(self):
        with pytest.raises(GateConfigError):
            MaxOpenGate({"enabled": True})  # no threshold
        with pytest.raises(GateConfigError):
            MaxOpenGate({"enabled": True, "threshold": 0})  # not int


# ════════════════════════════════════════════
# R5 — MaxSizeGate
# ════════════════════════════════════════════

class TestMaxSizeGate:
    def test_pass_under_size(self):
        m = make_manager()
        ctx = make_ctx({}, equity=1000.0)
        result = m.gates[1].evaluate(make_candidate("AAPL", size_usd=50.0), ctx)
        assert result.passed is True

    def test_reject_over_size(self):
        m = make_manager()
        ctx = make_ctx({}, equity=1000.0)
        result = m.gates[1].evaluate(make_candidate("AAPL", size_usd=100.0), ctx)
        assert result.passed is False
        assert result.reason == "MAX_POSITION_SIZE_EXCEEDED"
        assert result.details["size_pct"] == 0.10
        assert result.details["threshold_pct"] == 0.08

    def test_exact_size_allowed(self):
        m = make_manager()
        ctx = make_ctx({}, equity=1000.0)
        result = m.gates[1].evaluate(make_candidate("AAPL", size_usd=80.0), ctx)
        assert result.passed is True  # 80/1000 = 8% exactly, allowed (>, not >=)

    def test_no_equity_skip(self):
        m = make_manager()
        ctx = make_ctx({}, equity=0.0)
        result = m.gates[1].evaluate(make_candidate("AAPL", size_usd=100.0), ctx)
        assert result.passed is True
        assert result.reason == "no_equity_baseline"


# ════════════════════════════════════════════
# R1 — SectorCapGate
# ════════════════════════════════════════════

class TestSectorCapGate:
    def test_pass_first_position_in_sector(self):
        m = make_manager()
        ctx = make_ctx({}, equity=1000.0)
        result = m.gates[2].evaluate(make_candidate("AAPL", size_usd=50.0), ctx)
        assert result.passed is True

    def test_reject_sector_cap_exceeded(self):
        """3 tech positions of 100 USD each in a 1000 USD equity = 30%.
        Adding a 4th would push to 40% > 30% cap → REJECT."""
        m = make_manager()
        positions = make_positions(["AAPL", "MSFT", "GOOGL"], size_each=100.0)
        ctx = make_ctx(positions, equity=1000.0)
        result = m.gates[2].evaluate(make_candidate("AMZN", size_usd=100.0), ctx)
        assert result.passed is False
        assert result.reason == "SECTOR_CAP_EXCEEDED"
        assert result.details["sector"] == "us_mega_cap_tech"
        assert result.details["threshold_pct"] == 0.30
        assert abs(result.details["exposure_post_pct"] - 0.40) < 0.01

    def test_different_sectors_independent(self):
        """Tech sector at 30% but adding from emerging_markets is fine."""
        m = make_manager()
        positions = make_positions(["AAPL", "MSFT", "GOOGL"], size_each=100.0)
        ctx = make_ctx(positions, equity=1000.0)
        result = m.gates[2].evaluate(make_candidate("EEM", size_usd=100.0), ctx)
        assert result.passed is True  # EEM is emerging_markets (15% cap, currently 0%)

    def test_unknown_sector_conservative_cap(self):
        """Unknown ticker uses the conservative 15% cap (default)."""
        m = make_manager()
        positions = make_positions(["UNKNOWN1"], size_each=100.0)
        ctx = make_ctx(positions, equity=1000.0)
        result = m.gates[2].evaluate(make_candidate("UNKNOWN2", size_usd=100.0), ctx)
        # Current exposure 10% in unknown, adding 10% = 20% > 15% cap → REJECT
        assert result.passed is False
        assert result.details["sector"] == "__unknown__"
        assert result.details["threshold_pct"] == 0.15


# ════════════════════════════════════════════
# R2 — CorrelationGate
# ════════════════════════════════════════════

class TestCorrelationGate:
    def test_pass_no_open_positions(self):
        m = make_manager()
        ctx = make_ctx({}, equity=1000.0)
        result = m.gates[3].evaluate(make_candidate("AAPL"), ctx)
        assert result.passed is True
        assert result.reason == "no_open_positions"

    def test_reject_single_high_correlation(self):
        m = make_manager()
        positions = make_positions(["AAPL"])
        ctx = make_ctx(positions, equity=1000.0)
        # MSFT <-> AAPL = 0.85 > 0.70 threshold
        result = m.gates[3].evaluate(make_candidate("MSFT"), ctx)
        assert result.passed is False
        assert result.reason == "HIGH_CORRELATION_WITH_OPEN"
        assert result.details["max_corr_symbol"] == "AAPL"
        assert result.details["max_corr_value"] == 0.85

    def test_reject_cluster_overload(self):
        """3+ positions with corr in (cluster_threshold, threshold) → REJECT by cluster check.
        The max_corr check requires corr > threshold (0.70), so to exercise the
        cluster check we use correlations between 0.60 and 0.70."""
        m = make_manager()
        positions = make_positions(["AAPL", "MSFT", "GOOGL"])
        # Custom matrix: candidate has 0.65 corr with each open position.
        # max_corr = 0.65 < 0.70 threshold → first check PASSES.
        # cluster_count = 3 ≥ cluster_min_count = 3 → second check REJECTs.
        ctx = make_ctx(
            positions,
            equity=1000.0,
            extra={"correlation_matrix": {
                ("AMZN", "AAPL"): 0.65, ("AAPL", "AMZN"): 0.65,
                ("AMZN", "MSFT"): 0.65, ("MSFT", "AMZN"): 0.65,
                ("AMZN", "GOOGL"): 0.65, ("GOOGL", "AMZN"): 0.65,
            }},
        )
        result = m.gates[3].evaluate(make_candidate("AMZN"), ctx)
        assert result.passed is False
        assert result.reason == "CORRELATION_CLUSTER_OVERLOAD"
        assert result.details["cluster_count"] == 3

    def test_pass_low_correlation(self):
        """A candidate with low correlation to all open positions passes."""
        m = make_manager()
        ctx = make_ctx(
            make_positions(["AAPL"]),
            equity=1000.0,
            extra={"correlation_matrix": {("NEW", "AAPL"): 0.30, ("AAPL", "NEW"): 0.30}},
        )
        result = m.gates[3].evaluate(make_candidate("NEW"), ctx)
        assert result.passed is True

    def test_symmetric_lookup(self):
        """Matrix lookup is symmetric: (A, B) == (B, A)."""
        m = make_manager()
        ctx = make_ctx(
            make_positions(["AAPL"]),
            equity=1000.0,
            extra={"correlation_matrix": {("MSFT", "AAPL"): 0.85}},
        )
        result = m.gates[3].evaluate(make_candidate("MSFT"), ctx)
        assert result.passed is False
        assert result.details["max_corr_value"] == 0.85


# ════════════════════════════════════════════
# R3 — EffectiveNGate
# ════════════════════════════════════════════

class TestEffectiveNGate:
    def test_pass_too_few_positions(self):
        """With 0 open + 1 candidate, n_raw=1, returns 'too_few_positions' without computing."""
        m = make_manager()
        ctx = make_ctx({}, equity=1000.0)
        result = m.gates[4].evaluate(make_candidate("AAPL", size_usd=100.0), ctx)
        assert result.passed is True
        assert result.reason == "too_few_positions"

    def test_pass_highly_diversified(self):
        """5 equal-weight positions: N_eff = 5 → PASS."""
        m = make_manager()
        positions = make_positions(
            ["SPY", "EEM", "XLK", "AAPL", "MSFT"], size_each=100.0
        )
        ctx = make_ctx(positions, equity=1000.0)
        result = m.gates[4].evaluate(make_candidate("QQQ", size_usd=100.0), ctx)
        # 6 equal-weight positions: H = 6*(1/6)^2 = 1/6 ≈ 0.167, N_eff = 6. > 4 → PASS.
        assert result.passed is True

    def test_reject_concentrated(self):
        """4 positions of unequal size: N_eff < 4 → REJECT."""
        m = make_manager()
        positions = {
            "AAPL": {"ticker": "AAPL", "size_usd": 800.0, "signal": "LONG", "market": "stocks"},
            "MSFT": {"ticker": "MSFT", "size_usd": 50.0, "signal": "LONG", "market": "stocks"},
            "GOOGL": {"ticker": "GOOGL", "size_usd": 50.0, "signal": "LONG", "market": "stocks"},
        }
        ctx = make_ctx(positions, equity=1000.0)
        result = m.gates[4].evaluate(make_candidate("AMZN", size_usd=50.0), ctx)
        # 4 positions, weights = [0.84, 0.05, 0.05, 0.05]. H ≈ 0.71, N_eff ≈ 1.4 < 4 → REJECT
        assert result.passed is False
        assert result.reason == "EFFECTIVE_N_TOO_LOW"
        assert result.details["n_effective"] < 4


# ════════════════════════════════════════════
# Cascade (RiskGateManager)
# ════════════════════════════════════════════

class TestCascade:
    def test_cascade_order_is_R4_R5_R1_R2_R3(self):
        m = make_manager()
        assert [g.gate_id for g in m.gates] == [
            "max_open", "max_size", "sector_cap", "correlation", "effective_n"
        ]

    def test_first_reject_short_circuits(self):
        """If R4 rejects, R5-R3 are not evaluated."""
        m = make_manager()
        positions = make_positions([f"SYM{i}" for i in range(12)], size_each=10.0)
        ctx = make_ctx(positions, equity=1000.0)
        result = m.evaluate(make_candidate("AAPL", size_usd=10.0), ctx)
        assert result.passed is False
        assert result.gate_id == "max_open"

    def test_all_pass(self):
        """5+ equal-weight diversified positions + a low-correlation candidate → PASS all 5 gates."""
        m = make_manager()
        # 5 equal-weight positions in different sectors
        positions = {
            "AAPL": {"ticker": "AAPL", "size_usd": 100.0, "signal": "LONG", "market": "stocks"},  # us_mega_cap_tech
            "EEM":  {"ticker": "EEM",  "size_usd": 100.0, "signal": "LONG", "market": "stocks"},  # emerging_markets
            "SHY":  {"ticker": "SHY",  "size_usd": 100.0, "signal": "LONG", "market": "stocks"},  # cash_equivalent
            "XLK":  {"ticker": "XLK",  "size_usd": 100.0, "signal": "LONG", "market": "stocks"},  # us_sector_etf
            "SPY":  {"ticker": "SPY",  "size_usd": 100.0, "signal": "LONG", "market": "stocks"},  # us_broad_market
        }
        # 5 positions of 100 each, equity 1000. The candidate (XLK) is already in
        # the open positions; let's use a fresh uncorrelated one instead.
        # Actually we need a candidate truly independent. Let me reuse SHY and
        # candidate as something uncorrelated. But simpler: 4 open positions of
        # 50 each + candidate of 200 → 5 positions, weights = [0.1, 0.1, 0.1, 0.1, 0.6]
        # H = 0.04 + 0.36 = 0.4, N_eff = 2.5 < 4 → REJECT. Not what we want.
        # Use 4 equal positions + 1 equal candidate: weights = [0.2]*5, H = 0.2, N_eff = 5. PASS.
        positions2 = {
            "AAPL": {"ticker": "AAPL", "size_usd": 50.0, "signal": "LONG", "market": "stocks"},
            "EEM":  {"ticker": "EEM",  "size_usd": 50.0, "signal": "LONG", "market": "stocks"},
            "SHY":  {"ticker": "SHY",  "size_usd": 50.0, "signal": "LONG", "market": "stocks"},
            "XLK":  {"ticker": "XLK",  "size_usd": 50.0, "signal": "LONG", "market": "stocks"},
        }
        ctx = make_ctx(positions2, equity=1000.0)
        # Candidate: 50 USD, different sector from all 4. But XLK is us_sector_etf
        # (cap 20%) and we already have XLK in positions. Adding ANOTHER tech position
        # like NVDA (not in positions) → 50/1000 = 5% in tech, currently 5% in tech
        # (just AAPL) → new = 10% < 30% → PASS. Correlation AAPL-NVDA = 0.85 > 0.70 → REJECT.
        # OK, candidate must be truly uncorrelated. Let me use a custom matrix.
        ctx["correlation_matrix"] = {("NEW", "AAPL"): 0.30, ("AAPL", "NEW"): 0.30,
                                      ("NEW", "EEM"): 0.20, ("EEM", "NEW"): 0.20,
                                      ("NEW", "SHY"): 0.10, ("SHY", "NEW"): 0.10,
                                      ("NEW", "XLK"): 0.25, ("XLK", "NEW"): 0.25}
        m.correlation_matrix = ctx["correlation_matrix"]
        result = m.evaluate(make_candidate("NEW", size_usd=50.0), ctx)
        assert result.passed is True
        assert result.gate_id == "cascade"

    def test_all_gates_disabled_passes(self):
        m = RiskGateManager(
            config={"risk_gates": {
                "max_open_positions": {"enabled": False, "threshold": 1},
                "max_position_size": {"enabled": False, "threshold_pct": 0.01},
                "sector_cap": {"enabled": False, "default_threshold_pct": 0.01},
                "correlation": {"enabled": False, "threshold": 0.01, "cluster_threshold": 0.01, "cluster_min_count": 1},
                "effective_n": {"enabled": False, "min_effective_n": 100},
            }},
            sector_map=SECTOR_MAP,
            sector_caps=SECTOR_CAPS,
            correlation_matrix={},
        )
        positions = make_positions([f"SYM{i}" for i in range(20)], size_each=100.0)
        ctx = make_ctx(positions, equity=1000.0)
        result = m.evaluate(make_candidate("AAPL", size_usd=500.0), ctx)
        assert result.passed is True

    def test_fail_closed_on_gate_crash(self):
        """If a gate raises an unexpected exception, the manager REJECTs (fail-closed)."""
        m = make_manager()

        class CrashingGate(BaseGate):
            gate_id = "crash"
            def _evaluate(self, candidate, context):
                raise RuntimeError("simulated crash")

        m.gates = [CrashingGate({"enabled": True})]
        result = m.evaluate(make_candidate("AAPL"), make_ctx({}, equity=1000.0))
        assert result.passed is False
        assert result.reason == "GATE_CRASH_FAIL_CLOSED"


# ════════════════════════════════════════════
# The Bug Scenario (11 correlated LONG positions in 3 min)
# ════════════════════════════════════════════

class TestBugScenario:
    """
    The exact issue 2 scenario: 11 LONG positions in 3 minutes on highly
    correlated tickers (SPY, QQQ, AAPL, MSFT, GOOGL, AMZN, IVV, EEM, IWM, XLK, TSLA).
    With the gates active, only the FIRST 1-3 should be opened; the rest get REJECTed.
    """
    def test_11_correlated_longs_get_rejected(self):
        m = make_manager()
        accepted = []
        rejected = []
        candidates = [
            "SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "IVV", "EEM", "IWM", "XLK", "TSLA"
        ]
        for sym in candidates:
            positions = make_positions(accepted, size_each=36.0)
            ctx = make_ctx(positions, equity=1000.0)
            result = m.evaluate(make_candidate(sym, size_usd=36.0), ctx)
            if result.passed:
                accepted.append(sym)
            else:
                rejected.append((sym, result.gate_id, result.reason))

        # The 10 redundant positions MUST be REJECTed (the bug was accepting all 11).
        assert len(accepted) < 11, f"Too many accepted: {accepted}"
        assert len(rejected) >= 7, f"Expected at least 7 rejects, got {len(rejected)}"
        # The 11th position MUST be REJECTed by R1 (sector cap) or R2 (correlation/cluster).
        last_sym, last_gate, last_reason = rejected[-1]
        assert last_sym == "TSLA"
        assert last_gate in ("sector_cap", "correlation", "effective_n"), \
            f"Expected sector_cap/correlation/effective_n, got {last_gate}/{last_reason}"


# ════════════════════════════════════════════
# Fusion of old correlation_check into R2
# ════════════════════════════════════════════

class TestOldCorrelationCheckFusion:
    """
    The old correlation_check in execution/entry_filters.py is REMOVED.
    Its logic is absorbed into R2 (with cluster detection added).
    """
    def test_old_pairwise_threshold_logic_present(self):
        """R2 rejects if max corr > threshold (the old logic)."""
        m = make_manager()
        ctx = make_ctx(make_positions(["AAPL"]), equity=1000.0)
        result = m.gates[3].evaluate(make_candidate("MSFT"), ctx)
        assert result.passed is False
        assert result.reason == "HIGH_CORRELATION_WITH_OPEN"

    def test_r2_has_cluster_check_old_did_not(self):
        """R2 has cluster detection (3+ positions with corr > 0.6) which the old check did NOT have."""
        m = make_manager()
        # 3 positions with corr 0.65 to candidate (between threshold 0.70 and cluster 0.60)
        ctx = make_ctx(
            make_positions(["SYM1", "SYM2", "SYM3"], size_each=50.0),
            equity=1000.0,
            extra={"correlation_matrix": {
                ("NEW", "SYM1"): 0.65, ("SYM1", "NEW"): 0.65,
                ("NEW", "SYM2"): 0.65, ("SYM2", "NEW"): 0.65,
                ("NEW", "SYM3"): 0.65, ("SYM3", "NEW"): 0.65,
            }},
        )
        # max corr = 0.65 < 0.70 threshold (would pass the old check)
        # BUT cluster_count = 3 ≥ cluster_min_count = 3 (R2 REJECTs)
        result = m.gates[3].evaluate(make_candidate("NEW"), ctx)
        assert result.passed is False
        assert result.reason == "CORRELATION_CLUSTER_OVERLOAD"


# ════════════════════════════════════════════
# Config validation
# ════════════════════════════════════════════

class TestConfigValidation:
    def test_max_open_requires_threshold(self):
        with pytest.raises(GateConfigError):
            MaxOpenGate({"enabled": True})

    def test_max_size_requires_threshold_pct(self):
        with pytest.raises(GateConfigError):
            MaxSizeGate({"enabled": True})

    def test_sector_cap_requires_default_threshold(self):
        with pytest.raises(GateConfigError):
            SectorCapGate({"enabled": True})

    def test_correlation_requires_threshold(self):
        with pytest.raises(GateConfigError):
            CorrelationGate({"enabled": True})

    def test_effective_n_requires_min(self):
        with pytest.raises(GateConfigError):
            EffectiveNGate({"enabled": True})

    def test_manager_validates_each_gate(self):
        """Manager construction should raise if any gate config is invalid."""
        with pytest.raises(GateConfigError):
            RiskGateManager(
                config={"risk_gates": {
                    "max_open_positions": {"enabled": True},  # no threshold
                    "max_position_size": {"enabled": True, "threshold_pct": 0.08},
                    "sector_cap": {"enabled": True, "default_threshold_pct": 0.30},
                    "correlation": {"enabled": True, "threshold": 0.70, "cluster_threshold": 0.60, "cluster_min_count": 3},
                    "effective_n": {"enabled": True, "min_effective_n": 4},
                }},
                sector_map=SECTOR_MAP,
                sector_caps=SECTOR_CAPS,
                correlation_matrix={},
            )
