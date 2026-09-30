"""arc.affect — persistent affective state engine (computational hypothesis, not
consciousness). Interpretable dimensions with decay/regulation and explicit
influence policy on retrieval and response strategy.
"""
from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

_DIMENSIONS = (
    "valence",          # -1..1  (negative..positive)
    "arousal",          # 0..1   (calm..activated)
    "stability",        # 0..1   (labile..stable)
    "uncertainty",      # 0..1   (certain..uncertain)
    "cognitive_load",   # 0..1   (low..high load)
    "coherence_pressure",  # 0..1 (pressured..coherent)
)

_RANGES = {
    "valence": (-1.0, 1.0),
    "arousal": (0.0, 1.0),
    "stability": (0.0, 1.0),
    "uncertainty": (0.0, 1.0),
    "cognitive_load": (0.0, 1.0),
    "coherence_pressure": (0.0, 1.0),
}

_BASELINE = {
    "valence": 0.0,
    "arousal": 0.5,
    "stability": 0.5,
    "uncertainty": 0.5,
    "cognitive_load": 0.3,
    "coherence_pressure": 0.5,
}

# Per-dimension decay rate toward baseline (per second)
_DECAY = {
    "valence": 0.25,
    "arousal": 0.35,
    "stability": 0.15,
    "uncertainty": 0.30,
    "cognitive_load": 0.45,
    "coherence_pressure": 0.20,
}


def _clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


@dataclass
class Dimension:
    """One affective dimension with explicit decay/regulation policy."""
    name: str
    value: float
    baseline: float
    decay_rate: float  # exponential decay per second toward baseline
    lo: float
    hi: float
    confidence: float = 1.0
    sources: List[str] = field(default_factory=list)
    last_change: float = field(default_factory=time.time)
    rate_of_change: float = 0.0

    def decay(self, dt: float) -> None:
        """Exponential decay toward baseline (regulation)."""
        before = self.value
        self.value = self.baseline + (self.value - self.baseline) * math.exp(-self.decay_rate * dt)
        self.value = _clip(self.value, self.lo, self.hi)
        self.rate_of_change = (self.value - before) / max(dt, 1e-6)
        self.last_change += dt
        self.confidence = max(0.0, self.confidence - 0.01 * dt) if self.sources else 0.5

    def bump(self, delta: float, cause: str = "") -> None:
        lo, hi = self.lo, self.hi
        before = self.value
        self.value = _clip(self.value + delta, lo, hi)
        dt = max(time.time() - self.last_change, 1e-6)
        self.rate_of_change = (self.value - before) / dt
        self.last_change = time.time()
        if cause:
            self.sources.append(cause)
            # bounded buffer of recent causes
            if len(self.sources) > 16:
                self.sources = self.sources[-16:]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ArcAffectiveState:
    """Persistent affective state (computational hypothesis).

    Not consciousness — a set of interpretable dimensions with explicit,
    inspectable influence policies on retrieval salience and response strategy.
    """

    def __init__(self, identity_hash: str = "") -> None:
        self.dimensions: Dict[str, Dimension] = {
            name: Dimension(
                name=name,
                value=_BASELINE[name],
                baseline=_BASELINE[name],
                decay_rate=_DECAY[name],
                lo=_RANGES[name][0],
                hi=_RANGES[name][1],
            )
            for name in _DIMENSIONS
        }
        self.identity_hash = identity_hash
        self._t0 = time.time()

    def tick(self, dt: Optional[float] = None) -> None:
        """Advancing time → decay toward baseline (regulation)."""
        dt = dt if dt is not None else max(time.time() - self._t0, 0.0)
        for d in self.dimensions.values():
            d.decay(dt)
        self._t0 = time.time()

    def update_from_event(self, event) -> Dict[str, float]:
        """Compute explicit affect response to an event (inspectable)."""
        changes: Dict[str, float] = {}
        content = ""
        if isinstance(event.payload, dict):
            content = str(event.payload.get("content", ""))
        text = (event.event_type + " " + content).lower()

        # Valence: positive/negative keyword mapping (explicit, reviewable)
        positive = ["success", "complete", "good", "creative", "coherent", "resolved", "win", "growth",
                    "persistent", "achievement", "pride", "breakthrough", "reward", "stable", "flourish"]
        negative = ["failure", "error", "conflict", "drift", "degraded", "loss", "fragment", "stuck",
                    "collapse", "decay", "uncertain", "fragmented", "paralysis", "stale"]
        pos = sum(1 for w in positive if w in text)
        neg = sum(1 for w in negative if w in text)
        valence_delta = _clip((pos - neg) * 0.08, -0.4, 0.4)
        if valence_delta:
            self.dimensions["valence"].bump(valence_delta, cause=event.event_id)
            changes["valence"] = valence_delta

        # Uncertainty rises on conflict/contradiction events
        unc = 0.0
        if event.event_type == "contradiction.detected":
            unc = min(0.9, self.dimensions["uncertainty"].value + 0.25)
            self.dimensions["uncertainty"].bump(0.25, cause=event.event_id)
            changes["uncertainty"] = 0.25
        # cognitive load rises on high-volume experience
        self.dimensions["cognitive_load"].bump(0.01, cause=event.event_id)
        changes["cognitive_load"] = 0.01

        # coherence pressure: positive when contradictions exist
        cp_delta = -0.01 if event.event_type == "contradiction.detected" else 0.0
        if cp_delta:
            self.dimensions["coherence_pressure"].bump(cp_delta, cause=event.event_id)
            changes["coherence_pressure"] = cp_delta
        return changes

    @property
    def valence(self) -> float:
        return self.dimensions["valence"].value

    @property
    def uncertainty(self) -> float:
        return self.dimensions["uncertainty"].value

    def current(self) -> Dict[str, float]:
        return {name: d.value for name, d in self.dimensions.items()}

    def rates(self) -> Dict[str, float]:
        return {name: d.rate_of_change for name, d in self.dimensions.items()}

    def retrieval_boost(self, record_salience: float) -> float:
        """Affective charge modulates retrieval salience (explicit policy).

        Higher |valence| and higher arousal amplify retrieval; higher cognitive
        load dampens it (capacity-limited attention).
        """
        v = abs(self.dimensions["valence"].value)
        a = self.dimensions["arousal"].value
        load = self.dimensions["cognitive_load"].value
        boost = 1.0 + (0.15 * v) + (0.10 * a) - (0.20 * load)
        return _clip(boost, 0.0, 2.0)

    def response_strategy(self) -> Dict[str, float]:
        """Explicit mapping from affect to response-strategy factors.

        risk_tolerance, persistence, self_monitor — all interpretable.
        """
        v = self.dimensions["valence"].value
        a = self.dimensions["arousal"].value
        u = self.dimensions["uncertainty"].value
        load = self.dimensions["cognitive_load"].value
        return {
            "risk_tolerance": _clip(0.5 + 0.40 * v + 0.10 * a - 0.10 * load, 0.0, 1.0),
            "persistence": _clip(0.5 + 0.30 * v - 0.10 * u, 0.0, 1.0),
            "self_monitor": _clip(0.5 + 0.25 * u + 0.20 * load, 0.0, 1.0),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions": {n: d.to_dict() for n, d in self.dimensions.items()},
            "identity_hash": self.identity_hash,
        }
