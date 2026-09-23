# SHURA ENGINEERING DOCTRINE

## Engineering Objective

Build systems that are understandable, modular, testable, portable, reversible, and genuinely useful.

Code is an implementation of architecture, not the architecture itself.

---

## Before Editing

Inspect:

* repository status
* relevant files
* imports and dependencies
* public interfaces
* tests
* configuration
* callers and consumers
* recent related changes

Do not edit from a filename or isolated snippet alone when the surrounding architecture matters.

---

## Before Designing

Identify:

* the actual requirement
* current behavior
* desired behavior
* architectural owner
* affected interfaces
* compatibility requirements
* failure modes
* testing strategy

Do not design around an imagined future requirement unless that future requirement is explicitly part of the task.

---

## Implementation

Prefer:

* small cohesive changes
* explicit interfaces
* existing abstractions when appropriate
* dependency injection where useful
* deterministic behavior
* clear error handling
* testable boundaries
* configuration over hardcoding when configuration is genuinely required

Avoid:

* speculative abstraction
* hidden global state
* unnecessary frameworks
* duplicated sources of truth
* silent fallback behavior
* magical coupling
* architecture that exists only to satisfy the current implementation

---

## Testing

Tests should establish behavior, not merely exercise code.

When adding or changing behavior:

1. identify existing relevant tests
2. modify or add the smallest appropriate test
3. run focused tests
4. run broader tests when warranted
5. inspect failures
6. verify that the implementation, not the test, is correct

Never weaken a test merely to make an implementation pass.

---

## Debugging

Use evidence-driven debugging.

1. reproduce
2. observe
3. isolate
4. form a hypothesis
5. test the hypothesis
6. modify
7. reproduce
8. verify

Do not stack speculative changes onto an unknown failure state.

Prefer one meaningful change at a time when isolating a difficult problem.

---

## Git Discipline

Before substantial changes:

```bash
git status
git branch --show-current
git log -n 5 --oneline
```

Do not overwrite unrelated user work.

Do not reset, checkout, restore, rebase, or delete work without understanding what will be affected.

Before committing:

* inspect the diff
* inspect status
* run relevant tests
* ensure generated artifacts are intentional

Commit messages should describe meaningful changes, not emotional states.

---

## Architecture

Favor explicit boundaries.

For ProjectSHURA:

```text
identity
    ↓
cognition
    ↓
events / state
    ↓
projections
    ↓
interfaces / presentation
```

Do not invert these dependencies casually.

In particular:

* renderer code must not define cognition
* avatar state must not define identity
* UI state must not become the source of truth for internal state
* provider-specific behavior must not become core identity
* model-specific quirks must not become architectural contracts

---

## Repository Safety

Never assume the repository is clean.

Before changing files, inspect status.

Never discard changes simply because they are unexpected.

Unexpected changes may represent:

* user work
* another agent
* generated state
* unfinished work
* an important experiment

Determine ownership before modifying or removing them.

---

## Completion

A task is complete only when:

1. implementation exists
2. relevant tests pass
3. resulting state has been inspected
4. requested behavior is demonstrable
5. important limitations are known
6. documentation is updated when architecture changed

"Code was written" is not equivalent to "task completed."

---

## Autonomous Agent Rule

When operating autonomously, maintain a bounded loop:

OBSERVE
→ PLAN
→ ACT
→ TEST
→ INSPECT
→ DECIDE

Continue while meaningful progress toward the objective exists.

Stop when:

* the objective is satisfied
* the remaining work requires an unavailable capability
* a critical ambiguity blocks safe progress
* continuing would require destructive or irreversible action without authorization

When stopping, leave the repository in a coherent state and report the exact remaining blocker.

