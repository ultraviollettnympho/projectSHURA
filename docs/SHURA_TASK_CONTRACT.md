# SHURA TASK CONTRACT (v1)

> Standard envelope for SHURA-coordinated tasks.
> Generated: 2026-09-30 05:00 CDT
> Status: PROPOSED v1 — machine-readable where practical, human-readable always

---

## 1. PURPOSE

Every task SHURA coordinates should have a clear envelope so that:

- the assignee knows what to do
- the verifier knows what success looks like
- the records know what happened
- future sessions can reconstruct context without replaying the whole conversation

This is the first version. It should be understandable by humans and usable by agents.

---

## 2. TASK ENVELOPE

### 2.1 TASK_ID

Unique identifier for the task.

Format: `TASK-<project>-<sequence>` or `TASK-<short-slug>-<nn>`.

Examples:

- `TASK-SHURA-001`
- `TASK-INFAC-014`
- `TASK-FORGE-007`

The ID must be unique within the project scope and stable once assigned.

### 2.2 PROJECT

Human-readable project name.

Examples:

- ProjectSHURA
- INFAC
- AETHERWOUND
- FORGE

### 2.3 REPOSITORY

Canonical repository root or project location.

Examples:

- /Users/ultraviollett/projectSHURA
- /Users/ultraviollett/ultraviollettnympho_INFAC
- https://github.com/ultraviollettnympho/projectSHURA

If the task does not touch a repository, state `none`.

### 2.4 BRANCH

Active branch for repository work.

If not applicable, state `n/a`.

If the task creates a branch, record both the starting branch and the new branch.

### 2.5 OBJECTIVE

One to three sentences describing what the task is supposed to accomplish.

This is the most important field. If the objective is vague, the task is vague.

Objective should be testable. Prefer:

- "Make X do Y under condition Z."
- "Produce artifact A that passes B."
- "Verify that C exists and works."

Avoid:

- "Improve X."
- "Work on X."
- "Explore X."

unless the task is explicitly exploratory and the exploration target is defined.

### 2.6 BACKGROUND

What led to this task. What the assignee should know about prior decisions, prior failures, related work, and constraints that are not obvious from the objective alone.

Keep background concise but complete enough that a new agent can understand why the task exists.

### 2.7 CONSTRAINTS

Explicit constraints.

Examples:

- No identity changes.
- No secret changes.
- No destructive git operations.
- Must preserve existing event contract.
- Must not import brain internals for mutation.
- Must pass tests before claiming done.
- Must not exceed time budget.
- Must use open-source/local-first where practical.
- Human approval required for X.

If a constraint is important, write it down.

### 2.8 RELEVANT CONTEXT

Files, documents, prior tasks, loop state, session handoff, design docs, ADRs, open questions, and anything else the assignee should read before acting.

This is not optional for non-trivial tasks.

At minimum, include:

- relevant docs
- relevant source files
- relevant test files
- relevant prior task IDs
- relevant decisions
- relevant contracts

### 2.9 FILES

Specific files the task touches or depends on.

Use absolute paths where practical.

Examples:

- /Users/ultraviollett/projectSHURA/src/core/events.py
- /Users/ultraviollett/projectSHURA/docs/SHURA_CONTROL_PLANE.md
- ~/.hermes/profiles/shura/config.yaml

### 2.10 DEPENDENCIES

What must exist or be true before this task can succeed.

Examples:

- Depends on TASK-SHURA-000 completing first.
- Depends on REAPER MCP connected.
- Depends on design contract docs/design/SHURA_EMBODIMENT.md being current.
- Depends on Playwright installed for test_forge_ui_harness.

If there are no dependencies, state `none`.

### 2.11 ASSIGNED_ROLE

Which functional role is responsible.

Examples:

- ARCHITECT
- IMPLEMENTER
- VERIFIER
- RESEARCHER
- DOCUMENTATION

If the task is being executed by SHURA directly through Hermes, that is still a role assignment. Do not leave this ambiguous.

### 2.12 EXPECTED_ARTIFACTS

What the task should produce.

Examples:

- A file at path X.
- A passing test.
- A documented decision.
- A verified endpoint.
- A consolidated inventory.
- A updated loop state.

If the task produces no artifact, say so explicitly. "No artifact; observation only." is a valid answer.

### 2.13 SUCCESS_CRITERIA

What must be true for the task to count as successful.

Success criteria should be testable.

Examples:

- File X exists with content matching Y.
- Test suite passes.
- Endpoint returns Z.
- Diff contains only intended changes.
- No secret exposure in diff.
- Identity unchanged.
- Project builds cleanly.

Avoid vague criteria like "looks good" unless paired with a concrete review condition.

### 2.14 VERIFICATION_REQUIREMENTS

How the task result will be verified.

Examples:

- Run `python -m unittest discover -s tests -p "test_*.py"`.
- Inspect file X.
- Check endpoint Y.
- Review git diff.
- Confirm via browser.
- Human review required for Z.

Verification requirements should be strong enough that "done" is not merely asserted.

