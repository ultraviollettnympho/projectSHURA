---
name: shura.arc-foundation
description: "Transform ProjectSHURA repository into initial shura.arc cognitive architecture — full Phase 1-8 per user directive."
date: 2026-09-30
path: architectural
design_document: this-file
---

# Design Spec — shura.arc Phase 1 Foundation

## Source / Approval
Design derived from user directive pasted 2026-09-30 (`pasted_content_...`). User approved full Phase 1-8 sequence (Option B) via clarify.

## Scope
ProjectSHURA remains the substrate (ADR-001). shura.arc is the cognitive architecture layer built within it (ADR-002).

## Key Constraints (from directive)
- Identity independent of provider/model/renderer (ADR-005, ADR-006)
- Consciousness claims = OPEN RESEARCH QUESTIONS, not architectural requirements (ADR-008)
- Canonical history = append-only event log; derived state reconstructable (ADR-003, ADR-004)
- Presentation must not own cognitive state (ADR-007)
- Self-modification staged and reversible (ADR-010)
- Existing ProjectSHURA functionality preserved (tests pass, skills intact, brain/consciousness/event systems untouched except for adapter interfaces)

## Module Boundaries (Phase 4 — initial, not all implemented)
`arc/` contains: `identity/`, `state/`, `events/`, `memory/`, `provenance/`, `observer/`, `coherence/`, `affect/`, `drives/`, `attention/`, `action/`, `consolidation/`, `self_model/`, `governance/`, `evaluation/`, `runtime/`.

Only the boundary directories and interface contracts are required for this phase. Full module implementations deferred.

## Contracts (Phase 5 — minimal initial set)
1. CognitiveState  2. Event  3. MemoryRecord  4. ProvenanceRecord  5. Observation  6. SelfModel  7. AffectiveState  8. DriveState  9. ActionProposal  10. GovernanceDecision
Every field must have a reason; no speculative fields.

## Event Schema (Phase 3 — initial)
Required fields: event_id, timestamp, source, actor, event_type, payload, provenance, confidence, causal_parent, session_context_id, schema_version.
Append-only. No mutation of canonical history.

## Milestone (Phase 8 — first testable)
"Birth test" — 10-point verification:
1. SHURA starts. 2. Identity loaded. 3. Cognitive event occurs. 4. Event written to canonical history. 5. Derived state updated. 6. Reconstruction from history works. 7. Retrieval of relevant history works. 8. Provider/model swap does not destroy identity/state. 9. Provenance exposed for retrieved state. 10. Existing ProjectSHURA functionality intact.

## Uncertainties Documented
- The exact interface between new `arc/` events and existing `src/core/events.py` is not fully defined; adapter approach preferred over replacement.
- Dream projection boundary (`docs/DREAM_ENGINE.md`) must remain intact; arc observer must observe via events/projections, not import brain/consciousness internals for mutation.
- Workspace framework durability (`docs/operations/AUTONOMOUS_LOOP.md`) must not be compromised by new module structure.
- The `infac/` domain (new untracked directory) is not yet reconciled with arc boundaries.

## Non-Goals for This Phase
- Full consciousness implementation (open research question).
- Replacement of brain/consciousness/event core.
- Rewriting Hermes integration.
- New avatar/renderer systems.
- Full database migration (only schema definition required).
