"""arc.state — derived cognitive state (reconstructable, not canonical).

CognitiveState is DERIVED state. It is rebuilt from canonical events and is
safe to discard. The canonical store (ArcEventStore) is the source of truth.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CognitiveState:
    """Derived cognitive state view.

    Why each field:
      identity_hash         — link to immutable identity (drift detection)
      identity_loaded_at    — continuity of identity across a runtime
      self_model            — mutable beliefs about self (reconstructed from events)
      goals                 — active goal set (current)
      attention             — current salience focus
      working_memory        — what matters now (episodic slices)
      coherence             — latest coherence signal snapshot
      session_id            — session correlation
      reconstructed         — True when rebuilt purely from canonical events
      reconstructed_at      — when reconstruction completed
    """
    identity_hash: str = ""
    identity_loaded_at: float = 0.0
    self_model: Dict[str, Any] = field(default_factory=dict)
    goals: List[Any] = field(default_factory=list)
    attention: Dict[str, Any] = field(default_factory=dict)
    working_memory: List[Any] = field(default_factory=list)
    coherence: Dict[str, Any] = field(default_factory=dict)
    session_id: str = ""
    reconstructed: bool = False
    reconstructed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity_hash": self.identity_hash,
            "identity_loaded_at": self.identity_loaded_at,
            "self_model": self.self_model,
            "goals": self.goals,
            "attention": self.attention,
            "working_memory": self.working_memory,
            "coherence": self.coherence,
            "session_id": self.session_id,
            "reconstructed": self.reconstructed,
            "reconstructed_at": self.reconstructed_at,
        }

    def snapshot(self) -> Dict[str, Any]:
        """Mutable snapshot used for equality comparison in reconstruction tests."""
        return self.to_dict()

    # Ephemeral, process-time-derived keys that legitimately vary across a
    # restart and are therefore excluded from reconstruction-equivalence.
    _EPHEMERAL_KEYS = {"reconstructed_at", "reconstructed", "last_accessed"}

    @classmethod
    def _normalize(cls, value: Any) -> Any:
        """Deep-strip ephemeral timing fields so reconstruction equality is
        about *content and structure*, not per-record wall-clock timestamps."""
        if isinstance(value, dict):
            return {k: cls._normalize(v) for k, v in value.items()
                    if k not in cls._EPHEMERAL_KEYS}
        if isinstance(value, list):
            return [cls._normalize(v) for v in value]
        return value

    def equals_snapshot(self, other: Dict[str, Any]) -> bool:
        a = self._normalize(self.to_dict())
        b = self._normalize(dict(other))
        return a == b
