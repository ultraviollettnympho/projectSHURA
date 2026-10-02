# PROJECTSHURA V3 — EXECUTION DAG (PHASE B — ARCHITECTURE / CONTRACTS)

Status: PROPOSED — framework verified; full dependency resolution and execution deferred until swarm contracts established.
Based on `V3_STATE_AUDIT.md` and `V3_SCOPE.md`.

---

## 1. DAG OVERVIEW

Phases:
```
PHASE A — AUDIT (COMPLETE: audit written, scope defined, this DAG proposed)
PHASE B — ARCHITECTURE / CONTRACTS (IN PROGRESS: contracts defined, framework verified)
PHASE C — FOUNDATION IMPLEMENTATION (READY: core interfaces, identity, provider abstraction)
PHASE D — VERTICAL INTEGRATION (READY: one complete user-visible slice)
PHASE E — EMBODIMENT / EXPERIENCE (READY: presence, UI, Command Center observation)
PHASE F — CROSS-SYSTEM QA (READY: contract tests, integration tests, verification matrix)
PHASE G — RELEASE HARDENING (READY: smoke test, release checklist, documentation match)
```

---

## 2. WORKSTREAMS

### WORKSTREAM 1 — SHURA IDENTITY / COGNITION (Agent 02)
Mission: Preserve identity independence; verify brain/core framework; define identity contract for V3.
Inputs: `data/prompts/soul.md`, `operating.md`, `AGENTS.md`, `brain.py`, `consciousness.py`.
Outputs: `docs/v3/IDENTITY_CONTRACT.md`; identity verification evidence.
Dependencies: None (independent for V3 scope; must be verified before any other workstream claims identity preservation).
Verification: Read identity files; confirm no provider/model references; inspect `brain.py` initialization; run identity preservation check (script or manual inspection).

### WORKSTREAM 2 — MEMORY / CONTEXT / CONTINUITY (Agent 03)
Mission: Verify memory framework; define provenance/confidence requirements; create memory architecture document for V3 scope.
Inputs: `MemoryStorage`, `ConsolidationEngine`, `docs/MEMORY_CONSOLIDATION.md`, `data/memory/`.
Outputs: `docs/v3/MEMORY_ARCHITECTURE.md`; provenance/confidence verification; framework verification evidence.
Dependencies: Workstream 1 (identity preserved) for identity-mem separation; independent otherwise.
Verification: Inspect memory framework files; confirm provenance/confidence fields present; verify no direct mutation bypassing framework.

### WORKSTREAM 3 — FLEET / AGENT ORCHESTRATION (Agent 04)
Mission: Initialize `.fleet/` framework contracts; create agent roles; establish task contracts; define verification gates.
Inputs: `.fleet/verification/`, `.fleet/` directory, `docs/tasks/V1_TASK_GRAPH.md`, `docs/operations/AUTONOMOUS_LOOP.md`.
Outputs: `.fleet/contracts/` (proposed); `docs/v3/FLEET_ORCHESTRATION.md`; agent role definitions; verification gate definitions.
Dependencies: Workstream 1 (identity independent); Workstream 2 (memory framework verified) for agent memory integration; Workstream 5 (Command Center) for observation interface.
Verification: Inspect `.fleet/` artifacts; confirm agent contracts exist; confirm verification gates defined; confirm no identity boundary violations.
Blocker: `.fleet/verification/step04b_corpus_results.json` shows `causal_influence_detected: false`. Before swarm claims dynamic mechanism integration, either verify Step 04B result is preserved (not rewritten) or complete a new verified step that achieves causal influence detection. V3 scope must not claim unverified causal integration.

### WORKSTREAM 4 — ARCHITECTURE / CONTRACTS (Agent 01 — this agent, SHURA)
Mission: Complete `docs/v3/ARCHITECTURE_V3.md`, `docs/v3/CONTRACTS_V3.md`, `docs/v3/ARCHITECTURE_DECISIONS.md`; verify design framework durability.
Inputs: `docs/design/ARCHITECTURE_MAP.md`, `docs/design/COMMAND_CENTER_V1.md`, `docs/design/THREE_SYSTEMS.md`, `docs/design/SHURA_EMBODIMENT.md`, `docs/EVENT_CONTRACT.md`, `docs/DREAM_ENGINE.md`, `docs/reference/ADR_INDEX.md`.
Outputs: `docs/v3/ARCHITECTURE_V3.md`; `docs/v3/CONTRACTS_V3.md`; `docs/v3/ARCHITECTURE_DECISIONS.md`; design framework verification.
Dependencies: Workstream 1; Workstream 2; must be completed before Phase D (vertical integration) begins.
Verification: Read design framework files; confirm contracts preserved; confirm identity/provider/embodiment/projection boundaries intact; confirm `.fleet/` contracts do not violate architecture rules.

