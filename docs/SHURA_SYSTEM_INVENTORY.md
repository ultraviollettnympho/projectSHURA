# SHURA SYSTEM INVENTORY

> Canonical environment inventory for SHURA control plane.
> Generated: 2026-09-30 05:00 CDT (CDT, UTC-05:00)
> Branch: shura-foundation → origin/shura-foundation
> Status: VERIFIED from direct inspection

---

## 1. RUNTIME

| Component | Value | Source |
|---|---|---|
| Hermes version | 2.88.1 (`gh version`) | CLI |
| Runtime mode | desktop (HERMES_DESKTOP=1) | env |
| Profile | shura | HERMES_SESSION_PROFILE |
| Python | 3.14.3 (Clang 16) | `python3 --version` |
| Node | v24.14.0 | `node --version` |
| npm | 11.9.0 | `npm --version` |
| uv | /Users/ultraviollett/.local/bin/uv | `which uv` |
| Project package manager | uv (pyproject.toml) | pyproject.toml |
| Hermes Agent package | not importable as `hermes_agent` module (runtime is Hermes process itself) | import test |

---

## 2. MODEL PROVIDERS (config.yaml)

### Primary

| Field | Value |
|---|---|
| Default model | upstage/solar-pro4:free |
| Provider | nous |
| Base URL | https://inference-api.nousresearch.com/v1 |
| API mode | chat_completions |

### Configured providers

| Name | Backend | Default model | Discoverable |
|---|---|---|---|
| AIHubMix | https://aihubmix.com/v1 | coding-glm-5.3-free | yes (API key: AIHUBMIX_API_KEY) |
| ollama-launch | http://127.0.0.1:11434/v1 | qwen3.5:4b-mlx | yes |
| omniroute | http://localhost:20128/v1 | auto/best-coding | yes (many model labels) |

Note: `ollama` CLI not installed locally, but ollama-launch provider configured. Ollama process not running at inventory time (no ps match).

### Custom provider (mlx-community)

```
name: mlx-community/Qwen3.5-9B-MLX-4bit
base_url: http://127.0.0.1:8080/v1
model: mlx-community/Qwen3.5-9B-MLX-4bit
```

---

## 3. HERMES CONFIGURATION (config.yaml, 4065 lines)

### Display

- personality: `uwu`
- streaming: false
- show_reasoning: true
- inline_diffs: true
- tool_progress: all
- interim_assistant_messages: true

### TTS

- provider: openai (default)
- voices configured: edge, elevenlabs, openai, xai, mistral, neutts
- use_gateway: true

### STT

- provider: openai (default)
- local model: base
- use_gateway: true

### Voice

- record_key: ctrl+b
- max_recording_seconds: 120
- auto_tts: false
- silence_threshold: 200
- silence_duration: 3

### Context/Memory

- context engine: compressor
- memory_enabled: true
- user_profile_enabled: true
- memory_char_limit: 2200
- user_char_limit: 1375

### Delegation

- max_iterations: 250
- model/provider/base_url/api_key: empty (inherits primary)

### Approvals

- mode: smart
- timeout: 60

### Plugins (enabled)

- superpowers

### Security

- redact_secrets: true
- tirith_enabled: true (tirith_timeout: 5, tirith_fail_open: true)
- website_blocklist: disabled

### MCP servers (configured)

| Name | Type | URL/Command | Auth | Enabled |
|---|---|---|---|---|
| hugging_face | url | https://huggingface.co/mcp | oauth | true |
| amplitude | url | https://mcp.amplitude.com/mcp | oauth | true |
| majiks-studio | url | http://127.0.0.1:8478/mcp | Bearer ${MCP_MAJIKS_STUDIO_API_KEY} | true |
| reaper | command | /Library/Frameworks/Python.framework/Versions/3.14/bin/reaper-mcp | none (CLI) | true |

### Fallback model

- Unconfigured (commented out).

