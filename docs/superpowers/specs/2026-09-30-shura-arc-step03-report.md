# shura.arc — Step 03 Report: Dynamic Cognitive Mechanisms

- Status: **VERIFIED** (2026-09-30)
- Objective: extend identity→history→memory→observer→self-model with
  affect→drives→attention→action-arbitration→consolidation, and prove the
  mechanisms **causally influence behavior** (directive §2, §14, §16).
- Evidence: 206 tests pass (31 new); causal demo returns **CAUSAL INFLUENCE
  DETECTED**; no regressions; identity/.env/C4 untouched.

## 1. What was built

### 1.1 Affective state engine — `src/arc/affect/`
- `Dimension` dataclass: value, baseline, decay_rate, last_change, rate_of_change, confidence, sources.
- 6 interpretable dimensions: `valence` (-1..1), `arousal`, `stability`,
  `uncertainty`, `cognitive_load`, `coherence_pressure` (0..1).
- `update_from_event`: explicit keyword policy (positive/negative lexicons);
  per-dimension bumps with causes tagged by event_id.
- `response_strategy()`: maps dimensions → `risk_tolerance`, `persistence`,
  `self_monitor` (the explicit policy channel, NOT prompt injection).
- `retrieval_boost()`: affective charge × |valence| + arousal, damped by
  cognitive_load — modulates memory salience.
- Exponential decay toward baselines each `tick()`.

### 1.2 Drive system — `src/arc/drives/`
- 5 drives: curiosity, coherence, completion, exploration, maintenance.
- Each `Drive`: pressure, activation, satisfaction, decay, frustration;
  `conflict()` returns contending drives when multiple high.
- `update_from_event(affective_state, event)`: contradiction events raise
  `coherence` pressure (verifiable — see test_drive_pressure_rises_on_contradiction).

### 1.3 Attention / salience — `src/arc/attention/`
- `SalienceEngine.score_memory(record, context, affective, drives, goals)` →
  `SalienceFactors` with 8 explicit factors + total + explanation dict.
- Inspectable: every factor has a named contribution (test_salience_scoring_inspectable).

### 1.4 Action arbitration — `src/arc/action/`
- `ActionArbitrator.propose` is a **pure ranker** (after ADR-016.2 fix): the
  runtime's `evaluate_and_decide` performs interpretable scoring, writes a `decided`
  canonical event preserving `rejected`, `all_candidates`, `drive_pressures`.
- `ActionProposal` carries `decision`, `confidence`, `provenance`, `evidence`,
  `alternatives` (Phase 5 contract).

### 1.5 Dynamic wiring in `ShuraARC.runtime.py`
- `sense(ev)`: canonical event → affective + drive dynamics (the bridge from
  append-only history to continuously-evolving state).
- `experience()` now calls `sense(ev)` when affect/drives enabled.
- `evaluate_and_decide()`: end-to-end arbitration via salience + drives + affect.
- `consolidate()`, `apply_decay()`, `cross_channel_affect()` (observer-side
  shadow estimate vs self-report), `detect_drift()` (identity vs self-model),
  `toggle_feature()` (ablation switch), `inspect()` extended.
- `decide()` (Step 02 aesthetic-direction path) **preserved** — no birth-test
  regression; `evaluate_and_decide` is the Step 03 dynamic path.

### 1.6 Governance — `src/arc/governance/`
- `AuthorityTier` (OBSERVE/PROPOSE/INFLUENCE/MODIFY/EXECUTE/VETO).
- Actor→tier map (ADR-016.1): LLM/model = PROPOSE only; identity requires VETO.
- `canonical_history` append-only via `_CANONICAL_WRITERS`; observer cannot
  mutate canonical state.

### 1.7 Memory decay — `src/arc/decay/`
- Applies access-decay to **derived accessibility scores only**; canonical
  events never deleted (test_decay_does_not_delete_canonical).

### 1.8 Multiscale scheduling — `src/arc/multiscale/`
- `Timescale` FAST/MEDIUM/SLOW with `MultiscaleScheduler` enqueue/dispatch.
- Future home for drive/arousal-gated timescale selection (out of current scope).

### 1.9 Experiment / evaluation harness — `src/arc/experiment/`
- `ResearchLedger`: permanent HYPOTHESIS/IMPLEMENTATION/EXPERIMENT/BASELINE/
  RESULT/INTERPRETATION/CONFIDENCE/FAILURE_MODES/NEXT_TEST records.
