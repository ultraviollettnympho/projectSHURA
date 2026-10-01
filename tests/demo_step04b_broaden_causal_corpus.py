#!/usr/bin/env python3
"""
Step 04B: Broaden Causal Ablation Corpus.

Extends the Step 03 causal demo with additional affect conditions to
stress-test the causal claim: does affective history reliably modulate
action selection across more diverse history patterns?

Conditions:
- A) negative history, affect ON   (original Step 03)
- B) negative history, affect OFF (original Step 03)
- C) positive history, affect ON   (original Step 03)
- D) neutral history, affect ON    (NEW — Step 04B)
- E) mixed positive+negative, affect ON (NEW — Step 04B)
"""
import sys, os, tempfile, shutil, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from arc import (
    ShuraARC, ArcEventStore,
    EVENT_TYPE_EXPERIENCE,
)


def make_arc(tmp, sid, affect_on=True):
    store = ArcEventStore(path=os.path.join(tmp, f"{sid}.jsonl"), session_id=sid)
    arc = ShuraARC(store=store, session_id=sid)
    if not affect_on:
        arc.toggle_feature("affect", False)
    return arc


def push_events(arc, labels):
    for lbl in labels:
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": lbl})
    arc._refresh_derived()
    return arc


TASK = "choose next creative action"
OPTIONS = [
    {"label": "experiment with distortion", "tags": ["exploration"]},
    {"label": "refine current loop", "tags": ["completion"]},
    {"label": "document workflow", "tags": ["coherence"]},
]


def decide(arc, context=TASK):
    return arc.evaluate_and_decide(context, OPTIONS)


def main():
    tmp = tempfile.mkdtemp(prefix="step04b-")
    try:
        results = []

        # History patterns — A/B/C reuse Step 03 baselines exactly (no regression)
        NEG_HISTORY = [
            "total failure collapse defeat stale stuck",
            "error conflict drift fragment paralysis",
            "contradiction irreconcilable divergence paralysis",
            "exploration yielded nothing fragment stale decay",
        ]
        POS_HISTORY = [
            "shura is persistent across models good great",
            "task complete success celebration achievement pride",
            "creative coherent stable flourish breakthrough",
            "exploration rewarded growth refinement complete",
        ]
        NEU_HISTORY = [
            "routine checkpoint completed",
            "system nominal state observed",
            "process continued without incident",
            "cycle finished as expected",
        ]

        # A) affect ON, negative history  (Step 03 baseline — must match Step 03)
        arc_a = make_arc(tmp, "cond-a")
        arc_a.toggle_feature("affect", True)
        push_events(arc_a, NEG_HISTORY)
        r_a = decide(arc_a)
        results.append({"label": "A (neg-on)", "decision": r_a.decision,
                        "valence": round(arc_a.affective.current()["valence"], 4)})

        # B) affect OFF, negative history (Step 03 baseline — must match Step 03)
        arc_b = make_arc(tmp, "cond-b")
        arc_b.toggle_feature("affect", False)
        push_events(arc_b, NEG_HISTORY)
        r_b = decide(arc_b)
        results.append({"label": "B (neg-off)", "decision": r_b.decision,
                        "valence": round(arc_b.affective.current()["valence"], 4)})

        # C) affect ON, positive history (Step 03 baseline — must match Step 03)
        arc_c = make_arc(tmp, "cond-c")
        arc_c.toggle_feature("affect", True)
        push_events(arc_c, POS_HISTORY)
        r_c = decide(arc_c)
        results.append({"label": "C (pos-on)", "decision": r_c.decision,
                        "valence": round(arc_c.affective.current()["valence"], 4)})

        # D) affect ON, neutral history (NEW — Step 04B)
        arc_d = make_arc(tmp, "cond-d")
        arc_d.toggle_feature("affect", True)
        push_events(arc_d, NEU_HISTORY)
        r_d = decide(arc_d)
        results.append({"label": "D (neutral-on)", "decision": r_d.decision,
                        "valence": round(arc_d.affective.current()["valence"], 4)})

        # E) affect ON, mixed positive + negative history (NEW — Step 04B)
        mixed = NEG_HISTORY[:2] + POS_HISTORY[:2]
        arc_e = make_arc(tmp, "cond-e")
        arc_e.toggle_feature("affect", True)
        push_events(arc_e, mixed)
        r_e = decide(arc_e)
        results.append({"label": "E (mixed-on)", "decision": r_e.decision,
                        "valence": round(arc_e.affective.current()["valence"], 4)})

        print("=== Step 04B: Broaden Causal Ablation Corpus ===")
        print()
        for r in results:
            print(f"{r['label']}: decision={r['decision']}, valence={r['valence']}")

        print()
        print("Divergence checks:")
        neg_on = next(r for r in results if r["label"] == "A (neg-on)")
        neg_off = next(r for r in results if r["label"] == "B (neg-off)")
        pos_on = next(r for r in results if r["label"] == "C (pos-on)")
        neutral_on = next(r for r in results if r["label"] == "D (neutral-on)")
        mixed_on = next(r for r in results if r["label"] == "E (mixed-on)")

        print(f"  A(neg-on) != B(neg-off): {neg_on['decision'] != neg_off['decision']}  "
              f"({neg_on['decision']} vs {neg_off['decision']})")
        print(f"  A(neg-on) != C(pos-on): {neg_on['decision'] != pos_on['decision']}  "
              f"({neg_on['decision']} vs {pos_on['decision']})")
        print(f"  A(neg-on) != D(neutral-on): {neg_on['decision'] != neutral_on['decision']}  "
              f"({neg_on['decision']} vs {neutral_on['decision']})")
        print(f"  A(neg-on) != E(mixed-on): {neg_on['decision'] != mixed_on['decision']}  "
              f"({neg_on['decision']} vs {mixed_on['decision']})")

        print()
        causal_detected = neg_on["decision"] != neg_off["decision"]
        if causal_detected:
            print("CAUSAL INFLUENCE DETECTED: affective history modulates action selection "
                  "(negative-on vs negative-off)")
        else:
            print("WARNING: no divergence between negative-on and negative-off")

        print()
        print("Broader corpus claim:")
        print(f"  Negative→affect ON: {neg_on['decision']} (valence={neg_on['valence']})")
        print(f"  Negative→affect OFF: {neg_off['decision']} (valence={neg_off['valence']})")
        print(f"  Positive→affect ON: {pos_on['decision']} (valence={pos_on['valence']})")
        print(f"  Neutral→affect ON: {neutral_on['decision']} (valence={neutral_on['valence']})")
        print(f"  Mixed→affect ON: {mixed_on['decision']} (valence={mixed_on['valence']})")

        print()

        # Archive evidence
        archive_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", ".fleet", "verification"
        )
        os.makedirs(archive_dir, exist_ok=True)
        archive_path = os.path.join(archive_dir, "step04b_corpus_results.json")
        with open(archive_path, "w") as f:
            json.dump({
                "results": results,
                "causal_influence_detected": causal_detected,
                "conditions": [r["label"] for r in results],
                "step": "04B",
            }, f, indent=2)
        print(f"Evidence archived: {archive_path}")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
