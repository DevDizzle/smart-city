"""
VeritAI Protocol Engineering Layer

This module defines the VeritAI Protocol Specification (VeritAI-PS)
for governed multi-agent reasoning systems.
"""

from .rules import ProtocolRule, GovernanceRules, Severity, Recommendation
from .checkpoints import ProtocolCheckpoint, Checkpoints
from .trace import ProtocolTrace, ProtocolEvent

__all__ = [
    "ProtocolRule",
    "GovernanceRules",
    "Severity",
    "Recommendation",
    "ProtocolCheckpoint",
    "Checkpoints",
    "ProtocolTrace",
    "ProtocolEvent",
]

# Export schemas
from .schemas import (
    SpecialistFinding,
    CriticFinding,
    ValidatorDecision,
    WorkflowState,
    Recommendation,
    Severity,
    CanonicalIntent,
)