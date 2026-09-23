# Tamanitomo Architectural Reference — Lessons for ProjectSHURA

Status: REFERENCE (architectural knowledge integration; not source of truth for ProjectSHURA implementation)
Source: `https://github.com/tamanitomo/tamanitomo` (sovereign, self-hosted AI companion built on Hermes Agent)
License constraint: Tamanitomo is licensed under **PolyForm Noncommercial 1.0.0**. This document records architectural lessons only — no source code is copied, forked, or vendored. Any future code reuse requires a separate legal/licensing review.

---

## 1. Purpose

This document makes the architectural lessons from the Tamanitomo project permanently available to:

- future Hermes runs working in this repository
- future contributors
- future SHURA/ATLAS/FORGE development
- future architectural decisions

It is an **architectural reference**, not an implementation guide. It identifies which Tamanitomo patterns are ADOPTED, ADAPTED, REJECTED, or REFERENCE-ONLY for ProjectSHURA, with reasons grounded in existing ProjectSHURA architecture.

**Related reference:** `docs/reference/OPENHUMAN_REFERENCE.md` covers a different source project (OpenHuman). The two references are parallel, not competing — each source project gets its own document.

---

## 2. Verified Facts About Tamanitomo

Verified by README inspection (`github.com/tamanitomo/tamanitomo`):

- Sovereign/self-hosted AI companion application built around Hermes Agent
- Licensed under PolyForm Noncommercial 1.0.0
- Runs 24/7 on own hardware (Linux, Android Termux, Windows, macOS)
- Features: append-only timeline ledger, grounded memory with cited proof, code-enforced boundaries, outbox messaging pattern, multi-companion roster, photo albums, voice notes, local Git recovery
- Uses episode ledger as authoritative state record
- Separates model judgment from deterministic constraints
- Fingerprinting before expensive autonomy loop (avoids redundant model calls)
- Optional sensors degrade to "unknown" rather than stale
- Local Git as recovery mechanism for important state

---

## 3. Architectural Comparison Matrix

### 3.1 Matrix Format

Each row: Pattern | Tamanitomo approach | Current SHURA approach | Convergence | Decision | Reason | Affected subsystem | Future trigger

---

### 3.2 Core Patterns