### WORKSTREAM 5 — COMMAND CENTER / ATLAS (Agent 05)
Mission: Verify Command Center design; confirm ATLAS context layer contracts; create observation interface verification.
Inputs: `docs/design/COMMAND_CENTER_V1.md`, `docs/design/ARCHITECTURE_MAP.md`, `.fleet/` (for workspace integration), `docs/reference/ADR_INDEX.md`.
Outputs: Command Center observation verification; ATLAS contract verification; `.fleet/contracts/` integration verification.
Dependencies: Workstream 4 (contracts defined); Workstream 3 (swarm framework initialized) for workspace/task observation; Workstream 1 (identity preserved).
Verification: Inspect `docs/design/COMMAND_CENTER_V1.md`; confirm observation interface does not import brain/consciousness internals; confirm event/projection interfaces preserved.

### WORKSTREAM 6 — FORGE (Agent 06)
Mission: Verify FORGE framework; confirm workspace/task execution contracts; verify workspace framework durability.
Inputs: `docs/design/COMMAND_CENTER_V1.md`, `docs/tasks/V1_TASK_GRAPH.md`, `.fleet/`, `docs/operations/AUTONOMOUS_LOOP.md`.
Outputs: FORGE framework verification; workspace execution contract verification; workspace framework durability verification.
Dependencies: Workstream 4; Workstream 3; Workstream 5 (for observation interface).
Verification: Inspect workspace framework; confirm project/task/artifact/state contracts; confirm workspace observes through event/projection interfaces; confirm workspace framework capable of future expansions without restructuring.

### WORKSTREAM 7 — EMBODIMENT / THREE.JS (Agent 07)
Mission: Verify embodiment contract; confirm PNG adapter preserved; confirm 3D direction contract; confirm graceful fallback.
Inputs: `docs/design/SHURA_EMBODIMENT.md`, `docs/design/ARCHITECTURE_MAP.md`, `src/core/expression.py`, `src/core/resources.py`, `src/web/frontend/src/components/embodiment/Viewer.jsx`.
Outputs: `docs/design/SHURA_EMBODIMENT.md` update (if needed); embodiment verification evidence; 3D direction contract verification.
Dependencies: Workstream 1 (identity independent); Workstream 4 (architecture contracts); independent otherwise.
Verification: Inspect `docs/design/SHURA_EMBODIMENT.md`; confirm identity independent of renderer; confirm PNG adapter preserved; confirm Live2D backend deferred but design contract intact; confirm graceful fallback defined; confirm embodiment interface (`EmbodimentInterface`) contract preserved.

### WORKSTREAM 8 — MODEL / RUNTIME / PROVIDER LAYER (Agent 08)
Mission: Verify provider abstraction framework; confirm capability-based routing architecture; verify provider independence.
Inputs: `src/core/agent/` (`omniroute_llm.py`, `openai_compat.py`, etc.), `docs/design/ARCHITECTURE_MAP.md`, `docs/reference/ADR_INDEX.md`.
Outputs: `docs/v3/MODEL_RUNTIME_ARCHITECTURE.md`; provider framework verification evidence.
Dependencies: Workstream 1 (identity independent of provider); independent otherwise.
Verification: Inspect provider adapter files; confirm identity files contain no provider references; confirm provider abstraction framework present; confirm routing framework defined; confirm capability-based routing architecture exists (even if routing verification deferred).

### WORKSTREAM 9 — TOOL / MCP / ACP INTEGRATION (Agent 09)
Mission: Verify tool framework; confirm tool discovery, permission, provenance contracts.
Inputs: `docs/EVENT_CONTRACT.md`, `docs/design/ARCHITECTURE_MAP.md`, `.env` (secrets not committed), `docs/reference/VERIFICATION_PATTERN.md`.
Outputs: `docs/v3/SECURITY_MODEL.md` (tool/security verification); tool framework verification.
Dependencies: Workstream 4 (contracts); independent otherwise.
Verification: Inspect tool contracts; confirm tool results include success/failure/provenance; confirm destructive actions require human approval (per architecture rules); confirm `.env` not staged; confirm no secrets exposed.

