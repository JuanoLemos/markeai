"""
RiskGateManager — orchestrates the 5 pre-trade gates in cascade.

The cascade order is FIXED (cheapest first, most expensive last):
    R4 (max_open) -> R5 (max_size) -> R1 (sector_cap) -> R2 (correlation) -> R3 (effective_n)

If any gate returns passed=False, the cascade STOPS and the result is
returned to the orchestrator. The orchestrator does NOT send the order
to the broker. The result is logged with the gate_id, reason, and details.

Context contract (what the manager expects in `evaluate` calls):
    positions (dict): symbol -> {ticker, signal, size_usd, entry_price, ...}
    equity (float): total current equity
    correlation_matrix (dict): (sym_a, sym_b) -> correlation in [-1, 1]
    sector_map (dict): symbol -> sector name
    sector_caps (dict): sector -> cap_pct (overrides default)

The manager does NOT own the matrix; the orchestrator precomputes it
(out of scope here) and passes it in. See spec section 1 (R2 setup).
"""
import logging
from .base import BaseGate, GateResult
from .max_open import MaxOpenGate
from .max_size import MaxSizeGate
from .sector_cap import SectorCapGate
from .correlation import CorrelationGate
from .effective_n import EffectiveNGate


class RiskGateManager:
    """Runs the 5-gate cascade before every order."""

    def __init__(
        self,
        config: dict,
        sector_map: dict,
        sector_caps: dict,
        correlation_matrix: dict,
        log: logging.Logger = None,
    ):
        """
        Args:
            config: the 'risk_gates' section of config.yaml.
            sector_map: {symbol -> sector_name} (from config/sectors.yaml).
            sector_caps: {sector_name -> cap_pct} (overrides for sector_cap gate).
            correlation_matrix: {(sym_a, sym_b) -> float} precalculated matrix
                                 (T-1 data, persisted in DB by orchestrator).
            log: optional logger; if None, a default module logger is used.
        """
        self.config = config
        self.sector_map = sector_map
        self.sector_caps = sector_caps
        self.correlation_matrix = correlation_matrix
        self.log = log or logging.getLogger(__name__)

        # Build the 5 gates in cascade order. Disabled gates are still
        # constructed (BaseGate.evaluate returns PASS for them) so the
        # cascade order stays consistent and we can toggle per-gate via
        # config without code changes.
        rg = config.get("risk_gates", config)  # tolerate flat or nested
        self.gates: list = [
            MaxOpenGate(rg.get("max_open_positions", {"enabled": False})),
            MaxSizeGate(rg.get("max_position_size", {"enabled": False})),
            SectorCapGate(rg.get("sector_cap", {"enabled": False})),
            CorrelationGate(rg.get("correlation", {"enabled": False})),
            EffectiveNGate(rg.get("effective_n", {"enabled": False})),
        ]

    def set_correlation_matrix(self, matrix: dict) -> None:
        """Update the precalculated matrix (e.g. once per cycle)."""
        self.correlation_matrix = matrix or {}

    def evaluate(self, candidate: dict, context: dict) -> GateResult:
        """
        Run the cascade. Returns the first REJECT, or the final PASS.

        Args:
            candidate: {symbol, market, signal, size_usd}
            context: {positions, equity, ...} — plus correlation_matrix and
                     sector_map/sector_caps injected from the manager state
                     if not present in context.
        """
        # Inject manager-owned state into the per-call context.
        ctx = dict(context)
        ctx.setdefault("correlation_matrix", self.correlation_matrix)
        ctx.setdefault("sector_map", self.sector_map)
        ctx.setdefault("sector_caps", self.sector_caps)
        # If equity not in context, try to derive from positions (sum of size_usd).
        if "equity" not in ctx or ctx["equity"] is None:
            positions = ctx.get("positions", {}) or {}
            ctx["equity"] = sum(float(p.get("size_usd", 0.0)) for p in positions.values())
            if ctx["equity"] == 0:
                # Fall back to a non-zero baseline to avoid divide-by-zero.
                ctx["equity"] = 1.0

        for gate in self.gates:
            try:
                result = gate.evaluate(candidate, ctx)
            except Exception as e:
                # Fail-closed: if a gate crashes, REJECT. Better safe than sorry.
                self.log.error(
                    f"[RISK.GATE] {gate.gate_id} crashed: {e} — REJECT (fail-closed)"
                )
                return GateResult(
                    passed=False,
                    gate_id=gate.gate_id,
                    reason="GATE_CRASH_FAIL_CLOSED",
                    details={"error": str(e), "candidate_symbol": candidate.get("symbol", "?")},
                )
            if not result.passed:
                self.log.warning(result.to_log())
                return result

        # All gates passed (or were disabled and short-circuited to PASS).
        return GateResult(passed=True, gate_id="cascade", reason="all_passed")