| Pattern | Tamanitomo | Current SHURA | Convergence | Decision | Reason | Subsystem | Trigger |
|---|---|---|---|---|---|---|---|
| **Authoritative ledger** | Episode ledger is authoritative; current state derived from it | Event journal (`EventJournal` in `events.py`) is authoritative; projections derived from it via `subscribe()`/`replay()` | **High** — SHURA already treats event ledger as source of truth | **ADOPT** | Reinforces existing `event → projection → presentation` architecture | Events, Projection | If multiple "current state" files appear |
| **Append-only history** | Timeline ledger is append-only; corrections supersede; retirements retire | `EventJournal` appends JSONL; bounded retention truncates old events; no in-place mutation of past events | **High** — SHURA already appends only | **ADOPT** | Already implemented; principle confirmed | Events | If event editing/deletion is introduced |
| **Projections** | Ledger → derived views; multiple read models | `build_projection()` / `PresenceProjection` / `ForgeProjection` — read-only, deterministic, replay-safe | **High** — SHURA projection layer already implements this | **ADOPT** | Already core architecture | Dream, Presence, FORGE | If projection imports brain internals for mutation |
| **Provenance** | Evidence-backed memory; cited proof; separates authored fiction from facts | No formal provenance vocabulary; `BrainEvent.source` records producer but no epistemic status | **Low** — SHURA has no equivalent | **ADAPT** | Provenance vocabulary should be added when memory architecture matures; not justified for current scope | Memory, Dream | When memory consolidation pipeline is implemented |
| **Deterministic rules** | Code enforces permissions, invariants, schemas, limits; model decides meaning/narrative | `BrainConfig` enforces config; `MemoryConsolidationTransaction` enforces commit validation; skills have permissions | **Medium** — partial; more rules in prompts than code | **ADAPT** | Move prompt-level constraints into code where practical; prompts remain for model judgment | All subsystems | When a prompt rule causes inconsistent behavior |
| **Outbox** | Model → queued candidate → policy gate → dispatcher → external channel | No outbox; expression.py emits directly; no queuing or gating layer | **None** — SHURA has no equivalent | **ADAPT** | Design an outbox pattern for future proactive messaging (Telegram, voice output, UI notifications) | Expression, Skills | When SHURA needs to send unsolicited messages |
| **Autonomy fingerprinting** | Fingerprints state before invoking autonomy loop; skips model calls when nothing changed | No fingerprinting; consciousness loop runs on schedule regardless of state change | **None** — SHURA has no equivalent | **ADOPT** | Add change-detection to avoid redundant model calls; critical for local/constrained hardware | Consciousness, Agent | When model cost/latency becomes a problem |
| **Presence (stale/unknown)** | Optional sensors degrade to "unknown"; admits when inference unreachable | `PresenceRuntime` has `OFFLINE` state; no explicit "unknown" or "stale" distinction | **Medium** — offline exists but stale/unknown conflated | **ADAPT** | Add `UNKNOWN` and `STALE` to `PresenceState` enum; sensors report absence explicitly | Presence | When location/weather/calendar sensors are added |
| **Unconfirmed state** | Represents "last known state, not reconfirmed" | `PresenceRuntime` holds last state; no reconfirmation tracking | **None** — SHURA has no equivalent | **ADAPT** | Add confirmation timestamp + state to presence; enables "since 3pm, unconfirmed" semantics | Presence | When presence sensors become intermittent |
| **Identity mutability** | Identity can evolve within limits; architecture/build/boundary locked | `data/prompts/soul.md` protected; `docs/design/SHURA_EMBODIMENT.md` locks embodiment contract; AGENTS.md governs changes | **High** — SHURA already separates mutable identity from locked architecture | **ADOPT** | Already implemented; principle confirmed | Identity, Architecture | When model proposes identity or boundary changes |
| **Dream provenance** | Dreams are meaningful without being literal facts; evidence/provenance distinction | Dream domain (`domain.py`, `transaction.py`) separates dream from factual memory; `MemoryConsolidationTransaction` validates before commit | **High** — SHURA already prevents dream material from silently becoming fact | **ADOPT** | Already core architecture | Dream, Memory | If dream content appears in factual memory without validation |
| **Git-backed recovery** | Local Git auto-commits every 15 minutes; state recoverable file-by-file | No Git-backed state recovery; state in ChromaDB + JSONL journal; `.gitignore` ignores local runtime DBs | **None** — SHURA has no equivalent | **REFERENCE** | Idea worth remembering; not justified until state format stabilizes; local-first already valued | State, Memory | When state corruption recovery is needed |
| **Hermes boundaries** | Application sits beside Hermes; Hermes owns model calls/profiles/conversations | SHURA identity ≠ Hermes; cognition ≠ one provider; presence ≠ one renderer; memory ≠ one storage; interface ≠ FORGE; workspace ≠ ATLAS | **High** — SHURA already enforces this via ABCs and factory pattern | **ADOPT** | Already core architecture | All layers | If a layer becomes coupled to Hermes-specific API |
| **Vault/knowledge layer** | Vault inspects timeline, memories, plans, artifacts without owning them | ATLAS (`atlas/service.py`) is operational layer over events/projections; does not own identity/cognition/memory | **High** — SHURA's ATLAS boundary already implements this principle | **ADOPT** | Already core architecture | ATLAS | If ATLAS starts owning identity or cognition |
| **Workspace/UI** | Workspace exposes companion's present, history, jobs, memory, creation surfaces | FORGE (`forge/contract.py`, `COMMAND_CENTER_V1.md`) is avatar-centered, SHURA-native; consumes semantic state | **Medium** — different design center (avatar vs. companion dashboard) | **ADAPT** | FORGE should remain SHURA-native, not a Tamanitomo clone; useful UI patterns may be borrowed | FORGE | When FORGE workspace surfaces are implemented |
| **Voice/images** | Voice notes, photo albums, multimodal presence | `expression.py` owns TTS/OBS; image generation via ComfyUI/remote; STT via `STTInterface` | **Medium** — capability exists but less structured | **REFERENCE** | Ideas for future multimodal expansion; not currently justified for implementation | Expression, Perception | When multimodal perception is added |
| **Multiple companions** | Multi-companion roster; each with own memory/personality/journal | SHURA is single-identity; one brain; one soul; skills extend capabilities | **None** — fundamentally different design | **REJECT** | Multi-companion contradicts SHURA's single-identity architecture; skills extend SHURA, they don't create new SHURAs | Identity | If user explicitly requests multi-companion mode |
| **Provider independence** | Bring-your-own-weights; Ollama/LM Studio/vLLM; API failover chains | `src/modules/llm/` factory: omniroute, openai, groq, openrouter; `BrainConfig` provider-agnostic | **High** — SHURA already implements provider abstraction | **ADOPT** | Already core architecture | LLM, Config | If a provider-specific coupling appears |

