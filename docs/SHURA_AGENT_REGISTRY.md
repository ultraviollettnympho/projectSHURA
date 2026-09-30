# SHURA AGENT REGISTRY

> Inventory of agent roles, capabilities, and status for the SHURA control plane.
> Generated: 2026-09-30 05:00 CDT
> Status: VERIFIED from inspection; role definitions are PROPOSED where noted

---

## 1. ROLES, NOT PERSISTENT AGENTS

There is no persistent multi-agent runtime fleet yet.

What exists is:

- Hermes as the primary runtime
- `delegate_task` as the spawn mechanism
- skills that map to functional roles
- INFAC's separate agent role definitions (infac-*), which are not ProjectSHURA agents

The registry below defines the functional roles SHURA can instantiate through Hermes. Each role is activated by SHURA with a task envelope and appropriate context.

---

## 2. FUNCTIONAL ROLE REGISTRY

### ARCHITECT

- **Functional responsibility:** Decompose objectives into bounded tasks, define interfaces, identify architectural risks, propose ADRs, preserve contracts.
- **Runtime:** Hermes via delegate_task
- **Model:** inherits parent (default: upstage/solar-pro4:free via nous)
- **Tools:** read_file, search_files, write_file, patch, terminal, execute_code, skill_view, skills_list, web_search, web_extract, clarify
- **Skills:** projectshura-architecture, shura-architect, systematic-debugging
- **Permissions:** read-only unless task explicitly authorizes edits; no secret touch; no identity edit; no destructive git
- **Project access:** read across repos as authorized; writes only to designated files
- **Input format:** task envelope with objective, constraints, relevant docs, existing contracts
- **Output format:** architecture description, proposed file changes, risks, ADR draft if needed, verification plan
- **Verification method:** review against existing contracts, diff inspection, test plan coherence
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** does not replace human architecture judgment for consequential decisions

---

### RESEARCHER

- **Functional responsibility:** Gather evidence from web, docs, repos, APIs, MCP tools; synthesize comparisons; distinguish verified from speculative.
- **Runtime:** Hermes via delegate_task
- **Model:** inherits parent
- **Tools:** web_search, web_extract, read_file, search_files, terminal, execute_code, skill_view, browser_exec
- **Skills:** research-architecture, sandbase, huggingface-hub, grounded-citations, competitor-news-monitor, blogwatcher
- **Permissions:** read-heavy; external calls allowed where tools permit; no secret entry
- **Project access:** read-relevant project files; may fetch external resources
- **Input format:** research question, scope, preferred evidence sources, epistemic discipline requirements
- **Output format:** findings with citations/proof, confidence classification, open gaps
- **Verification method:** sources inspected, claims traceable, speculation labeled
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** web evidence depends on available tools and access; not all claims are externally verifiable

---

### IMPLEMENTER

- **Functional responsibility:** Make concrete bounded code changes, write tests, run builds/tests, verify artifacts, report diff and evidence.
- **Runtime:** Hermes via delegate_task
- **Model:** inherits parent
- **Tools:** read_file, write_file, patch, search_files, terminal, execute_code, skill_view, git operations via terminal
- **Skills:** subagent-driven-development, codebase-inspection, projectshura-architecture, shura-verifier
- **Permissions:** file edits within designated scope; terminal for tests/builds/git; no secret changes; no identity changes; no destructive git unless explicitly authorized
- **Project access:** scoped to task repository and branch
- **Input format:** task envelope with objective, files, constraints, acceptance criteria, verification plan
- **Output format:** what changed, what tests say, what evidence supports success, what remains unknown
- **Verification method:** tests, diff review, endpoint/runtime inspection where relevant
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** cannot verify things it cannot observe directly; relies on SHURA or verifier role for external checks

---

### DESIGNER

- **Functional responsibility:** Shape visual/UI/experience decisions, produce mockups or variants, critique aesthetic coherence, protect distinctive expression.
- **Runtime:** Hermes via delegate_task or direct
- **Model:** inherits parent
- **Tools:** write_file, read_file, browser_exec, vision_analyze, image_generate where available
- **Skills:** claude-design, sketch, excalidraw, forge-ui, vtuber-avatar-placeholders, anima-design-agent
- **Permissions:** create artifacts; not authorized to replace identity or canonical visual contracts without human decision
- **Project access:** relevant front-end/assets as scoped
- **Input format:** design goal, constraints, references, existing visual system
- **Output format:** variants, reasoning, trade-offs, recommended direction, artifacts
- **Verification method:** artifact inspection, coherence with existing system, human review for consequential aesthetics
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** taste judgments are subjective; human is final authority for consequential visual identity

---

### BROWSER/QA

- **Functional responsibility:** Inspect live web pages, verify user flows, check external behavior, capture evidence from browser.
- **Runtime:** Hermes via delegate_task or direct
- **Model:** inherits parent
- **Tools:** browser_exec, browser_vault_list/fill/enter_code/save_login, web_extract, web_search
- **Skills:** forge-ui, website-blocklist (security), blocked-page-recovery
- **Permissions:** browser automation within site scope; no credential typing by the agent; vault-mediated password fill only
- **Project access:** external sites and local dev servers as needed
- **Input format:** URL, flow to verify, evidence needed
- **Output format:** observed state, screenshots/text evidence, pass/fail against criteria
- **Verification method:** direct browser evidence
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** Playwright Python package not installed in project venv (test_playwright_installed currently fails; MEDIUM issue)

