"""
test_arc_contracts.py — Contract / interface freeze for shura.arc dynamic modules.

STEP-04A: "Freeze the dynamic module contracts."
These tests lock down the PUBLIC shape and INVARIANTS of every arc subsystem as
they ACTUALLY exist in src/arc/. They assert what IS, so any future refactor
that changes a contract surface or breaks an invariant fails here first.

Behavioral / causal tests live in test_arc_dynamics.py and test_arc_birth.py.

ADR-016.4: This file is the contract boundary; it must FAIL if a module
changes its public surface or any documented invariant.

(NOTE: a prior version of this file imported `src.core.arc` — a path that does
not exist — and referenced a divergent API. It is replaced here with contracts
that match the real src/arc/ implementation.)
"""
from __future__ import annotations

import os
import sys
import time
import hashlib
import tempfile
import unittest
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from arc import (
    ShuraARC, ArcEvent, ProvenanceRecord, ArcEventStore,
    SCHEMA_VERSION,
    Identity, IdentityGovernance,
    MemoryRecord, MemoryKind, MemoryIndex,
    SelfModel, CognitiveState, Observer,
    AuthorityTier, GovernanceController,
    ResearchLedger, AblationHarness, AblationResult,
)
from arc.events.canonical import (
    EVENT_TYPE_STATE, EVENT_TYPE_EXPERIENCE, EVENT_TYPE_DECIDED,
    EVENT_TYPE_MEMORY_RECORDED, EVENT_TYPE_CONTRADICTION,
    EVENT_TYPE_SELFMODEL_CLAIM, EVENT_TYPE_SELFMODEL_UPDATE,
    EVENT_TYPE_OBSERVATION, EVENT_TYPE_COHERENCE,
    EVENT_TYPE_IDENTITY_LOADED,
)
from arc.action.arbitrator import ActionCandidate, ActionArbitrator, ArbitrationRecord
from arc.affect.affective_state import ArcAffectiveState, Dimension, _DIMENSIONS, _RANGES, _BASELINE, _DECAY
from arc.drives.drive_system import Drive, DriveSystem
# _DRIVES does not exist as a module-level constant; drives are created
# in DriveSystem._initial_drives(). The canonical set is locked by this contract.
_DRIVES = {"curiosity", "coherence", "completion", "exploration", "maintenance"}
from arc.attention.salience import SalienceEngine, SalienceFactors
from arc.consolidation.engine import ConsolidationEngine, ConsolidationResult
from arc.decay.engine import MemoryDecay, DecayFactors
from arc.multiscale.scheduler import MultiscaleScheduler, Timescale, ScheduledAction
from arc.observation import ReadFacade


def _arc(d, sid):
    store = ArcEventStore(path=os.path.join(d, f"{sid}.jsonl"), session_id=sid)
    return ShuraARC(store=store, session_id=sid), store


