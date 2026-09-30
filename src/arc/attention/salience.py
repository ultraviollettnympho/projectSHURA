"""arc.attention — salience engine with inspectable multi-factor scoring."""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..affect.affective_state import ArcAffectiveState
from ..drives.drive_system import DriveSystem
from ..memory.layers import MemoryRecord


@dataclass
class SalienceFactors:
    """Every factor is inspectable (directive §5)."""
    relevance: float = 0.0
    recency: float = 0.5
    affective_charge: float = 0.0
    unresolved_contradiction: float = 0.0
    drive_pressure: float = 0.0
    temporal_importance: float = 0.0
    provenance_confidence: float = 1.0
    goal_alignment: float = 0.0
    total: float = 0.0
    explanation: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            k: (v if not isinstance(v, dict) else v)
            for k, v in self.__dict__.items()
        }


class SalienceEngine:
    """Scores candidates on multiple interpretable factors; produces inspectable
    decisions answering: 'why did this become relevant NOW?'"""

    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []

    def score_memory(
        self,
        record: MemoryRecord,
        context: str,
        affective: ArcAffectiveState,
        drives: DriveSystem,
        goals: List[str],
        now: Optional[float] = None,
    ) -> SalienceFactors:
        now = now or time.time()
        factors = SalienceFactors()

        # relevance: textual overlap with context
        ctx = context.lower()
        content = record.content.lower()
        factors.relevance = _overlap(ctx, content)
        factors.explanation["relevance"] = f"context overlap={factors.relevance:.2f}"

        # recency (exponential decay over ~minutes)
        age = max(now - record.created_at, 0.0)
        factors.recency = math.exp(-age / 180.0)
        factors.explanation["recency"] = f"age={age:.1f}s, recency={factors.recency:.2f}"

        # affective charge via affective retrieval boost
        boost = affective.retrieval_boost(0.5)
        factors.affective_charge = (boost - 1.0) / 2.0  # normalize ~[-0.5,0.5]
        factors.explanation["affective_charge"] = f"affective boost={boost:.2f}"

        # unresolved contradiction involving this memory
        factors.unresolved_contradiction = 0.0
        factors.explanation["contradiction"] = "none"

        # drive pressure: sum of drive pressures
        total_drive = sum(d.pressure for d in drives.drives.values()) / max(len(drives.drives), 1)
        factors.drive_pressure = total_drive
        factors.explanation["drive_pressure"] = f"avg drive={total_drive:.2f}"

        # temporal importance: recency-weighted
        factors.temporal_importance = factors.recency

        # provenance confidence
        prov = record.provenance
        conf = float(prov.get("confidence", 1.0)) if isinstance(prov, dict) else 1.0
        factors.provenance_confidence = conf
        factors.explanation["provenance_confidence"] = f"confidence={conf:.2f}"

        # goal alignment
        ga = 1.0 if any(g and g.lower() in content for g in goals if g) else 0.0
        factors.goal_alignment = ga
        factors.explanation["goal_alignment"] = "aligned" if ga else "neutral"

        # weighted total (explicit weights — inspectable)
        weights = {
            "relevance": 0.30,
            "recency": 0.15,
            "affective_charge": 0.15,
            "unresolved_contradiction": 0.10,
            "drive_pressure": 0.10,
            "temporal_importance": 0.05,
            "provenance_confidence": 0.10,
            "goal_alignment": 0.05,
        }
        total = (
            weights["relevance"] * factors.relevance
            + weights["recency"] * factors.recency
            + weights["affective_charge"] * max(0, factors.affective_charge + 0.5)
            + weights["unresolved_contradiction"] * factors.unresolved_contradiction
            + weights["drive_pressure"] * factors.drive_pressure
            + weights["temporal_importance"] * factors.temporal_importance
            + weights["provenance_confidence"] * factors.provenance_confidence
            + weights["goal_alignment"] * factors.goal_alignment
        )
        factors.total = float(total)
        self.history.append({"content": record.content[:40], "total": factors.total, "factors": factors.explanation})
        return factors


def _overlap(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    a_words = set(a.split())
    b_words = set(b.split())
    if not a_words:
        return 0.0
    return len(a_words & b_words) / len(a_words)
