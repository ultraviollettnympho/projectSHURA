"""arc.memory.layers — layered memory with provenance, non-resolving contradictions."""
from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..events.canonical import ArcEvent, ProvenanceRecord, EVENT_TYPE_MEMORY_RECORDED


class MemoryKind(str, Enum):
    """Memory layer taxonomy (directive §3).

    Why these layers:
      EPISODIC        — what happened (events, interactions)
      SEMANTIC        — what has been learned/generalized (facts)
      PROCEDURAL      — how something is done (skills, workflows)
      AUTOBIOGRAPHICAL — continuity narrative (who SHURA is over time)
      WORKING         — what matters now
    """
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    AUTOBIOGRAPHICAL = "autobiographical"
    WORKING = "working"


@dataclass
class MemoryRecord:
    """A retrievable memory with provenance.

    A memory without provenance is degraded evidence, never equivalent to
    verified state (directive: "A memory without provenance should be treated
    as degraded evidence").
    """
    memory_id: str
    kind: MemoryKind
    content: str
    created_at: float
    provenance: ProvenanceRecord
    confidence: float = 1.0
    last_accessed: float = field(default_factory=time.time)
    salience: float = 0.0
    corroboration: List[str] = field(default_factory=list)  # memory_ids corroborating this
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        from dataclasses import asdict
        d = asdict(self)
        d["kind"] = d["kind"].value if hasattr(d["kind"], "value") else d["kind"]
        d["provenance"] = self.provenance.to_dict()
        return d


@dataclass
class Contradiction:
    """Two competing claims retained WITHOUT automatic resolution.

    Resolution is evidence-driven (directive §4); the registry preserves
    uncertainty rather than collapsing it.
    """
    contradiction_id: str
    claim_a: str
    claim_b: str
    evidence_a: ProvenanceRecord
    evidence_b: ProvenanceRecord
    confidence: float = 0.5
    corroboration: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution: Optional[str] = None


class ContradictionRegistry:
    """Stores contradictions without auto-resolving (directive §4)."""

    def __init__(self) -> None:
        self.items: List[Contradiction] = []

    def register(
        self,
        claim_a: str,
        claim_b: str,
        evidence_a: ProvenanceRecord,
        evidence_b: ProvenanceRecord,
        confidence: float = 0.5,
    ) -> Contradiction:
        c = Contradiction(
            contradiction_id=str(uuid.uuid4()),
            claim_a=claim_a,
            claim_b=claim_b,
            evidence_a=evidence_a,
            evidence_b=evidence_b,
            confidence=confidence,
        )
        self.items.append(c)
        return c

    def unresolved(self) -> List[Contradiction]:
        return [c for c in self.items if not c.resolved]


