from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional, Callable, Iterator
import time
import uuid
import json
import os
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger("bea.events")

# ------------------------------------------------------------------
# Event taxonomy constants
# ------------------------------------------------------------------
EVENT_TYPE_INFO = "info"
EVENT_TYPE_STATE = "state"
EVENT_TYPE_LIFECYCLE = "lifecycle"
EVENT_TYPE_ERROR = "error"
EVENT_TYPE_WARNING = "warning"
EVENT_TYPE_PROGRESS = "progress"
EVENT_TYPE_MUTATION = "mutation"
EVENT_TYPE_OBSERVATION = "observation"
EVENT_TYPE_REHEARSAL = "rehearsal"
EVENT_TYPE_CONFLICT = "conflict"

# ------------------------------------------------------------------
# Categories (extended; old values preserved)
# ------------------------------------------------------------------
class EventCategory(str, Enum):
    SYSTEM = "system"
    INPUT = "input"         # user input
    OUTPUT = "output"       # ai response
    THOUGHT = "thought"     # internal reasoning
    SKILL = "skill"         # skill triggers
    TOOL = "tool"           # tool usage
    ERROR = "error"
    MEMORY = "memory"
    AGENT = "agent"
    DREAM = "dream"
    EMBODIMENT = "embodiment"

# ------------------------------------------------------------------
# Severity / Visibility
# ------------------------------------------------------------------
class EventSeverity(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    LEARNING = "learning"
    APPROVAL = "approval"
    DREAM = "dream"

class EventVisibility(str, Enum):
    UI = "ui"
    DEBUG = "debug"
    AUDIT = "audit"

# ------------------------------------------------------------------
# Canonical event envelope (backward-compatible extension)
# ------------------------------------------------------------------
@dataclass
class BrainEvent:
    category: EventCategory = EventCategory.SYSTEM
    source: str = "unknown"
    message: str = ""
    # New fields — appended after legacy fields for compatibility
    event_type: str = EVENT_TYPE_INFO
    subsystem: str = "core"
    run_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    severity: str = EventSeverity.INFO.value
    visibility: str = EventVisibility.UI.value
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    sequence: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)

