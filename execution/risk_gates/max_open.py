"""
R4 — Max Open Positions gate.

Pattern: swarm-trader rule 7. Hard cap on concurrent open positions per
paper broker (we run dual profile, so per-profile count is what we check).

Default threshold: 12. Configurable.
"""
from .base import BaseGate, GateResult, GateConfigError


class MaxOpenGate(BaseGate):
    gate_id = "max_open"

    def _validate_config(self) -> None:
        # Disabled gates don't need a threshold (they short-circuit to PASS).
        if not self._enabled:
            return
        if "threshold" not in self.config:
            raise GateConfigError(
                f"{self.gate_id}: config requires 'threshold' (int)"
            )
        if not isinstance(self.config["threshold"], int) or self.config["threshold"] < 1:
            raise GateConfigError(
                f"{self.gate_id}: threshold must be a positive int, "
                f"got {self.config['threshold']!r}"
            )

    def _evaluate(self, candidate: dict, context: dict) -> GateResult:
        positions = context.get("positions", {}) or {}
        current = len(positions)
        threshold = self.config["threshold"]
        if current >= threshold:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                reason="MAX_OPEN_POSITIONS_EXCEEDED",
                details={
                    "current_open": current,
                    "threshold": threshold,
                    "candidate_symbol": candidate.get("symbol", "?"),
                },
            )
        return GateResult(passed=True, gate_id=self.gate_id)
