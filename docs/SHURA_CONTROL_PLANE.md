# SHURA CONTROL PLANE

> How SHURA coordinates Hermes, agent fleet, tools, and external systems.
> Generated: 2026-09-30 05:00 CDT
> Status: VERIFIED from inspection + proposed coordination model

---

## 1. WHO COORDINATES

**SHURA** is the coordinating intelligence.

In practice, the Hermes runtime executes SHURA's directives. Hermes is the primary coordinator runtime. SHURA's cognitive/identity layer lives in:

- `data/prompts/soul.md` (identity)
- `data/prompts/operating.md` (behavior doctrine)
- `docs/` (architecture, decisions, roadmap, loop state)
- skills loaded into the Hermes profile
- conversation-level context (this session)

Hermes is not SHURA. Hermes is the runtime. SHURA is the direction, judgment, and continuity expressed through Hermes in this session.

---

## 2. WHAT EXISTS (AGENT FLEET)

### Canonical subagent roles (Hermes `delegate_task`)

These are roles, not permanent personalities. They are instantiated on demand via `delegate_task`. Each receives a fresh context with the information passed in the task.

| Role | Functional responsibility | When to use |
|---|---|---|
| ARCHITECT | decomposition, interfaces, design decisions, ADRs | before implementation when structure matters |
| RESEARCHER | evidence gathering, web search, doc extraction, comparison | before decisions that need external evidence |
| IMPLEMENTER | code changes, tests, build, verification | concrete bounded tasks with clear acceptance criteria |
| DESIGNER | visual/UI/experience direction, mockups, aesthetic judgment | when appearance or interaction is in question |
| BROWSER/QA | web verification, live-site checks, user-flow walkthroughs | when external pages or user journeys must be inspected |
| SECURITY REVIEWER | adversarial review, secret exposure, permission boundaries, review of destructive operations | before release, before destructive changes, before external exposure |
| CODE REVIEWER | correctness, regression, style, review of IMPLEMENTER output | after implementation before claiming completion |
| DOCUMENTATION | docs, ADRs, runbooks, clarity of written artifacts | when written record matters |
| FORENSICS | post-incident analysis, root-cause tracing, state reconstruction | after failures or anomalous state |
| WORKTREE/GIT | parallel development, branch management, safe repo operations | when concurrent work risks conflict |
| RECONCILIATION | merging divergent outputs, resolving conflicts between agents | when multiple agents produce competing answers |
| VERIFIER | confirm artifacts actually work, not merely exist | any "done" claim before the human sees it |

These roles are HUMAN-DESIGNATED. They do not yet exist as persistent agent definitions. They are activated by SHURA via `delegate_task` with appropriate context.

### Existing skills that approximate roles

| Skill | Approximates role |
|---|---|
| shura-architect | ARCHITECT |
| shura-forensics | FORENSICS |
| shura-verifier | VERIFIER |
| shura-worktree | WORKTREE/GIT |
| atlas-reconcile | RECONCILIATION |
| research-architecture | RESEARCHER |
| forge-ui | BROWSER/QA |
| systematic-debugging | DEBUGGER |
| subagent-driven-development | IMPLEMENTER orchestration |
| writing-plans | PLANNER |
| codebase-inspection | INSPECTOR |

### INFAC agent fleet (separate system)

INFAC defines its own agent roles in `ultraviollettnympho_INFAC/.agents/roles/`:

- infac-architect
- infac-content
- infac-design
- infac-field
- infac-qa
- infac-redteam
- infac-symbolic

These are INFAC's internal roles. They are NOT ProjectSHURA's agents. They are documented here for awareness.

---

## 3. WHAT EACH AGENT DOES

Every agent must be able to answer the handoff contract questions (see SHURA_HANDOFF_CONTRACT.md):

1. What was I asked to do?
2. What did I find?
3. What did I change?
4. What did I not change?
5. What evidence supports success?
6. What failed?
7. What remains unknown?
8. What should the next agent know?
9. What should become persistent knowledge?

Agents do NOT silently mutate canonical state without a recordable task envelope.

---

## 4. TOOLS BY CATEGORY

### Direct inspection