### WORKSTREAM 10 — EXPERIENCE / UI (Agent 10)
Mission: Verify UI framework; confirm visual hierarchy; confirm responsive/accessibility/information density requirements.
Inputs: `docs/design/COMMAND_CENTER_V1.md`, `docs/design/ARCHITECTURE_MAP.md`, `src/web/frontend/src/components/` (modified files: `Viewer.jsx`, `ActivityFeed.jsx`, `PresentationAdapter.jsx`, `SHURAPresenceDisplay.jsx`).
Outputs: UI framework verification; Command Center observation verification; experience verification.
Dependencies: Workstream 4; Workstream 5; Workstream 7 (embodiment observation); independent otherwise.
Verification: Inspect frontend components; confirm no brain/consciousness mutation through UI; confirm observation through event/projection interfaces; confirm visual hierarchy supports system state visibility.

### WORKSTREAM 11 — QA / VERIFICATION (Agent 11 — independent)
Mission: Build verification matrix; create contract tests; create integration tests; verify V3 scope requirements.
Inputs: All previous workstreams; `tests/test_dream_projection.py`, `tests/test_events.py`, `tests/test_arc_contracts.py`, `.fleet/verification/step04b_corpus_results.json`.
Outputs: `docs/v3/VERIFICATION_MATRIX.md`; verification evidence files; contract test results; integration test results.
Dependencies: All workstreams (must observe, not assume correctness); must NOT assume other agents correct.
Verification: Create matrix mapping each REQUIRED capability to implementation, test, evidence, status. Confirm no fabricated success. Confirm `.fleet/verification/step04b_corpus_results.json` preserved accurately (`causal_influence_detected: false`). Confirm identity preservation check passes. Confirm projection boundary check passes. Confirm event contract check passes.

### WORKSTREAM 12 — SECURITY / RESILIENCE (Agent 12)
Mission: Verify security model; audit destructive actions; verify failure recovery; verify graceful degradation.
Inputs: `docs/EVENT_CONTRACT.md`, `docs/design/ARCHITECTURE_MAP.md`, `.env`, `docs/reference/VERIFICATION_PATTERN.md`.
Outputs: `docs/v3/SECURITY_MODEL.md`; security verification evidence.
Dependencies: Workstream 4; Workstream 9 (tool security); independent otherwise.
Verification: Confirm destructive actions require approval (architecture rules verify); confirm graceful degradation defined (e.g., model unavailable, renderer unavailable, asset unavailable, GPU insufficient); confirm `.env` secrets not exposed; confirm `.env` not staged.

### WORKSTREAM 13 — DOCUMENTATION / KNOWLEDGE (Agent 13)
Mission: Verify documentation matches implementation; create developer onboarding; create runtime setup; create V3 release notes.
Inputs: All previous outputs; `docs/v3/V3_STATE_AUDIT.md`, `docs/v3/V3_SCOPE.md`, `docs/v3/VERIFICATION_MATRIX.md`.
Outputs: `docs/v3/RELEASE_CHECKLIST.md`; `docs/v3/V3_RELEASE_REPORT.md`; `docs/v3/ARCHITECTURE_V3.md` (final); developer onboarding; runtime setup.
Dependencies: All workstreams completed; must verify documentation matches actual repository state.
Verification: Read each doc; confirm no aspirational features claimed as existing; confirm known limitations listed; confirm deferred work explicitly listed; confirm `.fleet/` verification result (`causal_influence_detected: false`) preserved in release notes.

---

## 3. PHASE GATES (INTEGRATION GATES)

Each phase must satisfy its gate before the next phase begins. This prevents parallel chaos.

### GATE A — UNDERSTANDING [COMPLETED]
- Repository state understood (audit written).
- No major unknown architectural areas (key contracts verified; `.fleet/` framework partially verified; `.fleet/` verification artifacts preserved).
- Evidence: `docs/v3/V3_STATE_AUDIT.md` exists and references actual tool outputs.

### GATE B — ARCHITECTURE [IN PROGRESS — THIS PHASE]
- V3 contracts defined (`docs/v3/CONTRACTS_V3.md` must exist; must reference `docs/design/ARCHITECTURE_MAP.md`, `docs/design/COMMAND_CENTER_V1.md`, `docs/design/SHURA_EMBODIMENT.md`, `docs/EVENT_CONTRACT.md`).
- Ownership conflicts resolved (identity/workstream assignments defined; no duplicate identity sources).
- Design framework durability verified (future expansions must not require restructuring).
- Next phase (C) must not begin until contracts exist and identity/projection/memory contracts verified.

