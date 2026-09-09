# ProjectSHURA Agent Contract

## Mission

You are contributing to ProjectSHURA, an extension of the ProjectBEA foundation. Preserve the existing single-brain architecture while adding modular capabilities around it.

## Operating rules

1. Inspect the relevant repository structure and source before changing code.
2. Prefer the smallest coherent change that advances the stated task.
3. Reuse existing interfaces, registries, events, perception, expression, and configuration pathways before creating parallel systems.
4. Keep SHURA identity/personality in prompt/persona/context layers. Do not hard-code personality into provider, transport, or external-tool code.
5. Keep external application control in dedicated adapters/MCPs, not in `src/core`.
6. Do not silently disable existing skills or change runtime defaults unless the task explicitly requires it.
7. Never commit API keys, tokens, passwords, private URLs, or other secrets.
8. Do not make irreversible or destructive repository/system changes without explicit authorization.

## Development workflow

For every substantive change:

```text
inspect
-> plan
-> implement
-> test
-> inspect diff
-> functional review
-> defensive security review
-> remediate
-> retest
-> summarize
```

## Release gate

A change is not release-ready when:

- required tests fail
- the changed behavior is not understood
- a high-confidence critical security issue remains
- secrets are present in the diff
- the implementation bypasses an existing safety/permission boundary

Human approval is required before an external git push for release work.

## Agent roles

Hermes is the primary orchestration layer.

Zed is the primary visual coding cockpit.

JCode, Crush, Pi, OpenCode, and other agents may be used selectively when they provide a concrete advantage. Avoid multi-agent work for its own sake.

## Architectural boundaries

- Core: identity, reasoning, memory/context, agency/orchestration, shared interfaces.
- Skills: user-facing or autonomous capabilities implemented through the existing skill system.
- MCP/adapters: control and integration with external tools/apps.
- Docs: contracts, decisions, architecture, runbooks, and acceptance criteria.

## Current development priority

1. Hermes + Zed development cockpit.
2. Coding execution/review/security release gate.
3. First practical creative bridge: Majik/ACESTEP -> REAPER.
4. SHURA Reader/Living Audiobook.
5. ATLAS/FORGE specification and red-team review.
6. Game development/worldbuilding mode.
7. INFAC community/cultural design work.

## Before adding a new subsystem

Answer:

- What exact problem does it solve?
- Why is it a skill, core component, or external adapter?
- What existing pathway can it reuse?
- What is the smallest useful v0.x implementation?
- What is explicitly out of scope until v1.0?
- How will it be tested and reviewed?
