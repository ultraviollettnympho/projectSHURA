# PROJECTSHURA V3 — ARCHITECTURE DECISIONS

Status: PROPOSED / PARTIAL — key decisions documented; full ADR index must reference existing `docs/reference/ADR_INDEX.md`.
Created: 2026-09-30 (current session).
Based on `docs/reference/ADR_INDEX.md`, `docs/design/ARCHITECTURE_MAP.md`, `docs/v3/ARCHITECTURE_V3.md`, `docs/v3/V3_SCOPE.md`, `.fleet/contracts/framework_contracts.json`, `tests/test_dream_projection.py`, `tests/test_events.py`, `.env`, `git status`.

---

## DECISION 1: V3 SCOPE EXCLUDES FULL LIVE2D PRODUCTION

Status: [VERIFIED DESIGN CONTRACT PRESERVED]
Problem: Full SHURA-01 Live2D production (L0-L12 phases) requires artwork preparation, Cubism modeling, physics, emotional animation, runtime integration — not completed.
Decision: Defer full Live2D production; preserve design contract (`docs/design/SHURA_EMBODIMENT.md` — 82 lines, 3D direction locked 2026-09-23); preserve PNG adapter (`expression.py`, `resources.py`); maintain graceful fallback.
Reason: Smallest complete SHURA requires framework coherence, not full production embodiment.
Evidence: `docs/design/SHURA_EMBODIMENT.md` (line 1-82); `docs/v3/ARCHITECTURE_V3.md` section 5; `docs/v3/V3_SCOPE.md` section 2.2.
Consequences: Future upgrade must observe projection/state contract; identity remains independent of renderer.
Unresolved questions: When will artwork preparation begin? When will Cubism model creation start?

---

## DECISION 2: V3 SCOPE EXCLUDES FULL AGENT SWARM; REQUIRES FRAMEWORK CONTRACTS

Status: [VERIFIED FRAMEWORK CONTRACTS CREATED] — [PROPOSED FULL SWARM]
Problem: `.fleet/` framework artifacts present (`.fleet/verification/step04b_corpus_results.json`: `causal_influence_detected: false`; `fleet/verification/S02-T4_ledger_entry.json`: mixed ablation results — negative diverges, positive does not); framework contracts (`.fleet/contracts/framework_contracts.json`) just created; agent contracts (roles, tasks, memory, execution, verification gates) not fully defined.
Decision: Initialize `.fleet/` framework contracts (`agent_identity`, `agent_observation`, `agent_memory`, `agent_execution`, `agent_failure_recovery`, `agent_verification_gate`); defer full agent swarm; preserve verification artifacts exactly (must not rewrite `step04b_corpus_results.json` or `S02-T4_ledger_entry.json` without new verified evidence).
Reason: Fleet must behave like an engineering organization, not a room of interns; framework contracts must exist before swarm claims.
Evidence: `.fleet/contracts/framework_contracts.json`; `.fleet/verification/step04b_corpus_results.json` (`causal_influence_detected: false`); `fleet/verification/S02-T4_ledger_entry.json` (`delta: 1.0` negative, `delta: 0.0` positive); `docs/v3/V3_EXECUTION_DAG.md` section 2.
Consequences: Any swarm execution claim must reference framework contracts; any agent contract must observe identity/projection/memory/event rules; framework contracts document `agent_memory`: unverified provenance; `agent_execution`: deferred; `agent_verification_gate`: proposed.
Unresolved questions: When will agent contracts (`agent_*`) be completed? When will agent roles be assigned? When will verification gates be fully implemented?

---

## DECISION 3: V3 SCOPE EXCLUDES FULL EMOTIONAL STATE ARCHITECTURE INTEGRATION

