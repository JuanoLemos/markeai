"""
R2 — Pre-Trade Correlation Gate.

Pattern: swarm-trader implicit + portfolio construction standard (Markowitz
/ ML4T of Stefan Jansen). REJECT a candidate whose correlation with ANY
open position exceeds the threshold, OR if 3+ positions already correlate
above the cluster threshold with the candidate (independent of the max-corr
check).

The matrix is PRECALCULATED and passed in via context['correlation_matrix'].
The matrix uses T-1 data (no look-ahead). This gate does NOT calculate
correlations; it just looks them up. The setup pipeline is responsible
for precalculating + caching.

FUSION NOTE: this gate ABSORBS the logic of the old `correlation_check` in
`execution/entry_filters.py`. That function did a simple pairwise check
with a hard-coded threshold (0.80 default, 0.85 in config). R2 is the new
authoritative check: same pairwise idea, but with configurable threshold,
cluster detection, and a proper correlation matrix as source of truth.
The old `correlation_check` is REMOVED (no two systems, per spec v1.1).
"""
from .base import BaseGate, GateResult, GateConfigError


class CorrelationGate(BaseGate):
    gate_id = "correlation"

    def _validate_config(self) -> None:
        if not self._enabled:
            return
        if "threshold" not in self.config:
            raise GateConfigError(
                f"{self.gate_id}: config requires 'threshold' (float 0-1)"
            )
        if "cluster_threshold" not in self.config:
            raise GateConfigError(
                f"{self.gate_id}: config requires 'cluster_threshold'"
            )
        if "cluster_min_count" not in self.config:
            raise GateConfigError(
                f"{self.gate_id}: config requires 'cluster_min_count'"
            )

    def _lookup(self, matrix: dict, a: str, b: str) -> float:
        """Symmetric lookup. Returns 0.0 (uncorrelated) if not in matrix."""
        if not matrix:
            return 0.0
        if (a, b) in matrix:
            return float(matrix[(a, b)])
        if (b, a) in matrix:
            return float(matrix[(b, a)])
        return 0.0

    def _evaluate(self, candidate: dict, context: dict) -> GateResult:
        symbol = candidate.get("symbol", "")
        matrix = context.get("correlation_matrix", {}) or {}
        positions = context.get("positions", {}) or {}
        threshold = float(self.config["threshold"])
        cluster_threshold = float(self.config["cluster_threshold"])
        cluster_min_count = int(self.config["cluster_min_count"])

        if not positions:
            return GateResult(passed=True, gate_id=self.gate_id, reason="no_open_positions")

        # Find max correlation and cluster count against open positions.
        max_corr = -2.0
        max_corr_symbol = None
        cluster_count = 0
        for pos_symbol in positions:
            corr = self._lookup(matrix, symbol, pos_symbol)
            if corr > max_corr:
                max_corr = corr
                max_corr_symbol = pos_symbol
            if corr > cluster_threshold:
                cluster_count += 1

        # Check 1: max correlation vs threshold.
        if max_corr > threshold:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                reason="HIGH_CORRELATION_WITH_OPEN",
                details={
                    "candidate_symbol": symbol,
                    "max_corr_symbol": max_corr_symbol or "?",
                    "max_corr_value": round(max_corr, 4),
                    "threshold": threshold,
                },
            )

        # Check 2: cluster overload (independent of max-corr check).
        if cluster_count >= cluster_min_count:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                reason="CORRELATION_CLUSTER_OVERLOAD",
                details={
                    "candidate_symbol": symbol,
                    "cluster_count": cluster_count,
                    "cluster_threshold": cluster_threshold,
                    "cluster_min_count": cluster_min_count,
                },
            )

        return GateResult(passed=True, gate_id=self.gate_id)
