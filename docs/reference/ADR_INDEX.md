# ADR Index — Architecture Decision Records

Status: Framework initialized; updated by autonomous loop when architecture decisions made.
Every entry must reference design framework (`docs/design/`), milestone framework (`docs/tasks/V1_ROADMAP.md`), verification evidence, and must not restructure framework without documentation.

---

## ADR-001: OpenHuman Reference — Selective Reimplementation Over Direct Fork

Status: PROPOSED (design recommendation; verified by file inspection and reference analysis)

Context:
- OpenHuman reference artifact (`tinyhumansai/openhuman`) ingested (`docs/reference/OPENHUMAN_REFERENCE.md`).
- Artifact is 50,358,637 bytes, 1,309,666 lines; contains React/Vite frontend, Rust backend, agent/task/workflow framework, workspace surfaces.
- ProjectSHURA requires portable identity (`data/prompts/soul.md`), modular cognition (`brain.py` / `consciousness.py` / `expression.py`), event/projection boundary (`src/core/dream/projection.py`), and workspace framework (`docs/design/COMMAND_CENTER_V1.md`).

Decision (Selective Reimplementation — Option B from `docs/design/FORK_STRATEGY.md`):
- Do NOT directly import OpenHuman code into ProjectSHURA (would couple identity to foreign framework, violate identity independence, and create maintenance burden).
- Do NOT treat OpenHuman as authoritative source of truth (validated by architecture audit: identity independence, projection boundary, modular skills are ProjectSHURA-specific and must be preserved).
- REIMPLEMENT selected concepts (workspace surfaces framework, agent/task observation framework, skill registry visibility, event feed, workspace persistence mechanism framework) in ProjectSHURA's design framework, observing existing event/projection interfaces and preserving identity independence.
- DEFER full workspace shell, full agent execution framework, full memory integration, Live2D/3D embodiment upgrade, full ATLAS operational layer, full Dream Transaction pipeline, full autonomous loop execution.

Consequences:
- Workspace framework (`docs/design/COMMAND_CENTER_V1.md`) remains durable; future workspace surfaces can be added without restructuring framework.
- Design framework (`docs/design/`) must remain complete; any ambiguity must become ADR entry or open question (`docs/reference/OPEN_QUESTIONS.md`).
- Reference framework (`docs/reference/`) must include `OPENHUMAN_REFERENCE.md`, `OPENHUMAN_TO_FORGE.md`, `FORK_STRATEGY.md`.
- No identity divergence allowed; no secret exposure allowed; no Dream boundary collapse; projection layer (`tests/test_dream_projection.py`) must remain read-only; event contract (`docs/EVENT_CONTRACT.md`) must be preserved.

Verification Evidence:
- File inspection: `docs/reference/OPENHUMAN_REFERENCE.md` present; `docs/reference/OPENHUMAN_TO_FORGE.md` present; `docs/design/FORK_STRATEGY.md` present; `docs/design/ARCHITECTURE_MAP.md` verified; `docs/design/SHURA_EMBODIMENT.md` verified; `docs/design/COMMAND_CENTER_V1.md` verified.
- Boundary verification: `tests/test_dream_projection.py` 11 passing (read-only verified by `test_projection_does_not_mutate_domain`); projection does not import brain/consciousness/expression for mutation logic.
- Identity verification: `data/prompts/soul.md` unchanged (`git diff -- data/prompts/soul.md` empty); `.env` unchanged; identity independent of provider/model/avatar (`docs/design/SHURA_EMBODIMENT.md` contract verified).
- Design framework durability: `docs/design/` complete; framework allows future workspace surfaces framework expansions; framework allows future workspace persistence mechanism; framework allows future workspace interaction framework expansions; framework allows future workspace framework expansions.

