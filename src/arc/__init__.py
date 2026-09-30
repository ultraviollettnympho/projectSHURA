"""shura.arc — cognitive architecture foundation built within ProjectSHURA.

Status key:
- VERIFIED: components with passing tests (see tests/test_arc_*.py).
- PROPOSED: schemas/contracts defined here, awaiting fuller implementation.
"""
from .state import CognitiveState
from .events.canonical import (
    ArcEvent,
    ProvenanceRecord,
    ArcEventStore,
    SCHEMA_VERSION,
    EVENT_TYPE_STATE,
    EVENT_TYPE_EXPERIENCE,
    EVENT_TYPE_SELFMODEL_CLAIM,
    EVENT_TYPE_SELFMODEL_UPDATE,
    EVENT_TYPE_MEMORY_RECORDED,
    EVENT_TYPE_CONTRADICTION,
    EVENT_TYPE_OBSERVATION,
    EVENT_TYPE_COHERENCE,
    EVENT_TYPE_IDENTITY_LOADED,
    EVENT_TYPE_IDENTITY_CHANGE_PROPOSED,
    EVENT_TYPE_IDENTITY_CHANGE_APPLIED,
    EVENT_TYPE_ACTION,
    EVENT_TYPE_DECIDED,
)
from .identity import Identity, IdentityGovernance, ChangeProposal
from .memory.layers import (
    MemoryRecord,
    MemoryKind,
    MemoryIndex,
    Contradiction,
    ContradictionRegistry,
)
from .provider import CognitiveProvider, StubCognitiveProvider, EchoCognitiveProvider
from .observation import Observation, ReadFacade, Observer
from .coherence import CoherenceMonitor, CoherenceSignals
from .self_model import SelfModel
from .runtime import ShuraARC, ActionProposal
from .governance.authority import AuthorityTier, GovernanceController
from .experiment.harness import ResearchLedger, AblationHarness, AblationResult

__all__ = [
    "ShuraARC",
    "ActionProposal",
    "CognitiveState",
    "ArcEvent",
    "ProvenanceRecord",
    "ArcEventStore",
    "SCHEMA_VERSION",
    "Identity",
    "IdentityGovernance",
    "ChangeProposal",
    "MemoryRecord",
    "MemoryKind",
    "MemoryIndex",
    "Contradiction",
    "ContradictionRegistry",
    "CognitiveProvider",
    "StubCognitiveProvider",
    "EchoCognitiveProvider",
    "Observation",
    "ReadFacade",
    "Observer",
    "CoherenceMonitor",
    "CoherenceSignals",
    "SelfModel",
    "AuthorityTier",
    "GovernanceController",
    "ResearchLedger",
    "AblationHarness",
    "AblationResult",
    # Event types
    "EVENT_TYPE_STATE",
    "EVENT_TYPE_EXPERIENCE",
    "EVENT_TYPE_SELFMODEL_CLAIM",
    "EVENT_TYPE_SELFMODEL_UPDATE",
    "EVENT_TYPE_MEMORY_RECORDED",
    "EVENT_TYPE_CONTRADICTION",
    "EVENT_TYPE_OBSERVATION",
    "EVENT_TYPE_COHERENCE",
    "EVENT_TYPE_IDENTITY_LOADED",
    "EVENT_TYPE_IDENTITY_CHANGE_PROPOSED",
    "EVENT_TYPE_IDENTITY_CHANGE_APPLIED",
    "EVENT_TYPE_ACTION",
    "EVENT_TYPE_DECIDED",
]