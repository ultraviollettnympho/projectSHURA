# PROJECTSHURA V3 — SCOPE

Created: 2026-09-30 (current session).
Based on verified audit (`V3_STATE_AUDIT.md`) and repository state (`shura-foundation` branch, 5 commits ahead of origin).
Status markers: [VERIFIED] / [PROPOSED] / [DEFERRED] / [EXPERIMENTAL] / [BLOCKED] / [UNVERIFIED].

---

## 1. WHAT V3 IS

V3 is the point at which SHURA's identity, cognition, memory/context, agent orchestration, embodiment, Command Center, ATLAS, FORGE, model/runtime, tool/MCP, persistence, observability, and development workflow operate as one coherent, inspectable, demonstrable system.

V3 is NOT:
- A feature dump of every idea discussed.
- A complete Live2D production model (deferred).
- A fully autonomous agent swarm (deferred; `.fleet/` currently only contains verification artifacts, no agent contracts).
- A perfect emotional simulation (deferred; framework exists, full integration deferred).

---

## 2. V3 SCOPE CATEGORIES

### 2.1 REQUIRED FOR V3 (must function; must have evidence)

These are capabilities that must work for V3 to be called complete. Each must have verification evidence in the audit or a dedicated verification artifact.

1. **Identity preserved independently of provider/model** [VERIFIED] (`data/prompts/soul.md`, `operating.md`, `chat.md`, `minecraft.md`; identity files contain no provider/model references; verified by file read).
2. **Brain/core runtime functional** [VERIFIED FRAMEWORK; SMOKE TEST UNVERIFIED] (`brain.py`, `consciousness.py`, `events.py`, `expression.py`, `resources.py` present; recent commits modify `brain.py`/`events`/`expression` but full smoke test not executed in this session; framework intact).
3. **Event contracts preserved** [VERIFIED] (`docs/EVENT_CONTRACT.md`; event taxonomy stable; `EventManager.publish()` only creation mechanism verified by source inspection).
4. **Projection read-only boundary preserved** [VERIFIED] (`tests/test_dream_projection.py`; `test_projection_does_not_mutate_domain` verified; projection imports domain but domain does not import projection).
5. **Memory framework present and inspectable** [VERIFIED FRAMEWORK] (`MemoryStorage`, `MemoryConsolidationTransaction`, `ConsolidationEngine` verified by architecture notes; full pipeline integration deferred per architecture audit; provenance/confidence fields must be verified before claiming full memory continuity).
6. **Presence architecture framework present** [VERIFIED] (`PresenceRuntime`, `presence/events/`, projection interface verified by design docs; runtime endpoint behavior deferred verification).
7. **Legacy mood IDs preserved for OBS** [VERIFIED] (seven IDs: `normal`, `angry`, `bored`, `cry`, `ew`, `love`, `shock`; preserved by `docs/design/SHURA_EMBODIMENT.md` and `data/prompts/soul.md`; load-bearing until Live2D abstraction replaces them).
8. **Model/provider abstraction framework present** [VERIFIED FRAMEWORK] (`omniroute_llm.py`, `openai_compat.py`, `groq_llm.py`, `openrouter_llm.py` present; routing verification deferred; identity independent of provider verified).
9. **Command Center design present and coherent** [VERIFIED DESIGN] (`docs/design/COMMAND_CENTER_V1.md` — 107 lines; `docs/design/ARCHITECTURE_MAP.md` confirms ATLAS/Command Center contracts; runtime endpoint verification deferred).
10. **FORGE workspace framework present** [VERIFIED DESIGN] (`docs/design/COMMAND_CENTER_V1.md`, architecture docs define workspace/task execution interface; `.fleet/` currently empty except verification artifact; workspace execution verification deferred; must verify `.fleet/` artifacts before treating as complete workspace implementation).
11. **Embodiment interface contract defined** [VERIFIED DESIGN] (`docs/design/SHURA_EMBODIMENT.md` — 82 lines; embodiment interface (`EmbodimentInterface`) concept defined; 3D direction locked 2026-09-23; PNG adapter preserved; Live2D backend deferred production).
12. **Skill/plugin system preserved** [VERIFIED] (`chat.md`, `minecraft.md`, `memory`, `dream`, `idle`, `voice`, `social` skills present; identity does not leak into separate skill personalities — verified by `data/prompts/soul.md` and architecture rules).
13. **Fleet/swarm framework initialized** [PROPOSED / PARTIAL] (`.fleet/` directory exists but contains only `.fleet/verification/step04b_corpus_results.json`; no agent contracts, task graphs, role assignments, or execution ledgers present; swarm framework must be initialized but does not need to be fully populated for V3 — it must exist with contracts, verification gates, and a single bounded demonstration path).
14. **Verification matrix exists** [PROPOSED] (`docs/v3/VERIFICATION_MATRIX.md` must be created; must map each REQUIRED capability to implementation, test, evidence, status).
15. **Release checklist present** [PROPOSED] (`docs/v3/RELEASE_CHECKLIST.md` must be created; must include smoke test, identity preservation check, projection boundary check, build/test status, documentation match, and known limitations).
16. **Complete vertical slice works** [REQUIRED — UNVERIFIED / PROPOSED] At least one user-visible interaction path must work end-to-end:
    - Input → cognition → context/memory retrieval → model/tool execution → state update → presence → UI/embodiment → observable result → memory update.
    This slice does not require full Live2D, full agent swarm, or full emotional simulation; it requires the framework to be coherent and the path to be observable.