# ─────────────────────────────────────────────────────────────────────────
# 1. AFFECTIVE STATE — Dimension + ArcAffectiveState contract
# ─────────────────────────────────────────────────────────────────────────
class TestAffectiveContracts(unittest.TestCase):
    def test_dimension_required_fields(self):
        d = Dimension(name="test", value=0.5, baseline=0.5,
                      decay_rate=0.1, lo=0.0, hi=1.0)
        for f in ("name", "value", "baseline", "decay_rate", "lo", "hi",
                  "confidence", "sources", "last_change", "rate_of_change"):
            self.assertTrue(hasattr(d, f), f"Dimension missing field: {f}")

    def test_dimension_value_clipped_to_range(self):
        d = Dimension(name="t", value=0.9, baseline=0.5, decay_rate=0.1, lo=0.0, hi=1.0)
        d.bump(5.0); self.assertLessEqual(d.value, d.hi)
        d.bump(-5.0); self.assertGreaterEqual(d.value, d.lo)

    def test_dimension_decay_approaches_baseline(self):
        d = Dimension(name="t", value=1.0, baseline=0.0, decay_rate=1.0, lo=0.0, hi=1.0)
        d.decay(10.0)
        self.assertLess(d.value, 1.0); self.assertGreaterEqual(d.value, 0.0)

    def test_bump_cause_tracked_and_bounded(self):
        d = Dimension(name="t", value=0.5, baseline=0.5, decay_rate=0.1, lo=0.0, hi=1.0)
        for i in range(30): d.bump(0.01, cause=f"event_{i}")
        self.assertLessEqual(len(d.sources), 16)

    def test_six_canonical_dimensions(self):
        self.assertEqual(set(_DIMENSIONS),
                         {"valence", "arousal", "stability", "uncertainty",
                          "cognitive_load", "coherence_pressure"})
        state = ArcAffectiveState(identity_hash="test")
        self.assertEqual(set(state.dimensions.keys()), set(_DIMENSIONS))

    def test_valence_range_is_negative_to_positive(self):
        self.assertEqual(_RANGES["valence"], (-1.0, 1.0))
        for name in _DIMENSIONS:
            lo, hi = _RANGES[name]
            self.assertEqual((lo, hi), (0.0, 1.0)) if name != "valence" else None
            if name != "valence":
                self.assertEqual(_RANGES[name], (0.0, 1.0))

    def test_response_strategy_keys_and_ranges(self):
        d = tempfile.mkdtemp(); arc, _ = _arc(d, "rs0")
        s = arc.affective.response_strategy()
        for k in ("risk_tolerance", "persistence", "self_monitor"):
            self.assertIn(k, s); self.assertGreaterEqual(s[k], 0.0); self.assertLessEqual(s[k], 1.0)

    def test_retrieval_boost_in_range(self):
        d = tempfile.mkdtemp(); arc, _ = _arc(d, "rb0")
        b = arc.affective.retrieval_boost(0.5)
        self.assertGreaterEqual(b, 0.0); self.assertLessEqual(b, 2.0)

    def test_update_from_explicit_keywords(self):
        state = ArcAffectiveState(identity_hash="t")
        class E:  # minimal event-like object
            event_type = "task.completed"; event_id = "e1"
            payload = {"content": "success achieved"}
        before = state.dimensions["valence"].value
        state.update_from_event(E())
        self.assertGreater(state.dimensions["valence"].value, before)


# ─────────────────────────────────────────────────────────────────────────
# 2. DRIVE SYSTEM — Drive + DriveSystem contract
# ─────────────────────────────────────────────────────────────────────────
class TestDriveContracts(unittest.TestCase):
    def test_drive_required_fields(self):
        d = Drive(name="curiosity", pressure=0.5, activation=0.0,
                  satisfaction=0.5, decay_rate=0.1, frustration=0.0,
                  homeostasis=0.2, candidate_actions=[], sources=[])
        for f in ("name", "pressure", "activation", "satisfaction",
                  "decay_rate", "frustration", "homeostasis",
                  "candidate_actions", "sources"):
            self.assertTrue(hasattr(d, f), f"Drive missing field: {f}")

    def test_drive_pressure_clipped_0_to_1(self):
        d = Drive(name="t", pressure=0.5, activation=0.0, satisfaction=0.5,
                  decay_rate=0.1, frustration=0.0, homeostasis=0.2,
                  candidate_actions=[], sources=[])
        self.assertTrue(hasattr(d, "update"))
        for delta in [5.0, -5.0, 100.0, -100.0]:
            d.pressure = 0.5; d.update(delta)
            self.assertGreaterEqual(d.pressure, 0.0); self.assertLessEqual(d.pressure, 1.0)

    def test_five_canonical_drives(self):
        self.assertEqual(set(_DRIVES), {"curiosity", "coherence",
                                        "completion", "exploration", "maintenance"})
        ds = DriveSystem()
        self.assertEqual(set(ds.drives.keys()), set(_DRIVES))

    def test_conflict_returns_contenders(self):
        ds = DriveSystem()
        for d in ds.drives.values(): d.pressure = 0.9
        c = ds.conflict()
        self.assertIsInstance(c, list)
        self.assertGreater(len(c), 1)