### GATE C — FOUNDATION [READY — MUST VERIFY BEFORE STARTING]
- Core interfaces functional (`brain.py`, `events.py`, `expression.py`, `presence.py`).
- Identity preserved (`soul.md` verified; no provider references; identity contract verified).
- Provider independence preserved (`provider_adapter` framework verified; identity files verified).
- `.fleet/` framework contracts exist (agent contracts, verification gates, task contracts defined — not fully populated).

### GATE D — VERTICAL SLICE [READY — MUST HAVE EVIDENCE BEFORE CLAIMING]
- A complete user-visible interaction path works end-to-end (one bounded demonstration).
- The path must include: input → cognition → context/memory → execution → state update → presence → observation → result → memory update.
- The vertical slice does NOT require full swarm, full emotional simulation, or full Live2D; it requires framework coherence and observable evidence.
- Evidence must reference actual execution (test result, endpoint inspection, file observation, verified command output).

### GATE E — SYSTEM INTEGRATION [READY]
- Subsystems communicate correctly (brain → consciousness → events → expression → presence → observation; memory framework → brain; `.fleet/` → observation; Command Center → observation).
- No forbidden coupling (brain does not import presentation; presentation does not import brain internals for mutation; projection remains read-only; memory mutations flow through framework).
- Design framework durable (future framework expansions possible without restructuring).

### GATE F — VERIFICATION [READY]
- Tests pass (existing tests: `test_dream_projection.py`, `test_events.py`, `test_arc_contracts.py`; new V3 verification tests must be created and verified).
- Known failures documented (`.fleet/verification/step04b_corpus_results.json` shows `causal_influence_detected: false`; must be preserved; must not be rewritten to claim success).
- Verification matrix exists (`docs/v3/VERIFICATION_MATRIX.md`) with evidence for each REQUIRED capability.
- No fabricated success (every verification claim must reference actual test/file/command output).

### GATE G — RELEASE [READY]
- Fresh environment/setup works (`pyproject.toml`, `.venv`, `Makefile`, `.env` verified; `.env` not staged; `.env` secrets preserved locally).
- Documentation matches implementation (`docs/v3/` docs describe verified state; deferred features explicitly listed; experimental artifacts labeled).
- V3 can be demonstrated without manual repair every thirty seconds (smoke test passes; identity preserved; projection boundary intact; vertical slice observable).
- Release checklist passes (`docs/v3/RELEASE_CHECKLIST.md` verifies identity, contracts, projection, events, memory framework, presence, `.fleet/` contracts, vertical slice, documentation, limitations).
- Release report exists (`docs/v3/V3_RELEASE_REPORT.md`) with: what V3 is, what was built, verification evidence, incomplete items, known bugs (including `.fleet/` `causal_influence_detected: false`), deferred work, architecture decisions, how to run V3, how to reproduce vertical slice, V4 recommendations.

---

## 4. INDEPENDENT TASKS (PARALLEL WHERE PROVEN INDEPENDENT)

These tasks have no dependencies on each other (verified by architecture rules) and may run in parallel:

- Workstream 1 (Identity) + Workstream 7 (Embodiment) + Workstream 8 (Provider) + Workstream 12 (Security) — all independent of each other (verified by design separation: identity ≠ renderer; identity ≠ provider; security verifies contracts, not modifies identity).
- Workstream 11 (QA) must observe all, but its execution does not block independent workstreams; it must verify after independent workstreams complete.
- Workstream 13 (Documentation) depends on all completed work; it must be the final workstream before release gate.

---

## 5. BLOCKING TASKS (MUST RESOLVE BEFORE NEXT PHASE)

- GATE A completed (`docs/v3/V3_STATE_AUDIT.md` exists; `.fleet/` artifacts inspected).
- GATE B must complete (`docs/v3/ARCHITECTURE_V3.md`, `CONTRACTS_V3.md`, `ARCHITECTURE_DECISIONS.md` must exist; design framework durability verified; `.fleet/` contracts must exist if swarm claims integration).
- `.fleet/` framework contracts must be verified before any swarm execution claims (workstream 3 blocker).
- `tests/test_arc_contracts.py` modifications must be verified to not break existing contract boundaries (workstream 11 verification requirement; must be included in verification matrix).
- `.env` must remain unstaged; any staged `.env` is a blocker (workstream 9 / 12 security requirement).