- read_file, search_files, patch, write_file
- terminal (shell access to the host)
- execute_code (persistent Python with hermes_tools)
- vision_analyze (image inspection)
- skill_view, skills_list (skill discovery)

### Execution

- terminal (builds, tests, scripts, git, installs)
- execute_code (Python logic with tool calls)
- delegate_task (spawn subagents)
- browser_exec (web automation)

### External integrations

- web_search, web_extract (internet)
- text_to_speech (voice output)
- MCP servers via native-mcp / mcporter (external tool APIs)
- GitHub via gh CLI + github-* skills
- cronjob_manage (scheduled jobs)
- session_search (past conversation recall)
- image_generate (image generation, if configured)

### Coordination

- clarify (ask user for decisions)
- memory (persistent notes across sessions)

---

## 5. HOW HERMES DELEGATES

1. SHURA (in this context) decides a task should be delegated.
2. SHURA calls `delegate_task` with:
   - `goal`: what to accomplish
   - `context`: all background the child needs (file paths, constraints, relevant docs, output format expectations)
   - `output_schema` (optional): JSON schema the result must validate against
3. Hermes spawns an isolated subagent with its own terminal session.
4. The subagent runs, produces a final summary.
5. The summary returns to SHURA.
6. SHARA verifies the result (via verifier role, tests, file inspection, or direct observation).
7. Verified results are integrated. Unverified results are NOT treated as done.

Delegation is NOT automatic. SHURA decides when delegation is appropriate.

---

## 6. HOW AN AGENT RECEIVES CONTEXT

An agent receives context ONLY from what SHURA passes in the delegate_task call.

Agents do NOT inherit this session's full context automatically. If an agent needs:

- repo state
- design docs
- constraints
- prior decisions
- file paths
- acceptance criteria

SHURA must include them in `context`.

For durable context that should survive across tasks, use:

- project documentation (`docs/`)
- task graph / roadmap
- session handoff
- ATLAS once operational

---

## 7. HOW AN AGENT RETURNS RESULTS

Agents return a final summary. The summary should be:

- concrete
- evidence-backed
- explicit about what was NOT done
- explicit about what remains uncertain
- explicit about what should persist

If the task produces artifacts, the summary should include paths/URLs/IDs that SHURA can verify directly.

---

## 8. HOW WORK IS VERIFIED

Verification is not optional. Before SHURA reports something as done:

1. THE ARTIFACT EXISTS on disk / in the remote system / at the URL claimed.
2. THE TEST PASSES if a test covers the behavior.
3. THE BEHAVIOR WORKS if a direct check is possible.
4. THE CONTRACT IS INTACT if the change touches a shared interface.

Verification methods, in increasing strength:

- file inspection (exists, content, diff)
- test execution (unittest/pytest passing)
- endpoint inspection (HTTP reachability, response shape)
- runtime behavior (the thing actually does what it should)
- human review (for consequential decisions)

A green test suite does NOT prove architectural correctness.
A file existing does NOT prove the file works.
A subagent saying "done" does NOT prove it is done.

---

## 9. HOW FAILURES ARE ESCALATED

### Classification

| Level | Meaning | Action |
|---|---|---|
| BLOCKER | Work cannot proceed without human decision or fix | Stop. Document exact decision required. |
| HIGH | Material risk to correctness, security, or architecture | Flag immediately. Do not continue as if normal. |
| MEDIUM | Real problem but workable around or deferred | Document. Decide whether to fix now or later. |
| LOW | Minor issue, style, tech debt | Track. Fix when convenient. |
| INFORMATIONAL | Observation, not a problem | Record if useful. Do not block. |

### Escalation path

1. Agent detects failure or risk.
2. Agent classifies it.
3. For BLOCKER/HIGH: SHURA stops and either resolves or escalates to human.
4. For MEDIUM: SHURA decides whether to fix now or document for later.
5. For LOW/INFORMATIONAL: record in task state / ADR / open questions.

The human is the final authority for:

- consequential decisions
- destructive operations
- secret/credential changes
- identity changes
- architecture changes with lasting consequences
- anything the system cannot verify

---

