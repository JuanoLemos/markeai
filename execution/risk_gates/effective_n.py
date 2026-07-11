"""
R3 — Effective-N Position Cap.

Pattern: effective diversification (Markowitz). Convert "N raw positions"
into "N effective" by discounting correlation. 11 correlated positions
have N_eff ~1.5; 11 truly diversified positions have N_eff ~11.

If N_effective < N_effective_min, REJECT.

This is the most "sophisticated" of the 5 gates (Herfindahl-based). The
user (Juano) decided: R3 is a GATE from day 1, NOT observability first.
The defense of 4 "independent bets" is hard from day 1 per the spec v1.1.

Formula: N_eff = 1 / sum(w_i^2)  (inverse Herfindahl)
    where w_i = position_i / total_exposure
"""
from .base import BaseGate, GateResult, GateConfigError


class EffectiveNGate(BaseGate):
    gate_id = "effective_n"

    def _validate_config(self) -> None:
        if not self._enabled:
            return
        if "min_effective_n" not in self.config:
            raise GateConfigError(
                f"{self.gate_id}: config requires 'min_effective_n' (float)"
            )

    def _evaluate(self, candidate: dict, context: dict) -> GateResult:
        positions = context.get("positions", {}) or {}
        candidate_size = float(candidate.get("size_usd", 0.0))
        min_eff = float(self.config["min_effective_n"])

        # Build weights: each open position + the candidate (projected).
        sizes = []
        for pos in positions.values():
            s = float(pos.get("size_usd", 0.0))
            if s > 0:
                sizes.append(s)
        if candidate_size > 0:
            sizes.append(candidate_size)

        n_raw = len(sizes)
        if n_raw < 2:
            # With <2 positions there is no "diversification" to evaluate.
            return GateResult(passed=True, gate_id=self.gate_id, reason="too_few_positions")

        total = sum(sizes)
        if total <= 0:
            return GateResult(passed=True, gate_id=self.gate_id, reason="no_exposure")

        # Herfindahl: sum of squared weights. N_eff = 1 / H.
        hhi = sum((s / total) ** 2 for s in sizes)
        if hhi <= 0:
            return GateResult(passed=True, gate_id=self.gate_id, reason="zero_weights")
        n_eff = 1.0 / hhi

        # Approx avg correlation for logging (Herfindahl → avg_corr is reversible
        # only for uniform N, but the formula is: H = (1 + (N-1)*avg_corr) / N
        # => avg_corr = (N*H - 1) / (N - 1)
        if n_raw > 1:
            avg_corr = max(-1.0, min(1.0, (n_raw * hhi - 1) / (n_raw - 1)))
        else:
            avg_corr = 0.0

        if n_eff < min_eff:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                reason="EFFECTIVE_N_TOO_LOW",
                details={
                    "candidate_symbol": candidate.get("symbol", "?"),
                    "n_raw": n_raw,
                    "n_effective": round(n_eff, 2),
                    "threshold": min_eff,
                    "avg_corr": round(avg_corr, 4),
                },
            )
        return GateResult(passed=True, gate_id=self.gate_id)
