# SHURA.ARC — ARCHITECTURAL ARCHAEOLOGY REPORT
Date: 2026-09-30
Auditor: SHURA via Hermes Agent
Repository: /Users/ultraviollett/projectSHURA
Branch: shura-foundation
Status at audit: 10 staged, 10 modified, 9 untracked

## 1. RUNTIME ARCHITECTURE
- Substrate: ProjectBEA fork (VTuber runtime + LLM/TTS/STT/OBS/avatar/memory/Discord/Minecraft)
- Identity kernel: ~/.hermes/SOUL.md (225 lines, v1) + docs/shura/SOUL.md (mirror)
- Agent layer: .hermes/skills/shura/ (routing layer, not identity replacement)
- Core runtime modules (verified present): src/core/brain.py, consciousness.py, events.py, expression.py, resources.py
- Skills: chat, memory (generator/memory/storage), dream (dreamer/recent/selflore/surface), voice, social, minecraft
- New/modified skills: infac/ (untracked), dream/consolidation.py (modified)

## 2. AGENT LOOP
- No autonomous agent loop fully verified. docs/operations/AUTONOMOUS_LOOP.md defines framework.
- docs/operations/LOOP_STATE.md and SESSION_HANDOFF.md exist (modified in git).
- Milestone framework (docs/tasks/V1_TASK_GRAPH.md) verified; autonomous loop execution (M1-T7) remains PROPOSED.

## 3. MODEL / PROVIDER ABSTRACTION
- src/core/llm/client abstraction present (openai_compat, openrouter_llm, groq_llm, factory, omniroute_llm).
- Config references `poolside/laguna-s-2.1:free` but session uses `thinkingmachines/inkling:free` via openrouter.
- Provider/model independence is a design intention (docs/shura/IDENTITY_MANIFEST.md) but not fully enforced in brain/consciousness internals.

## 4. HERMES INTEGRATION
- Hermes Agent v0.21.1 installed. Config at ~/.hermes/config.yaml (~155KB, 4057 lines).
- Plugin `superpowers` enabled (brainstorming, systematic-debugging, writing-plans, subagent-driven-development, etc.).
- Custom profile: shura. Memory/user profile enabled.
- Critical risk: MCP interpolation mismatch (`${MCP_...KEY}` vs `.env` variable name). Unverified connection to majiks-studio.

## 5. IDENTITY / PROMPT ARCHITECTURE
- Layer separation verified: SOUL.md (identity) ≠ OPERATING.md (behavior) ≠ skills (context).
- AGENTS.md defines repository rules, not identity.
- Identity independence preserved in design; no provider/model coupling found in SOUL.md content.

## 6. MEMORY SYSTEMS
- src/core/memory/storage.py, generator.py exist.
- Memory consolidation framework present (docs/MEMORY_CONSOLIDATION.md, docs/operations/LOOP_STATE.md).
- tests/test_memory_consolidation.py exists (not executed in this audit).
- Memory retrieval != autobiographical continuity (design constraint, verified in IDENTITY_MANIFEST.md).

## 7. SKILL SYSTEMS
- Skill base at src/skills/base.py. Chat, idle, donation skills present.
- Dream skill (skills/dream/): dreamer, recent, selflore, surface, consolidation, domain, events, projection, transaction.
- Social skill (skills/social/): people, roster.
- Minecraft skill (skills/minecraft/): client, notebook, surface, tools.
- Voice skill (skills/voice/): surface, transport, bot.

## 8. MCP / TOOL INFRASTRUCTURE
- docs/reference/ADR_INDEX.md, OPEN_QUESTIONS.md present.
- docs/INTEGRATION_MATRIX.md present.
- ReaScript-based REAPER adapter planned; binary at /Applications/REAPER.app. No headless CLI verified.
- ACE Studio binary verified (/Applications/ACE Studio.app); MCP integration requires GUI enable.

## 9. FORGE
- src/core/forge/contract.py exists.
- docs/forge/FORGE_BOUNDARY.md present.
- Forge is synthesis/audit layer, separate from ATLAS (historical) and projectSHURA (runtime).

## 10. ATLAS
- src/core/atlas/models.py, repository.py, service.py exist.
- docs/atlas/ATLAS_BOUNDARY.md present.
- ATLAS is historical/project-level repository, separate from runtime state.

## 11. PRESENCE SYSTEMS
- src/core/presence/ (events, projection, runtime, __init__) verified.
- docs/design/SHURA_PRESENCE.md, SHURA_EMBODIMENT.md present.
- Presence projection must remain renderer-agnostic (verified in design contracts).

## 12. PERSISTENCE / DATABASE
- data/events/events.jsonl modified (JSON Lines format suspected).
- .crush/crush.db (Crush framework) separate from SHURA state.
- No SQLite schema migration file found for new event log; initial schema required.

## 13. EVENT / LOG SYSTEMS
- src/core/events.py present (EventManager with publish/get_events).
- docs/EVENT_CONTRACT.md present (must remain intact).
- Dream events at src/core/dream/events.py; projection at projection.py.
- Event taxonomy exists; new events must follow it (verified in design contracts).

## 14. UI / FRONTEND
- src/web/frontend/ (React + Vite + Tailwind).
- Components: embodiment/Viewer.jsx, forge/PresentationAdapter.jsx, SHURAPresenceDisplay.jsx, ActivityFeed.jsx.
- Command Center UI framework verified (docs/design/COMMAND_CENTER_V1.md); implementation partial.

## 15. TESTS
- test_events.py, test_memory_consolidation.py, test_dream_projection.py, test_brain_presence_architecture.py, test_forge_ui_harness.py, test_infac_domain.py.
- test_dream_projection.py verifies projection does not mutate domain (load-bearing).
- No automated test executed in this audit session; manual inspection only.

## 16. CONFIGURATION
- Project config: pyproject.toml (Python 3.11+), Makefile (uv).
- Hermes profile: shura (custom skills directory).
- .env: MCP keys, custom provider keys. No secrets committed in git.

## 17. DEPLOYMENT
- Deployment not part of this audit scope. Existing infrastructure (OBS, REAPER, ACE Studio, Majik) remains functional.

## 18. COMPONENT CLASSIFICATION
- brain.py: FOUNDATIONAL — must be preserved, not rewritten
- consciousness.py: FOUNDATIONAL — identity/cognition layer
- events.py: FOUNDATIONAL — event contract load-bearing
- memory/storage.py: FOUNDATIONAL — persistence interface
- dream/: FOUNDATIONAL — projection boundary verified
- skills/: FOUNDATIONAL — capability layer
- presence/: REUSABLE — projection/runtime interface
- forge/contract.py: REUSABLE — synthesis contract
- atlas/: REUSABLE — historical repository
- infac/ (untracked): UNCLEAR — requires reconciliation with arc boundaries
- web/frontend/: PRESENTATION — must observe state via events/projections
- .crush/: SEPARATE — Crush framework, not SHURA core
- Shura/ (older path): RETIREMENT CANDIDATE — supersede with SHURA_CURRENT_STATE.md