# ─────────────────────────────────────────────────────────────────────────
# 3. SALIENCE — SalienceFactors contract
# ─────────────────────────────────────────────────────────────────────────
class TestSalienceContracts(unittest.TestCase):
    FACTOR_FIELDS = {"relevance", "recency", "affective_charge",
                     "unresolved_contradiction", "drive_pressure",
                     "temporal_importance", "provenance_confidence",
                     "goal_alignment", "total", "explanation"}

    def test_salience_factors_fields(self):
        sf = SalienceFactors()
        self.assertEqual(set(sf.__dict__.keys()) | {"total","explanation"},
                         self.FACTOR_FIELDS)
        self.assertIsInstance(sf.explanation, dict)

    def test_score_memory_returns_inspectable_factors(self):
        d = tempfile.mkdtemp(); arc, _ = _arc(d, "sal0")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "cyan aesthetic"})
        rec = arc.memory.recent(1)[0]
        f = arc.salience.score_memory(rec, "cyan aesthetic", arc.affective,
                                      arc.drives, [])
        self.assertIsInstance(f, SalienceFactors)
        self.assertIsInstance(f.total, float)
        self.assertGreater(len(f.explanation), 0)


# ─────────────────────────────────────────────────────────────────────────
# 4. ACTION ARBITRATION — ActionCandidate / ArbitrationRecord / ActionArbitrator
# ─────────────────────────────────────────────────────────────────────────
class TestActionArbitrationContracts(unittest.TestCase):
    def test_action_candidate_fields(self):
        c = ActionCandidate(label="x", utility=0.5)
        for f in ("label", "kind", "utility", "reasons",
                  "drive_contributions", "provenance", "risk"):
            self.assertIn(f, c.__dataclass_fields__)

    def test_arbitration_record_fields(self):
        for f in ("chosen", "all_candidates", "rejected",
                  "timestamp", "provenance"):
            self.assertIn(f, ArbitrationRecord.__dataclass_fields__)

    def test_arbitrator_is_pure_ranker(self):
        c_hi = ActionCandidate(label="a", utility=0.9)
        c_lo = ActionCandidate(label="b", utility=0.1)
        rec = ActionArbitrator().propose([c_hi, c_lo], {}, {"risk_tolerance": 0.5})
        self.assertEqual(rec.chosen, "a")
        self.assertEqual(rec.rejected, ["b"])
        self.assertEqual(len(rec.all_candidates), 2)


# ─────────────────────────────────────────────────────────────────────────
# 5. GOVERNANCE — AuthorityTier + actor→tier binding
# ─────────────────────────────────────────────────────────────────────────
class TestGovernanceContracts(unittest.TestCase):
    def test_tier_enum_values(self):
        self.assertEqual({t.value for t in AuthorityTier},
                         {"observe", "propose", "influence", "modify", "execute", "veto"})

    def test_actor_tier_binding(self):
        g = GovernanceController()
        self.assertEqual(g.actor_tiers["llm"], AuthorityTier.PROPOSE)
        self.assertEqual(g.actor_tiers["model"], AuthorityTier.PROPOSE)
        self.assertEqual(g.actor_tiers["user"], AuthorityTier.VETO)
        self.assertEqual(g.actor_tiers["system"], AuthorityTier.VETO)
        self.assertEqual(g.actor_tiers["observer"], AuthorityTier.OBSERVE)

    def test_identity_requires_veto(self):
        g = GovernanceController()
        self.assertFalse(g.can_modify_identity("llm"))
        self.assertFalse(g.can_modify_identity("model"))
        self.assertTrue(g.can_modify_identity("user"))
        self.assertTrue(g.can_modify_identity("system"))

    def test_canonical_writers_only(self):
        g = GovernanceController()
        self.assertTrue(g.can_modify_canonical("runtime"))
        self.assertFalse(g.can_modify_canonical("observer"))
        self.assertFalse(g.can_modify_canonical("llm"))

    def test_authorized_uses_actor_and_component(self):
        g = GovernanceController()
        # observer cannot modify identity (OBSERVE < VETO) even though identity permits OBSERVE
        self.assertFalse(g.authorized("identity", AuthorityTier.VETO, actor="observer"))
        self.assertTrue(g.authorized("identity", AuthorityTier.OBSERVE, actor="observer"))