# ------------------------------------------------------------------
# Persistent JSONL journal
# ------------------------------------------------------------------
class EventJournal:
    """Append-only JSONL event journal with bounded retention."""

    def __init__(
        self,
        path: str = "data/events/events.jsonl",
        max_size_bytes: int = 5_000_000,
        max_lines: int = 20_000,
    ):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_bytes
        self.max_lines = max_lines
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")

    def _current_size(self) -> int:
        try:
            return self.path.stat().st_size
        except Exception:
            return 0

    def append(self, event_dict: Dict[str, Any]) -> None:
        line = json.dumps(event_dict, default=str, ensure_ascii=False) + "\n"
        current_size = self._current_size()
        line_bytes = len(line.encode("utf-8"))
        if current_size + line_bytes > self.max_size_bytes:
            self._rotate()
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)

    def _rotate(self) -> None:
        """Bounded retention: truncate to the most recent half when overflowing."""
        events = self.read_all()
        # Check both line count and file size independently
        needs_rotation = (
            len(events) > self.max_lines
            or self._current_size() > self.max_size_bytes
        )
        if not needs_rotation:
            return
        # Continue rotating until both limits are satisfied
        while len(events) > self.max_lines or self._current_size() > self.max_size_bytes:
            truncated = events[-self.max_lines // 2 :]
            # Write to temp file and atomically replace
            temp_path = self.path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                for ev in truncated:
                    f.write(json.dumps(ev, default=str, ensure_ascii=False) + "\n")
            os.replace(temp_path, self.path)
            events = self.read_all()

    def read_all(self) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        if not self.path.exists():
            return events
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    # Fail-safe: skip malformed lines without corrupting replay
                    continue
        return events

    def replay(
        self,
        event_type: Optional[str] = None,
        subsystem: Optional[str] = None,
        run_id: Optional[str] = None,
        parent_event_id: Optional[str] = None,
        sequence_start: Optional[int] = None,
        severity: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        events = self.read_all()
        # Replay filters preserve original IDs; no new event IDs produced
        if event_type is not None:
            events = [e for e in events if e.get("event_type") == event_type]
        if subsystem is not None:
            events = [e for e in events if e.get("subsystem") == subsystem]
        if run_id is not None:
            events = [e for e in events if e.get("run_id") == run_id]
        if parent_event_id is not None:
            events = [e for e in events if e.get("parent_event_id") == parent_event_id]
        if sequence_start is not None:
            events = [e for e in events if e.get("sequence", 0) >= sequence_start]
        if severity is not None:
            events = [e for e in events if e.get("severity") == severity]
        if visibility is not None:
            events = [e for e in events if e.get("visibility") == visibility]
        return events

# ------------------------------------------------------------------
# Event manager (extended backward-compatibly)
# ------------------------------------------------------------------
class EventManager:
    def __init__(
        self,
        max_history: int = 200,
        journal_path: Optional[str] = None,
        max_size_bytes: int = 5_000_000,
        max_lines: int = 20_000,
    ):
        self.events: List[BrainEvent] = []
        self.max_history = max_history
        self._subscribers: List[Dict[str, Any]] = []
        # Default journal location follows existing data conventions
        default_path = journal_path or "data/events/events.jsonl"
        self.journal = EventJournal(
            path=default_path,
            max_size_bytes=max_size_bytes,
            max_lines=max_lines,
        )
        # Initialize sequence from the highest existing journal entry
        # so new events continue numbering after retained entries
        self._sequence = 0
        try:
            existing = self.journal.read_all()
            if existing:
                self._sequence = max(e.get("sequence", 0) for e in existing)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Backward-compatible publish (existing callers unchanged)
    # ------------------------------------------------------------------
    def publish(
        self,
        category: EventCategory,
        source: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        event_type: str = EVENT_TYPE_INFO,
        subsystem: str = "core",
        run_id: Optional[str] = None,
        parent_event_id: Optional[str] = None,
        severity: Optional[str] = None,
        visibility: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> BrainEvent:
        if metadata is None:
            metadata = {}
        self._sequence += 1
        event = BrainEvent(
            category=category,
            source=source,
            message=message,
            event_type=event_type,
            subsystem=subsystem,
            run_id=run_id,
            parent_event_id=parent_event_id,
            severity=severity or EventSeverity.INFO.value,
            visibility=visibility or EventVisibility.UI.value,
            payload=payload or {},
            timestamp=time.time(),
            sequence=self._sequence,
            id=str(uuid.uuid4()),
            metadata=metadata,
        )
        self.events.append(event)
        if len(self.events) > self.max_history:
            self.events.pop(0)
        # Persistent journal
        event_dict = self._to_dict(event)
        try:
            self.journal.append(event_dict)
        except Exception as e:
            logger.warning(f"Event journal append failed: {e}")
        # Notify subscribers
        for sub in self._subscribers:
            try:
                if sub["filter_fn"](event_dict):
                    sub["handler"](event_dict, event)
            except Exception as e:
                logger.error(f"Event subscriber handler failed: {e}")
        logger.debug(f"[{category.value}] [{source}] {message}")
        return event

    # ------------------------------------------------------------------
    # Subscription (composable filters, no UI dependency)
    # ------------------------------------------------------------------
    def subscribe(
        self,
        handler: Callable[[Dict[str, Any], BrainEvent], None],
        event_type: Optional[str] = None,
        subsystem: Optional[str] = None,
        run_id: Optional[str] = None,
        severity: Optional[str] = None,
        visibility: Optional[str] = None,
        source: Optional[str] = None,
    ) -> None:
        def filter_fn(event_dict: Dict[str, Any]) -> bool:
            if event_type is not None and event_dict.get("event_type") != event_type:
                return False
            if subsystem is not None and event_dict.get("subsystem") != subsystem:
                return False
            if run_id is not None and event_dict.get("run_id") != run_id:
                return False
            if severity is not None and event_dict.get("severity") != severity:
                return False
            if visibility is not None and event_dict.get("visibility") != visibility:
                return False
            if source is not None and event_dict.get("source") != source:
                return False
            return True
        self._subscribers.append({"filter_fn": filter_fn, "handler": handler})

    def unsubscribe(self, handler: Callable[[Dict[str, Any], BrainEvent], None]) -> None:
        self._subscribers = [s for s in self._subscribers if s["handler"] is not handler]

    # ------------------------------------------------------------------
    # Filtering / Replay
    # ------------------------------------------------------------------
    def filter_events(
        self,
        event_type: Optional[str] = None,
        subsystem: Optional[str] = None,
        run_id: Optional[str] = None,
        severity: Optional[str] = None,
        visibility: Optional[str] = None,
        source: Optional[str] = None,
        parent_event_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results = [self._to_dict(e) for e in self.events]
        if event_type is not None:
            results = [r for r in results if r.get("event_type") == event_type]
        if subsystem is not None:
            results = [r for r in results if r.get("subsystem") == subsystem]
        if run_id is not None:
            results = [r for r in results if r.get("run_id") == run_id]
        if severity is not None:
            results = [r for r in results if r.get("severity") == severity]
        if visibility is not None:
            results = [r for r in results if r.get("visibility") == visibility]
        if source is not None:
            results = [r for r in results if r.get("source") == source]
        if parent_event_id is not None:
            results = [r for r in results if r.get("parent_event_id") == parent_event_id]
        return results

    def replay(
        self,
        event_type: Optional[str] = None,
        subsystem: Optional[str] = None,
        run_id: Optional[str] = None,
        parent_event_id: Optional[str] = None,
        sequence_start: Optional[int] = None,
        severity: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.journal.replay(
            event_type=event_type,
            subsystem=subsystem,
            run_id=run_id,
            parent_event_id=parent_event_id,
            sequence_start=sequence_start,
            severity=severity,
            visibility=visibility,
        )

    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------
    def get_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [self._to_dict(e) for e in self.events[-limit:]]

    def _to_dict(self, event: BrainEvent) -> Dict[str, Any]:
        return {
            "id": event.id,
            "event_id": event.id,
            "timestamp": event.timestamp,
            "sequence": event.sequence,
            "event_type": event.event_type,
            "category": event.category.value,
            "source": event.source,
            "message": event.message,
            "subsystem": event.subsystem,
            "run_id": event.run_id,
            "parent_event_id": event.parent_event_id,
            "severity": event.severity,
            "visibility": event.visibility,
            "payload": event.payload,
            "metadata": event.metadata,
        }

    def event_to_dict(self, event: BrainEvent) -> Dict[str, Any]:
        return self._to_dict(event)
