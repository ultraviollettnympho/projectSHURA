"""arc.observation — read-only observer (structurally enforced read-only).

The observer subsystem is *structurally distinct* from the executor/cognitive
process (directive §6). It receives a read-only facade and can never publish
canonical events or mutate cognitive state. It produces Observations plus
recommendations; it does not rewrite cognition.

Enforcement: ``Observer`` holds only a ``ReadFacade``, which exposes reads only.
There is no write path available to it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .events.canonical import ArcEvent, ArcEventStore
from .identity import Identity
from .self_model import SelfModel


@dataclass
class Observation:
    """A piece of structural observation (no side effects).

    kind        — signal category
    detail      — structured detail
    confidence  — 0..1
    recommendation — optional structured recommendation (never auto-applied)
    """
    kind: str
    detail: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    recommendation: Optional[Dict[str, Any]] = None


class ReadFacade:
    """Structurally read-only view of cognitive state.

    Exposes ONLY read methods. No append/publish/mutate methods exist here,
    which structurally prevents the Observer (and any consumer of the facade)
    from mutating canonical state.
    """

    def __init__(self, store: ArcEventStore, self_model: SelfModel, identity: Identity) -> None:
        self._store = store
        self._self_model = self_model
        self._identity = identity

    def events(self) -> List[ArcEvent]:
        return list(self._store.read_all())

    def replay(self, event_type: Optional[str] = None) -> List[ArcEvent]:
        return list(self._store.replay(event_type=event_type))

    def self_model(self) -> Dict[str, Any]:
        return self._self_model.as_dict()

    def identity_hash(self) -> str:
        return self._identity.hash

    def identity_fingerprint(self) -> Dict[str, Any]:
        return self._identity.fingerprint()

    @property
    def session_id(self) -> str:
        return self._store.session_id

    @property
    def sequence(self) -> int:
        return self._store._seq


class Observer:
    """A pure observer. Holds a ReadFacade only — cannot mutate canonical state.

    Produces Observations + recommendations. It does not write events and does
    not call any mutation method. The runtime may choose to record an
    observation as an event, but that is the runtime's action, not the
    observer's.
    """

    def __init__(self, facade: ReadFacade) -> None:
        self.facade = facade

    def observe_all(self) -> List[Observation]:
        return [
            *self._observe_identity_drift(),
            *self._observe_selfmodel_divergence(),
            *self._observe_recent_state(),
        ]

    def _observe_identity_drift(self) -> List[Observation]:
        id_hash = self.facade.identity_hash()
        events = self.facade.events()
        drift_events = [e for e in events if e.event_type == "identity.loaded"]
        if drift_events:
            first = drift_events[0]
            consistent = first.payload.get("identity_hash") == id_hash
        else:
            consistent = False
        return [
            Observation(
                kind="identity.drift",
                detail={
                    "identity_hash": id_hash,
                    "consistent_with_events": consistent,
                    "identity_events": len(drift_events),
                },
                confidence=0.9,
                recommendation=None if consistent else {
                    "action": "flag",
                    "reason": "identity history inconsistent with loaded identity",
                },
            )
        ]

    def _observe_selfmodel_divergence(self) -> List[Observation]:
        sm = self.facade.self_model()
        divergences = sm.get("divergences", {})
        if not divergences:
            return [
                Observation(
                    kind="selfmodel.divergence",
                    detail={"divergence_count": 0},
                    confidence=0.8,
                    recommendation=None,
                )
            ]
        out = [
            Observation(
                kind="selfmodel.divergence",
                detail={"fields": list(divergences.keys())},
                confidence=0.7,
                recommendation={"action": "surface", "fields": list(divergences.keys())},
            )
        ]
        return out

    def _observe_recent_state(self) -> List[Observation]:
        events = self.facade.events()
        recent = events[-5:] if events else []
        return [
            Observation(
                kind="state.recent",
                detail={
                    "event_count": len(events),
                    "recent_types": [e.event_type for e in recent],
                    "sequence": self.facade.sequence,
                },
                confidence=0.6,
                recommendation=None,
            )
        ]