# ─────────────────────────────────────────────────────────────────────────
# 6. MEMORY DECAY — derived accessibility, canonical untouched
# ─────────────────────────────────────────────────────────────────────────
class TestDecayContracts(unittest.TestCase):
    DECAY_FIELDS = {"age", "access_frequency", "importance", "affective_salience",
                    "corroboration", "relevance", "provenance_quality",
                    "accessibility", "explanation"}

    def test_decay_factors_fields(self):
        self.assertEqual(set(DecayFactors.__dataclass_fields__), self.DECAY_FIELDS)

    def test_decay_accessibility_bounded_and_no_canonical_deletion(self):
        d = tempfile.mkdtemp(); arc, store = _arc(d, "dec0")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "decay me"})
        arc._refresh_derived()
        rec = arc.memory.records[0]
        fac = arc.decay.score(rec, now=time.time(), context="")
        self.assertIsInstance(fac, DecayFactors)
        self.assertGreaterEqual(fac.accessibility, 0.05)
        self.assertLessEqual(fac.accessibility, 0.95)
        # canonical store unchanged by scoring
        self.assertEqual(len(store.read_all()), 1)  # only experience (identity loaded during start())


# ─────────────────────────────────────────────────────────────────────────
# 7. CONSOLIDATION — non-destructive, speculative-marked
# ─────────────────────────────────────────────────────────────────────────
class TestConsolidationContracts(unittest.TestCase):
    def test_result_fields(self):
        for f in ("semantic_facts", "updated_records", "contradictions_found",
                  "self_model_updates", "patterns", "speculative",
                  "timestamp", "provenance"):
            self.assertIn(f, ConsolidationResult.__dataclass_fields__)

    def test_never_deletes_canonical(self):
        d = tempfile.mkdtemp(); arc, store = _arc(d, "con0")
        for i in range(5):
            arc.experience(EVENT_TYPE_EXPERIENCE, {"content": f"event {i} shura is persistent"})
        n_before = len(store.read_all())
        arc.consolidate()
        n_after = len(store.read_all())
        self.assertEqual(n_after, n_before + 1)  # only added consolidation.completed


# ─────────────────────────────────────────────────────────────────────────
# 8. MULTISCALE — Timescale + scheduler
# ─────────────────────────────────────────────────────────────────────────
class TestMultiscaleContracts(unittest.TestCase):
    def test_timescale_enum(self):
        self.assertEqual({t.name for t in Timescale}, {"FAST", "MEDIUM", "SLOW"})

    def test_scheduler_interface(self):
        s = MultiscaleScheduler()
        for m in ("schedule", "drain", "status"):
            self.assertTrue(callable(getattr(s, m, None)), f"scheduler missing {m}")