---

## 4. Architectural Principles Derived from Tamanitomo

The following principles are **ADOPTED** as part of SHURA's architectural canon. They are grounded in existing ProjectSHURA architecture or represent clear improvements that do not contradict it.

### P1: Authoritative Ledger → Projections → Presentation

Current state is derived from an append-only event ledger, not maintained independently in competing files. **One authoritative history. Projections are derived. Presentation is a downstream concern.**

Evidence: `events.py` (EventJournal append-only), `dream/projection.py` (read-only), `presence/projection.py` (read-only).

### P2: Append-Only History

Important information is not casually overwritten or deleted. Corrections supersede prior records. Retirements retire records. Archives preserve history. Derived files can be regenerated. **The underlying historical record remains recoverable.**

Evidence: `EventJournal` appends JSONL; no update/delete API; bounded retention preserves recent history.

### P3: Rules Belong in Code

Model judgment decides meaning, interpretation, intention, narrative, plans, reflections, conversational content. Code decides permissions, invariants, schemas, state transitions, persistence, scheduling boundaries, message frequency limits, expiry, provenance rules, safety boundaries, transport behavior, duplicate prevention. **Prompts are not authoritative policy.**

Evidence: `BrainConfig` enforces config schema; `MemoryConsolidationTransaction` enforces commit validation; skills have explicit permission boundaries.

### P4: Deciding to Speak Is Not Speaking

An intention to communicate must not automatically become an irreversible side effect. **Intention → queued candidate → policy gate → dispatcher → external channel.** SHURA should be able to express an intention without that intention automatically becoming an external message.

Evidence: Currently no outbox pattern. ADAPT — design for future proactive messaging.

### P5: Absent Sensor ≠ Stale Sensor Data

When a sensor is absent or fails, its state must degrade to "unknown," not silently continue presenting old observations as current truth. **Distinguish: known, unknown, stale, inferred, confirmed.** Do not collapse them into a single boolean.

Evidence: Current `PresenceState` has `OFFLINE` but no `UNKNOWN` or `STALE`. ADAPT — extend enum when sensors are added.

### P6: Unconfirmed State Remains Honest

When the system has continuity of state but cannot currently verify that state, it must represent this honestly: **"this remains the last known state, but has not been reconfirmed."** Do not silently convert continuity into certainty.

Evidence: Current `PresenceRuntime` does not track reconfirmation. ADAPT — add confirmation timestamp and state.

### P7: Expensive Thinking Should Be Conditional

Before invoking an expensive model call, fingerprint relevant state. If nothing meaningful changed, do not invoke the model. **Distinguish: event/state changed, projection changed, model reasoning actually required, presentation update required.**

Evidence: Current consciousness loop has no change detection. ADOPT — critical for constrained hardware and local models.

### P8: Identity and Boundaries Have Different Mutability

SHURA's identity can evolve within explicitly defined limits. Architecture, invariants, security boundaries, event contracts, and core governance must not become mutable merely because a model decided they would be convenient to change.

Evidence: `data/prompts/soul.md` is protected by AGENTS.md review requirements; `docs/design/SHURA_EMBODIMENT.md` locks embodiment contract; `docs/EVENT_CONTRACT.md` is the canonical event taxonomy.

### P9: Age / Duration Should Be Derived

Do not persist values that can be safely derived from canonical dates. Persist the source fact. Compute the derivative. **Age, duration, time since event, time since confirmation, elapsed relationship interval** — all derived from timestamps.

Evidence: `BrainEvent.timestamp` is the canonical time field; no derived duration fields currently exist. ADOPT — apply when adding duration-sensitive state.

### P10: Git-Backed Local Recoverability

Local Git history is a recovery mechanism for important state. Version-controlled plain-text/structured state is a major architectural asset, not an incidental development convenience. **Portable files are preferable to opaque hosted databases.**

Evidence: Current state in ChromaDB + JSONL; `.gitignore` ignores local runtime DBs. REFERENCE — idea worth remembering; not justified until state format stabilizes.