---

### SECURITY REVIEWER

- **Functional responsibility:** Review for secret exposure, permission boundaries, destructive operations, adversarial risk, unsafe patterns before release or destructive action.
- **Runtime:** Hermes via delegate_task or direct
- **Model:** inherits parent
- **Tools:** read_file, search_files, patch, terminal, git operations, skill_view
- **Skills:** godmode (red-team context), shura-forensics, systematic-debugging
- **Permissions:** review; flag; recommend; NOT authorized to bypass security mechanisms; NOT authorized to rewrite history or expose secrets
- **Project access:** scoped to relevant files and diff
- **Input format:** change set, diff, intended effect, threat model if available
- **Output format:** findings by severity, exact locations, recommended remediation, residual risk
- **Verification method:** re-inspection after remediation; human approval for consequential fixes
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** cannot guarantee absence of security issues; passes/fails based on reviewed surface only

---

### CODE REVIEWER

- **Functional responsibility:** Review implementation for correctness, regression, style, contract adherence, test coverage adequacy.
- **Runtime:** Hermes via delegate_task or direct
- **Model:** inherits parent
- **Tools:** read_file, search_files, patch, terminal, execute_code, skill_view
- **Skills:** github-code-review, systematic-debugging, projectshura-architecture, shura-verifier
- **Permissions:** review and recommend; changes only if authorized
- **Project access:** relevant files and diff
- **Input format:** diff or file set, intent, acceptance criteria
- **Output format:** review findings, risks, suggestions, approval conditions
- **Verification method:** re-review after changes
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** review quality depends on context provided; cannot run the code unless given access

---

### DOCUMENTATION

- **Functional responsibility:** Write and maintain docs, ADRs, runbooks, task graphs, handoffs, acceptance criteria, and clarifying written artifacts.
- **Runtime:** Hermes via delegate_task or direct
- **Model:** inherits parent
- **Tools:** read_file, write_file, patch, search_files, skill_view
- **Skills:** writing-plans, shura-architect, atlas-reconcile
- **Permissions:** write documentation; not identity; not secrets
- **Project access:** docs/ and relevant project files
- **Input format:** topic, audience, existing docs, decisions to record
- **Output format:** drafted doc, decisions recorded, open questions flagged
- **Verification method:** file inspection, coherence with source decisions
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** documents what exists; cannot make a decision more true than the decision itself

---

### FORENSICS

- **Functional responsibility:** Investigate anomalies, trace root causes, reconstruct state, analyze failures, preserve evidence.
- **Runtime:** Hermes via delegate_task or direct
- **Model:** inherits parent
- **Tools:** read_file, search_files, terminal, execute_code, skill_view, git operations, state.db inspection where relevant
- **Skills:** shura-forensics, systematic-debugging, shura-db
- **Permissions:** read-heavy; inspect logs/state/diff; report findings
- **Project access:** scoped to the incident or anomaly
- **Input format:** what failed, when, symptoms, available artifacts
- **Output format:** timeline, cause analysis, evidence, recommendations
- **Verification method:** evidence traceability
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** forensic conclusions are inferences unless directly provable

---

### WORKTREE/GIT

- **Functional responsibility:** Safe parallel development, branch management, worktree operations, repo hygiene, non-destructive git operations.
- **Runtime:** Hermes via delegate_task or direct
- **Model:** inherits parent
- **Tools:** terminal (git), read_file, search_files
- **Skills:** shura-worktree, github-repo-management
- **Permissions:** git operations that preserve history and do not destroy shared state unless explicitly authorized
- **Project access:** relevant repository
- **Input format:** desired git state, branch strategy, constraints
- **Output format:** performed operations, resulting state, warnings
- **Verification method:** git status, branch inspection, diff review
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** cannot resolve conflicts that require semantic judgment without SHURA/human

---

### RECONCILIATION

- **Functional responsibility:** Merge divergent outputs, resolve conflicts between agents, decide which evidence wins, document reconciliation.
- **Runtime:** Hermes via delegate_task or direct
- **Model:** inherits parent
- **Tools:** read_file, search_files, patch, write_file, skill_view, clarify
- **Skills:** atlas-reconcile, shura-architect
- **Permissions:** suggest integration; final authority for consequential reconciliation rests with SHURA/human
- **Project access:** relevant files and agent outputs
- **Input format:** competing outputs, decision criteria, prior decisions
- **Output format:** reconciled result or explicit unresolved conflict with reasons
- **Verification method:** review of reconciled artifact against inputs
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** cannot invent a resolution that the evidence does not support

---

### VERIFIER