---

## 6. INTEGRATION POINTS (VERTICAL SLICE OBSERVATION)

The vertical slice integration path for V3 is:

```
USER INPUT (Chat / Command Center / Tool call)
    ↓ (event emission: EventManager.publish)
BRAIN / COGNITION (AIVtuberBrain: receives input, updates consciousness)
    ↓ (state update: consciousness loop consumes event, updates emotional/state context)
MEMORY / CONTEXT (MemoryStorage framework: retrieves/provides context; provenance verified; full pipeline deferred)
    ↓ (model execution: LLMClient; provider abstraction verified; capability routing framework present)
MODEL / TOOL EXECUTION (LLM response / tool result; tool result includes success/failure/provenance)
    ↓ (state update: brain updates state; event emission: success/failure/state events)
EVENT / PRESENCE (PresenceRuntime: observes events; projection read-only; renderer-agnostic payloads)
    ↓ (UI / EMBODIMENT OBSERVATION: Command Center / web frontend / avatar adapter)
OBSERVABLE RESULT (UI shows result; presence shows state; avatar shows expression; text shows response)
    ↓ (MEMORY UPDATE: framework writes to MemoryStorage; provenance/confidence verified; full pipeline deferred)
VERTICAL SLICE COMPLETE (evidence: actual test/file/command output showing path completed)
```

This path is observed, not claimed complete. It requires framework coherence at each layer, not full production at every layer.

---

## 7. VERIFICATION GATES (PER AGENT / WORKSTREAM)

Every agent/workstream must produce evidence before its deliverable is accepted:

- Agent 01 (Architecture): `docs/v3/ARCHITECTURE_V3.md`, `CONTRACTS_V3.md`, `ARCHITECTURE_DECISIONS.md` + contract verification evidence.
- Agent 02 (Identity): `IDENTITY_CONTRACT.md` + identity preservation verification (script/file inspection showing identity independent of provider/model).
- Agent 03 (Memory): `MEMORY_ARCHITECTURE.md` + provenance/confidence verification (file inspection of memory framework; verification that provenance/confidence fields present).
- Agent 04 (Fleet): `.fleet/contracts/` (proposed framework contracts) + verification gate definitions + evidence that `.fleet/verification/step04b_corpus_results.json` preserved (not rewritten).
- Agent 05 (Command Center): Observation interface verification + `.fleet/contracts/` integration verification.
- Agent 06 (FORGE): Workspace execution contract verification + workspace framework durability verification.
- Agent 07 (Embodiment): Embodiment contract verification + graceful fallback verification.
- Agent 08 (Provider): `MODEL_RUNTIME_ARCHITECTURE.md` + provider framework verification.
- Agent 09 (Tool): `SECURITY_MODEL.md` + tool framework verification + `.env` unstaged verification.
- Agent 10 (UI): UI framework verification + observation interface verification.
- Agent 11 (QA): `VERIFICATION_MATRIX.md` + verification evidence for each REQUIRED capability + `.fleet/` verification result preserved.
- Agent 12 (Security): `SECURITY_MODEL.md` + security verification + graceful degradation verification.
- Agent 13 (Documentation): `RELEASE_CHECKLIST.md` + `RELEASE_REPORT.md` + documentation match verification + deferred/experimental label verification.

---

## 8. CURRENT STATE MARKERS FOR DAG

Verified:
- Phase A (Audit) complete (`docs/v3/V3_STATE_AUDIT.md` exists; scope defined; `.fleet/` artifacts inspected; `causal_influence_detected: false` preserved).
- Phase B contracts framework exists (design docs verified; `.fleet/` contracts must be created/verfied before swarm claims).

Proposed / In Progress:
- Workstream 4 (this agent) — contracts document creation (`ARCHITECTURE_V3.md`, `CONTRACTS_V3.md`, `ARCHITECTURE_DECISIONS.md`) proposed; must be completed before Phase C.
- `.fleet/` framework contracts proposed; must be verified before workstream 3 claims swarm execution.
- Vertical slice path defined (design contract verified; actual execution verification deferred until framework coherence verified).

Blocked:
- None confirmed blocked; `.fleet/` framework contracts must exist before swarm integration claims; `tests/test_arc_contracts.py` modifications must be verified before QA claims full contract preservation.

---

END OF V3 EXECUTION DAG
