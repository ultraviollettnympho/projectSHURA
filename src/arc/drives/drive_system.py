"""arc.drives — persistent drives as dynamic motivational pressures.

Each drive carries a pressure that rises/falls with state, activation,
satisfaction, and decay. Drives produce candidate actions; conflicts between
drives surface as a list of competing pressures (no paralysis — arbitration
decides).
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..events.canonical import ArcEvent


@dataclass
class Drive:
    """A motivational pressure with explicit lifecycle dynamics."""
    name: str
    pressure: float = 0.5       # current motivational pressure 0..1
    activation: float = 0.0     # how strongly currently active
    satisfaction: float = 0.0   # accumulated satisfaction of last action
    decay_rate: float = 0.05    # baseline decay/sec toward neutral
    homeostasis: float = 0.2    # neutral target pressure
    last_update: float = field(default_factory=time.time)
    candidate_actions: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    def tick(self, dt: float) -> None:
        """Decay pressure toward homeostasis."""
        self.pressure = self.homeostasis + (self.pressure - self.homeostasis) * math.exp(-self.decay_rate * dt)
        self.pressure = max(0.0, min(1.0, self.pressure))
        self.activation = max(0.0, self.activation - 0.1 * dt)
        self.last_update = time.time()

    def update(self, delta: float, cause: str = "") -> float:
        before = self.pressure
        self.pressure = max(0.0, min(1.0, self.pressure + delta))
        self.activation = max(self.activation, self.pressure)
        if cause:
            self.sources.append(cause)
            self.sources = self.sources[-16:]
        return self.pressure - before

    def sate(self, amount: float) -> None:
        """Satisfy the drive by an amount (0..1)."""
        self.pressure = max(0.0, self.pressure - amount)
        self.satisfaction = min(1.0, self.satisfaction + amount)
        self.activation = 0.0

class DriveSystem:
    """Collection of drives that vary with state and alter action selection.

    NOT scheduled tasks: drive pressures are dynamic motivational variables.
    """

    def __init__(self) -> None:
        self.drives: Dict[str, Drive] = self._initial_drives()
        self._t0 = time.time()

    def _initial_drives(self) -> Dict[str, Drive]:
        return {
            "curiosity": Drive("curiosity", homeostasis=0.3,
                               candidate_actions=["ask", "explore_memory", "probe"],
                               decay_rate=0.04),
            "coherence": Drive("coherence", homeostasis=0.25,
                               candidate_actions=["reconcile", "detect_contradiction", "align"],
                               decay_rate=0.03),
            "completion": Drive("completion", homeostasis=0.15,
                                candidate_actions=["continue_task", "close_loop", "finalize"],
                                decay_rate=0.02),
            "exploration": Drive("exploration", homeostasis=0.2,
                                 candidate_actions=["branch", "sample", "diverge"],
                                 decay_rate=0.05),
            "maintenance": Drive("maintenance", homeostasis=0.5,
                                 candidate_actions=["stabilize", "recover", "protect"],
                                 decay_rate=0.01),
        }

    def tick(self, dt: float) -> None:
        for d in self.drives.values():
            d.tick(dt)
        self._t0 = time.time()

    def update_from_event(self, affective_pressure: Dict[str, float], event: ArcEvent) -> Dict[str, float]:
        """Translate affective/event signals into drive pressure updates."""
        changes: Dict[str, float] = {}
        # curiosity rises with uncertainty and novelty
        if event.event_type == "selfmodel.claimed":
            changes["curiosity"] = self.drives["curiosity"].update(0.05, cause=event.event_id)
        if event.event_type == "contradiction.detected":
            changes["coherence"] = self.drives["coherence"].update(0.3, cause=event.event_id)
        if event.event_type == "decided":
            changes["completion"] = self.drives["completion"].update(0.1, cause=event.event_id)
        # maintenance pressure from coherence_pressure affective dimension
        cp = affective_pressure.get("coherence_pressure", 0.5)
        changes["maintenance"] = self.drives["maintenance"].update((cp - 0.5) * 0.2, cause=event.event_id)
        # uncertainty -> curiosity
        unc = affective_pressure.get("uncertainty", 0.5)
        changes["curiosity"] = self.drives["curiosity"].update((unc - 0.5) * 0.1, cause=event.event_id)
        return changes

    def active_drives(self, threshold: float = 0.0) -> List[Drive]:
        return sorted(
            [d for d in self.drives.values() if d.pressure > threshold],
            key=lambda d: d.pressure,
            reverse=True,
        )

    def conflict(self) -> List[Drive]:
        """Drives competing for action (top contenders). Returns top-2 if split."""
        active = self.active_drives()
        if len(active) < 2:
            return active[:1]
        return active[:2]

    def pressures(self) -> Dict[str, float]:
        return {name: d.pressure for name, d in self.drives.items()}

    def to_dict(self) -> Dict[str, Any]:
        return {name: {
            "pressure": d.pressure,
            "activation": d.activation,
            "satisfaction": d.satisfaction,
            "homeostasis": d.homeostasis,
            "candidate_actions": list(d.candidate_actions),
            "sources": list(d.sources),
        } for name, d in self.drives.items()}
