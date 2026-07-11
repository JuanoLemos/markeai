"""
R1 — Sector/Theme Cap gate.

Pattern: swarm-trader rule 10. Aggregate exposure to a single sector/theme
must not exceed its cap (default 30%, configurable per sector).

Sector mapping is MANUAL via config/sectors.yaml (loaded by the manager and
passed in via context['sector_map']). Tickers not in the map use a
conservative default cap (15%).

Decision: REJECT if (current_exposure_in_sector + candidate_size) / equity
exceeds the cap for that sector.
"""
from .base import BaseGate, GateResult, GateConfigError


class SectorCapGate(BaseGate):
    gate_id = "sector_cap"

    def _validate_config(self) -> None:
        if not self._enabled:
            return
        if "default_threshold_pct" not in self.config:
            raise GateConfigError(
                f"{self.gate_id}: config requires 'default_threshold_pct'"
            )

    def _evaluate(self, candidate: dict, context: dict) -> GateResult:
        symbol = candidate.get("symbol", "")
        size = float(candidate.get("size_usd", 0.0))
        equity = float(context.get("equity", 0.0))
        sector_map = context.get("sector_map", {}) or {}
        sector_caps = context.get("sector_caps", {}) or {}
        default_cap = float(self.config.get("default_threshold_pct", 0.30))
        unknown_cap = float(
            self.config.get("unknown_sector_threshold_pct", default_cap)
        )

        if equity <= 0:
            return GateResult(passed=True, gate_id=self.gate_id, reason="no_equity_baseline")

        sector = sector_map.get(symbol)
        if not sector:
            # Unknown ticker: apply conservative cap.
            # Per spec: "Ticker no clasificado → default 15% (conservador) + flag para revisión manual"
            cap = unknown_cap
            sector_label = "__unknown__"
        else:
            cap = float(sector_caps.get(sector, default_cap))
            sector_label = sector

        # Sum current exposure in this sector (mark-to-market size_usd).
        positions = context.get("positions", {}) or {}
        current_exposure = 0.0
        for pos_symbol, pos in positions.items():
            if sector_map.get(pos_symbol) == sector_label or (
                sector_label == "__unknown__" and pos_symbol not in sector_map
            ):
                current_exposure += float(pos.get("size_usd", 0.0))

        new_exposure_pct = (current_exposure + size) / equity
        if new_exposure_pct > cap:
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                reason="SECTOR_CAP_EXCEEDED",
                details={
                    "candidate_symbol": symbol,
                    "sector": sector_label,
                    "exposure_pre_pct": round(current_exposure / equity, 4),
                    "exposure_post_pct": round(new_exposure_pct, 4),
                    "threshold_pct": cap,
                    "size_usd": round(size, 2),
                    "equity": round(equity, 2),
                },
            )
        return GateResult(passed=True, gate_id=self.gate_id)
