"""arc.action — explicit action arbitration layer.

Multiple drives/memories/goals may conflict. The arbitrator scores candidate
actions through interpretable factors and preserves rejected alternatives,
reasons, and competing pressures (directive §6). Arbitration is NOT hidden
inside a single LLM call.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..events.canonical import ProvenanceRecord


@dataclass
class ActionCandidate:
    """An action evaluated by the arbitrator."""
    label: str
    kind: str = "task"
    utility: float = 0.0
    reasons: List[str] = field(default_factory=list)
    drive_contributions: Dict[str, float] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    risk: float = 0.0


@dataclass
class ArbitrationRecord:
    chosen: str
    all_candidates: List[Dict[str, Any]]
    rejected: List[str]
    timestamp: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=dict)


class ActionArbitrator:
    """Scores candidates via interpretable factors; preserves alternatives."""

    def __init__(self, affective_provider=None) -> None:
        self.affective = affective_provider
        self.history: List[ArbitrationRecord] = []

    def propose(self, candidates: List[ActionCandidate], drives: Dict[str, float],
                strategy: Optional[Dict[str, float]] = None) -> ArbitrationRecord:
        """Rank pre-scored candidates by utility and preserve alternatives.

        Scoring (base utility + drive + affective policy) is performed by the
        runtime's ``evaluate_and_decide``; this method is a pure, inspectable
        router that picks the highest-utility candidate and records the
        rejected alternatives, reasons, and competing pressures (directive §6).
        """
        strategy = strategy or {}
        ordered = sorted(candidates, key=lambda c: c.utility, reverse=True)
        chosen = ordered[0] if ordered else None
        record = ArbitrationRecord(
            chosen=chosen.label if chosen else "",
            all_candidates=[_cand_to_dict(c) for c in ordered],
            rejected=[c.label for c in ordered[1:]],
            provenance=ProvenanceRecord(source="arbitrator", actor="shura",
                                        trust_level="verified").to_dict(),
        )
        self.history.append(record)
        return record


def _cand_to_dict(c: ActionCandidate) -> Dict[str, Any]:
    return {
        "label": c.label,
        "kind": c.kind,
        "utility": round(float(c.utility), 4),
        "reasons": list(c.reasons),
        "drive_contributions": dict(c.drive_contributions),
        "risk": round(float(c.risk), 4),
    }


def _clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))