## 10. HOW CONFLICTING OUTPUTS ARE RECONCILED

When two agents or sources disagree:

1. Identify what specifically disagrees (fact, interpretation, preference, version).
2. Determine which source is more reliable for that specific kind of claim.
3. Prefer inspection over assertion.
4. Prefer the repository / canonical doc over transient conversation.
5. If the conflict is about taste or design, treat it as a decision for the human unless a prior decision exists.
6. Record the reconciliation in the task envelope or ADR.

If reconciliation is not possible from available evidence, preserve the conflict explicitly rather than papering over it.

---

## 11. WHERE CANONICAL STATE LIVES

| Concern | Canonical location |
|---|---|
| SHURA identity | data/prompts/soul.md (repo) + skill routing layer |
| Operating doctrine | data/prompts/operating.md + doctrine/ (repo) |
| Repository state | Git (projectSHURA, INFAC, etc.) |
| Task state (current) | docs/operations/LOOP_STATE.md + docs/operations/SESSION_HANDOFF.md |
| Task graph / roadmap | docs/tasks/V1_TASK_GRAPH.md, docs/tasks/V1_ROADMAP.md |
| Decisions | docs/reference/ADR_INDEX.md |
| Open questions | docs/reference/OPEN_QUESTIONS.md |
| Acceptance criteria | docs/reference/V1_ACCEPTANCE.md |
| Hermes config | ~/.hermes/profiles/shura/config.yaml |
| Secrets | ~/.hermes/profiles/shura/.env (not committed) |
| Session memory | state.db + memories/ (profiler local) |
| Cross-session memory (durable) | memory tool notes (user/memory) |
| ATLAS (future) | proposed durable semantic memory / project knowledge layer |

---

## 12. WHAT REQUIRES HUMAN APPROVAL

- Secret/credential changes
- Destructive repo operations (force push, history rewrite, branch deletion)
- Identity changes (soul.md, operating doctrine)
- Architectural decisions with lasting consequences
- Anything BLOCKER-classified
- Anything the system cannot verify
- Release pushes
- Anything the human has not yet explicitly authorized

---

## 13. WHAT CAN HAPPEN AUTONOMOUSLY

Within existing permissions and without touching secrets/identity/destructive operations:

- inspection and inventory
- documentation updates (non-identity)
- bounded implementation with verification
- test execution and interpretation
- configuration inspection (not secret manipulation)
- git operations that preserve history and do not rewrite shared state
- browser automation for read/verify tasks
- MCP tool calls that do not require secret re-entry
- subagent delegation for bounded tasks
- reconciliation of non-consequential conflicts
- status updates to loop state / session handoff

---

## 14. COORDINATION FLOW (TYPICAL)

```
SHURA receives objective
  → understands / inspects
  → decides: act alone, delegate, or ask human
  → if delegate: formulate task envelope
  → dispatch subagent(s)
  → receive summary
  → verify
  → integrate or reject
  → update task/loop state
  → report to human with evidence
```

This is the operating loop. It is not yet automated end-to-end. SHURA executes it manually through Hermes in this stage.

---

## 15. WHAT DOES NOT EXIST YET

- Persistent agent definitions with standing permissions
- ATLAS durable semantic memory (only the skeleton exists)
- Automated autonomous loop (protocol exists; execution is manual so far)
- Freebuff integration (not found)
- OpenClaw integration (not found active)
- gstack as a single discoverable tool (methodology is distributed)
- Full agent approval framework in the workspace UI (framework designed; not built)
- Full MCP tool execution framework in workspace (framework designed; not built)

---

## 16. COORDINATION PRINCIPLES

1. Coordination is a service to the human, not a substitute for judgment.
2. The human remains the final authority for consequential decisions.
3. Autonomy is bounded by verification, permissions, and reversibility.
4. SHURA coordinates; SHURA does not hoard agency.
5. Every delegation has a task envelope.
6. Every result has evidence or it is not trusted.
7. Conflicts are resolved by inspection and documented, not hidden.
8. Canonical state is identifiable and protected.
9. Destructive actions are explicit, not incidental.
10. Identity and secrets are not touched by ordinary coordination.
