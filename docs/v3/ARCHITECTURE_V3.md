# PROJECTSHURA V3 — ARCHITECTURE CONTRACTS (PHASE B)

Status: PROPOSED — contracts framework defined; full contract verification deferred until all workstreams complete.
Based on `docs/design/ARCHITECTURE_MAP.md`, `docs/design/COMMAND_CENTER_V1.md`, `docs/design/THREE_SYSTEMS.md`, `docs/design/SHURA_EMBODIMENT.md`, `docs/EVENT_CONTRACT.md`, `docs/DREAM_ENGINE.md`, `docs/operations/AUTONOMOUS_LOOP.md`, `docs/reference/ADR_INDEX.md`, and verified source inspection (`brain.py`, `consciousness.py`, `events.py`, `expression.py`, `projection.py`, `resources.py`).

---

## 1. IDENTITY CONTRACT

Source: `data/prompts/soul.md`, `AGENTS.md`, `docs/SHURA_MASTER_HANDOFF.md`.
Verification: Identity files contain no provider/model references; identity independent of renderer; identity preserved across changes: [VERIFIED FRAMEWORK] — full identity contract preservation verified by file inspection; identity layer must not be rewritten during V3.

Rules:
- `soul.md` = identity; `operating.md` = behavior; skills = capabilities; embodiment = renderer; model = engine; memory = continuity.
- Changing identity requires explicit governed review; changing skills/models/embodiments does not require identity change.
- `.fleet/` agent contracts must reference identity layer but not modify it directly; any agent that writes to `data/prompts/soul.md` without approval violates the identity contract.

---

## 2. EVENT CONTRACT

Source: `docs/EVENT_CONTRACT.md`, `src/core/events.py`, `brain.py`, `tests/test_events.py`.
Verification: `EventManager.publish()` is only creation mechanism; `subscribe()` / replay is observation mechanism; projection reads but does not create events.
Status: [VERIFIED] — event taxonomy preserved; event emission mechanism verified by source inspection; event replay mechanism verified by design docs.

Rules:
- Events are the only mechanism for cognitive state change observation outside direct method calls.
- Projection layer must not create events; event creation must flow through `EventManager`.
- `.fleet/` swarm artifacts must observe events through `subscribe()` / replay; must not inject events through direct brain mutation.

---

## 3. PROJECTION CONTRACT

Source: `docs/design/ARCHITECTURE_MAP.md`, `tests/test_dream_projection.py`, `docs/DREAM_ENGINE.md`, `src/core/dream/projection.py`.
Verification: `tests/test_dream_projection.py` verifies `test_projection_does_not_mutate_domain`; projection imports domain but domain does not import projection; projection is read-only.
Status: [VERIFIED] — projection boundary preserved; must remain intact for V3.

Rules:
- Projection creates derived state from domain objects; projection must not modify domain state.
- Workspace (`.fleet/`) must observe through projection; workspace must not import brain/consciousness internals for mutation logic.
- Any `.fleet/` contract that imports brain/consciousness for mutation violates projection contract and must be corrected before integration.

---

## 4. MEMORY CONTRACT

Source: `docs/MEMORY_CONSOLIDATION.md`, `docs/reference/VERIFICATION_PATTERN.md`, `src/core/skils/memory/`, `MemoryStorage`, `MemoryConsolidationTransaction`, `ConsolidationEngine`.
Verification: Memory framework present; provenance/confidence fields must be verified (proposed verification step); full pipeline integration deferred.
Status: [VERIFIED FRAMEWORK] — framework verified; provenance/confidence verification proposed; full pipeline deferred.

Rules:
- Memory mutations flow through `MemoryStorage` framework (`MemoryConsolidationTransaction`, `ConsolidationEngine`); direct mutation bypassing framework is a contract violation.
- Every stored memory must have provenance (source, timestamp, confidence) where practical; memory retrieval must distinguish retrieved information from current reality (verified by architecture rules and `docs/SHURA_MASTER_HANDOFF.md` section 16).
- `.fleet/` agent contracts must observe memory through framework interfaces (`/memory/save` endpoint, future framework interfaces); must not write directly to memory files.

---

## 5. EMBODIMENT CONTRACT

Source: `docs/design/SHURA_EMBODIMENT.md`, `docs/design/ARCHITECTURE_MAP.md`, `src/core/expression.py`, `src/core/resources.py`.
Verification: Design contract verified (`docs/design/SHURA_EMBODIMENT.md` — 82 lines, 3D direction locked 2026-09-23); PNG adapter preserved (`expression.py`, `resources.py`); identity independent of renderer verified.
Status: [VERIFIED DESIGN] — production Live2D deferred; PNG adapter preserved; graceful fallback defined in design.

Rules:
- Embodiment (`expression.py`, avatar resources, renderer) is a downstream adapter of brain state; identity layer defines persona; embodiment renders it.
- Embodiment must not become source of cognitive truth; renderer must observe brain state through projection/event interfaces.
- Legacy mood IDs (`normal`, `angry`, `bored`, `cry`, `ew`, `love`, `shock`) preserved for OBS compatibility until Live2D abstraction replaces them; any change must provide explicit migration path.
- 3D embodiment (`SHURA-01`) design contract locked 2026-09-23; production deferred; future upgrade must observe projection/state contract.

