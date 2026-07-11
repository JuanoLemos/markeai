"""
R5 — Max Position Size gate.

Pattern: swarm-trader rule 9. No individual position may exceed
threshold_pct of equity at the moment of opening.

Default: 0.08 (8%). Configurable.
"""
from .base import BaseGate, GateResult, GateConfigError


class MaxSizeGate(BaseGate):
    gate_id = "max_size"

    def _validate_config(self) -> None:
        if not self._enabled:
            return
        if "threshold_pct" not in self.config:
            raise GateConfigError(
                f"{self.gate_id}: config requires 'threshold_pct' (float 0-1)"
            )
        pct = self.config["threshold_pct"]
        if not isinstance(pct, (int, float)) or pct <= 0 or pct > 1:
            raise GateConfigError(
                f"{self.gate_id}: threshold_pct must be in (0, 1], got {pct!r}"
            )

    def _evaluate(self, candidate: dict, context: dict) -> GateResult:
        size = float(candidate.get("size_usd", 0.0))
        equity = float(context.get("equity", 0.0))
        threshold_pct = float(self.config["threshold_pct"])
        if equity <= 0:
            # No equity baseline: skip size check (let downstream fail-safe).
            return GateResult(passed=True, gate_id=self.gate_id, reason="no_equity_baseline")
        size_pct = size / equity
        if size_pct > threshold_pct:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                reason="MAX_POSITION_SIZE_EXCEEDED",
                details={
                    "candidate_symbol": candidate.get("symbol", "?"),
                    "size_usd": round(size, 2),
                    "size_pct": round(size_pct, 4),
                    "threshold_pct": threshold_pct,
                    "equity": round(equity, 2),
                },
            )
        return GateResult(passed=True, gate_id=self.gate_id)
