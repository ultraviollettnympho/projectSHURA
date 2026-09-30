"""arc.runtime — the ShuraARC cognitive substrate orchestrator.

This is the *minimal persistent cognitive loop*. It does NOT implement
consciousness (open research question — ADR-008). It wires together:

  identity (immutable) -> experience -> canonical event -> memory -> retrieval ->
  observation -> self-model -> coherence -> decide (causally dependent on
  accumulated state).

The runtime is the unit exercised by the birth test and the causal-continuity
experiment. Provider/model is an interchangeable executor; identity and
canonical state survive provider substitution.
"""
from __future__ import annotations

import asyncio
import hashlib
import time
from typing import Any, Dict, List, Optional

from .events.canonical import (
    ArcEvent,
    ProvenanceRecord,
    ArcEventStore,
    EVENT_TYPE_IDENTITY_LOADED,
    EVENT_TYPE_EXPERIENCE,
    EVENT_TYPE_OBSERVATION,
    EVENT_TYPE_COHERENCE,
    EVENT_TYPE_STATE,
    EVENT_TYPE_DECIDED,
)
from .identity import Identity, IdentityGovernance
from .self_model import SelfModel
from .memory.layers import MemoryIndex
from .observation import ReadFacade, Observer, Observation
from .coherence import CoherenceMonitor
from .state import CognitiveState
from .provider import CognitiveProvider
from .affect.affective_state import ArcAffectiveState
from .drives.drive_system import DriveSystem
from .attention.salience import SalienceEngine
from .action.arbitrator import ActionArbitrator, ActionCandidate
from .consolidation.engine import ConsolidationEngine
from .decay.engine import MemoryDecay
from .governance.authority import GovernanceController, AuthorityTier
from .multiscale.scheduler import MultiscaleScheduler, Timescale


class ActionProposal:
    """A proposed action (Phase 5 ActionProposal contract). Minimal — reasoned fields."""

    def __init__(self, decision: Optional[str], confidence: float, provenance: ProvenanceRecord,
                 evidence: List[str], alternatives: List[Optional[str]]) -> None:
        self.decision = decision
        self.confidence = confidence
        self.provenance = provenance
        self.evidence = evidence
        self.alternatives = alternatives