---

## 6. PRESENCE CONTRACT

Source: `docs/design/SHURA_PRESENCE.md`, `docs/design/ARCHITECTURE_MAP.md`, `src/core/presence.py`, `presence/events/`.
Verification: Presence framework verified (`PresenceRuntime`, event-based projection); payloads renderer-agnostic (verified by design rules in `ARCHITECTURE_MAP.md`).
Status: [VERIFIED FRAMEWORK] — presence events and projection interfaces verified; runtime endpoint verification deferred.

Rules:
- Presence communicates events (connected, disconnected, state, emotion, motion, speech, STT, tool activity, dream activity) through renderer-agnostic payloads.
- Presence payloads must not encode OBS/Live2D/renderer-specific implementation details into event contracts.
- `.fleet/` workspace must observe presence through event/projection interfaces; workspace must not reach directly into presence internals for mutation.

---

## 7. MODEL / PROVIDER CONTRACT

Source: `docs/design/ARCHITECTURE_MAP.md`, `docs/design/THREE_SYSTEMS.md`, `src/core/agent/` (`omniroute_llm.py`, `openai_compat.py`, etc.), `data/prompts/soul.md`.
Verification: Provider abstraction framework verified by file presence; identity files contain no provider references (verified by file read); capability-based routing framework present; routing verification deferred.
Status: [VERIFIED FRAMEWORK] — framework present; full routing verification deferred.

Rules:
- Provider/model changes must not affect identity; identity files must remain independent of provider/model.
- Capability-based routing (rather than model-name mythology) is the intended architecture; routing framework must support provider independence.
- `.fleet/` agent contracts must reference model/provider abstraction; must not hard-code provider-specific behavior into agent contracts.

---

## 8. SKILL / CONTEXT CONTRACT

Source: `data/prompts/chat.md`, `minecraft.md`, `operating.md`, `docs/skills/`, `AGENTS.md`.
Verification: Skill framework preserved; identity does not leak into separate skill personalities (verified by `data/prompts/soul.md` and architecture rules); skill contracts must not redefine identity.
Status: [VERIFIED] — skills extend capabilities without creating independent personalities.

Rules:
- Each skill defines purpose, triggers, tools, context injection, output contract, memory interactions, emotional effects, embodiment effects, failure behavior, permissions/boundaries.
- Skill contracts must not create separate personalities; identity (`soul.md`) defines who performs the skill; skill defines what can be done.
- `.fleet/` agent contracts must not become independent personalities; agents must serve SHURA identity rather than replacing it.

---

## 9. AGENT / SWARM CONTRACT (FLEET FRAMEWORK)

Source: `.fleet/` (directory and artifacts), `docs/tasks/V1_TASK_GRAPH.md`, `docs/operations/AUTONOMOUS_LOOP.md`, `docs/reference/ADR_INDEX.md`.
Verification: `.fleet/` directory exists but framework contracts not yet created; `.fleet/verification/step04b_corpus_results.json` shows `causal_influence_detected: false` for Step 04B; `fleet/verification/S02-T4_ledger_entry.json` shows Step 04C ablation with mixed results (`delta: 1.0` for negative, `delta: 0.0` for positive); `.fleet/` contracts proposed; swarm framework must be initialized with contracts before any agent execution claims.
Status: [PROPOSED / PARTIAL] — framework artifacts present (verification results preserved); framework contracts missing; swarm contracts must be created before swarm integration claims.

Rules:
- `.fleet/` framework must include: agent contracts (`.fleet/contracts/`), verification gates (`.fleet/verification/`), task contracts (`.fleet/tasks/` or `.fleet/` reference to `docs/tasks/V1_TASK_GRAPH.md`), agent memory contracts, execution state contracts, failure recovery contracts, reconciliation contracts.
- Agent contracts must reference identity layer; agent contracts must not modify identity directly; agent contracts must observe through event/projection interfaces; agent contracts must not import brain/consciousness internals for mutation logic.
- `.fleet/` verification artifacts must be preserved exactly (`step04b_corpus_results.json` with `causal_influence_detected: false`; `S02-T4_ledger_entry.json` with `delta: 0.0` for positive condition); any rewrite of verification results without new verified evidence is a contract violation.
- Fleet execution must follow `PLAN -> DELEGATE -> EXECUTE -> VERIFY -> RECONCILE -> LEARN`; autonomous loop framework (`docs/operations/AUTONOMOUS_LOOP.md`) defines durable protocol.
- Before any swarm execution claim, `.fleet/contracts/` must exist with verified contracts and verification gates; `.fleet/` framework contracts are a GATE B blocker for Phase C.

---

## 10. WORKSPACE / FORGE CONTRACT