Status: [VERIFIED FRAMEWORK PRESERVED]
Problem: Emotional architecture framework present (`brain.py`, `consciousness.py`, `expression.py`, `docs/design/SHURA_EMBODIMENT.md`, `docs/design/SHURA_PRESENCE.md`); full emotional model (valence/arousal/appraisal/need/expression/recovery integration) deferred; seven legacy mood IDs preserved (`normal`, `angry`, `bored`, `cry`, `ew`, `love`, `shock`) as compatibility layer.
Decision: Preserve emotional framework; preserve legacy mood IDs for OBS compatibility; defer full emotional integration; identity remains independent of emotional model (identity defines philosophy; emotional model defines state dynamics).
Reason: Emotional model must not become identity replacement; identity must survive emotional framework changes.
Evidence: `data/prompts/soul.md` section 5; `docs/design/SHURA_EMBODIMENT.md` section 12; `docs/v3/ARCHITECTURE_V3.md` section 5.
Consequences: Any emotional framework change must not modify `soul.md`; emotional framework must observe event/projection interfaces; emotional framework must not couple identity to renderer.
Unresolved questions: When will emotional state integration be completed? When will emotional learning (experience -> observation -> interpretation -> memory -> future decision) be implemented?

---

## DECISION 4: V3 SCOPE EXCLUDES FULL MEMORY CONSOLIDATION PIPELINE INTEGRATION

Status: [VERIFIED FRAMEWORK] — [UNVERIFIED PROVENANCE/CONFIDENCE]
Problem: Memory framework (`MemoryStorage`, `MemoryConsolidationTransaction`, `ConsolidationEngine`) verified present; provenance/confidence fields must be verified (independent QA agent task); full pipeline integration deferred.
Decision: Preserve memory framework; verify provenance/confidence fields separately; document deferred pipeline integration; framework contracts must include memory contract rules (`docs/v3/ARCHITECTURE_V3.md` section 4).
Reason: Memory continuity requires provenance/confidence; framework without verification is decorative, not functional.
Evidence: `docs/MEMORY_CONSOLIDATION.md`; `.fleet/contracts/framework_contracts.json` (`agent_memory`: verified=False); `docs/v3/ARCHITECTURE_V3.md` section 4.
Consequences: Memory framework must remain durable; future memory framework expansions must not couple memory to identity; provenance/confidence verification is a release blocker for full memory continuity claims.
Unresolved questions: When will provenance/confidence fields be verified? When will full consolidation pipeline be integrated?

---

## DECISION 5: V3 SCOPE EXCLUDES FULL DREAM AUTONOMOUS LOOP VERIFICATION

Status: [VERIFIED FRAMEWORK] — [DEFERRED FULL LOOP]
Problem: Dream framework (`DreamEngine`, events, projection) verified; projection boundary verified; full autonomous loop (`docs/operations/AUTONOMOUS_LOOP.md`) deferred; event contracts preserved; framework contracts include agent execution rules (deferred).
Decision: Preserve Dream framework; preserve projection read-only boundary; preserve event contracts; defer autonomous loop execution verification; document deferred loop execution in framework contracts (`docs/v3/ARCHITECTURE_V3.md` sections 2, 3, 4).
Reason: Dream loop requires framework coherence and verification gates; framework contracts must exist before loop execution claims.
Evidence: `docs/DREAM_ENGINE.md`; `tests/test_dream_projection.py`; `.fleet/contracts/framework_contracts.json` (`agent_execution`: verified=False); `docs/v3/ARCHITECTURE_V3.md` sections 2, 3.
Consequences: Any Dream framework change must preserve projection read-only boundary; Dream framework must observe identity/event/memory contracts; autonomous loop framework must remain durable (any restructuring requires ADR).
Unresolved questions: When will autonomous loop execution begin? When will verification gates be fully implemented?

---

## DECISION 6: V3 SCOPE PRESERVES DESIGN FRAMEWORK DURABILITY