# ─────────────────────────────────────────────────────────────────────────
# 9. RESEARCH LEDGER / ABLATION HARNESS
# ─────────────────────────────────────────────────────────────────────────
class TestExperimentContracts(unittest.TestCase):
    LEADER_FIELDS = {"hypothesis", "implementation", "experiment", "baseline",
                     "result", "interpretation", "confidence", "failure_modes",
                     "next_test", "timestamp"}
    RESULT_FIELDS = {"mechanism", "with_result", "without_result", "delta",
                     "significant", "baseline", "notes", "timestamp"}

    def test_ledger_record_fields(self):
        ledger = ResearchLedger()
        e = ledger.record(hypothesis="h", implementation="i", experiment="e",
                         baseline=0.0, result=1.0, interpretation="x",
                         confidence=0.9, failure_modes=[], next_test="n")
        self.assertEqual(set(e.keys()), self.LEADER_FIELDS)
        self.assertGreater(len(ledger.entries), 0)

    def test_ablation_result_fields(self):
        self.assertEqual(set(AblationResult.__dataclass_fields__), self.RESULT_FIELDS)

    def test_ablation_harness_runs_with_and_without(self):
        d = tempfile.mkdtemp()
        def factory():
            return ShuraARC(store=ArcEventStore(path=os.path.join(d, f"a_{id(factory)}.jsonl"),
                                                session_id="ab"), session_id="ab")
        def task(arc):
            arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "decision context"})
            return arc.evaluate_and_decide("pick", [{"label": "red", "tags": []},
                                                    {"label": "blue", "tags": []}])
        ledger = ResearchLedger()
        res = AblationHarness(ledger=ledger).run(
            "affect", task, lambda r: 1.0 if r.decision == "blue" else 0.0, factory)
        self.assertIsNotNone(res.with_result)
        self.assertIsNotNone(res.without_result)


# ─────────────────────────────────────────────────────────────────────────
# 10. OBSERVER READ-ONLY — ReadFacade exposes no writers
# ─────────────────────────────────────────────────────────────────────────
class TestObserverReadOnlyContract(unittest.TestCase):
    def test_read_facade_has_no_mutation_methods(self):
        for name in dir(ReadFacade):
            self.assertFalse(name.startswith(("write", "append", "delete",
                                              "clear", "update", "replace")),
                             f"ReadFacade exposes writer: {name}")

    def test_observer_only_reads(self):
        d = tempfile.mkdtemp(); arc, _ = _arc(d, "obs0")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "observe me"})
        self.assertIsInstance(arc.observer.facade, ReadFacade)
        self.assertTrue(len(arc.observer.observe_all()) >= 1)


# ─────────────────────────────────────────────────────────────────────────
# 11. MEMORY RECORD — fields + deterministic id
# ─────────────────────────────────────────────────────────────────────────
class TestMemoryRecordContract(unittest.TestCase):
    REQUIRED = {"memory_id", "kind", "content", "created_at", "provenance",
                "confidence", "last_accessed", "salience", "corroboration", "tags"}

    def test_fields(self):
        self.assertEqual(set(MemoryRecord.__dataclass_fields__), self.REQUIRED)

    def test_deterministic_id(self):
        d = tempfile.mkdtemp(); arc, store = _arc(d, "mr0")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "det id"})
        arc._refresh_derived()
        ev = store.replay(event_type="experience")[0]
        rec = arc.memory.records[0]
        expected = hashlib.sha256((EVENT_TYPE_MEMORY_RECORDED + ":" + ev.event_id).encode()).hexdigest()
        self.assertEqual(rec.memory_id, expected)

    def test_retrieval_returns_provenance(self):
        d = tempfile.mkdtemp(); arc, _ = _arc(d, "mr1")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "the cyan palette"})
        r = arc.retrieve("cyan")
        self.assertEqual(r["result_count"], 1)
        self.assertIn("provenance", r["results"][0])


# ─────────────────────────────────────────────────────────────────────────
# 12. CANONICAL EVENT STORE — append-only, no delete
# ─────────────────────────────────────────────────────────────────────────
class TestEventStoreContract(unittest.TestCase):
    EVENT_FIELDS = {"event_id", "timestamp", "source", "actor", "event_type",
                    "payload", "provenance", "confidence", "causal_parent",
                    "session_context_id", "schema_version", "sequence"}

    def test_arc_event_fields(self):
        ev = ArcEvent(source="t", actor="shura", event_type="experience", payload={})
        self.assertEqual(set(ev.__dataclass_fields__), self.EVENT_FIELDS)
        self.assertEqual(ev.schema_version, SCHEMA_VERSION)

    def test_append_only_no_delete(self):
        d = tempfile.mkdtemp(); store = _store(d, "es0")[1] if False else ArcEventStore(
            path=os.path.join(d, "es0.jsonl"), session_id="es0")
        ev = store.append(ArcEvent(source="t", actor="shura",
                                   event_type="experience", payload={}))
        self.assertEqual(len(store.read_all()), 1)
        self.assertEqual(store.read_all()[-1].event_id, ev.event_id)
        for m in dir(store):
            self.assertFalse(m.startswith(("delete", "replace")), f"store exposes {m}")

    def test_sequence_monotonic(self):
        d = tempfile.mkdtemp(); store = ArcEventStore(
            path=os.path.join(d, "es1.jsonl"), session_id="es1")
        for i in range(5):
            store.append(ArcEvent(source="t", actor="shura",
                                  event_type="experience", payload={"i": i}))
        seqs = [e.sequence for e in store.read_all()]
        self.assertEqual(seqs, sorted(seqs))