### Smart model routing

- enabled: false

### Cron

- wrap_response: true

### Session reset

- mode: none
- at_hour: 4
- idle_minutes: 1440

### Image gen

- provider: nous

---

## 4. HERMES PLUGINS (profiles/shura/plugins/)

```
agentchat
caveman_native
clawchat
github-studio
hermes-memory-ui
hermes-speech
hindsight
prompt-optimizer
skill-retrieval
superpowers
```

superpowers is the only enabled plugin (config.yaml).

---

## 5. HERMES SKILLS (profiles/shura/skills/)

Total: 142 SKILL.md files scanned.

### ProjectSHURA-specific skills

| Skill | Status | Purpose |
|---|---|---|
| shura | initial v1 draft | SHURA identity/routing bridge |
| shura-architect | v1 | architecture capability |
| shura-db | v1 | database inspection capability |
| shura-forensics | v1 | forensic investigation capability |
| shura-verifier | v1 | verification capability |
| shura-worktree | v1 | safe parallel development capability |
| atlas-project-map | v1 | ATLAS relationship maintenance |
| atlas-reconcile | v1 | ATLAS reconciliation capability |
| forge-ui | v1 | browser testing capability |
| music-production | v1 | music production orchestration |
| research-architecture | v1 | technical research capability |
| media-analysis | v1 | media inspection capability |

### GitHub skills (subdirectory)

- github-auth
- github-code-review
- github-issues
- github-pr-workflow
- github-repo-management

### Other notable skills

- subagent-driven-development
- systematic-debugging
- writing-plans
- plan
- codebase-inspection
- hermes-agent-skill-authoring
- projectshura-architecture
- projectshura-llm-provider
- blende-mcp
- unity-mcp-server
- touchdesigner-mcp
- comfyui
- sogni-creative-agent-skill
- huggingface-hub
- sandbase
- jupyter-live-kernel
- godmode (red-teaming)
- openhue (smart-home)
- xitter (social-media)
- imessage
- email-inbox-triage
- linear
- weekly-review-planning
- hivemind-goals / hivemind-graph / hivemind-memory

### gstack / GSTACK

NOT FOUND as a standalone skill. No `gstack` skill present. The engineering methodology described in the directive is embodied in:

- `projectshura-architecture` skill (audit/recon/milestones procedure)
- `shura` skill (coding workflow, delegation, integration audit pattern)
- `systematic-debugging` skill
- `subagent-driven-development` skill
- AGENTS.md engineering doctrine

Gstack as a named external tool was not detected.

---

## 6. HERMES PLATFORM INTEGRATIONS

### Git/GitHub