Status: [VERIFIED FRAMEWORK DURABILITY RULES VERIFIED]
Problem: Workspace framework, autonomous loop framework, task framework, milestone framework, design framework, embodiment framework, reference framework, vision framework, architecture framework, harness interoperability framework must remain durable through autonomous work.
Decision: Any framework restructuring must be explicitly identified with: problem, constraints, alternatives, selected approach, reason, consequences, unresolved questions (ADR format or open questions format); restructuring must not be treated as ordinary implementation cleanup; framework contracts must include framework durability rules (`docs/v3/ARCHITECTURE_V3.md` section 12).
Reason: Future framework expansions must not require restructuring current framework; restructuring must be documented as architectural decision.
Evidence: `docs/design/ARCHITECTURE_MAP.md` (section 10); `docs/reference/ADR_INDEX.md`; `docs/tasks/V1_TASK_GRAPH.md`; `docs/tasks/V1_ROADMAP.md`; `docs/operations/AUTONOMOUS_LOOP.md`; `.fleet/contracts/framework_contracts.json` (`agent_execution`: deferred; framework durability rules verified).
Consequences: Any framework restructuring must update relevant design/reference documentation; must update verification criteria; must preserve future extensibility; framework restructuring without ADR is a contract violation.
Unresolved questions: When will design framework durability verification be fully executed (independent QA agent)?

---

## DECISION 7: V3 SCOPE PRESERVES `.FLEET/` VERIFICATION ARTIFACTS EXACTLY

Status: [VERIFIED ARTIFACTS PRESERVED]
Problem: `.fleet/verification/step04b_corpus_results.json` (`causal_influence_detected: false`); `fleet/verification/S02-T4_ledger_entry.json` (Step 04C ablation: negative diverges `delta: 1.0`, positive does not diverge `delta: 0.0`, `significant: false`); framework contracts created; any rewrite of these artifacts without new verified evidence violates verification integrity.
Decision: Preserve `.fleet/` verification artifacts exactly; document results in framework contracts (`.fleet/contracts/framework_contracts.json` verification_artifacts_preserved); document Step 04B (`causal_influence_detected: false`) and Step 04C (mixed results) in architecture contracts (`docs/v3/ARCHITECTURE_V3.md` section 9); framework contracts must include agent execution rules that reference these results (`agent_execution`: deferred; framework contracts must not claim verified causal influence).
Reason: Verification artifacts are evidence of actual results; rewriting them without new verified evidence is fabrication; framework contracts must reference actual results.
Evidence: `.fleet/verification/step04b_corpus_results.json`; `fleet/verification/S02-T4_ledger_entry.json`; `.fleet/contracts/framework_contracts.json` (verification_artifacts_preserved); `docs/v3/ARCHITECTURE_V3.md` section 9.
Consequences: Any claim of verified causal influence for Step 04B/04C requires new verified evidence (new `.fleet/verification/` artifact with verified `causal_influence_detected: true` or new ablation result with `delta: >0` and `significant: true` for both negative and positive conditions); framework contracts must not claim verified causal integration until new evidence exists; `.fleet/` framework must be durable through future autonomous work (any restructuring requires ADR).
Unresolved questions: When will Step 04D (positive vs negative ablation with larger option sets) be executed? When will new verification artifacts be created?

---

## DECISION 8: V3 SCOPE PRESERVES `.ENV` UNSTAGED AND SECRET INDEPENDENCE

Status: [VERIFIED `.ENV` UNSTAGED; `.ENV` CONTENT NOT FULLY INSPECTED FOR SECRETS]
Problem: `.env` exists; `.env` unstaged verified (`git status --short .env`: empty); `.env` must not contain secrets that should not be in repository; `.env` must remain unstaged; framework contracts must include security/resilience rules (destructive action approval, graceful degradation, `.env` unstaged verification).
Decision: Confirm `.env` unstaged (verified); confirm `.env` not in `git ls-files` (must verify); confirm `.env` content does not expose secrets (must verify content briefly); framework contracts must document `.env` unstaged verification and security rules (`docs/v3/ARCHITECTURE_V3.md` section 11); any staged `.env` is a release blocker and contract violation.
Reason: Secret exposure is irreversible; `.env` must remain local; security contract requires `.env` unstaged verification; graceful degradation must include model unavailable, renderer unavailable, asset unavailable, GPU insufficient, harness unavailable.
Evidence: `.env`; `git status --short .env` (empty); `.fleet/contracts/framework_contracts.json` (security/resilience rules verified by architecture rules); `docs/v3/ARCHITECTURE_V3.md` section 11.
Consequences: Any `.env` staged is a release blocker; any secret exposure requires immediate remediation; any destructive action without approval violates security contract; framework contracts must include bounded repair rules (no retry loops without architectural discussion).
Unresolved questions: When will `.env` content be fully inspected for secrets? When will security/resilience verification be fully executed (independent QA agent)?