### P11: SHURA Is Not Hermes

SHURA identity ≠ Hermes. SHURA cognition ≠ one model provider. SHURA presence ≠ one renderer. SHURA memory ≠ one storage implementation. SHURA interface ≠ FORGE. SHURA knowledge workspace ≠ ATLAS. SHURA runtime ≠ Hermes. **Hermes is one important runtime/agent integration, not the ontological definition of SHURA.**

Evidence: `src/interfaces/` ABCs; `src/modules/llm/` factory pattern; `docs/design/SHURA_EMBODIMENT.md` embodiment independence.

### P12: Local-First, No Lock-In

A paywall or vendor shutdown must never be able to destroy the architecture. **Portable files > opaque hosted databases. Schemas must be documented. Important state must be exportable. Provider integrations must be replaceable. Local models must remain first-class. External services must be adapters, not foundations.**

Evidence: `src/interfaces/` ABCs; `src/modules/llm/` factory; `MemoryStorage` supports local ChromaDB; `docs/design/THREE_SYSTEMS.md` three-system separation.

---

## 5. Deliberately Rejected Patterns

These Tamanitomo patterns are explicitly **REJECTED** for ProjectSHURA. Future Hermes runs should not reintroduce them without a new architectural review.

### R1: Multi-Companion Roster

**Tamanitomo:** Multiple completely independent companions side-by-side, each with own memory, personality, journal.

**Rejected because:** SHURA is single-identity. Skills extend SHURA's capabilities; they do not create new SHURAs. The `SkillRegistry` plugin architecture is the correct extension mechanism. A multi-companion system would require a fundamentally different identity architecture and contradicts the `data/prompts/soul.md` single-soul design.

**If revisited:** Only if the user explicitly requests a multi-companion mode AND a new identity architecture is designed. Not a small change.

### R2: Git Auto-Commit as State Mechanism

**Tamanitomo:** Vault files auto-committed to local Git every 15 minutes as a recovery mechanism.

**Rejected because:** SHURA's state flows through explicit mutation interfaces (`/dream/run`, `/memory/save`, `/atlas/*`). The event journal (`EventJournal`) is the authoritative record, not vault files. Git history is a development tool, not a runtime state mechanism. Auto-committing runtime state would conflate version control with state persistence and create noise in git history.

**If revisited:** If state corruption recovery becomes a critical problem, consider explicit snapshot/backup mechanisms rather than auto-commit.

### R3: Vault as Primary Knowledge Store

**Tamanitomo:** Vault is the primary store for timeline, memories, plans, artifacts.

**Rejected because:** ATLAS is the knowledge/operational layer over SHURA state, not a second brain. SHURA's knowledge architecture separates identity (`soul.md`), cognition (`brain.py`/`consciousness.py`), memory (`MemoryStorage`), and operational context (`ATLAS`). A vault that owns knowledge would compete with these layers and violate the single-brain architecture.

**If revisited:** If ATLAS matures into a full knowledge service, it should still be a projection/inspection layer over canonical SHURA state, not an independent owner.

### R4: Tamanitomo's Presence Loop Design

**Tamanitomo:** Presence loop that rewrites the same scene every few minutes; consecutive identical beats collapse into one with the span they covered.

**Rejected because:** SHURA has its own presence architecture (`PresenceRuntime`, `PresenceProjection`, `ForgePresenceState`). The Tamanitomo presence loop is coupled to its own ledger/scene model. SHURA's presence is derived from `EventManager` subscriptions and semantic state transitions, not scene rewriting.

**If revisited:** The concept of collapsing consecutive identical state representations is interesting for UI efficiency, but should be implemented within SHURA's existing projection architecture, not copied from Tamanitomo.

---

## 6. Ambiguities and Open Questions

### Q9: Provenance Vocabulary — When to Formalize?

Tamanitomo uses a formal provenance vocabulary: `observed`, `user_asserted`, `tool_observed`, `model_inferred`, `dream`, `imagined`, `generated`, `imported`, `system_derived`. SHURA currently records `source` on events but has no epistemic status field.

**Open question:** When should SHURA formalize provenance? Candidate triggers: memory consolidation pipeline implementation, dream-to-fact boundary enforcement, ATLAS knowledge layer.

**Current stance:** ADAPT — add provenance when memory architecture matures; do not add speculative schema now.

