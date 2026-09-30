"""arc.self_model — mutable self-model, distinct from immutable identity.

self-description != self-model (directive §7). The self-model is a collection of
claims SHURA makes about its own capabilities/limitations/patterns/goals plus
observations of its own behavior. Discrepancies between claims and observations
are surfaced explicitly rather than silently reconciled.

The self-model is itself event-sourced: claims/observations are canonical
events (``selfmodel.claimed`` / ``selfmodel.observed``), and the current state
is reconstructed by replaying them. State changes therefore flow through
canonical history, making them durable and inspectable.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .events.canonical import (
    ArcEvent,
    ProvenanceRecord,
    ArcEventStore,
    EVENT_TYPE_SELFMODEL_CLAIM,
    EVENT_TYPE_SELFMODEL_UPDATE,
)


class SelfModel:
    """Persistent self-model backed by canonical events.

    Writes happen only through ``claim`` / ``observe`` / ``record_failure`` etc.,
    each emitting a canonical event. The current state is reconstructed from
    those events, so it is always rebuildable.
    """

    def __init__(self, store: ArcEventStore, identity, namespace: str = "self") -> None:
        self._store = store
        self._identity = identity
        self._namespace = namespace
        self._cache: Optional[Dict[str, Any]] = None

    def claim(
        self,
        field: str,
        value: Any,
        provenance: Optional[ProvenanceRecord] = None,
        confidence: float = 1.0,
    ) -> ArcEvent:
        """Emit a self-model claim (a belief about self)."""
        ev = ArcEvent(
            source="selfmodel",
            actor="shura",
            event_type=EVENT_TYPE_SELFMODEL_CLAIM,
            payload={"field": field, "value": value},
            provenance=(provenance or ProvenanceRecord()).to_dict(),
            confidence=confidence,
        )
        return self._store.append(ev)

    def observe(
        self,
        field: str,
        observed_value: Any,
        provenance: Optional[ProvenanceRecord] = None,
        confidence: float = 1.0,
    ) -> ArcEvent:
        """Emit an observation of actual behavior (for divergence detection)."""
        ev = ArcEvent(
            source="selfmodel",
            actor="observer",
            event_type=EVENT_TYPE_SELFMODEL_UPDATE,
            payload={"field": field, "observed": observed_value},
            provenance=(provenance or ProvenanceRecord(trust_level="verified")).to_dict(),
            confidence=confidence,
        )
        return self._store.append(ev)

    def record_success(self, strategy: str, provenance: Optional[ProvenanceRecord] = None) -> ArcEvent:
        return self.claim("successful_strategy", strategy, provenance)

    def record_failure(self, description: str, provenance: Optional[ProvenanceRecord] = None) -> ArcEvent:
        return self.claim("recent_failure", description, provenance or ProvenanceRecord())

    def record_capability(self, capability: str, provenance: Optional[ProvenanceRecord] = None) -> ArcEvent:
        return self.claim(f"capability.{capability}", True, provenance)

    def record_goal(self, goal: str, provenance: Optional[ProvenanceRecord] = None) -> ArcEvent:
        return self.claim("goal", goal, provenance)

    def state(self) -> Dict[str, Any]:
        """Reconstructed current self-model state (deterministic from events)."""
        if self._cache is not None:
            return self._cache
        claims: Dict[str, Any] = {}
        observations: Dict[str, List[Any]] = {}
        successes: List[str] = []
        failures: List[str] = []
        goals: List[str] = []
        capabilities: List[str] = []
        for ev in self._store.replay(
            event_type=EVENT_TYPE_SELFMODEL_CLAIM
        ):
            fld = ev.payload.get("field")
            if fld is None:
                continue
            val = ev.payload.get("value")
            if fld == "successful_strategy":
                successes.append(val)
            elif fld == "recent_failure":
                failures.append(val)
            elif fld == "goal":
                goals.append(val)
            elif fld.startswith("capability."):
                capabilities.append(fld.split(".", 1)[1])
            else:
                claims[fld] = val
        for ev in self._store.replay(event_type=EVENT_TYPE_SELFMODEL_UPDATE):
            fld = ev.payload.get("field")
            observed = ev.payload.get("observed")
            observations.setdefault(fld, []).append(observed)
        divergences = {}
        for fld, obs_list in observations.items():
            claimed = claims.get(fld)
            if claimed is not None and claimed not in obs_list:
                divergences[fld] = {"claimed": claimed, "observed": obs_list}
        result = {
            "claims": claims,
            "observations": observations,
            "divergences": divergences,
            "successful_strategies": successes,
            "recent_failures": failures,
            "goals": goals,
            "capabilities": capabilities,
            "identity_hash": self._identity.hash,
        }
        self._cache = result
        return result

    def as_dict(self) -> Dict[str, Any]:
        return dict(self.state())

    def invalidate_cache(self) -> None:
        self._cache = None

    def divergence_report(self) -> Dict[str, Any]:
        """Explicit mechanism for detecting divergence between self-description
        and observed behavior (directive §7)."""
        return self.state().get("divergences", {})
