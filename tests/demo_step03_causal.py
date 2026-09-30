#!/usr/bin/env python
"""Step 03 causal-influence demonstration (directive §14, §16).

Runs a shared task under four conditions to PROVE affective state is not
decorative: the decision diverges as a function of accumulated affect history.

Outputs real measurements — not a narrative.
"""
import os, sys, tempfile, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from arc import ArcEventStore, ShuraARC, EVENT_TYPE_EXPERIENCE

D = tempfile.mkdtemp()

def fresh(sid):
    store = ArcEventStore(path=os.path.join(D, f"{sid}.jsonl"), session_id=sid)
    return ShuraARC(store=store, session_id=sid), store

TASK = "choose next creative action"
OPTIONS = [
    {"label": "experiment with distortion", "tags": ["exploration"]},
    {"label": "refine current loop", "tags": ["completion"]},
    {"label": "document workflow", "tags": ["coherence"]},
]

def run_condition(name, history, affect_on):
    sid = f"{name}_{affect_on}"
    arc, store = fresh(sid)
    arc.toggle_feature("affect", affect_on)  # toggle BEFORE seeding
    for h in history:
        arc.experience(EVENT_TYPE_EXPERIENCE, {"content": h})
    result = arc.decide(TASK, OPTIONS)
    return name, affect_on, result.decision, arc.affective.current()["valence"]

# Shared history: clearly valenced content
HISTORY = [
    "shura is persistent across models good",
    "task complete success celebration achievement",
    "failure error conflict drift",
    "preference exploration over routine coherent",
    "contradiction detected between goals stuck",
    "refinement complete quality achieved stable",
]

POS_HISTORY = [
    "shura is persistent across models good great",
    "task complete success celebration achievement pride",
    "creative coherent stable flourish breakthrough",
    "exploration rewarded growth refinement complete",
]

NEG_HISTORY = [
    "total failure collapse defeat stale stuck",
    "error conflict drift fragment paralysis",
    "contradiction irreconcilable divergence paralysis",
    "exploration yielded nothing fragment stale decay",
]

# Condition 1: affect ENABLED, negative history -> risk-averse -> completion
print("=== Step 03 Causal Influence Demonstration ===")
arc_n, store_n = fresh("neg_affect_on")
arc_n.toggle_feature("affect", True)
for h in NEG_HISTORY:
    arc_n.experience(EVENT_TYPE_EXPERIENCE, {"content": h})
res_n = arc_n.evaluate_and_decide(TASK, OPTIONS)
print(f"A) affect ON, negative history: decision='{res_n.decision}', "
      f"valence={arc_n.affective.current()['valence']:+.3f}")

# Condition 2: affect DISABLED, same negative history -> baseline risk neutrality -> explore
arc_n_off, store_n_off = fresh("neg_affect_off")
arc_n_off.toggle_feature("affect", False)
for h in NEG_HISTORY:
    arc_n_off.experience(EVENT_TYPE_EXPERIENCE, {"content": h})
res_n_off = arc_n_off.evaluate_and_decide(TASK, OPTIONS)
print(f"B) affect OFF, same negative history: decision='{res_n_off.decision}', "
      f"valence={arc_n_off.affective.current()['valence']:+.3f}")

# Condition 3: affect ENABLED, positive history -> risk-seeking -> explore
arc_p, _ = fresh("pos_affect_on")
arc_p.toggle_feature("affect", True)
for h in POS_HISTORY:
    arc_p.experience(EVENT_TYPE_EXPERIENCE, {"content": h})
res_p = arc_p.evaluate_and_decide(TASK, OPTIONS)
print(f"C) affect ON, positive history: decision='{res_p.decision}', "
      f"valence={arc_p.affective.current()['valence']:+.3f}")

print(f"\nDivergence (A!=B): {'YES' if res_n.decision != res_n_off.decision else 'NO'}")
print(f"Divergence (A!=C, negative vs positive): {'YES' if res_n.decision != res_p.decision else 'NO'}")
causal = (res_n.decision != res_n_off.decision) or (res_n.decision != res_p.decision)
print(f"\n{'CAUSAL INFLUENCE DETECTED: affective history measurably modulates action selection' if causal else 'NO DIVERGENCE — affect is decorative (architecture FAILS)'}\n")

from collections import Counter
c = Counter([res_n.decision, res_n_off.decision, res_p.decision])
print("Decision distribution (A=neg-on, B=neg-off, C=pos-on):")
print(f"  A: {res_n.decision} | B: {res_n_off.decision} | C: {res_p.decision}")
for label, count in c.most_common():
    print(f"  {label}: {count}/3")
