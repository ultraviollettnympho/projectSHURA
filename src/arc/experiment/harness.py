"""arc.experiment — research ledger + controlled ablation harness (directive §14, §17).

Ablation runs compare WITH mechanism vs WITHOUT mechanism under controlled
conditions. The research ledger preserves HYPOTHESIS / IMPLEMENTATION /
EXPERIMENT / BASELINE / RESULT / INTERPRETATION / CONFIDENCE / FAILURE MODES /
NEXT TEST entries permanently.
"""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..events.canonical import ArcEventStore
from ..runtime import ShuraARC


@dataclass
class AblationResult:
    mechanism: str
    with_result: Any
    without_result: Any
    delta: float
    significant: bool
    baseline: Any = None
    notes: str = ""
    timestamp: float = field(default_factory=time.time)


class ResearchLedger:
    """Permanent record of empirical findings (directive §17)."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.entries: List[Dict[str, Any]] = []
        self.path = path

    def record(
        self,
        hypothesis: str,
        implementation: str,
        experiment: str,
        baseline: Any,
        result: Any,
        interpretation: str,
        confidence: float,
        failure_modes: List[str] = None,
        next_test: str = "",
    ) -> Dict[str, Any]:
        entry = {
            "hypothesis": hypothesis,
            "implementation": implementation,
            "experiment": experiment,
            "baseline": baseline,
            "result": result,
            "interpretation": interpretation,
            "confidence": confidence,
            "failure_modes": failure_modes or [],
            "next_test": next_test,
            "timestamp": time.time(),
        }
        self.entries.append(entry)
        self._persist()
        return entry

    def _persist(self) -> None:
        if not self.path:
            return
        import json, os
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, default=str, indent=2, ensure_ascii=False)

    def summary(self) -> Dict[str, Any]:
        return {"entry_count": len(self.entries), "entries": self.entries}


class AblationHarness:
    """Controlled WITH/WITHOUT mechanism comparisons.

    Uses the ShuraARC runtime. A mechanism is toggled by a config flag; the
    harness runs an identical task with the mechanism on and off, then
    measures a scalar outcome (e.g. decision divergence, retrieval salience).
    """

    def __init__(self, ledger: Optional[ResearchLedger] = None) -> None:
        self.ledger = ledger or ResearchLedger()

    def run(
        self,
        mechanism: str,
        task: Callable[[ShuraARC], Any],
        measure: Callable[[Any], float],
        store_factory: Callable[[], ShuraARC],
        baseline: Any = None,
    ) -> AblationResult:
        """Run task with mechanism ON then OFF (or DISABLED then ENABLED)."""
        # WITH mechanism (enabled)
        arc_on = store_factory()
        setattr(arc_on, "_features", dict(getattr(arc_on, "_features", {})))
        arc_on._features[mechanism] = True
        res_on = task(arc_on)
        val_on = measure(res_on)

        # WITHOUT mechanism (disabled)
        arc_off = store_factory()
        arc_off._features = dict(getattr(arc_off, "_features", {}))
        arc_off._features[mechanism] = False
        res_off = task(arc_off)
        val_off = measure(res_off)

        delta = val_on - val_off
        result = AblationResult(
            mechanism=mechanism,
            with_result=res_on,
            without_result=res_off,
            delta=delta,
            significant=abs(delta) > 0.01,
            baseline=baseline,
        )
        self.ledger.record(
            hypothesis=f"mechanism '{mechanism}' causally influences task outcome",
            implementation=f"arc.{mechanism}",
            experiment=f"ablation: {mechanism} ON vs OFF",
            baseline=baseline,
            result={"with": val_on, "without": val_off, "delta": delta, "significant": result.significant},
            interpretation="non-zero delta indicates the mechanism alters behavior" if result.significant
            else "no measurable difference; mechanism may be decorative",
            confidence=0.9 if result.significant else 0.7,
            failure_modes=[],
            next_test="increase sample size; vary contexts",
        )
        return result
