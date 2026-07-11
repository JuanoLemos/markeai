"""
BaseGate — abstract contract for all pre-trade risk gates.

A gate inspects a CANDIDATE order + the current portfolio CONTEXT and returns
a GateResult (passed=True/False, plus reason + details for logging).

Gates are pure-ish: they read from a passed-in context (positions, equity,
correlation matrix, sector map) and don't mutate state. The orchestrator
holds the source-of-truth; gates are stateless evaluators.
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass
class GateResult:
    """Outcome of a single gate evaluation."""
    passed: bool
    gate_id: str
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_log(self) -> str:
        """One-line log-friendly representation."""
        prefix = f"[RISK.GATE.{self.gate_id.upper()}]"
        if self.passed:
            return f"{prefix} PASS"
        # REJECT: include key details
        kv = " ".join(f"{k}={v}" for k, v in self.details.items())
        return f"{prefix} REJECT reason={self.reason} {kv}".strip()

    def to_dict(self) -> dict:
        return asdict(self)


class GateConfigError(ValueError):
    """Raised when a gate is misconfigured."""


class BaseGate:
    """
    Base class for a pre-trade risk gate.

    Subclasses MUST set `gate_id` and implement `evaluate(candidate, context)`.
    The cascade contract: gates are run in a fixed order. If a gate returns
    passed=False, the cascade stops. The orchestrator logs the result and
    does NOT send the order to the broker.
    """
    gate_id: str = "base"

    def __init__(self, config: dict):
        if not isinstance(config, dict):
            raise GateConfigError(
                f"{self.gate_id}: config must be a dict, got {type(config).__name__}"
            )
        self.config = config
        self._enabled = bool(config.get("enabled", True))
        self._validate_config()

    def _validate_config(self) -> None:
        """Hook for subclasses to validate their specific config. Override."""
        return

    def evaluate(self, candidate: dict, context: dict) -> GateResult:
        """
        Args:
            candidate: dict describing the proposed order. Required keys:
                - symbol (str): ticker
                - market (str): 'forex' | 'polymarket' | 'stocks'
                - signal (str): 'LONG' | 'SHORT'
                - size_usd (float): projected position size in USD
            context: dict with current portfolio state. Required keys:
                - positions (dict[str, dict]): symbol -> position record
                - equity (float): total current equity (incl. cash)
                - correlation_matrix (dict): (sym_a, sym_b) -> correlation in [-1, 1]
                - sector_map (dict): symbol -> sector name
                - sector_caps (dict): sector -> cap_pct (or use default)
                - default_sector_cap_pct (float)
                - unknown_sector_cap_pct (float)

        Returns:
            GateResult(passed=True, gate_id=self.gate_id) if the order is OK,
            otherwise GateResult(passed=False, reason="...", details={...}).
        """
        if not self._enabled:
            return GateResult(passed=True, gate_id=self.gate_id, reason="disabled")
        return self._evaluate(candidate, context)

    def _evaluate(self, candidate: dict, context: dict) -> GateResult:
        raise NotImplementedError(
            f"{self.gate_id}: subclasses must implement _evaluate"
        )