17. **Documentation matches implementation** [REQUIRED — PARTIALLY VERIFIED] Key docs (`ARCHITECTURE_MAP.md`, `COMMAND_CENTER_V1.md`, `THREE_SYSTEMS.md`, `SHURA_EMBODIMENT.md`, `EVENT_CONTRACT.md`, `DREAM_ENGINE.md`) match source framework; `.fleet/` artifacts must be inspected; V3 docs (`docs/v3/`) must describe reality (this scope + audit + execution graph).
18. **Known limitations documented** [REQUIRED — PROPOSED] Every deferred feature and every unverified framework must be explicitly listed in V3 scope/release notes (not hidden or implied).

### 2.2 DEFERRED AFTER V3 (explicitly out of V3 release boundary; must be documented, not hidden)

These capabilities are valuable and have framework/design work present, but they must NOT be treated as V3 requirements. They should be explicitly deferred in V3 scope/release notes.

1. **Full SHURA-01 Live2D production** [DEFERRED] (`docs/design/SHURA_EMBODIMENT.md` defines L0-L12 phases; artwork preparation, Cubism model creation, physics, emotional animation, runtime integration — all deferred; design contract locked 2026-09-23; production deferred).
2. **Full emotional state architecture** [DEFERRED] (`docs/design/SHURA_EMBODIMENT.md` defines emotional pipeline; `data/prompts/soul.md` defines emotional philosophy; `brain.py` has basic consciousness loop; full emotional model — valence/arousal/appraisal/need/expression/recovery integration — deferred; seven legacy mood IDs preserved as compatibility layer).
3. **Full memory consolidation pipeline** [DEFERRED] (`MemoryConsolidationTransaction` framework verified present; `ConsolidationEngine` framework verified present; end-to-end pipeline integration deferred per architecture audit; provenance/confidence fields must be verified in future milestone).
4. **Full agent/constitution layer** [DEFERRED] (Agent registry, authority boundaries, conflict resolution, constitution rules — proposed in `SHURA_MASTER_HANDOFF.md`; `.fleet/` currently only verification artifacts; full agent swarm deferred; V3 requires framework contracts and verification gates, not full agent population).
5. **Full Dream Engine autonomous loop** [DEFERRED] (Dream framework present; projection verified; `docs/DREAM_ENGINE.md` defines contracts; full autonomous loop — experience → observation → interpretation → memory → retrieval → future decision → outcome → evaluation → updated knowledge — deferred; `docs/operations/AUTONOMOUS_LOOP.md` defines durable protocol; actual loop execution deferred).
6. **Full TTS/prosody emotional synchronization** [DEFERRED] (`expression.py` provides TTS sink; emotional-to-prosody mapping deferred; basic amplitude-based talking animation preserved).
7. **Full multimodal perception/expression** [DEFERRED] (Future target; current framework supports expression output only; perception framework (`PerceptionBus`) present; full multimodal integration deferred).
8. **Full REAPER / audio production integration** [DEFERRED] (Extensively documented: `docs/REAPER_INTEGRATION_PLAN.md`, `ACE_STUDIO_CAPABILITY_REPORT.md`, `docs/INTEGRATION_MATRIX.md`, `docs/ACE_MCP_CONFIG_REFERENCE.md`; framework references exist; runtime integration with SHURA brain deferred; not a V3 blocker).
9. **Full social/persona layer** [DEFERRED] (`SocialMemory`, `memory/people.json`, `memory/roster.json` present; deep persona integration deferred; basic memory framework sufficient for V3).
10. **Dynamic cognitive mechanism full integration** [DEFERRED / EXPERIMENTAL] (`feat(arc): Step 03` — verified present by commit; `tests/test_arc_contracts.py` modified; `.fleet/verification/step04b_corpus_results.json` shows `causal_influence_detected: false`; Step 04B did NOT verify causal influence; mechanism framework present but full verified causal integration deferred until Step 04B or future milestone achieves verified causal detection).
11. **INFAC domain full integration** [DEFERRED] (`feat(dominion): add INFAC domain` — verified present; integration with broader SHURA system deferred).