def _clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class ShuraARC:
    """Minimal persistent cognitive substrate.

    The core test (directive §10): if historical state is removed, does
    behavior measurably change? ``decide`` consults the event-sourced
    self-model and memory, so removing history changes the decision output.
    """

    def __init__(
        self,
        identity: Optional[Identity] = None,
        store: Optional[ArcEventStore] = None,
        provider: Optional[CognitiveProvider] = None,
        soul_path: str = "data/prompts/soul.md",
        session_id: Optional[str] = None,
        memory_index: Optional[MemoryIndex] = None,
    ) -> None:
        from .provider import StubCognitiveProvider

        self.identity: Identity = identity or Identity.load(soul_path)
        self.store: ArcEventStore = store or ArcEventStore(session_id=session_id)
        self.session_id: str = self.store.session_id
        self.provider: CognitiveProvider = provider or StubCognitiveProvider()
        self.identity_governance = IdentityGovernance(self.identity)
        self.self_model = SelfModel(self.store, self.identity, namespace=self.session_id)
        self.memory: MemoryIndex = memory_index or MemoryIndex()
        self.memory.index_events(self.store.read_all())
        self.coherence = CoherenceMonitor()
        self.observer = Observer(ReadFacade(self.store, self.self_model, self.identity))
        self.state: CognitiveState = self._initial_state()
        self._started: bool = False

        # --- Step 03: dynamic cognitive mechanisms ---
        # Mechanism feature toggles (default on); ablations set these False.
        self._features: Dict[str, bool] = {
            "affect": True, "drives": True, "salience": True,
            "arbitration": True, "consolidation": True, "decay": True,
        }
        self.affective = ArcAffectiveState(identity_hash=self.identity.hash)
        self.drives = DriveSystem()
        self.salience = SalienceEngine()
        self.arbitrator = ActionArbitrator()
        self.consolidator = ConsolidationEngine()
        self.decay = MemoryDecay()
        self.governance = GovernanceController()
        self.scheduler = MultiscaleScheduler()

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------
    def _initial_state(self) -> CognitiveState:
        return CognitiveState(
            identity_hash=self.identity.hash,
            identity_loaded_at=self.identity.loaded_at,
            self_model=self.self_model.as_dict(),
            session_id=self.session_id,
        )

    async def start(self) -> CognitiveState:
        """BOOTSTRAP: identity loaded (directive Phase 8, point 2)."""
        self._started = True
        self.state.identity_hash = self.identity.hash
        self.state.identity_loaded_at = self.identity.loaded_at
        ev = ArcEvent(
            source="runtime",
            actor="shura",
            event_type=EVENT_TYPE_IDENTITY_LOADED,
            payload={"identity_hash": self.identity.hash,
                     "manifest_path": self.identity.manifest_path,
                     "length_chars": len(self.identity.text),
                     "identity_loaded_at": self.identity.loaded_at},
            provenance=ProvenanceRecord(source="runtime", actor="system",
                                        trust_level="verified").to_dict(),
            confidence=1.0,
        )
        self.store.append(ev)
        self._refresh_derived()
        return self.state

    # ------------------------------------------------------------------
    # experience -> canonical event -> derived state
    # ------------------------------------------------------------------
    def experience(
        self,
        event_type: str,
        payload: Dict[str, Any],
        provenance: Optional[ProvenanceRecord] = None,
        actor: str = "shura",
        confidence: float = 1.0,
        causal_parent: Optional[str] = None,
    ) -> ArcEvent:
        """Record an experience into canonical history and refresh derived state."""
        ev = ArcEvent(
            source="experience",
            actor=actor,
            event_type=event_type or EVENT_TYPE_EXPERIENCE,
            payload=payload or {},
            provenance=(provenance or ProvenanceRecord()).to_dict(),
            confidence=float(confidence),
            causal_parent=causal_parent,
        )
        self.store.append(ev)
        if self._features.get("affect") or self._features.get("drives"):
            self.sense(ev)
        self._refresh_derived()
        return ev

    # ------------------------------------------------------------------
    # Step 03: dynamic cognitive mechanisms
    # ------------------------------------------------------------------
    def sense(self, ev: ArcEvent) -> Dict[str, Any]:
        """First-order dynamics: an event updates affective state + drives.

        This is the bridge from canonical events to continuously-evolving state.
        Affects and drives are derived (reconstructable from events + their
        deterministic update rules).
        """
        changes: Dict[str, Any] = {}
        if self._features.get("affect"):
            self.affective.tick()
            changes["affect"] = self.affective.update_from_event(ev)
            changes["affect_state"] = self.affective.current()
        if self._features.get("drives"):
            ap = changes.get("affect_state", self.affective.current())
            changes["drives"] = self.drives.update_from_event(ap, ev)
            changes["drive_pressures"] = self.drives.pressures()
        return changes

    def _refresh_derived(self) -> None:
        self.memory.index_events(self.store.read_all())
        self.self_model.invalidate_cache()
        self.state.self_model = self.self_model.as_dict()
        self.state.working_memory = [r.to_dict() for r in self.memory.recent(10)]
        self.state.attention = self._attention()
        self.state.coherence = self.coherence.assess(
            self.store.read_all(), self.state.self_model, self.identity
        ).raw

    def _attention(self) -> Dict[str, Any]:
        """Current salience focus from memory."""
        recent = self.memory.recent(5)
        return {
            "focus": recent[0].content if recent else None,
            "recent_kinds": [r.kind.value for r in recent],
        }

    # ------------------------------------------------------------------
    # reconstruction (Phase 8, point 6)
    # ------------------------------------------------------------------
    def reconstruct(self) -> CognitiveState:
        """Rebuild derived state purely from canonical events."""
        events = self.store.read_all()
        mem = MemoryIndex()
        mem.index_events(events)
        # Fresh self-model bound to same store; state rebuilt from events
        sm = SelfModel(self.store, self.identity, namespace=self.session_id)
        sig = self.coherence.assess(events, sm.as_dict(), self.identity)
        # Reconstruct identity_loaded_at from canonical identity.loaded event
        id_loaded_at = time.time()
        id_events = [e for e in events if e.event_type == "identity.loaded"]
        if id_events:
            id_loaded_at = float(id_events[0].payload.get("identity_loaded_at", time.time()))
        st = CognitiveState(
            identity_hash=self.identity.hash,
            identity_loaded_at=id_loaded_at,
            self_model=sm.as_dict(),
            goals=list(sm.state().get("goals", [])),
            attention={
                "focus": mem.recent(1)[0].content if mem.recent(1) else None,
                "recent_kinds": [r.kind.value for r in mem.recent(5)],
            },
            working_memory=[r.to_dict() for r in mem.recent(10)],
            coherence=sig.raw,
            session_id=self.session_id,
            reconstructed=True,
            reconstructed_at=time.time(),
        )
        # NOTE: does not mutate self.state — returns a fresh view
        return st

    # ------------------------------------------------------------------
    # retrieval with provenance (Phase 8, point 7)
    # ------------------------------------------------------------------
    def retrieve(self, query: str) -> Dict[str, Any]:
        self._refresh_derived()
        return self.memory.retrieve(query)

    # ------------------------------------------------------------------
    # decide — causally dependent on accumulated state (Phase 8, point 10)
    # ------------------------------------------------------------------
    def decide(self, context: str, options: List[Dict[str, Any]]) -> ActionProposal:
        """Choose an option influenced by the event-sourced self-model and memory.

        The choice is deterministic given identical canonical history. Removing
        history (state-disabled) changes the decision output — the causal
        continuity requirement.
        """
        self._refresh_derived()
        retrieval = self.memory.retrieve(context)
        sm = self.self_model.as_dict()

        chosen = None
        confidence = 0.5
        evidence: List[str] = []
        for opt in options:
            tags = opt.get("tags", []) or []
            aesthetic = sm.get("claims", {}).get("aesthetic_direction")
            if aesthetic and aesthetic in tags:
                chosen = opt["label"]
                confidence = 0.9
                evidence.append(f"selfmodel.aesthetic_direction={aesthetic}")
                break
            # capability match
            for cap in sm.get("capabilities", []):
                if cap in tags:
                    if chosen is None:
                        chosen = opt["label"]
                        confidence = 0.7
                        evidence.append(f"selfmodel.capability={cap}")

        if chosen is None:
            # Default: first option, neutral confidence
            chosen = options[0]["label"] if options else None
            confidence = 0.3
            evidence.append("default-selection-no-supporting-history")

        if retrieval["result_count"] > 0:
            evidence.append(f"retrieved {retrieval['result_count']} memory record(s) for '{context}'")

        ev = ArcEvent(
            source="runtime",
            actor="shura",
            event_type="decided",
            payload={
                "context": context,
                "chosen": chosen,
                "confidence": confidence,
                "evidence": evidence,
                "alternatives": [o.get("label") for o in options],
            },
            provenance=ProvenanceRecord(source="runtime", actor="shura",
                                        trust_level="verified" if confidence >= 0.7 else "inferred",
                                        confidence=confidence).to_dict(),
            confidence=confidence,
        )
        self.store.append(ev)
        self._refresh_derived()
        return ActionProposal(
            decision=chosen,
            confidence=confidence,
            provenance=ProvenanceRecord(source="runtime", actor="shura"),
            evidence=evidence,
            alternatives=[o.get("label") for o in options],
        )

    # ------------------------------------------------------------------
    # observation / coherence surface (directive §11 observability)
    # ------------------------------------------------------------------
    def observe(self) -> List[Dict[str, Any]]:
        self._refresh_derived()
        return [o.__dict__ for o in self.observer.observe_all()]

    def coherence_signals(self) -> Dict[str, Any]:
        self._refresh_derived()
        sig = self.coherence.assess(
            self.store.read_all(), self.state.self_model, self.identity
        )
        d = sig.__dict__
        d["raw_recommendations"] = sig.recommendations
        return d

    # ------------------------------------------------------------------
    # Step 03 dynamic mechanisms
    # ------------------------------------------------------------------
    def evaluate_and_decide(
        self,
        context: str,
        options: List[Dict[str, Any]],
        *,
        salience_context: bool = True,
    ) -> ActionProposal:
        """Action arbitration through interpretable scoring (directive §6).

        Candidate actions are scored via salience + drive pressure + affective
        response strategy. Rejected alternatives, reasons, and competing
        pressures are preserved on the returned ActionProposal.
        """
        self._refresh_derived()
        # Feature-gated ablation: without arbitration, fall back to first option
        if not self._features.get("arbitration"):
            chosen = options[0]["label"] if options else None
            ev = ArcEvent(
                source="runtime",
                actor="shura",
                event_type=EVENT_TYPE_DECIDED,
                payload={"context": context, "chosen": chosen, "fallback": True},
                provenance=ProvenanceRecord(source="runtime", actor="shura",
                                            trust_level="verified").to_dict(),
                confidence=0.3,
            )
            self.store.append(ev)
            self._refresh_derived()
            return ActionProposal(
                decision=chosen, confidence=0.3,
                provenance=ProvenanceRecord(source="runtime", actor="shura"),
                evidence=[chosen] if chosen else [],
                alternatives=[o.get("label") for o in options],
            )
        strategy = self.affective.response_strategy() if self._features.get("affect") else \
            {"risk_tolerance": 0.5, "persistence": 0.5, "self_monitor": 0.5}
        drive_pressures = self.drives.pressures() if self._features.get("drives") else {}

        cand_list: List[ActionCandidate] = []
        for opt in options:
            tags = opt.get("tags", [])
            reasons = []
            drive_contrib = {}
            # salience as interpretability anchor
            score = 0.5
            if salience_context:
                # textual relevance to context via memory records (if any)
                mems = self.memory.search(context)
                if mems:
                    score += 0.1 * min(len(mems), 3) / 3.0
                    reasons.append("salient memory matched context")
            for tag in tags:
                # drive pressure contribution
                for dname in drive_pressures:
                    if tag == dname:
                        drive_contrib[dname] = drive_pressures[dname]
                        score += 0.1 * drive_pressures[dname]
                        reasons.append(f"drive={dname}:{drive_pressures[dname]:.2f}")
                    elif tag in self.state.self_model.get("capabilities", []):
                        score += 0.1
                        reasons.append(f"capability={tag}")
            cand = ActionCandidate(
                label=opt["label"], kind=opt.get("kind", "task"),
                utility=_clip(score, 0.0, 1.0), reasons=reasons,
                drive_contributions=drive_contrib,
                risk=opt.get("risk", 0.1),
            )
            # --- affective policy: strategy dims modulate acceptability ---
            # Exploration rides risk_tolerance (risk-seeker); completion rides
            # the *inverse* of risk_tolerance (risk-averse safe fallback). This
            # explicit channel makes a positive/negative affect history flip the
            # chosen action — the causal test in tests/demo_step03_causal.py.
            tags_l = tags
            if "exploration" in tags_l:
                cand.utility = _clip(cand.utility + 0.60 * (strategy["risk_tolerance"] - 0.5), 0.0, 1.0)
                cand.reasons.append(f"affect.risk_tolerance={strategy['risk_tolerance']:.2f}")
            if "completion" in tags_l:
                cand.utility = _clip(cand.utility + 0.60 * (0.5 - strategy["risk_tolerance"]), 0.0, 1.0)
                cand.reasons.append(f"affect.risk_averse={0.5 - strategy['risk_tolerance']:.2f}")
            if "coherence" in tags_l:
                cand.utility = _clip(cand.utility + 0.40 * (strategy["self_monitor"] - 0.5), 0.0, 1.0)
                cand.reasons.append(f"affect.self_monitor={strategy['self_monitor']:.2f}")
            cand_list.append(cand)

        record = self.arbitrator.propose(cand_list, drive_pressures, strategy)
        ev = ArcEvent(
            source="arbitrator",
            actor="shura",
            event_type=EVENT_TYPE_DECIDED,
            payload={
                "context": context,
                "chosen": record.chosen,
                "chosen_utility": [c for c in record.all_candidates if c["label"] == record.chosen],
                "rejected": record.rejected,
                "all_candidates": record.all_candidates,
                "drive_pressures": drive_pressures,
            },
            provenance=ProvenanceRecord(source="arbitrator", actor="shura",
                                        trust_level="verified").to_dict(),
            confidence=0.5,
        )
        self.store.append(ev)
        self._refresh_derived()
        return ActionProposal(
            decision=record.chosen,
            confidence=0.5,
            provenance=ProvenanceRecord(source="arbitrator", actor="shura"),
            evidence=[c["label"] for c in record.all_candidates],
            alternatives=[c["label"] for c in record.all_candidates],
        )

    def consolidate(self) -> Any:
        """Run offline consolidation (directive §7). Does NOT delete canonical events."""
        result = self.consolidator.run(self.store.read_all(), self.memory)
        # Record consolidation summary as an event (canonical, non-destructive)
        ev = ArcEvent(
            source="consolidation",
            actor="shura",
            event_type="consolidation.completed",
            payload={
                "facts_derived": len(result.semantic_facts),
                "contradictions_found": result.contradictions_found,
                "patterns": len(result.patterns),
                "speculative": len(result.speculative),
            },
            provenance=ProvenanceRecord(source="consolidation", actor="shura",
                                        trust_level="verified").to_dict(),
            confidence=0.9,
        )
        self.store.append(ev)
        self._refresh_derived()
        return result

    def apply_decay(self, now: Optional[float] = None) -> List[Dict[str, Any]]:
        """Derived accessibility decay (directive §8). No canonical deletion."""
        now = now or time.time()
        records = self.memory.records
        return self.decay.apply(records, now=now)

    def cross_channel_affect(self) -> Dict[str, Any]:
        """Observer-side shadow-estimation vs self-reported affect (directive §13).

        Compares: (A) affective state, (B) behavioral indicators (event rates),
        (C) recent decisions' risk. Detects divergence — NOT a proof of feeling.
        """
        events = self.store.read_all()
        # (B) behavioral indicators: event rate
        if events:
            span = max(time.time() - events[0].timestamp, 1e-6)
            rate = len(events) / span
        else:
            rate = 0.0
        # (C) recent decision risk
        decided = [e for e in events if e.event_type == "decided"]
        risk_taken = 0.0
        if decided:
            risks = [float(e.payload.get("chosen_utility", [{}])[0].get("risk", 0.1))
                     for e in decided if isinstance(e.payload.get("chosen_utility"), list)]
            risk_taken = sum(risks) / len(risks) if risks else 0.0
        reported = self.affective.current()
        divergence = abs(reported.get("valence", 0.0) - (risk_taken - 0.5))
        return {
            "self_reported_valence": reported.get("valence"),
            "behavioral_rate": round(rate, 4),
            "recent_risk_taken": round(risk_taken, 4),
            "divergence": round(divergence, 4),
            "consistent": divergence < 0.4,
        }

    def detect_drift(self) -> Dict[str, Any]:
        """Compare immutable identity vs self-model vs observed behavior (directive §10)."""
        sm = self.self_model.as_dict()
        id_hash = self.identity.hash
        # identity hash consistency
        id_events = [e for e in self.store.read_all() if e.event_type == "identity.loaded"]
        id_consistent = all(
            e.payload.get("identity_hash") == id_hash for e in id_events
        ) if id_events else True
        # self-model goal divergence from identity fingerprint
        goals = sm.get("goals", [])
        sm_identity_hash = sm.get("identity_hash", "")
        identity_drift = sm_identity_hash != id_hash
        return {
            "identity_hash": id_hash,
            "identity_consistent_with_events": id_consistent,
            "self_model_identity_hash": sm_identity_hash,
            "self_model_identity_drift": identity_drift,
            "self_model_goals": goals,
            "self_model_divergences": sm.get("divergences", {}),
        }

    def toggle_feature(self, mechanism: str, enabled: bool) -> None:
        """Ablation toggle — used by the evaluation harness."""
        self._features[mechanism] = enabled


    def inspect(self) -> Dict[str, Any]:
        """Machine-readable inspection of internal state (directive §11)."""
        return {
            "identity": self.identity.fingerprint(),
            "state": self.state.to_dict(),
            "self_model": self.self_model.as_dict(),
            "affective_state": self.affective.current(),
            "drive_pressures": self.drives.pressures(),
            "governance": self.governance.to_dict(),
            "scheduler": self.scheduler.status(),
            "features": dict(self._features),
            "session_id": self.session_id,
            "provider": self.provider.name(),
            "event_count": len(self.store.read_all()),
        }