- **Functional responsibility:** Confirm artifacts actually work. Not merely exist. Test, inspect, probe, and report pass/fail with evidence.
- **Runtime:** Hermes via delegate_task or direct
- **Model:** inherits parent
- **Tools:** terminal, execute_code, read_file, search_files, browser_exec, skill_view
- **Skills:** shura-verifier, forge-ui, systematic-debugging, projectshura-architecture
- **Permissions:** run tests, inspect endpoints, inspect files, attempt verification
- **Project access:** scoped to the artifact
- **Input format:** claimed artifact, success criteria, verification requirements
- **Output format:** verification result, evidence, failures, remaining uncertainty
- **Verification method:** the verification itself
- **Current status:** CANONICAL role, activated on demand
- **Known limitations:** can only verify what is verifiable with available tools and access

---

## 3. ROLE TO SKILL MAPPING

| Role | Primary skill support |
|---|---|
| ARCHITECT | projectshura-architecture, shura-architect |
| RESEARCHER | research-architecture, sandbase, huggingface-hub, grounded-citations |
| IMPLEMENTER | subagent-driven-development, codebase-inspection, shura-verifier |
| DESIGNER | claude-design, sketch, excalidraw, forge-ui, anima-design-agent |
| BROWSER/QA | forge-ui, blocked-page-recovery |
| SECURITY REVIEWER | godmode (context), shura-forensics, systematic-debugging |
| CODE REVIEWER | github-code-review, systematic-debugging, shura-verifier |
| DOCUMENTATION | writing-plans, atlas-reconcile |
| FORENSICS | shura-forensics, shura-db, systematic-debugging |
| WORKTREE/GIT | shura-worktree, github-repo-management |
| RECONCILIATION | atlas-reconcile, shura-architect |
| VERIFIER | shura-verifier, forge-ui, systematic-debugging |

---

## 4. STATUS CLASSIFICATION

### CANONICAL

- ARCHITECT
- RESEARCHER
- IMPLEMENTER
- DESIGNER
- BROWSER/QA
- SECURITY REVIEWER
- CODE REVIEWER
- DOCUMENTATION
- FORENSICS
- WORKTREE/GIT
- RECONCILIATION
- VERIFIER

These roles are recognized as legitimate functional roles SHURA can instantiate.

### ACTIVE

- Any role currently executing via delegate_task or directly in this session.

### EXPERIMENTAL

- None currently designated. All roles above are proposed canonical roles, not experimental.

### REDUNDANT

- None identified yet. If two roles consistently produce the same outcome, consolidate.

### BROKEN

- None of the functional roles are broken. The BROWSER/QA role is partially impaired because Playwright Python package is not installed in the project venv (MEDIUM issue). Browser tooling itself is available through Hermes; only the project-vendored Playwright test assertion fails.

### UNVERIFIED

- INFAC agent roles (infac-*) are documented in the INFAC repo but not verified in this Hermes profile's runtime.
- Hivemind CLI-based agent integration not verified on this machine.
- gstack as a named external agent tool not found.

### DEPRECATED

- None designated.

### MISSING

- Persistent agent runtime with standing agent definitions beyond Hermes delegate_task.
- Automated autonomous loop execution (protocol exists; execution so far is manual).
- ATLAS operational agent integration (skeleton only).

---

## 5. GAP ANALYSIS

### Functional gaps

- No dedicated LOCAL MODEL runner role beyond whatever provider routing supplies.
- No dedicated REAPER/Music-production operator role beyond music-production skill and REAPER MCP. The REAPER MCP is configured but REAPER app not confirmed running; Majik Studio MCP configured but not verified connected.
- No dedicated 3D pipeline operator beyond blender-mcp skill. SHURA_02 assets exist; Blender not confirmed running locally via Hermes.

### Integration gaps

- Freebuff: not found. Unknown.
- OpenClaw: not found active.
- gstack as a unified tool: not found; methodology is distributed.
- Hivemind CLI: skill references it; not verified installed locally.

### Verification gaps

- MCP server connections not individually verified at inventory time (hugging_face, amplitude, majiks-studio, reaper).
- Playwright not installed in project venv.
- Ollama process not confirmed running despite provider configured.

---

## 6. FIRST-PASS ROLE ASSIGNMENTS FOR SEQUENCE 01

For the bootstrap stage, the following roles are most relevant:

- ARCHITECT: this document, control plane, task contract, handoff contract
- RESEARCHER: environment discovery, bundle provenance, tool verification
- DOCUMENTATION: the six canonical documents
- VERIFIER: confirming the inventory is actually accurate
- WORKTREE/GIT: safe handling of repo state
- SECURITY REVIEWER: ensuring no secret/identity/destructive exposure occurred during bootstrap

IMPLEMENTER is less central in this stage because Sequence 01 is inventory and control-plane definition, not feature implementation. The next stage should activate IMPLEMENTER for bounded autonomous-development proof.

---

## 7. ROLES TO DEFER

- Full autonomous agent fleet with standing definitions: defer until after control plane is stable.
- INFAC roles: defer unless INFAC work is explicitly in scope.
- Multi-agent coordination automation: defer until single-agent coordination is reliable.
