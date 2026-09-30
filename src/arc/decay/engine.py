"""arc.decay — selective forgetting on DERIVED accessibility (directive §8).

Memory does not grow without consequence. Decay applies to derived
accessibility/importance/salience — it NEVER deletes canonical events.
Older, rarely-accessed, uncorroborated, or low-provenance memories become
less accessible over time.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..memory.layers import MemoryIndex, MemoryRecord


@dataclass
class DecayFactors:
    age: float
    access_frequency: float
    importance: float
    affective_salience: float
    corroboration: float
    relevance: float
    provenance_quality: float
    accessibility: float  # derived 0..1 — lower means harder to retrieve
    explanation: Dict[str, str] = field(default_factory=dict)


class MemoryDecay:
    """Applies access decay to memory records (derived only). Returns updated
    accessibility scores. Canonical events are untouched.
    """

    def __init__(self) -> None:
        self.access_log: Dict[str, List[float]] = {}

    def _log_access(self, record_id: str, now: float) -> None:
        self.access_log.setdefault(record_id, []).append(now)
        # bound the log
        if len(self.access_log[record_id]) > 1000:
            self.access_log[record_id] = self.access_log[record_id][-500:]

    def score(self, record: MemoryRecord, now: float, context: str = "") -> DecayFactors:
        """Compute derived accessibility for a record."""
        self._log_access(record.memory_id, now)
        accesses = self.access_log.get(record.memory_id, [])
        age = max(now - record.created_at, 0.0)
        # age factor: older -> less accessible
        age_score = math.exp(-age / 86400.0)  # 1-day half-life-ish
        # access frequency: frequent -> more accessible
        recent_accesses = sum(1 for t in accesses if now - t < 3600)
        freq_score = min(len(accesses) / 10.0, 1.0) if accesses else 0.2
        # corroboration: more corroborating -> more accessible
        corr_score = min(len(record.corroboration) / 3.0, 1.0) if record.corroboration else 0.3
        # provenance quality
        prov_dict = record.provenance
        if hasattr(prov_dict, "to_dict"):
            prov_dict = prov_dict.to_dict()
        prov_q = float(prov_dict.get("confidence", 0.5)) if isinstance(prov_dict, dict) else float(record.provenance.confidence)
        # affective salience: use record salience as proxy
        affect_score = record.salience

        accessibility = _weighted_average([
            (age_score, 0.25), (freq_score, 0.20), (corr_score, 0.15),
            (prov_q, 0.15), (affect_score, 0.15), (1.0, 0.10),
        ])
        accessibility = max(0.05, min(0.95, accessibility))

        return DecayFactors(
            age=age_score,
            access_frequency=freq_score,
            importance=prov_q,
            affective_salience=affect_score,
            corroboration=corr_score,
            relevance=1.0,
            provenance_quality=prov_q,
            accessibility=accessibility,
            explanation={
                "age": f"{age:.0f}s ago",
                "accesses": str(len(accesses)),
                "corroboration": str(len(record.corroboration)),
            },
        )

    def apply(self, records: List[MemoryRecord], now: float = None) -> List[Dict[str, Any]]:
        """Return derived accessibility scores for records (no canonical mutation)."""
        now = now or time.time()
        out = []
        for r in records:
            fac = self.score(r, now)
            out.append({"memory_id": r.memory_id, "accessibility": fac.accessibility,
                        "factors": fac.explanation})
        return out


def _weighted_average(pairs):
    total = sum(v * w for v, w in pairs)
    wsum = sum(w for _, w in pairs)
    return total / wsum if wsum else 0.0
