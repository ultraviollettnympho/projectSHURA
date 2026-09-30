# SHURA HANDOFF CONTRACT (v1)

> Standard for what every delegated task should return.
> Generated: 2026-09-30 05:00 CDT
> Status: PROPOSED v1

---

## 1. PURPOSE

When SHURA delegates work, the assignee returns more than a verdict.

The handoff contract exists so that:

- the result is evidence-backed
- the next agent does not start from zero
- persistent knowledge can be extracted
- failures are visible rather than absorbed
- continuity survives across sessions and agents

The handoff contract is the bridge between a single task and durable developmental memory.

---

## 2. THE NINE QUESTIONS

Every handoff should answer these nine questions.

### 2.1 WHAT WAS I ASKED TO DO?

 restate the objective as received, including:

- task ID
- objective
- constraints
- expected artifacts
- success criteria
- risk level
- any explicit permissions or prohibitions

If the assignee interpreted the task differently than stated, say so here.

### 2.2 WHAT DID I FIND?

What the assignee discovered before or during the work.

Include:

- relevant pre-existing state
- relevant files or docs consulted
- relevant prior decisions
- relevant risks or unknowns
- anything that changed the understanding of the task

This is where inspection results live.

### 2.3 WHAT DID I CHANGE?

What the assignee actually changed.

Be specific:

- files changed
- config changed
- docs changed
- repo state changed
- external state changed

If nothing was changed, say so explicitly.

Changes should be verifiable.

### 2.4 WHAT DID I NOT CHANGE?

What the assignee deliberately did not change and why.

Examples:

- Did not touch .env because no secret change was authorized.
- Did not modify identity because no identity decision was in scope.
- Did not rewrite git history because the task did not authorize it.
- Did not modify design contract because the change was only implementation.

This field protects against hidden scope creep.

### 2.5 WHAT EVIDENCE SUPPORTS SUCCESS?

What proves the result.

At minimum:

- file paths
- test output
- diff
- endpoint inspection
- screenshots or other directly inspectable evidence
- commands run and their output

A claim without evidence is not a completed handoff.

### 2.6 WHAT FAILED?

What did not work, including:

- errors
- blocked steps
- verification failures
- unexpected behavior
- assumptions that proved wrong

If nothing failed, say "no failures observed" rather than leaving it blank.

### 2.7 WHAT REMAINS UNKNOWN?

What the assignee could not verify, decide, or access.

Examples:

- MCP connection not verified
- external system not reachable
- human decision required
- evidence insufficient to conclude
- behavior not testable from current permissions

 unknowns should be listed explicitly, not absorbed into a confident-sounding summary.

### 2.8 WHAT SHOULD THE NEXT AGENT KNOW?

The most important handoff content.

This is the forward memory.

Include:

- what to do next
- what to avoid
- what is ready
- what is blocked
- what decisions were made
- what context is essential
- what files are now relevant
- what followup task ID should be activated

### 2.9 WHAT SHOULD BECOME PERSISTENT KNOWLEDGE?

What from this task is durable enough to record outside the task envelope.

Examples:

- a decision that should go into an ADR
- an open question that should be added to OPEN_QUESTIONS.md
- a lesson that should go into a skill
- a state update that should go into loop state or session handoff
- a provenance note
- a canonical file that should be updated

Not everything needs to persist. But when something does, say so here.

---

## 3. HANDOFF FORMAT

A handoff can be written as a structured section in a document, a structured message, or a machine-readable payload.

Minimal human-readable handoff:

```markdown
## HANDOFF — TASK-SHURA-001

### Asked
Inventory the current environment and produce the initial SHURA system inventory.

### Found
- Hermes profile shura active; config 4065 lines
- 142 skills present; 6 project-specific SHURA skills
- 4 MCP servers configured; none verified connected
- repo shura-foundation with staged/unstaged/untracked changes
- Playwright not installed in project venv
- INFAC project present at ~/ultraviollettnympho_INFAC
- bundle artifacts found under ~/Downloads

### Changed
- Created docs/SHURA_SYSTEM_INVENTORY.md
- Created docs/SHURA_CONTROL_PLANE.md
- Created docs/SHURA_AGENT_REGISTRY.md
- Created docs/SHURA_TASK_CONTRACT.md

### Did not change
- No identity files touched
- No .env touched
- No git history rewritten
- No MCP connections modified

### Evidence
- File inspection of created docs
- git diff of docs/
- Direct inspection of config, skills, repo state, env

### Failed
- test_playwright_installed fails (Playwright not installed in project venv)
- This failure is pre-existing and not caused by this task

### Unknown
- Freebuff status unknown
- OpenClaw active integration not confirmed
- gstack as unified tool not found
- Several MCP servers not individually verified connected

### Next agent should know
- Six canonical documents produced
- Two pre-existing test failures identified and classified
- Control plane and task/handoff contracts are now available
- Next stage is controlled autonomous-development proof

### Should persist
- Inventory document
- Control plane document
- Agent registry
- Task contract
- Handoff contract
- Open questions about Freebuff, OpenClaw, gstack, MCP verification
```

---

## 4. RULES

1. A handoff that skips failure or uncertainty is not a good handoff.
2. A handoff that cannot be verified is not complete.
3. A handoff that does not say what should persist is wasting information.
4. A handoff should be written for a future agent or future SHURA that does not have this conversation in context.
5. If the assignee is unsure, say unsure. Do not fake confidence.
6. If the assignee did not do something important, say that explicitly.

---

## 5. RELATION TO TASK CONTRACT

The task contract is the request.

The handoff contract is the response.

Together they form the basic developmental loop:

request → execute → handoff → verify → persist → next

---

## 6. HANDOFF AS DEVELOPMENTAL CONTINUITY

This is the beginning of SHURA's ability to accumulate knowledge across tasks.

The first durable layer is not a vector database or a fancy memory system.

It is:

- facts
- observations
- decisions
- plans
- artifacts
- events
- relationships
- hypotheses
- lessons
- superseded information
- provenance

The handoff contract is where those begin to be extracted from individual tasks.

ATLAS, when operational, is where they become durable at scale.

Until then, docs/, loop state, session handoff, and well-written handoffs are the continuity layer.

---

## 7. OUT OF SCOPE FOR v1

- Automatic handoff extraction from arbitrary conversation
- Semantic search across handoffs
- Handoff validation beyond basic completeness
- Handoff archival beyond whatever the project docs/ and memory systems provide

v1 is a usable handoff discipline, not a memory platform.