- `AblationHarness.run(mechanism, task, measure, store_factory)`: WITH vs
  WITHOUT mechanism, deterministic given identical canonical history.

## 2. Causal-influence experiment (the core Step 03 test)

Run `uv run python tests/demo_step03_causal.py`:

```
A) affect ON, negative history:  decision='refine current loop'    valence=-1.000
B) affect OFF, same history:    decision='experiment with distortion' valence=+0.000
C) affect ON, positive history: decision='experiment with distortion' valence=+1.000
Divergence (A!=B): YES
Divergence (A!=C, negative vs positive): YES
CAUSAL INFLIENCE DETECTED: affective history measurably modulates action selection
```

Interpretation (computational hypothesis, NOT consciousness):
- Negative affect history → low risk_tolerance → risk-averse `completion` wins.
- Positive affect history → high risk_tolerance → `explore` wins.
- Affect disabled → neutral baseline → `explore` (first-option-equivalent) wins.
Removing affect **changes the decision** on identical canonical history and
identical task → state is functional, not decorative.

## 3. Bug fixes discovered & resolved during Step 03

| Bug | Impact | Fix |
|-----|--------|-----|
| `evaluate_and_decide` fetched `response_strategy()` but never applied it to scoring | affect computed but causally inert ("decorative") | response_strategy dims modulate candidate utility (ADR-016.2) |
| `ActionArbitrator.propose` re-added `dpress * contrib` while runtime had baked pressure in | double-counted drive contributions, unpredictable ranking | arbitrator reduced to pure ranker |
| `GovernanceController.authorized` ignored actor; `can_modify_identity("llm")`=True | LLM could rewrite identity (violates identity-is-immutable) | actor→tier map; LLM=PROPOSE only (ADR-016.1) |
| `ConsolidationEngine.CLAIM_PATTERNS` `(?P<fact>shura is .*?)\b` captured only "shura is" | semantic fact extraction broken | greedy `[^,\.]+` capture |
| `runtime.py` relative imports `.events.canonical` from `arc/experiment/` | ImportError | corrected to `..events.canonical` |

## 4. Test results

```
$ uv run python -m unittest discover -s tests -p "test_*.py"
Ran 206 tests in 3.960s
FAILED (failures=1, skipped=2)
```
- Failures: `test_chromium_installed` (Playwright Chromium *not downloaded* —
  **pre-existing, environmental, unrelated** to arc).
- New green: `tests/test_arc_dynamics.py` (22), `tests/test_arc_birth.py` (9).
- Birth-test regression check: 9/9 pass (identity, canonical events,
  reconstruction equivalence, retrieval w/ provenance, provider swap,
  causal continuity, no-forbidden-coupling).

## 5. Boundary / identity preservation (verified)

- `data/prompts/soul.md`: 0 diff (identity independent of provider/model/renderer).
- `.env`: unchanged.
- `.hermes/config.yaml` line 4041: unchanged (C4 BLOCKED).
- arc modules import only canonical-event semantics — `test_10_no_forbidden_coupling`
  still passes (no `from src.core.brain import` etc.).
- Observer is read-only (ReadFacade); no brain/consciousness mutation.
- Consolidated/decayed state is **derived**; canonical events append-only.

## 6. What "consciousness" questions remain open (per ADR-008)

None of the mechanisms above implement or claim consciousness, phenomenal
experience, or subjective feeling. The `cross_channel_affect` divergence
metric (self-reported valence vs behavioral risk) is a **measurement probe**,
not evidence of inner experience. Open questions deferred to later phases:
developmental staging, recurrent neural substrates, dreaming-as-cognition.
See `docs/reference/OPEN_QUESTIONS.md` Q-AFFECT-01..Q-AFFECT-03.

## 7. Next steps (Phase 4–8 roadmap)

1. Freeze the dynamic module contracts (`tests/test_arc_contracts.py`).
2. Extend `sense()` → multiscale scheduler (drive/arousal-gated timescale).
3. Replace stub providers with a real provider adapter (ADR-016.3).
4. Broaden the causal ablation corpus beyond toy labels.
5. Wire `consolidate()` into a SLOW-timescale loop with the research ledger.
