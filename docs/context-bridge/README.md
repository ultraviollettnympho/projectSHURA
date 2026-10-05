# SHURA Context Bridge

Status: FOUNDATION / PROTOTYPE PLANNING
Branch: context-bridge-foundation

## Purpose

The Context Bridge is a small, harness-neutral continuity layer between strategic conversation and execution. It is not another assistant, another memory database, or a replacement for Hermes.

Its job is to make the current useful state of work portable between ChatGPT/SHURA, Hermes, VS Code, Git, and connected projects without requiring a transcript dump.

## Core division of labor

- ChatGPT / SHURA: strategy, synthesis, creative direction, architectural arbitration.
- Context Bridge: compressed, explicit, portable current state.
- Hermes: repository inspection, implementation, tests, bounded autonomous work.
- VS Code: visual coding/navigation surface.
- Holographic: retrieval substrate for durable memory, not canonical project state.
- Git/GitHub: evidence and history.
- Review/QA: independent challenge.
- ProjectSHURA: canonical SHURA architecture and implementation.
- Aether Relay / INFAC / other projects: consumers/participants, not hidden sources of truth.

## Canonical principle

The transcript is an input to continuity, not the continuity system.

The bridge should answer, quickly and deterministically:

1. What are we doing?
2. What is true right now?
3. What changed?
4. What decisions constrain the work?
5. What is blocked or uncertain?
6. What is the next bounded task?
7. Which files matter?
8. What evidence is required to call it done?

## Prototype boundary

The smallest functioning prototype is file-based:

ChatGPT/SHURA writes or updates a concise context packet -> Hermes reads it -> Hermes executes one bounded task -> Hermes writes a structured handoff/evidence result -> the bridge packet is updated -> a new agent/session can resume from that state.

No daemon, database, UI, bidirectional live sync, or autonomous multi-agent graph is required for v0.

## Non-goals for v0

- replacing Holographic
- replacing Hermes memory
- building ATLAS UI
- synchronizing complete chat transcripts
- creating a second task tracker
- creating a new agent framework
- changing ProjectSHURA core architecture
- automatic conflict resolution across every source

See ROADMAP.md for the staged expansion path.