### Q10: Outbox Pattern — What Policy Gates?

Tamanitomo's outbox has policy gates: quiet hours, daily frequency quotas, duplicate prevention. SHURA has no outbox.

**Open question:** What policy gates does SHURA need? Candidates: rate limiting, user attention state check, duplicate detection, priority ordering.

**Current stance:** ADAPT — design outbox when proactive messaging is needed; not justified for current scope.

### Q11: Derived Values — Where to Enforce?

Tamanitomo's principle: don't persist values that can be derived. SHURA currently persists some values that could be derived (e.g., presence state could be derived from events).

**Open question:** Where should derived-value enforcement be applied? Candidates: presence state, dream transaction status, ATLAS snapshots.

**Current stance:** ADOPT principle; apply incrementally as subsystems mature.

### Q12: Stale vs. Unknown — Sensor Integration Boundary

When is a sensor "absent" (unknown) vs. "stale" (was known, now outdated)? This distinction requires a sensor heartbeat or timeout mechanism.

**Open question:** What timeout intervals define stale for different sensor types? Who owns the heartbeat?

**Current stance:** ADAPT — add when sensors are integrated; not currently justified.

---

## 7. License Constraint

**Tamanitomo is licensed under PolyForm Noncommercial 1.0.0.**

This document records architectural lessons only. No source code from Tamanitomo has been copied, forked, or vendored into ProjectSHURA. The repository is treated as a reference implementation and architectural source.

**Any future code reuse from Tamanitomo must be treated as a separate legal/licensing decision** and is not part of this task or document.

---

## 8. Affected Subsystems Summary

| Subsystem | Impact | Decision |
|---|---|---|
| Events | Authoritative ledger already implemented | ADOPT — maintain |
| Projection | Read-only boundary already implemented | ADOPT — maintain |
| Dream | Provenance distinction already implemented | ADOPT — maintain |
| Presence | Stale/unknown distinction missing | ADAPT — extend when sensors added |
| Memory | Provenance vocabulary missing | ADAPT — add when pipeline matures |
| Expression | Outbox pattern missing | ADAPT — design when proactive messaging needed |
| Consciousness | Fingerprinting missing | ADOPT — add change detection |
| ATLAS | Already a projection layer | ADOPT — maintain |
| FORGE | SHURA-native, not Tamanitomo clone | ADAPT — borrow UI patterns only |
| Identity | Already protected | ADOPT — maintain |
| LLM/Provider | Already abstracted | ADOPT — maintain |

---

## 9. Future Triggers for Revisiting Decisions

| Trigger | Pattern to Revisit |
|---|---|
| Multiple "current state" files appear | Authoritative ledger (P1) |
| Event editing/deletion introduced | Append-only history (P2) |
| Projection imports brain internals for mutation | Projection boundary (P3) |
| Provenance violations (dream becomes fact without validation) | Dream provenance (P8) |
| Model cost/latency becomes a problem | Autonomy fingerprinting (P7) |
| Proactive messaging needed (Telegram, voice, UI) | Outbox pattern (P4) |
| Location/weather/calendar sensors added | Stale/unknown state (P5) |
| Presence sensors become intermittent | Unconfirmed state (P6) |
| State corruption recovery needed | Git-backed recovery (P10) |
| Layer becomes coupled to Hermes-specific API | Hermes boundaries (P11) |
| External service becomes sole state copy | Local-first (P12) |
| Memory consolidation pipeline implemented | Provenance vocabulary (Q9) |
| User requests multi-companion mode | R1 (Multi-Companion Roster) |
| ATLAS matures into full knowledge service | R3 (Vault as Knowledge Store) |

---

## 10. Related Documents

- `docs/reference/OPENHUMAN_REFERENCE.md` — OpenHuman reference (different source project)
- `docs/reference/ADR_INDEX.md` — ADR-002 covers this reference
- `docs/reference/OPEN_QUESTIONS.md` — Q9-Q12 cover Tamanitomo-derived questions
- `docs/EVENT_CONTRACT.md` — Event taxonomy (provenance extension point)
- `docs/design/ARCHITECTURE_MAP.md` — Three-tier architecture verification
- `docs/design/SHURA_PRESENCE.md` — Presence design (extends with stale/unknown)
- `docs/operations/AUTONOMOUS_LOOP.md` — Loop protocol (fingerprinting relevant)

---

**END OF REFERENCE DOCUMENT**
