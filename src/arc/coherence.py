"""arc.coherence — coherence monitoring with interpretable signals.

The coherence monitor observes but does NOT secretly rewrite cognition
(directive §5). It produces multiple interpretable signals rather than a
single magical "coherence score". When intervention appears necessary it
emits a structured recommendation; actual intervention is a governed decision,
not an automatic rewrite.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .identity import Identity
from .self_model import SelfModel


@dataclass
class CoherenceSignals:
    """Multiple interpretable coherence signals (not a single score)."""
    identity_drift: float = 1.0          # 1.0 = no drift
    context_discontinuity: bool = False
    contradiction_spikes: int = 0        # count of unresolved contradictions
    memory_anomaly: bool = False
    task_continuity: float = 1.0         # 1.0 = continuous
    unexplained_transitions: int = 0
    self_ref_loop: bool = False
    raw: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)


class CoherenceMonitor:
    """Side-effect-free coherence assessment.

    Takes a read view (store events + self_model + identity) and returns
    CoherenceSignals. Does NOT write canonical events; does NOT mutate cognition.
    """

    def __init__(self) -> None:
        pass

    def assess(
        self,
        events: List[Any],
        self_model_view: Dict[str, Any],
        identity: Identity,
    ) -> CoherenceSignals:
        recs: List[Dict[str, Any]] = []

        # --- identity drift: compare identity events' hash to current identity ---
        identity_events = [e for e in events if e.event_type == "identity.loaded"]
        if identity_events:
            stored_hash = identity_events[0].payload.get("identity_hash")
            identity_drift = 1.0 if stored_hash == identity.hash else 0.0
            if identity_drift < 1.0:
                recs.append({"action": "flag", "reason": "identity_history_mismatch"})
        else:
            identity_drift = 1.0  # nothing to compare -> assume consistent at start

        # --- contradiction spikes ---
        contradiction_events = [e for e in events if e.event_type == "contradiction.detected"]
        contradiction_events = [e for e in contradiction_events if not e.payload.get("resolved", False)]
        c_spikes = len(contradiction_events)

        # --- memory anomaly: self-model divergence ---
        divergences = self_model_view.get("divergences", {})
        memory_anomaly = bool(divergences)

        # --- self-referential loop: >3 consecutive thinking/output events with no external input ---
        self_ref_loop = self._detect_self_loop(events)

        # --- unexplained transitions: state changes with no causal_parent ---
        state_events = [e for e in events if e.event_type in ("state", "experience")]
        orphans = [e for e in state_events if not e.causal_parent]
        unexplained = len(orphans)

        signals = CoherenceSignals(
            identity_drift=identity_drift,
            context_discontinuity=memory_anomaly,
            contradiction_spikes=c_spikes,
            memory_anomaly=memory_anomaly,
            task_continuity=1.0 if len(orphans) <= 1 else 0.5,
            unexplained_transitions=unexplained,
            self_ref_loop=self_ref_loop,
            raw={
                "identity_events": len(identity_events),
                "contradiction_events": len(contradiction_events),
                "divergence_fields": list(divergences.keys()),
            },
            recommendations=recs,
        )
        return signals

    @staticmethod
    def _detect_self_loop(events: List[Any]) -> bool:
        thinking = [e for e in events if e.event_type == "thinking" or e.event_type == "state"]
        if len(thinking) < 4:
            return False
        last4 = thinking[-4:]
        return all(not e.causal_parent for e in last4)