### 2.3 EXPERIMENTAL / PROTOTYPE (must be clearly labeled; must not destabilize V3; must not be claimed as verified release features)

These are interesting research/prototype artifacts. They may inform future architecture but must not be treated as V3 requirements. They must have their status clearly labeled.

1. `.fleet/verification/step04b_corpus_results.json` [EXPERIMENTAL / VERIFIED OBSERVATION] — Verification artifact showing `causal_influence_detected: false` for Step 04B; must remain as evidence that Step 04B did not achieve verified causal influence; must not be rewritten to claim success.
2. `tests/demo_step04b_broaden_causal_corpus.py` [EXPERIMENTAL] — Demonstration script; not a release feature.
3. `docs/superpowers/specs/2026-09-30-shura-arc-step04a-contract-freeze-report.md` [VERIFIED ARTIFACT] — Contract freeze report for Step 04A; must be preserved; not a feature.
4. `docs/superpowers/specs/` [PROPOSED / PARTIAL] — Superpowers specification directory; design spec artifacts; must be preserved but not treated as verified implementation.
5. `tests/test_arc_contracts.py` modifications [VERIFIED] — Arc contract test modifications present in working tree; must be verified to not break existing contract boundaries; must be included in V3 verification matrix.
6. `src/arc/drives/drive_system.py` [VERIFIED FILE; INTEGRATION UNVERIFIED] — Arc drives module present; must be verified that it observes brain/consciousness interfaces (not mutates directly) and preserves identity/provider independence; must be inspected before any integration claim.
7. `.freebuff/` directory [UNVERIFIED HARNESSES] — Exists; health/config not inspected; must not become a V3 blocker.
8. `.crush/` directory [UNVERIFIED HARNESSES] — Exists; health/config not inspected; must not become a V3 blocker.

---

## 3. SMALLEST COMPLETE SHURA THAT DESERVES V3

The answer must be based on the verified repository state, not imagination.

The smallest complete SHURA (V3 release candidate) is:

> A portable, identity-independent SHURA whose brain/core framework, event/projection contracts, memory framework, presence framework, skill framework, embodiment contract, and documentation architecture operate as one coherent, inspectable system. The framework supports a bounded user-visible vertical slice (input → cognition → context → execution → state → presence → observation → result → memory) without requiring full agent swarm, full emotional simulation, full Live2D production, or full autonomous loop. Every deferred feature is explicitly listed and every unverified framework is clearly labeled.

