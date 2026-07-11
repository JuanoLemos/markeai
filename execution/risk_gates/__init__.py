"""
execution/risk_gates — Pre-trade risk gates for MarketAI.

Implements the 5 hard rules (R1-R5) from the swarm-trader pattern, applied
as a CASCADE before every order. Any gate that returns REJECT short-circuits
the cascade and the order is NOT sent to the broker.

Pattern: gate-first, NOT post-processor. Rules are code, not prompts.

Spec: scratchpad of the MarketAI session tree (v1.1, 2026-07-11).
"""
from .base import BaseGate, GateResult, GateConfigError
from .max_open import MaxOpenGate
from .max_size import MaxSizeGate
from .sector_cap import SectorCapGate
from .correlation import CorrelationGate
from .effective_n import EffectiveNGate
from .manager import RiskGateManager

__all__ = [
    "BaseGate",
    "GateResult",
    "GateConfigError",
    "MaxOpenGate",
    "MaxSizeGate",
    "SectorCapGate",
    "CorrelationGate",
    "EffectiveNGate",
    "RiskGateManager",
]