- gh CLI v2.88.1 installed and authenticated
- GitHub orgs/repositories accessible: ultraviollettnympho/*
- Skills: github-auth, github-code-review, github-issues, github-pr-workflow, github-repo-management

### Browser/Playwright

- Browser engine configured (AGENT_BROWSER_ENGINE env var present)
- `browser_exec`, `browser_vault_*` tools available
- Playwright Python package: NOT installed in project venv (causes `test_playwright_installed` failure; MEDIUM issue)

### MCP

- native-mcp skill available (built-in MCP client)
- mcporter skill available
- 4 MCP servers configured in config.yaml (see Section 3)

### Hivemind

- hivemind-goals, hivemind-graph, hivemind-memory skills present
- hivemind CLI: not verified on this machine (skill references `hivemind` shell command)

### Freebuff

- NOT FOUND in skills, config, or environment. Unknown status.

### OpenClaw

- NOT FOUND as active integration. `openclaw_residue_cleanup` onboarding flag seen (onboarding.seen), suggesting prior residue cleanup. No active OpenClaw configuration detected.

---

## 7. PROJECTS / REPOSITORIES

### projectSHURA (primary)

- Root: /Users/ultraviollett/projectSHURA
- Branch: shura-foundation
- Upstream: origin → https://github.com/ultraviollettnympho/projectSHURA.git (push/fetch)
- Fork upstream: upstream → https://github.com/emqnuele/projectBEA.git
- Status: 10 staged, 9 modified, 3 untracked
- Recent commits: 7f7f020 (embodiment SHURA_02 3D viewer), d09d64a (merge agent contracts), 13909b2 (loop state update + Command Center UI)
- Build system: pyproject.toml (uv/hatchling), Python package `projectshura`
- Frontend: React/Vite (src/web/frontend/)
- Tests: 175 total, 172 passing, 1 failing, 2 skipped

### INFAC

- Root: /Users/ultraviollett/INFAC (contains INFAC-foundation-2026-09-28 subdir + IDEA.md)
- Active repo: /Users/ultraviollett/ultraviollettnympho_INFAC (git repo, 22 commits, Vercel deployed)
- Agent fleet: 7 roles defined (.agents/roles/)
- Docs: extensive (ROADMAP_V0.3.md, DESIGN_CONSTITUTION.md, INFAC_AGENT_CONSTITUTION.md, etc.)

### INFAC-foundation-2026-09-28

- Root: /Users/ultraviollett/INFAC/INFAC-foundation-2026-09-28
- NOT a git repository (no .git)
- React/Vite app (package.json, vite.config.ts, src/, public/, docs/)
- Appears to be a snapshot/export of the INFAC site foundation

---

## 8. BUNDLES AND DOWNLOADS

Located in /Users/ultraviollett/Downloads/:

| File | Size | Notes |
|---|---|---|
| ProjectBEA Setup Review (1).pdf | 3.1 MB | Aug 10 — older |
| ProjectBEA Setup Review (2).pdf | 714 KB | Aug 10 |
| ProjectBEA Setup Review.pdf | 2.1 MB | Aug 10 |
| ChatGPT-ProjectBEA Setup Review.md | 351 KB | Aug 10 |
| ChatGPT-ProjectSHURA Workspace Setup.md | 58 KB | Aug 10 |
| ChatGPT-ProjectSHURA_Workspace_Setup.md.docx | 640 KB | Aug 10 |
| SHURA Master Specification — Identity & Behavioral Core.md | 13 KB | Sep 8 — identity doc |
| SHURA_02_Blender_Pipeline_Hermes.md | 8.7 KB | Sep 22 — embodiment pipeline guidance |
| 58f52c2c_shura_02_motion_set.blend | 12.9 MB | Sep 21 — Blender motion set |
| 6a64790e_shura_02_motion_set.glb | 5.9 MB | Sep 21 — glTF motion set |

No singular "project bundle" file found. The SHURA Master Specification and Blender Pipeline doc are the most relevant downloaded artifacts. The 3D motion assets (shura_02) are already integrated into the repo (src/web/frontend/src/components/embodiment/Viewer.jsx recently modified for Three.js/GLTFLoader).

---

## 9. STATE / MEMORY

### Hermes state.db

- Path: /Users/ultraviollett/.hermes/profiles/shura/state.db (20.8 MB)
- Tables: sessions, messages (2829 rows), async_delegations (1 row), gateway_heartbeats (79 rows), session_model_usage, system_prompts, compression_locks, conversation_generations, etc.
- WAL mode active (state.db-wal 4.1 MB, state.db-shm 32 KB)

### Session

- Current session ID: 20260930_045910_500b02
- Session source: desktop
- Session scope: isolated (no parent chat context)

### Memory

- profiles/shura/memories/ directory present (6 dirs deep)
- profiles/shura/.skills_prompt_snapshot.json (73 KB) — skills prompt snapshot
- profiles/shura/auth.json — credential pool (providers dict, credential_pool dict)
- profiles/shura/provider_models_cache.json (18 KB)
- profiles/shura/models_dev_cache.json (5.2 MB)

### Cron

- profiles/shura/cron/ directory with executions.db, ticker_heartbeat, ticker_last_success, output/

### Logs

- profiles/shura/logs/curator/
- profiles/shura/logs/process-results/
- profiles/shura/logs/ (14 subdirs)

---

## 10. ENVIRONMENT VARIABLES (relevant)

### API keys (redacted in env display, names confirmed)

HF_TOKEN, OPENROUTER_API_KEY, AIHUBMIX_API_KEY, MCP_MAJIKS_STUDIO_API_KEY, GMI_API_KEY, GROQ_API_KEY, GOOGLE_API_KEY, MINIMAX_API_KEY, DEEPSEEK_API_KEY, OLLAMA_API_KEY, ARCEEAI_API_KEY, DEEPINFRA_API_KEY, COMMANDCODE_API_KEY, MODEL_API_KEY, GLM_API_KEY, UPSTAGE_API_KEY, TELEGRAM_BOT_TOKEN (partial), WHATSAPP_ALLOWED_USERS

### Hermes runtime

HERMES_AGENT=true, HERMES_SESSION_PROFILE=shura, HERMES_SESSION_ID=20260930_045910_500b02, HERMES_HOME=/Users/ultraviollett/.hermes/profiles/shura, HERMES_REAL_HOME=/Users/ultraviollett, HERMES_DESKTOP=1, HERMES_QUIET=1, HERMES_MAX_ITERATIONS=150, HERMES_REDACT_SECRETS=true

### Provider base URLs

ANTHROPIC_BASE_URL=http://localhost:8082 (local proxy?)

### Project-specific

AI_AGENT=hermes-agent, TERMINAL_ENV=local, WHATSAPP_MODE=self-chat

---

## 11. AVAILABLE TOOLING (Hermes tools)

Direct tools available to SHURA in this runtime:

- read_file, write_file, patch, search_files
- terminal (foreground + background)
- execute_code (persistent Python kernel with hermes_tools)
- browser_exec, browser_vault_* (web automation)
- delegate_task (spawn subagents)
- clarify (ask user questions)
- memory (persistent notes)
- skill_view, skill_manage, skills_list
- text_to_speech
- web_search, web_extract
- vision_analyze
- tool_search, tool_describe, tool_call
- cronjob_manage (deferred)
- session_search (deferred)
- desktop_ui tools (deferred)
- image_generate (deferred)

---

## 12. DIRECTORY MAP (relevant locations)

```
~/.hermes/profiles/shura/          # active Hermes profile
  config.yaml                      # 4065-line config
  auth.json                        # credential pool
  skills/                          # 142 skills
  plugins/                         # 10 plugins
  memories/                        # persistent memory
  logs/                            # session logs
  state.db                         # session state (SQLite)
  cron/                            # cron jobs
  bin/tirith                       # security binary

~/projectSHURA/                    # primary repo (shura-foundation)
~/INFAC/                           # INFAC context dir
~/INFAC/INFAC-foundation-2026-09-28/  # INFAC site snapshot (no .git)
~/ultraviollettnympho_INFAC/       # INFAC live repo (git, Vercel)
~/Downloads/                       # bundles/docs/3D assets
```

---

## 13. OPEN QUESTIONS (unverified at inventory time)

- Freebuff: not found. Status unknown.
- OpenClaw: onboarding flag suggests prior cleanup; no active integration confirmed.
- gstack as named external tool: not found; methodology appears distributed across skills + AGENTS.md.
- Ollama process: not running locally despite ollama-launch provider configured.
- omniroute: configured but local process not verified running.
- Hivemind CLI: skill references it; not verified installed on this machine.
- REAPER MCP: configured in config.yaml; binary at /Library/Frameworks/.../reaper-mcp; REAPER app not confirmed running.
- Majik Studio MCP: configured, port 8478, auth required; not verified connected.
- HuggingFace MCP: configured with oauth; not verified connected.
- Amplitude MCP: configured with oauth; not verified connected.