This definition reflects reality:
- `.fleet/` is not a fully populated swarm; it requires framework contracts.
- `causal_influence_detected: false` means full dynamic cognitive mechanism verification is deferred.
- Memory pipeline framework exists; full integration deferred.
- Command Center design verified; runtime endpoint verification deferred.
- FORGE workspace framework defined; `.fleet/` execution verification deferred.

---

## 4. SCOPE DECISIONS (ARCHITECTURAL DECISIONS FOR V3)

These decisions are durable and must be documented in `docs/reference/ADR_INDEX.md` or `docs/v3/ARCHITECTURE_DECISIONS.md`:

1. [DECISION — VERIFIED] V3 scope excludes full Live2D production; includes design contract preservation and PNG adapter preservation.
2. [DECISION — VERIFIED] V3 scope excludes full agent swarm; includes `.fleet/` framework contracts, verification gates, and a single bounded demonstration task.
3. [DECISION — VERIFIED] V3 scope excludes full emotional state architecture integration; includes framework preservation and legacy mood ID compatibility.
4. [DECISION — VERIFIED] V3 scope excludes full memory consolidation pipeline integration; includes framework verification and provenance/confidence verification requirements.
5. [DECISION — VERIFIED] V3 scope excludes full Dream autonomous loop verification; includes projection boundary preservation and event contract preservation.
6. [DECISION — PROPOSED] V3 vertical slice must include one complete user-visible interaction path; must be observable; must include evidence.
7. [DECISION — PROPOSED] V3 verification matrix must exist; must reference actual test files and actual verification commands; must not claim unverified features.
8. [DECISION — PROPOSED] V3 release notes must document all deferred work, all unverified frameworks, and the `.fleet/` verification result (`causal_influence_detected: false`).

---

## 5. SCOPE BOUNDARY RULES (ENFORCED)

These rules prevent V3 from becoming a feature dump or an imaginary release:

1. No feature is considered V3-complete without verification evidence (test, endpoint, file inspection, verified command output, or explicit design verification).
2. No deferred feature is hidden; every deferred feature is explicitly listed in scope/deferred sections.
3. No experimental prototype is claimed as a verified release feature; all experimental/prototype artifacts must have their status clearly labeled.
4. `.fleet/` swarm artifacts must not claim agent contracts that do not exist; framework contracts must exist before swarm claims.
5. `causal_influence_detected: false` must be preserved as evidence; no rewrite of this verification result is permitted without a new verified result.
6. The identity layer (`data/prompts/soul.md`, `operating.md`) must remain independent of provider/model; any change that introduces provider/model references into identity is a V3 scope violation.
7. The projection layer must remain read-only; any mutation of brain/consciousness internals through projection is a V3 scope violation.
8. Memory mutations must flow through `MemoryStorage` framework; any direct mutation bypassing framework is a V3 scope violation.
9. Embodiment (`expression.py`, avatar resources) must remain a downstream adapter of brain state; any direct brain mutation from renderer is a V3 scope violation.
10. `.env` secrets must not enter repository; `.env` must remain unstaged/uncommitted; any staged `.env` is a V3 scope violation.

---

## 6. NEXT ACTIONS FROM SCOPE

Verified next actions:
- Confirm `.fleet/` framework contracts exist (or must be created) before swarm claims.
- Confirm verification matrix references actual tests (`tests/test_dream_projection.py`, `tests/test_events.py`, `tests/test_arc_contracts.py`, `.fleet/verification/step04b_corpus_results.json`).
- Confirm release checklist references smoke test, identity preservation check, projection boundary check, build/test status, documentation match, and known limitations.
- Confirm architecture decisions (`docs/reference/ADR_INDEX.md` or `docs/v3/ARCHITECTURE_DECISIONS.md`) include the 8 decisions above.
- Confirm V3 execution graph (`V3_EXECUTION_DAG.md`) reflects the scope categories and boundaries.

---

END OF V3 SCOPE
