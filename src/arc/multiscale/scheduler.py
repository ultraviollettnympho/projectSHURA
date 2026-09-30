"""arc.multiscale — three-timescale scheduling boundaries (directive §15).

FAST    — reflex / immediate execution
MEDIUM  — reasoning / planning / task processing
SLOW    — identity / consolidation / long-term adaptation

We implement scheduling/state boundaries (no neural simulation).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List


class Timescale(Enum):
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"


@dataclass
class ScheduledAction:
    timescale: Timescale
    action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    enqueued_at: float = field(default_factory=time.time)
    deadline: float = 0.0
    priority: float = 0.0


class MultiscaleScheduler:
    """Scheduling boundaries + queues for each timescale.

    FAST actions are dispatched immediately; MEDIUM queued for the
    reasoning loop; SLOW deferred to offline consolidation. This enforces
    the separation *before* measuring whether it creates useful behavior.
    """

    def __init__(self) -> None:
        self.queues: Dict[Timescale, List[ScheduledAction]] = {
            ts: [] for ts in Timescale
        }
        self.dispatch_log: List[Dict[str, Any]] = []
        self._now = time.time

    def schedule(self, timescale: Timescale, action: str,
                 payload: Dict[str, Any] = None, priority: float = 0.0) -> ScheduledAction:
        act = ScheduledAction(
            timescale=timescale, action=action, payload=payload or {}, priority=priority,
        )
        if timescale == Timescale.FAST:
            self.dispatch_log.append({"action": action, "timescale": "fast", "t": self._now()})
            return act
        self.queues[timescale].append(act)
        return act

    def drain(self, timescale: Timescale) -> List[ScheduledAction]:
        """Drain the queue for a timescale (called by its loop)."""
        queue = self.queues[timescale]
        drain_order = sorted(queue, key=lambda a: a.priority, reverse=True)
        self.queues[timescale] = []
        return drain_order

    def status(self) -> Dict[str, Any]:
        return {
            "queue_depths": {ts.value: len(q) for ts, q in self.queues.items()},
            "fast_dispatch_count": len(self.dispatch_log),
        }
