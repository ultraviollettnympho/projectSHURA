"""arc.consolidation — offline consolidation engine (NOT "dreaming").

Responsibilities: episodic→semantic abstraction, contradiction detection,
self-model updates, pattern discovery. Canonical events are NEVER deleted
by consolidation. Speculative discoveries are explicitly marked SPECULATIVE.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..events.canonical import ArcEvent
from ..memory.layers import MemoryIndex, MemoryRecord, MemoryKind


@dataclass
class ConsolidationResult:
    semantic_facts: List[Dict[str, Any]] = field(default_factory=list)
    updated_records: int = 0
    contradictions_found: int = 0
    self_model_updates: List[Dict[str, Any]] = field(default_factory=list)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    speculative: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=dict)


class ConsolidationEngine:
    """Offline / background consolidation producing DERIVED knowledge.

    Canonical events are immutable; consolidation only creates derived facts
    and marks them explicitly (SPECULATIVE vs VERIFIED).
    """

    # Keywords signalling factual claims in episodic content (explicit pattern)
    CLAIM_PATTERNS = [
        r"(?P<fact>shura is [^,\.]+)",
        r"(?P<fact>identity persists [^,\.]+)",
        r"(?P<fact>prefers [^,\.]+)",
    ]

    def __init__(self) -> None:
        self.last_run: float = 0.0

    def run(self, events: List[ArcEvent], memory: MemoryIndex) -> ConsolidationResult:
        """Consolidate episodic events into semantic facts + detect patterns.

        Does NOT emit or delete canonical events directly; returns derived
        results that the runtime may persist via canonical ``memory.recorded``
        events marked VERIFIED/SPECULATIVE.
        """
        self.last_run = time.time()
        result = self._abstractions(events, memory)
        result.contradictions_found = len(memory.contradictions.unresolved())
        self._detect_patterns(result, events)
        result.provenance = {"source": "consolidation", "actor": "shura",
                             "trust_level": "verified", "timestamp": self.last_run}
        return result

    def _abstractions(self, events: List[ArcEvent], memory: MemoryIndex) -> ConsolidationResult:
        """Episodic -> semantic: extract declarative facts from experience content."""
        result = ConsolidationResult()
        for ev in events:
            if ev.event_type != "experience" and ev.event_type != "state":
                continue
            content = ""
            if isinstance(ev.payload, dict):
                content = str(ev.payload.get("content", ""))
            for pat in self.CLAIM_PATTERNS:
                m = re.search(pat, content, flags=re.IGNORECASE)
                if m:
                    fact = m.group("fact").strip().rstrip(".")
                    result.semantic_facts.append({
                        "fact": fact,
                        "derived_from_event": ev.event_id,
                        "confidence": float(ev.confidence),
                        "status": "verified",
                        "tags": ["semantic", "consolidated"],
                    })
        return result

    def _detect_patterns(self, result: ConsolidationResult, events: List[ArcEvent]) -> None:
        """Pattern discovery — marked SPECULATIVE until corroborated."""
        if len(events) < 3:
            return
        # Detect repeated event types (candidate behavioral patterns)
        type_counts: Dict[str, int] = {}
        for ev in events:
            type_counts[ev.event_type] = type_counts.get(ev.event_type, 0) + 1
        for etype, count in type_counts.items():
            if count >= 3:
                result.patterns.append({
                    "pattern": f"recurring_{etype}",
                    "frequency": count,
                    "confidence": min(count / 5.0, 0.9),
                })
                result.speculative.append({
                    "description": f"behavioral_tendency_{etype}",
                    "frequency": count,
                    "status": "SPECULATIVE",
                    "rationale": "inferred from event frequency, not independently verified",
                })
