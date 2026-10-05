# Context Bridge Roadmap

## Prototype definition

A prototype is complete when a bounded task can travel this loop with inspectable evidence:

intent -> context packet -> Hermes execution -> verification -> handoff -> updated context packet -> resumed execution.

The prototype must work without a transcript dump.

## Phase 0 — Freeze the boundary

1. Keep the bridge harness-neutral.
2. Treat ProjectSHURA's existing architecture as canonical.
3. Treat Holographic as retrieval/memory infrastructure, not the source of project truth.
4. Do not duplicate AGENTS.md, soul.md, or the existing task graph.
5. Use links/references to deeper documents rather than copying them into NOW.

Acceptance: the bridge has a clearly defined role and no competing source of truth.

## Phase 1 — Create the minimum context packet

Create SHURA_CONTEXT/ with:
- NOW.md — current state, 1–3 pages maximum.
- MISSION.md — current strategic objective.
- DECISIONS.md — only decisions that affect current work.
- PROJECT_INDEX.md — project/system map with status.
- WORKFLOW.md — current toolchain and operating loop.
- LANGUAGE.md — shared vocabulary.
- SESSION_HANDOFF.md — latest execution handoff.

Acceptance: a fresh Hermes session can orient itself from these files plus the canonical repository docs.

## Phase 2 — Add a machine-readable contract

Add one small schema, preferably YAML or JSON, for a context packet:
- version
- timestamp
- mission
- state
- decisions
- blockers
- next_task
- source_artifacts
- required_evidence
- verification
- changed_files
- unresolved

Acceptance: the same packet can be consumed by shell scripts, Hermes, VS Code tooling, or another harness without interpretation-specific prose.

## Phase 3 — Build the first bridge CLI

Provide three operations:
- context read — print the current packet.
- context handoff — validate and record a completed execution handoff.
- context resume — emit the smallest execution-ready task envelope for Hermes.

Keep the implementation local-first and dependency-light.

Acceptance: one command produces a clean Hermes-ready task envelope from the canonical packet.

## Phase 4 — Connect Holographic without making it authoritative

Use Holographic for retrieval of historical/contextual material when the packet points to it.

The bridge should store references and provenance, not silently promote retrieved memories into current state.

Acceptance: historical recall can enrich a task while current state remains explicit and inspectable.

## Phase 5 — VS Code integration

Expose the same packet and task envelope through the VS Code workflow.

Minimum useful surface:
- open current context
- open mission
- open next task
- inspect evidence
- update handoff

Do not build a custom dashboard before this workflow proves useful.

## Phase 6 — Hermes execution loop

Standardize the handoff envelope around the existing Hermes fleet contract:
- task id
- project
- stage
- role
- objective
- context
- constraints
- scope
- success criteria
- evidence
- expected outputs
- verification

Acceptance: Hermes can consume the envelope and return a normalized result without transcript reconstruction.

## Phase 7 — Evidence and review gate

After execution:
1. inspect changed files
2. run focused tests
3. run broader tests when shared contracts are affected
4. inspect diff
5. record evidence
6. classify assertions as proven/unproven/failed
7. update context

Acceptance: done means evidence exists, not that an agent said done.

## Phase 8 — Optional visual layer

Only after the file/CLI workflow is stable, add a small visual companion.

Candidate surfaces:
- FigJam architecture map
- VS Code Mermaid preview
- future ATLAS/Forge projection

The visual artifact must be generated from the portable source where practical, not become a second manually maintained architecture truth.

## Phase 9 — Expansion

Only after the prototype survives real use:
- event-driven synchronization
- richer memory provenance
- multi-project context routing
- agent fleet orchestration
- ATLAS projections
- conflict detection
- automated session close/open
- cross-device portability

## Prototype implementation sequence

1. Create SHURA_CONTEXT/.
2. Write the seven human-readable context files.
3. Define the machine-readable packet schema.
4. Write validator tests.
5. Implement context read.
6. Implement context resume.
7. Implement context handoff.
8. Run one real Aether Relay or ProjectSHURA task through the loop.
9. Capture evidence and a session handoff.
10. Verify a fresh Hermes session can resume from the packet alone.
11. Add VS Code navigation/preview.
12. Add Holographic retrieval as an optional enrichment path.
13. Review architecture and remove duplication.
14. Freeze v0 acceptance criteria.

## Timeline

Assuming focused work rather than the traditional human practice of opening seventeen tabs and calling it a workflow:

- 0–30 min: Phase 0 + Phase 1 structure and first packet.
- 30–90 min: Phase 2 schema + validator.
- 90–150 min: Phase 3 CLI.
- 2.5–4 h: real vertical slice through Hermes.
- 4–6 h: VS Code surface + Holographic enrichment.
- 6–8 h: review, hardening, documentation, and prototype acceptance.

The first functioning prototype should therefore be reachable in roughly one focused day, with a much smaller proof of concept in the first 90–150 minutes.

## Success metrics

- Context packet read time: under 60 seconds for a fresh agent.
- Resume task extraction: deterministic.
- No transcript dump required.
- No duplicate source of truth introduced.
- Every completed task has evidence.
- A fresh Hermes session can resume a task using the bridge plus canonical project references.
- The same packet remains readable outside Hermes.