Related:
- Milestone 0 (verified): Design framework established.
- Milestone 1 (in progress): Workspace framework implementation framework (`docs/design/COMMAND_CENTER_V1.md`); workspace adapter endpoint (`/workspace/dream-events`) verified by `tests/test_workspace_events.py`.
- Milestone 2 (deferred): Full workspace surfaces (Dream Studio full, Memory workspace, Agents workspace, Skills workspace, MCP workspace, Artifacts workspace, Activity workspace, System workspace) deferred to milestone-based autonomous execution.
- Milestone 3-7 (deferred): Dream Studio full, Memory/Context integration, Agents/Tasks/MCP integration, Embodiment/Workspace polish, V1 Prototype validation.

---

## ADR-002: Tamanitomo Reference — Architectural Lessons (Reference Only, No Code Reuse)

Status: PROPOSED (architectural knowledge integration; not implementation)

Context:
- Tamanitomo (`https://github.com/tamanitomo/tamanitomo`) is a sovereign/self-hosted AI companion built on Hermes Agent.
- Licensed under PolyForm Noncommercial 1.0.0 — no source code copied, forked, or vendored.
- Repository treated as architectural/reference source.

Decision (Reference Only — Architectural Lessons):
- ADOPT: Authoritative ledger → projections → presentation (reinforces existing `event → projection → presentation`)
- ADOPT: Append-only history (already implemented in `EventJournal`)
- ADOPT: Rules belong in code (prompts are not authoritative policy)
- ADOPT: Identity and boundaries have different mutability (already protected)
- ADOPT: SHURA ≠ Hermes (already enforced via ABCs and factory pattern)
- ADAPT: Provenance vocabulary (add when memory architecture matures)
- ADAPT: Outbox pattern (design for future proactive messaging)
- ADAPT: Stale/unknown state distinction (extend `PresenceState` when sensors added)
- ADAPT: Unconfirmed state (add confirmation timestamp to presence)
- ADOPT: Autonomy fingerprinting (add change detection to avoid redundant model calls)
- REFERENCE: Git-backed recovery (idea worth remembering; not justified until state format stabilizes)
- REJECT: Multi-companion roster (contradicts single-identity architecture)
- REJECT: Git auto-commit as state mechanism (conflates version control with state persistence)
- REJECT: Vault as primary knowledge store (ATLAS is projection layer, not second brain)
- REJECT: Tamanitomo presence loop design (SHURA has its own presence architecture)

Consequences:
- `docs/reference/TAMANITOMO_REFERENCE.md` created as durable architectural reference
- No code changes; no identity changes; no boundary changes
- Future sessions can consult the reference without re-deriving lessons from source

Verification Evidence:
- File inspection: `docs/reference/TAMANITOMO_REFERENCE.md` present
- Boundary verification: `tests/test_dream_projection.py` 11 passing; `tests/test_events.py` 22 passing; `tests/test_dream_engine.py` 15 passing
- Identity verification: `data/prompts/soul.md` unchanged; `.env` unchanged
- No secret exposure; no C4 retry; no forbidden coupling

Related:
- Milestone 1 (M1-T10): Tamanitomo knowledge integration — documentation task
- `docs/reference/TAMANITOMO_REFERENCE.md` — full comparison matrix and principles

---

## ADR Reference Rules

Every future ADR entry must:
1. Reference the design framework (`docs/design/` files relevant).
2. Reference verification evidence (test module, endpoint, file inspection, boundary verification).
3. Confirm identity preservation (`data/prompts/soul.md` unchanged or identity sync documented).
4. Confirm Dream/event/projection boundary preserved (`tests/test_dream_projection.py` passing; projection read-only; event contract preserved).
5. Confirm no secret exposure (`.env` unchanged; `.hermes/config.yaml` line 4041 unchanged — C4 BLOCKED; not retried; not bypassed).
6. Confirm workspace framework durability (`docs/design/COMMAND_CENTER_V1.md` framework preserved; future expansions allowed without restructuring).
7. Include milestone framework reference (`docs/tasks/V1_ROADMAP.md` milestone; dependency relationships preserved).
8. Be updated by autonomous loop (`docs/operations/AUTONOMOUS_LOOP.md` protocol preserved; loop state updated; session handoff updated; bounded task completed safely; loop stops safely).