class MemoryIndex:
    """Hybrid memory index over canonical events.

    Builds memory records from canonical events and supports retrieval by:
      - lexical match on content/tags
      - temporal proximity (recent)
      - provenance (source/actor/trust_level)
      - kind
      - salience
    Retrieval ALWAYS returns provenance (directive §3).
    """

    def __init__(self) -> None:
        self.records: List[MemoryRecord] = []
        self.contradictions = ContradictionRegistry()

    def index_events(self, events: List[ArcEvent]) -> None:
        """Reindex all events (idempotent rebuild from canonical log)."""
        self.records = []
        # Reset contradictions on full rebuild (deterministic).
        self.contradictions = ContradictionRegistry()
        for ev in events:
            kind = self._classify(ev)
            if kind is None:
                continue
            # Build memory content from payload
            content = self._content_of(ev)
            if content is None:
                continue
            prov = ProvenanceRecord(
                source=ev.source,
                actor=ev.actor,
                confidence=float(ev.confidence),
                trust_level="verified" if ev.event_type else "inferred",
                origin_session=ev.session_context_id,
                origin_event_id=ev.event_id,
            )
            # Deterministic memory_id derived from the source event_id so
            # reindex/reconstruction is reproducible (not random UUIDs).
            mem_id = hashlib.sha256(
                (EVENT_TYPE_MEMORY_RECORDED + ":" + ev.event_id).encode("utf-8")
            ).hexdigest()
            rec = MemoryRecord(
                memory_id=mem_id,
                kind=kind,
                content=content,
                created_at=ev.timestamp,
                provenance=prov,
                confidence=float(ev.confidence),
                tags=ev.payload.get("tags", []) if isinstance(ev.payload, dict) else [],
            )
            self.records.append(rec)
        self._scan_contradictions()

    @staticmethod
    def _classify(ev: ArcEvent) -> Optional[MemoryKind]:
        et = ev.event_type
        if et == EVENT_TYPE_MEMORY_RECORDED and isinstance(ev.payload, dict):
            k = ev.payload.get("kind")
            if k:
                try:
                    return MemoryKind(k)
                except ValueError:
                    return MemoryKind.EPISODIC
        if et == "selfmodel.claimed" or et == "selfmodel.updated":
            return MemoryKind.AUTOBIOGRAPHICAL
        if et == "decided":
            return MemoryKind.PROCEDURAL
        if et == "experience" or et == "state":
            return MemoryKind.EPISODIC
        return MemoryKind.EPISODIC

    @staticmethod
    def _content_of(ev: ArcEvent) -> Optional[str]:
        if isinstance(ev.payload, dict):
            if "content" in ev.payload and isinstance(ev.payload["content"], str):
                return ev.payload["content"]
            if "message" in ev.payload:
                return str(ev.payload["message"])
            if "value" in ev.payload:
                return f"{ev.payload.get('field','field')}={ev.payload['value']}"
            # Fallback: stringify the payload
            return repr(ev.payload)
        return None

    def _scan_contradictions(self) -> None:
        """Detect competing claims about the same field (no auto-resolution)."""
        by_field: Dict[str, List[MemoryRecord]] = {}
        for r in self.records:
            # Records carrying a 'field' proposition
            pass
        # Lightweight contradiction detection on selfmodel claims
        claims = {}
        for r in self.records:
            if isinstance(r.content, str) and "=" in r.content and r.kind == MemoryKind.AUTOBIOGRAPHICAL:
                parts = r.content.split("=", 1)
                key = parts[0]
                claims.setdefault(key, []).append(r)
        for key, recs in claims.items():
            if len(recs) > 1:
                vals = {r.content for r in recs}
                if len(vals) > 1:
                    # conflicting claims for same key
                    ra, rb = recs[0], recs[1]
                    self.contradictions.register(
                        claim_a=ra.content,
                        claim_b=rb.content,
                        evidence_a=ra.provenance,
                        evidence_b=rb.provenance,
                        confidence=(ra.confidence + rb.confidence) / 2,
                    )

    # --- retrieval (always with provenance) ---

    def recent(self, limit: int = 10) -> List[MemoryRecord]:
        return sorted(self.records, key=lambda r: r.created_at, reverse=True)[:limit]

    def by_kind(self, kind: MemoryKind) -> List[MemoryRecord]:
        return [r for r in self.records if r.kind == kind]

    def search(self, query: str, kinds: Optional[List[MemoryKind]] = None) -> List[MemoryRecord]:
        q = query.lower()
        cands = self.records
        if kinds:
            ks = set(k.value for k in kinds)
            cands = [r for r in cands if r.kind.value in ks]
        results = [r for r in cands if q in r.content.lower() or any(q in t.lower() for t in r.tags)]
        results.sort(key=lambda r: (r.salience, r.created_at), reverse=True)
        for r in results:
            r.last_accessed = time.time()
        return results

    def retrieve(self, query: str) -> Dict[str, Any]:
        """Hybrid retrieval returning content + provenance + contradictions."""
        hits = self.search(query)
        return {
            "results": [r.to_dict() for r in hits],
            "contradictions": [
                {
                    "claim_a": c.claim_a,
                    "claim_b": c.claim_b,
                    "confidence": c.confidence,
                    "resolved": c.resolved,
                }
                for c in self.contradictions.unresolved()
            ],
            "result_count": len(hits),
        }