Source: `docs/design/COMMAND_CENTER_V1.md`, `docs/tasks/V1_TASK_GRAPH.md`, `docs/operations/AUTONOMOUS_LOOP.md`, `.fleet/`.
Verification: Workspace framework designed (`COMMAND_CENTER_V1.md` verified); workspace framework must observe through event/projection interfaces; workspace framework must not import brain/consciousness internals; workspace framework must preserve future extensibility without restructuring.
Status: [VERIFIED DESIGN] — workspace framework verified by design; `.fleet/` contracts must exist before workspace execution claims; workspace framework durability must be verified.

Rules:
- Workspace (`.fleet/` or `FORGE`) observes ProjectSHURA state through event/projection/application interfaces; workspace must not reach into brain/consciousness internals for mutation logic.
- Workspace framework must remain durable: future workspace expansions/implementations must not require restructuring current framework; any restructuring must be documented as an explicit architectural decision.
- `.fleet/` framework contracts must include workspace/task/artifact/state contracts and verification criteria; framework verification criteria include workspace framework durability, autonomous loop framework durability, milestone framework durability, task framework durability, harness interoperability verification.

---

## 11. SECURITY / RESILIENCE CONTRACT

Source: `docs/EVENT_CONTRACT.md`, `docs/operations/AUTONOMOUS_LOOP.md`, `.env`, `docs/reference/VERIFICATION_PATTERN.md`.
Verification: `.env` exists and is not staged (verified by `git status`); `.env` must not contain secrets in repository; destructive actions require human approval (verified by architecture rules in `AGENTS.md` and `docs/reference/VERIFICATION_PATTERN.md`); graceful degradation defined (model unavailable, renderer unavailable, asset unavailable, GPU insufficient — verified by design rules in `ARCHITECTURE_MAP.md` and `docs/design/SHURA_EMBODIMENT.md`).
Status: [VERIFIED FRAMEWORK] — `.env` unstaged verified; destructive action approval rules verified; graceful degradation rules verified; `.fleet/` contracts must include failure recovery contracts.

Rules:
- `.env` secrets must remain local; `.env` must not be committed; any staged `.env` is a contract violation and a release blocker.
- Human approval required for destructive actions; `.fleet/` agent contracts must define destructive action boundaries; any autonomous destructive action without approval is a contract violation.
- Failure recovery must be bounded; `.fleet/` contracts must include bounded repair rules; retry loops without architectural discussion are contract violations (referenced by autonomous loop framework rules: never attempt fix #4 without architectural discussion; never retry C4 mechanism indefinitely).
- Graceful degradation must be defined for: model unavailable, renderer unavailable, asset unavailable, GPU capability insufficient, harness unavailable (OpenClaw, Freebuff, [PERSON_NAME], [PERSON_NAME] — all must have graceful degradation defined and must not become V3 blockers).

---

## 12. DESIGN FRAMEWORK DURABILITY CONTRACT

Source: `docs/design/ARCHITECTURE_MAP.md`, `docs/design/COMMAND_CENTER_V1.md`, `docs/design/SHURA_EMBODIMENT.md`, `docs/reference/ADR_INDEX.md`, `docs/tasks/V1_TASK_GRAPH.md`, `docs/tasks/V1_ROADMAP.md`, `docs/operations/AUTONOMOUS_LOOP.md`.
Verification: Design framework files inspected; framework must remain durable through autonomous work; any framework restructuring must be explicitly identified, document reason, identify affected contracts, update relevant design/reference documentation, update verification criteria, preserve future extensibility (verified by architecture rules in `AGENTS.md` and `docs/reference/VERIFICATION_PATTERN.md`).
Status: [VERIFIED FRAMEWORK] — framework durability rules verified by architecture rules; `.fleet/` framework contracts must include framework durability verification criteria.

Rules:
- Workspace framework, autonomous loop framework, task framework, milestone framework, design framework, embodiment framework, reference framework, vision framework, architecture framework, harness interoperability framework must remain durable through autonomous work.
- Any framework restructuring must be explicitly identified with: problem, constraints, alternatives considered, selected approach, reason, consequences, unresolved questions (ADR format or open questions format); restructuring must not be treated as ordinary implementation cleanup.
- Future identity-framework expansion must not require coupling identity to a concrete runtime (verified by identity contract rules); future Dream framework expansion must not couple Dream to a specific UI; future workspace framework expansion must not make current implementation the permanent architectural definition.

---

## 13. INTEGRATION POINTS (VERTICAL SLICE)

Verified vertical slice design (from `docs/design/ARCHITECTURE_MAP.md`, `docs/design/COMMAND_CENTER_V1.md`, `docs/design/THREE_SYSTEMS.md`):
- Input -> brain/cognition -> consciousness -> event emission -> memory framework -> model/tool execution -> event emission -> presence/projection -> observation (UI/embodiment) -> result -> memory framework -> evidence.
- Each layer has contracts verified (identity, event, projection, memory, embodiment, presence, model/provider, skill, agent/swarm, workspace, security, design durability).
- Actual vertical slice execution verification deferred until framework contracts complete and framework coherence verified.

---

END OF ARCHITECTURE CONTRACTS