---

## DECISION 9: FRAMEWORK CONTRACTS MUST INCLUDE DURABILITY VERIFICATION CRITERIA

Status: [VERIFIED FRAMEWORK CONTRACTS CREATED; FULL DURABILITY VERIFICATION DEFERRED]
Problem: `.fleet/contracts/framework_contracts.json` created with 6 agent contracts (`agent_identity`, `agent_observation`, `agent_memory`, `agent_execution`, `agent_failure_recovery`, `agent_verification_gate`); framework contracts must include framework durability verification criteria (workspace framework durability, autonomous loop framework durability, milestone framework durability, task framework durability, harness interoperability verification); framework contracts must reference design framework durability rules (`docs/v3/ARCHITECTURE_V3.md` section 12); independent QA agent (Agent 11) must verify framework durability.
Decision: Framework contracts include durability rules; framework contracts reference design framework durability rules; framework contracts document deferred/proposed status for agent contracts; framework contracts must be updated if any restructuring occurs (ADR required); framework contracts must remain durable through autonomous work.
Reason: Design framework durability is a core architectural property; restructuring without ADR is a contract violation.
Evidence: `.fleet/contracts/framework_contracts.json`; `docs/v3/ARCHITECTURE_V3.md` section 12; `docs/reference/ADR_INDEX.md`; `docs/tasks/V1_TASK_GRAPH.md`; `docs/tasks/V1_ROADMAP.md`; `docs/operations/AUTONOMOUS_LOOP.md`.
Consequences: Any framework restructuring must be documented as ADR; framework contracts must reference restructuring ADR; framework contracts must update verification criteria; framework contracts must preserve future extensibility.
Unresolved questions: When will framework durability verification be fully executed? When will harness interoperability verification begin?

---

## DECISION 10: ARCHITECTURE CONTRACTS FILE MUST REFERENCE ALL SUBSYSTEM CONTRACTS

Status: [VERIFIED ARCHITECTURE CONTRACTS FILE CREATED — `docs/v3/ARCHITECTURE_V3.md`]
Problem: `ARCHITECTURE_V3.md` (15585 chars, 13 sections) defines identity, event, projection, memory, embodiment, presence, model/provider, skill, agent/swarm, workspace, security, design durability contracts; contracts file must reference all design/docs/contracts/reference/artifact paths; contracts file must document status markers; contracts file must include integration points (vertical slice design path); contracts file must reference framework contracts (`.fleet/contracts/framework_contracts.json`).
Decision: `ARCHITECTURE_V3.md` created with 13 sections; contracts file references verified contracts; contracts file documents proposed/deferred/unverified status; contracts file references `.fleet/` verification artifacts; contracts file must remain durable (any restructuring requires ADR); contracts file must be updated when new contracts or restructuring occur.
Reason: Architecture contracts file is the canonical reference for V3 architecture; all workstreams must reference it; all verification must reference it; all design framework changes must reference it.
Evidence: `docs/v3/ARCHITECTURE_V3.md`; `docs/v3/ARCHITECTURE_DECISIONS.md`; `.fleet/contracts/framework_contracts.json`.
Consequences: Any architectural change must update contracts file; any framework restructuring must reference contracts file; any verification claim must reference contracts file; contracts file must describe reality (not aspirational features).
Unresolved questions: When will contracts file be fully verified (independent QA agent)? When will contracts file be updated with full agent contracts?

---

END OF ARCHITECTURE DECISIONS