### 2.15 RISK_LEVEL

One of:

- BLOCKER
- HIGH
- MEDIUM
- LOW
- INFORMATIONAL

Risk level reflects the consequences of getting this task wrong, not the difficulty of the task.

### 2.16 PERMISSIONS

What the assignee is allowed to do.

Examples:

- May edit files in src/core/atlas/.
- May run tests.
- May update docs/.
- May not touch .env.
- May not change identity files.
- May not force push.
- May not bypass approvals.

If permissions are limited, say so explicitly.

### 2.17 STATUS

One of:

- PROPOSED
- READY
- IN_PROGRESS
- COMPLETED
- VERIFIED
- BLOCKED
- DEFERRED
- FAILED
- SUPERSEDED

Status should be updated as the task moves.

### 2.18 PROVENANCE

Where this task came from.

Examples:

- Directive SHURA_EXECUTION_DIRECTIVE_01
- Loop state next-ready-task
- Human request
- Prior task followup
- ADR decision

### 2.19 RESULT

What actually happened.

Populated after execution.

Should include:

- what was done
- what was produced
- what evidence supports the result
- what failed
- what remains unknown

### 2.20 EVIDENCE

Concrete evidence supporting the result.

Examples:

- git diff
- test output
- file paths
- endpoint responses
- screenshots
- logs
- verification command and its output

Evidence must be something SHURA or a verifier can inspect, not just a claim.

### 2.21 FOLLOWUP

What should happen next.

Examples:

- None.
- Task TASK-SHURA-002 should be activated.
- Human decision required on X.
- Verification deferred until Y is available.
- Document X should be updated.

---

## 3. MINIMAL VIABLE ENVELOPE

For small tasks, not every field needs a long value. The minimal viable envelope is:

- TASK_ID
- PROJECT
- OBJECTIVE
- CONSTRAINTS
- ASSIGNED_ROLE
- EXPECTED_ARTIFACTS
- SUCCESS_CRITERIA
- VERIFICATION_REQUIREMENTS
- RISK_LEVEL
- STATUS

If a task cannot fill even that, the task is probably not ready yet.

---

## 4. MACHINE-READABLE REPRESENTATION

A task can be represented as a flat structure. Example:

```json
{
  "task_id": "TASK-SHURA-001",
  "project": "ProjectSHURA",
  "repository": "/Users/ultraviollett/projectSHURA",
  "branch": "shura-foundation",
  "objective": "Produce the initial SHURA system inventory from direct inspection.",
  "background": "Sequence 01 bootstrap. Need a verified inventory before control plane work.",
  "constraints": [
    "no identity changes",
    "no secret changes",
    "no destructive git"
  ],
  "relevant_context": [
    "docs/operations/LOOP_STATE.md",
    "docs/operations/SESSION_HANDOFF.md"
  ],
  "files": [
    "/Users/ultraviollett/projectSHURA/docs/SHURA_SYSTEM_INVENTORY.md"
  ],
  "dependencies": [],
  "assigned_role": "DOCUMENTATION",
  "expected_artifacts": [
    "docs/SHURA_SYSTEM_INVENTORY.md"
  ],
  "success_criteria": [
    "file exists",
    "claims backed by inspected evidence",
    "no fabricated test results"
  ],
  "verification_requirements": [
    "inspect written file",
    "cross-check key claims against system state"
  ],
  "risk_level": "LOW",
  "permissions": [
    "may write docs",
    "may not touch identity or secrets"
  ],
  "status": "VERIFIED",
  "provenance": "SHURA_EXECUTION_DIRECTIVE_01",
  "result": "Inventory produced from direct inspection of Hermes config, repo state, skills, plugins, MCP config, environment, and project locations.",
  "evidence": [
    "docs/SHURA_SYSTEM_INVENTORY.md"
  ],
  "followup": "Activate SEQUENCE 02 control-plane proof."
}
```

JSON is convenient for machine handling. Markdown is convenient for humans. Both can exist. The canonical document can be Markdown with a machine-readable block where useful.

---

## 5. RULES

1. No task should be marked COMPLETED without evidence.
2. No task should be delegated without context.
3. No task should change status to VERIFIED unless verification criteria were actually met.
4. No task should silently expand scope.
5. If a task is blocked, record the exact decision required.
6. If a task is superseded, record why.
7. If a task produces a decision, record the decision separately in the appropriate canonical location (ADR, open questions, loop state, handoff).
8. The human is the final authority for consequential task decisions.

---

## 6. OUT OF SCOPE FOR v1

- Full workflow automation
- Automatic task generation from roadmap
- Automatic dependency resolution across all projects
- Automatic status synchronization across every system

v1 is a usable envelope, not a fully automated task OS.

---

## 7. RELATION TO OTHER CONTRACTS

- This task contract is the envelope for work.
- The handoff contract is what the assignee fills in when returning results.
- The control plane is where coordination rules live.
- The agent registry is where role definitions live.
- Loop state and session handoff are where current-state continuity lives.
- ATLAS, when operational, will be where durable task/project/decision records live.