# ─────────────────────────────────────────────────────────────────────────
# 13. IDENTITY — immutable hash, governed change proposals
# ─────────────────────────────────────────────────────────────────────────
class TestIdentityContract(unittest.TestCase):
    def test_identity_hashable(self):
        d = tempfile.mkdtemp(); arc, _ = _arc(d, "id0")
        self.assertTrue(arc.identity.hash)
        self.assertEqual(arc.state.identity_hash, arc.identity.hash)

    def test_change_proposal_not_auto_applied(self):
        d = tempfile.mkdtemp(); arc, _ = _arc(d, "id1")
        h_before = arc.identity.hash
        # LLM proposes — must NOT be applied without veto
        prop = arc.identity_governance.propose_change(
            "text", arc.identity.text, "modified version", "experiment", "llm")
        self.assertFalse(prop.approved)
        self.assertEqual(len(arc.identity_governance.proposals), 1)
        self.assertEqual(len(arc.identity_governance.applied), 0)
        self.assertEqual(h_before, arc.identity.hash)


# ─────────────────────────────────────────────────────────────────────────
# 14. END-TO-END CONTINUITY (Phase 8 points 1–10, contract-level)
# ─────────────────────────────────────────────────────────────────────────
class TestContinuityContract(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_start_loads_identity_and_records_canonical_event(self):
        arc, store = _arc(self.d, "cc1")
        asyncio.run(arc.start())
        self.assertTrue(arc._started)
        self.assertTrue(arc.identity.hash)
        self.assertEqual(len(store.read_all()), 1)
        self.assertEqual(store.read_all()[0].event_type, EVENT_TYPE_IDENTITY_LOADED)

    def test_provider_swap_preserves_identity(self):
        arc, _ = _arc(self.d, "cc2")
        h_before = arc.identity.hash
        arc.self_model.claim("color_preference", "cyan")
        arc._refresh_derived()
        arc.provider = __import__("arc", fromlist=["EchoCognitiveProvider"]).EchoCognitiveProvider()
        self.assertEqual(arc.provider.name(), "echo")
        self.assertEqual(arc.identity.hash, h_before)
        self.assertEqual(arc.state.self_model["claims"].get("color_preference"), "cyan")

    def test_history_changes_decision(self):
        """History-dependent decision: presence of an aesthetic_direction claim flips the choice
        via the Step 02 decide() aesthetic/capability path."""
        # SESSION A: aesthetic_direction claim present -> aesthetic match picks cyan
        arc_a, _ = _arc(self.d, "cc3a")
        arc_a.self_model.claim("aesthetic_direction", "cyan")
        arc_a._refresh_derived()
        opts = [{"label": "magenta", "tags": ["magenta"]},
                {"label": "cyan", "tags": ["cyan"]}]
        d_a = arc_a.decide("pick color", opts)
        # SESSION B: empty history -> default (first option)
        arc_b, _ = _arc(self.d, "cc3b")
        d_b = arc_b.decide("pick color", opts)
        self.assertEqual(d_a.decision, "cyan")
        self.assertEqual(d_b.decision, "magenta")


if __name__ == "__main__":
    unittest.main()
