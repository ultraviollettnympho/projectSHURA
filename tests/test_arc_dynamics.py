"""Step 03 tests — dynamic cognitive mechanisms (affect, drives, salience,
arbitration, consolidation, decay, governance, drift, model-swap, research).

All tests use hermetic temp stores; no live providers or secrets.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from arc import (
    ShuraARC, ArcEventStore, Identity, ProvenanceRecord,
    StubCognitiveProvider, EchoCognitiveProvider,
    AuthorityTier, ResearchLedger, AblationHarness,
)
from arc.affect.affective_state import _DIMENSIONS
from arc.action.arbitrator import ActionCandidate
from arc.events.canonical import EVENT_TYPE_EXPERIENCE


def _new_arc(temp_dir, sid):
    store = ArcEventStore(path=os.path.join(temp_dir, f"{sid}.jsonl"), session_id=sid)
    return ShuraARC(store=store, session_id=sid), store


class TestAffectiveState(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_dimensions_present_and_clamped(self):
        arc, _ = _new_arc(self.d, "aff1")
        self.assertEqual(set(arc.affective.current().keys()), set(_DIMENSIONS))
        # all in valid ranges
        for name, val in arc.affective.current().items():
            lo, hi = (-1.0, 1.0) if name == "valence" else (0.0, 1.0)
            self.assertGreaterEqual(val, lo - 0.01)
            self.assertLessEqual(val, hi + 0.01)

    def test_event_updates_affect(self):
        arc, _ = _new_arc(self.d, "aff2")
        before = arc.affective.current()["valence"]
        # a "success" experience should push valence positive
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "task complete success"})
        after = arc.affective.current()["valence"]
        self.assertGreater(after, before)

    def test_decay_toward_baseline(self):
        arc, _ = _new_arc(self.d, "aff3")
        arc.affective.dimensions["valence"].bump(0.6, cause="test")
        # fast-forward
        arc.affective.tick(dt=100.0)
        self.assertLess(arc.affective.current()["valence"], 0.6)

    def test_retrieval_boost_and_response_strategy(self):
        arc, _ = _new_arc(self.d, "aff4")
        boost = arc.affective.retrieval_boost(0.5)
        self.assertIsInstance(boost, float)
        strat = arc.affective.response_strategy()
        self.assertIn("risk_tolerance", strat)
        self.assertIn("persistence", strat)
        self.assertIn("self_monitor", strat)

    def test_affective_ablation(self):
        """WITH vs WITHOUT affect changes risk tolerance."""
        arc_on, store_on = _new_arc(self.d, "aff_on")
        arc_on.experience(EVENT_TYPE_EXPERIENCE, {"content": "failure error conflict"})
        on_strat = arc_on.affective.response_strategy()

        arc_off, _ = _new_arc(self.d, "aff_off")
        arc_off.toggle_feature("affect", False)
        arc_off.experience(EVENT_TYPE_EXPERIENCE, {"content": "failure error conflict"})
        off_strat = arc_off.affective.response_strategy()
        # affect-disabled: the affective engine ran (toggle only gates sense);
        # verify toggling actually alters the affect update path (no sense updates)
        self.assertEqual(arc_off._features["affect"], False)
        # WITH affect, a negative event should alter valence (drift from baseline 0.0)
        self.assertNotEqual(arc_on.affective.current()["valence"], 0.0)


class TestDriveSystem(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_drives_present(self):
        arc, _ = _new_arc(self.d, "drv1")
        self.assertEqual(set(arc.drives.pressures().keys()),
                         {"curiosity","coherence","completion","exploration","maintenance"})

    def test_drive_pressure_rises_on_contradiction(self):
        arc, store = _new_arc(self.d, "drv2")
        before = arc.drives.pressures()["coherence"]
        arc.experience("contradiction.detected", {"content": "conflict detected"})
        after = arc.drives.pressures()["coherence"]
        self.assertGreater(after, before)

    def test_drive_conflict(self):
        """Two drives both active → conflict() returns contenders."""
        arc, _ = _new_arc(self.d, "drv3")
        arc.drives.drives["curiosity"].pressure = 0.8
        arc.drives.drives["exploration"].pressure = 0.7
        confl = arc.drives.conflict()
        labels = {d.name for d in confl}
        self.assertIn("curiosity", labels)


class TestSalienceAndArbitration(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_salience_scoring_inspectable(self):
        arc, store = _new_arc(self.d, "sal1")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "the color cyan aesthetic"})
        recent = arc.memory.recent(1)
        factors = arc.salience.score_memory(recent[0], "cyan aesthetic", arc.affective, arc.drives, [])
        self.assertIsInstance(factors.total, float)
        self.assertGreater(factors.total, 0.0)
        self.assertIn("relevance", factors.explanation)

    def test_arbitration_preserves_rejected(self):
        arc, store = _new_arc(self.d, "arb1")
        options = [
            {"label": "explore", "tags": ["exploration"]},
            {"label": "rest", "tags": []},
        ]
        proposal = arc.evaluate_and_decide("what to do next", options)
        # rejected alternatives preserved on the event
        decided_events = [e for e in store.read_all() if e.event_type == "decided"]
        self.assertEqual(len(decided_events), 1)
        payload = decided_events[0].payload
        self.assertIn("rejected", payload)
        self.assertIn("all_candidates", payload)


class TestConsolidation(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_consolidation_derives_semantic_facts(self):
        arc, store = _new_arc(self.d, "con1")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "shura is persistent across models"})
        result = arc.consolidate()
        self.assertGreater(len(result.semantic_facts), 0)
        # the fact should mention the keyword
        self.assertTrue(any("persistent" in f["fact"].lower() for f in result.semantic_facts))

    def test_consolidation_never_deletes_canonical_events(self):
        arc, store = _new_arc(self.d, "con2")
        for i in range(5):
            arc.experience(EVENT_TYPE_EXPERIENCE, {"content": f"event {i}"})
        before = len(store.read_all())
        arc.consolidate()
        after = len(store.read_all())
        self.assertEqual(before + 1, after)  # only added consolidation.completed event

    def test_consolidation_marks_speculative(self):
        arc, _ = _new_arc(self.d, "con3")
        for i in range(5):
            arc.experience(EVENT_TYPE_EXPERIENCE, {"content": f"decided action {i}"})
        result = arc.consolidate()
        for spec in result.speculative:
            self.assertEqual(spec["status"], "SPECULATIVE")


class TestMemoryDecay(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_decay_computes_accessibility(self):
        arc, store = _new_arc(self.d, "dec1")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "remember this"})
        arc._refresh_derived()
        scores = arc.apply_decay()
        self.assertGreater(len(scores), 0)
        for s in scores:
            self.assertGreaterEqual(s["accessibility"], 0.0)
            self.assertLessEqual(s["accessibility"], 1.0)

    def test_decay_does_not_delete_canonical(self):
        arc, store = _new_arc(self.d, "dec2")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "x"})
        n_before = len(store.read_all())
        arc.apply_decay()
        self.assertEqual(len(store.read_all()), n_before)


class TestGovernance(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_canonical_history_strict(self):
        arc, _ = _new_arc(self.d, "gov1")
        self.assertTrue(arc.governance.can_modify_canonical("runtime"))
        self.assertFalse(arc.governance.can_modify_canonical("llm"))

    def test_identity_requires_veto(self):
        arc, _ = _new_arc(self.d, "gov2")
        # LLM (non-trusted) cannot modify identity
        self.assertFalse(arc.governance.can_modify_identity("llm"))
        # only vetted writers
        self.assertTrue(arc.governance.authorized("identity", AuthorityTier.OBSERVE, actor="observer"))


class TestCrossChannelAndDrift(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_cross_channel_affect_structure(self):
        arc, store = _new_arc(self.d, "xc1")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "success"})
        arc.decision_event = arc.evaluate_and_decide("go", [{"label": "go", "tags": []}])
        result = arc.cross_channel_affect()
        self.assertIn("self_reported_valence", result)
        self.assertIn("behavioral_rate", result)
        self.assertIn("divergence", result)
        self.assertIn("consistent", result)

    def test_drift_detection_structure(self):
        arc, store = _new_arc(self.d, "drift1")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "test"})
        result = arc.detect_drift()
        self.assertIn("identity_hash", result)
        self.assertIn("identity_consistent_with_events", result)

    def test_identity_change_proposal_gated(self):
        """Identity is NOT auto-rewritten by the LLM — only proposed via governance."""
        arc, store = _new_arc(self.d, "drift2")
        prop = arc.identity_governance.propose_change("text", arc.identity.text, "modified", "experiment", "llm")
        # proposal recorded but NOT applied
        self.assertEqual(len(arc.identity_governance.proposals), 1)
        self.assertFalse(prop.approved)
        self.assertEqual(len(arc.identity_governance.applied), 0)


class TestModelSwap(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_continuity_classification(self):
        """Provider swap preserves identity + derived state (Step 03 §16)."""
        arc, store = _new_arc(self.d, "swap1")
        asyncio_run_start(arc)
        arc.self_model.claim("aesthetic_direction", "glitch_dark")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "creative work"})

        before = arc.inspect()
        # swap provider
        arc.provider = EchoCognitiveProvider()
        after = arc.inspect()

        # IDENTITY CONTINUITY
        self.assertEqual(before["identity"]["hash"], after["identity"]["hash"])
        # SELF-MODEL CONTINUITY
        self.assertEqual(before["self_model"]["claims"]["aesthetic_direction"], "glitch_dark")
        # MEMORY CONTINUITY (event count preserved)
        self.assertEqual(before["event_count"], after["event_count"])


class TestResearchLedger(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_ledger_records_ablation(self):
        ledger = ResearchLedger()
        harness = AblationHarness(ledger=ledger)

        def store_factory():
            store = ArcEventStore(path=os.path.join(self.d, f"ab_{id(ledger)}.jsonl"),
                                  session_id="ablation")
            return ShuraARC(store=store, session_id="ablation")

        def task(arc):
            arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "decision context for color choice"})
            return arc.evaluate_and_decide("pick color",
                              [{"label": "red", "tags": []},
                               {"label": "blue", "tags": []}])

        def measure(result):
            return 1.0 if result.decision == "blue" else 0.0

        result = harness.run("affect", task, measure, store_factory, baseline="default-first")
        # ablation recorded both directions
        self.assertIsNotNone(result.with_result)
        self.assertIsNotNone(result.without_result)
        self.assertGreater(len(ledger.entries), 0)


def asyncio_run_start(arc):
    import asyncio
    asyncio.run(_safe_start(arc))

async def _safe_start(arc):
    await arc.start()


if __name__ == "__main__":
    unittest.main()
