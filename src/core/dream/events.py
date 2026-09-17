"""Dream event emission helpers — uses existing EventContract only.

No new persistence, no new event transport, no duplication of
Subscription/Replay/Journal logic.
"""

from typing import Optional, Dict, Any
import time

# Import the existing event contract (not a new event system)
from src.core.events import (
    EventCategory,
    EventSeverity,
    EventVisibility,
    EVENT_TYPE_INFO,
    EVENT_TYPE_STATE,
    EVENT_TYPE_LIFECYCLE,
    EVENT_TYPE_PROGRESS,
    EVENT_TYPE_ERROR,
)

# ------------------------------------------------------------------
# Dream event taxonomy (matches docs/EVENT_CONTRACT.md future target)
# ------------------------------------------------------------------
EVENT_DREAM_STARTED = "dream.started"
EVENT_DREAM_SNAPSHOT_CREATED = "dream.snapshot_created"
EVENT_DREAM_RECONCILIATION_STARTED = "dream.reconciliation_started"
EVENT_DREAM_RECONCILIATION_COMPLETED = "dream.reconciliation_completed"
EVENT_DREAM_COMPLETED = "dream.completed"
EVENT_DREAM_FAILED = "dream.failed"

# ------------------------------------------------------------------
# Event emission helpers (minimal; requires an existing EventManager instance)
# ------------------------------------------------------------------

def emit_dream_started(
    event_manager,
    run_id: str,
    parent_event_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    """Emit dream.started lifecycle event."""
    return event_manager.publish(
        category=EventCategory.DREAM,
        source="dream_engine",
        message=f"Dream started: {run_id}",
        event_type=EVENT_TYPE_LIFECYCLE,
        subsystem="dream",
        run_id=run_id,
        parent_event_id=parent_event_id,
        severity=EventSeverity.INFO.value,
        visibility=EventVisibility.UI.value,
        payload=payload or {},
    )


def emit_dream_snapshot_created(
    event_manager,
    run_id: str,
    snapshot_id: str,
    parent_event_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    return event_manager.publish(
        category=EventCategory.DREAM,
        source="dream_engine",
        message=f"Dream snapshot created: {snapshot_id}",
        event_type=EVENT_DREAM_SNAPSHOT_CREATED,
        subsystem="dream",
        run_id=run_id,
        parent_event_id=parent_event_id,
        severity=EventSeverity.INFO.value,
        visibility=EventVisibility.UI.value,
        payload=payload or {},
    )


def emit_dream_reconciliation_started(
    event_manager,
    run_id: str,
    parent_event_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    return event_manager.publish(
        category=EventCategory.DREAM,
        source="dream_engine",
        message=f"Dream reconciliation started: {run_id}",
        event_type=EVENT_DREAM_RECONCILIATION_STARTED,
        subsystem="dream",
        run_id=run_id,
        parent_event_id=parent_event_id,
        severity=EventSeverity.INFO.value,
        visibility=EventVisibility.UI.value,
        payload=payload or {},
    )


def emit_dream_reconciliation_completed(
    event_manager,
    run_id: str,
    parent_event_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    return event_manager.publish(
        category=EventCategory.DREAM,
        source="dream_engine",
        message=f"Dream reconciliation completed: {run_id}",
        event_type=EVENT_DREAM_RECONCILIATION_COMPLETED,
        subsystem="dream",
        run_id=run_id,
        parent_event_id=parent_event_id,
        severity=EventSeverity.SUCCESS.value,
        visibility=EventVisibility.UI.value,
        payload=payload or {},
    )


def emit_dream_completed(
    event_manager,
    run_id: str,
    parent_event_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    return event_manager.publish(
        category=EventCategory.DREAM,
        source="dream_engine",
        message=f"Dream completed: {run_id}",
        event_type=EVENT_DREAM_COMPLETED,
        subsystem="dream",
        run_id=run_id,
        parent_event_id=parent_event_id,
        severity=EventSeverity.SUCCESS.value,
        visibility=EventVisibility.UI.value,
        payload=payload or {},
    )


def emit_dream_failed(
    event_manager,
    run_id: str,
    parent_event_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    return event_manager.publish(
        category=EventCategory.DREAM,
        source="dream_engine",
        message=f"Dream failed: {run_id}",
        event_type=EVENT_DREAM_FAILED,
        subsystem="dream",
        run_id=run_id,
        parent_event_id=parent_event_id,
        severity=EventSeverity.ERROR.value,
        visibility=EventVisibility.UI.value,
        payload=payload or {},
    )
