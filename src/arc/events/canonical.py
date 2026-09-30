"""arc.events.canonical — canonical event record and append-only store.

Canonical history is the append-only append-only event log. It is the source of
truth for everything the arc subsystem reconstructs. Derived state is rebuilt
by replaying these records; canonical records are never mutated.

This adapts the design intent of docs/EVENT_CONTRACT.md and
src/core/events.py (EventJournal) into arc's authoritative canonical store.
It does NOT modify or replace those modules; arc owns its own canonical
journal so reconstruction equivalence and schema provenance are testable in
isolation (Phase 3: inspectability, reversibility, migration safety,
temporal ordering, provenance, deterministic reconstruction).
"""
from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = 1

VALID_TRUST_LEVELS = {"verified", "inferred", "speculated"}


@dataclass
class ProvenanceRecord:
    """Origin and trustworthiness of an event/fact.

    Why each field exists:
      source          — which system/component produced the record (for audit)
      actor           — who was agentively responsible (shura/user/tool/system)
      confidence      — quantified trustworthiness 0..1
      trust_level     — categorical trustworthiness bucket
      origin_session  — session that originally produced this fact
      origin_event_id — link back to a causal canonical event
    """
    source: str = "unknown"
    actor: str = "system"
    confidence: float = 1.0
    trust_level: str = "verified"
    origin_session: str = ""
    origin_event_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not (0.0 <= float(self.confidence) <= 1.0):
            raise ValueError("confidence must be within [0.0, 1.0]")
        if self.trust_level not in VALID_TRUST_LEVELS:
            raise ValueError(f"trust_level must be one of {VALID_TRUST_LEVELS}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ArcEvent:
    """Canonical immutable event record.

    Schema (Phase 5 Event contract). Every field has a reason:
      event_id           — global unique id; survives replay
      timestamp          — wall-clock emission time; temporal ordering
      source             — producer/system of origin
      actor              — agentive actor
      event_type         — explicit classification (taxonomy below)
      payload            — structured data; never arbitrary text
      provenance         — provenance record (serialized ProvenanceRecord)
      confidence         — trustworthiness of THIS event
      causal_parent      — link to a prior event (causal chain)
      session_context_id — correlation id grouping events into a logical run
      schema_version     — allows forward-compatible migration
      sequence           — monotonic local ordering within this store
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"
    actor: str = "system"
    event_type: str = "state"
    payload: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    causal_parent: Optional[str] = None
    session_context_id: str = ""
    schema_version: int = SCHEMA_VERSION
    sequence: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if not d.get("provenance"):
            d["provenance"] = {}
        if not (0.0 <= float(d.get("confidence", 1.0)) <= 1.0):
            d["confidence"] = 1.0
        return d


# Event type taxonomy (arc's classification; extends EVENT_CONTRACT.md).
EVENT_TYPE_STATE = "state"
EVENT_TYPE_EXPERIENCE = "experience"
EVENT_TYPE_SELFMODEL_CLAIM = "selfmodel.claimed"
EVENT_TYPE_SELFMODEL_UPDATE = "selfmodel.updated"
EVENT_TYPE_MEMORY_RECORDED = "memory.recorded"
EVENT_TYPE_CONTRADICTION = "contradiction.detected"
EVENT_TYPE_OBSERVATION = "observation"
EVENT_TYPE_COHERENCE = "coherence.assessed"
EVENT_TYPE_IDENTITY_LOADED = "identity.loaded"
EVENT_TYPE_IDENTITY_CHANGE_PROPOSED = "identity.change.proposed"
EVENT_TYPE_IDENTITY_CHANGE_APPLIED = "identity.change.applied"
EVENT_TYPE_ACTION = "action"
EVENT_TYPE_DECIDED = "decided"


class ArcEventStore:
    """Append-only canonical event store.

    Invariants:
      * Records are only ever appended, never updated or deleted in canonical form.
      * Sequence numbers are monotonic within a store instance and survive restarts
        (re-derived from the log on open).
      * Derived snapshots are optional, NOT canonical — they can be deleted without
        data loss; canonical history is the journal.
    """

    def __init__(
        self,
        path: Optional[str] = None,
        session_id: Optional[str] = None,
        snapshot_dir: Optional[str] = None,
    ) -> None:
        self.path = Path(path) if path else Path("data/arc/events.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")
        self.session_id = session_id or str(uuid.uuid4())
        self.snapshot_dir = (
            Path(snapshot_dir) if snapshot_dir else self.path.parent / "snapshots"
        )
        self._lock = threading.Lock()
        with self._lock:
            self._seq = 0
            for ev in self._read_file_raw():
                self._seq = max(self._seq, int(ev.get("sequence", 0)))

    def _read_file_raw(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        if not self.path.exists():
            return out
        for raw in self.read_text().splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                out.append(json.loads(raw))
            except json.JSONDecodeError:
                # Fail-safe: skip malformed lines without corrupting replay
                continue
        return out

    def read_text(self) -> str:
        if not self.path.exists():
            return ""
        return self.path.read_text(encoding="utf-8")

    def append(self, event: ArcEvent) -> ArcEvent:
        """Append a canonical event. Returns the event with sequence filled."""
        if not event.session_context_id:
            event.session_context_id = self.session_id
        with self._lock:
            self._seq += 1
            event.sequence = self._seq
        line = json.dumps(event.to_dict(), default=str, ensure_ascii=False) + "\n"
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)
        return event

    def read_all(self) -> List[ArcEvent]:
        raw = self._read_file_raw()
        fields = set(ArcEvent.__dataclass_fields__)
        out: List[ArcEvent] = []
        for d in raw:
            cleaned = {k: v for k, v in d.items() if k in fields}
            out.append(ArcEvent(**cleaned))
        return out

    def replay(
        self,
        event_type: Optional[str] = None,
        session: Optional[str] = None,
    ) -> List[ArcEvent]:
        evs = self.read_all()
        if event_type is not None:
            evs = [e for e in evs if e.event_type == event_type]
        if session is not None:
            evs = [e for e in evs if e.session_context_id == session]
        return evs

    def snapshot(self, name: str, state: Dict[str, Any]) -> Path:
        """Write a DERIVED snapshot (not canonical). Safe to delete."""
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        sp = self.snapshot_dir / f"{name}.json"
        sp.write_text(
            json.dumps(
                {"name": name, "sequence": self._seq, "state": state},
                default=str,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return sp

    def restore_snapshot(self, name: str) -> Dict[str, Any]:
        sp = self.snapshot_dir / f"{name}.json"
        if not sp.exists():
            return {}
        return json.loads(sp.read_text(encoding="utf-8")).get("state", {})
