"""Birth test — minimum persistent cognitive loop (Phase 8 / Step 02).

Verifies:
1. SHURA starts.
2. Identity is loaded.
3. A cognitive event occurs.
4. Event written to canonical history.
5. Derived state updated.
6. State reconstructed from history.
7. Retrieval of relevant historical information.
8. Provider swap does not destroy identity/state.
9. Provenance exposed for retrieved state.
10. No forbidden coupling to bea brain/consciousness internals.

CAUSAL CONTINUITY TEST: If history is removed, does behavior change?
- SESSION A: has claim "color_preference=cyan" → decide picks "cyan" option.
- SESSION B: empty store, no claim → decide picks default (first option "magenta").
Measurable difference: decision label differs.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from arc import (
    ShuraARC, ArcEventStore, ReadFacade,
    EchoCognitiveProvider,
    EVENT_TYPE_EXPERIENCE, EVENT_TYPE_SELFMODEL_CLAIM,
)


class TestArcBirth(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # --- Point 1: SHURA starts ---
    def test_01_shura_starts(self):
        store = ArcEventStore(path=os.path.join(self.temp_dir, "s1.jsonl"), session_id="test")
        arc = ShuraARC(store=store, session_id="test")
        self.assertFalse(arc._started)
        self.assertIsNotNone(arc.identity)

    # --- Point 2: Identity is loaded & hashable ---
    def test_02_identity_loaded(self):
        store = ArcEventStore(path=os.path.join(self.temp_dir, "s2.jsonl"), session_id="test")
        arc = ShuraARC(store=store, session_id="test")
        self.assertTrue(arc.identity.hash)
        self.assertEqual(arc.state.identity_hash, arc.identity.hash)

    # --- Points 3,4,5: event occurs, canonical, derived updated ---
    def test_03_04_05_event_causal(self):
        store = ArcEventStore(path=os.path.join(self.temp_dir, "s3.jsonl"), session_id="test")
        arc = ShuraARC(store=store, session_id="test")
        ev = arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "birth event"})
        self.assertEqual(len(store.read_all()), 1)
        self.assertGreater(len(arc.state.working_memory), 0)

    # --- Point 6: reconstruction equivalence ---
    def test_06_reconstruction(self):
        import asyncio
        store = ArcEventStore(path=os.path.join(self.temp_dir, "s6.jsonl"), session_id="test")
        arc = ShuraARC(store=store, session_id="test")
        asyncio.run(arc.start())  # emit canonical identity.loaded event
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "memory"})
        arc.self_model.claim("aesthetic_direction", "glitch_dark")
        arc._refresh_derived()
        original = arc.state.snapshot()

        # simulate restart: new instance over SAME store, NO re-emission of identity.loaded
        arc2 = ShuraARC(store=store, session_id="test")
        arc2.state = arc2.reconstruct()
        self.assertTrue(arc2.state.equals_snapshot(original))

    # --- Point 7: retrieval returns provenance ---
    def test_07_retrieval(self):
        store = ArcEventStore(path=os.path.join(self.temp_dir, "s7.jsonl"), session_id="test")
        arc = ShuraARC(store=store, session_id="test")
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": "felt tension"})
        arc.self_model.claim("color_preference", "cyan")
        result = arc.retrieve("cyan")
        self.assertEqual(result["result_count"], 1)
        prov = result["results"][0]["provenance"]
        self.assertIn("source", prov)
        self.assertIn("confidence", prov)

    # --- Point 8: provider swap leaves identity/state intact ---
    def test_08_provider_swap(self):
        store = ArcEventStore(path=os.path.join(self.temp_dir, "s8.jsonl"), session_id="test")
        arc = ShuraARC(store=store, session_id="test")
        arc.self_model.claim("color_preference", "cyan")
        h_before = arc.identity.hash

        arc.provider = EchoCognitiveProvider()
        self.assertEqual(arc.provider.name(), "echo")
        self.assertEqual(arc.identity.hash, h_before)
        arc._refresh_derived()
        self.assertEqual(arc.state.self_model["claims"].get("color_preference"), "cyan")

    # --- Point 9: provenance in canonical events ---
    def test_09_provenance(self):
        store = ArcEventStore(path=os.path.join(self.temp_dir, "s9.jsonl"), session_id="test")
        arc = ShuraARC(store=store, session_id="test")
        arc.self_model.claim("constraint", "budget", confidence=0.9)
        evs = store.replay(event_type=EVENT_TYPE_SELFMODEL_CLAIM)
        e = evs[0]
        self.assertIn("source", e.provenance)
        self.assertIn("confidence", e.provenance)

    # --- Point 10: no forbidden coupling ---
    def test_10_no_forbidden_coupling(self):
        import inspect
        for mod_name in ["arc", "arc.events.canonical", "arc.identity",
                         "arc.self_model", "arc.runtime", "arc.coherence",
                         "arc.observation", "arc.memory.layers", "arc.provider"]:
            mod = __import__(mod_name, fromlist=[""])
            src = inspect.getsource(mod)
            self.assertNotIn("from src.core.brain import", src)
            self.assertNotIn("from src.core.consciousness import", src)

    # --- Causal continuity: history changes behavior ---
    def test_causal_continuity(self):
        """SESSION A: with history, decision influenced. SESSION B: without history, default."""
        # SESSION A: has prior claim
        store_a = ArcEventStore(path=os.path.join(self.temp_dir, "a.jsonl"), session_id="session_a")
        arc_a = ShuraARC(store=store_a, session_id="session_a")
        arc_a.self_model.claim("aesthetic_direction", "cyan")  # FIELD NAME must match decide()'s lookup

        options_a = [
            {"label": "magenta", "tags": ["magenta"]},  # default first option
            {"label": "cyan", "tags": ["cyan"]},        # matches aesthetic_direction=cyan
        ]
        decision_a = arc_a.decide("pick color", options_a)
        self.assertEqual(decision_a.decision, "cyan", "SESSION A should pick cyan due to history")

        # SESSION B: fresh empty store
        store_b = ArcEventStore(path=os.path.join(self.temp_dir, "b.jsonl"), session_id="session_b")
        arc_b = ShuraARC(store=store_b, session_id="session_b")

        options_b = [
            {"label": "magenta", "tags": ["magenta"]},
            {"label": "cyan", "tags": ["cyan"]},
        ]
        decision_b = arc_b.decide("pick color", options_b)
        self.assertEqual(decision_b.decision, "magenta", "SESSION B should pick default magenta (no history)")

        # The key difference: prior event influenced SESSION A's decision
        self.assertIn("aesthetic_direction", str(decision_a.evidence).lower())
        self.assertIn("default", str(decision_b.evidence).lower())


if __name__ == "__main__":
    unittest.main()