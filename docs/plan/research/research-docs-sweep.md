# Harness-creator raw data sweep of `.tmp/docs_claude` (163 files, Claude Code docs snapshot ~mid-2026, CLI ≈ v2.1.200)

All paths below are relative to `/Users/seongjin/Documents/Coding/harness-creator/.tmp/docs_claude/`.

---

## 1. SKILLS AUTHORING
**Source:** `02-build-with-claude-code/03-skills/01-extend-claude-with-skills.md` (authoritative, 865 lines). Secondary: `06-agent-sdk/05-customize-behavior/03-skills.md`, `05-reference/08-plugins-reference.md` (plugin skills).

### Format
- Skill = directory with `SKILL.md` (required entrypoint) + optional supporting files (`reference.md`, `examples/`, `scripts/`, `template.md`). Reference supporting files FROM SKILL.md with markdown links so Claude knows when to load them.
- SKILL.md = YAML frontmatter between `---` markers + markdown body. **All frontmatter fields are optional; only `description` is recommended.** If frontmatter YAML is malformed, the body still loads with empty metadata (`/skill-name` works but no auto-invocation matching).
- Follows the agentskills.io open standard; Claude Code extends it (invocation control, subagent execution, dynamic context injection).

### Locations & precedence (same name across levels: enterprise > personal > project; any level overrides a bundled skill)
| Level | Path |
|---|---|
| Enterprise | managed settings dir `.claude/skills/` |
| Personal | `~/.claude/skills/<name>/SKILL.md` |
| Project | `.claude/skills/<name>/SKILL.md` |
| Plugin | `<plugin>/skills/<name>/SKILL.md` → namespaced `/plugin-name:skill-name` |
- Project skills load from `.claude/skills/` in the starting dir AND every parent up to repo root; nested `.claude/skills/` in subdirectories load on demand when Claude works with files there (name clash → directory-qualified `apps/web:deploy`).
- Symlinked skill directories are followed; deduped when reachable twice.
- Live change detection: SKILL.md edits apply within the session; a brand-new top-level skills dir requires restart. `/reload-skills` re-scans manually.
- `--add-dir`/`/add-dir` DO load `.claude/skills/` (exception); `permissions.additionalDirectories` does NOT.
- A skill folder containing `.claude-plugin/plugin.json` becomes a plugin `<name>@skills-dir` (can bundle agents/hooks/MCP). Scaffold with `claude plugin init <name>` (writes to `~/.claude/skills/<name>/`).

### Frontmatter fields (exact)
| Field | Notes |
|---|---|
| `name` | Display name only; command name comes from directory name (or filename for `.claude/commands/*.md`; or frontmatter `name` only for plugin-root SKILL.md) |
| `description` | What+when. Claude auto-invokes based on it. If omitted, first paragraph of body used. Combined `description`+`when_to_use` truncated at **1,536 chars** in the listing (configurable via `skillListingMaxDescChars`) |
| `when_to_use` | Extra trigger context, appended to description, counts toward 1,536 cap |
| `argument-hint` | e.g. `[issue-number]`, shown in autocomplete |
| `arguments` | Named positional args (space-separated string or YAML list) → `$name` substitution |
| `disable-model-invocation` | `true` = user-only; description NOT in context (zero context cost); also blocks preloading into subagents and (v2.1.196+) scheduled-task invocation. Default `false` |
| `user-invocable` | `false` = hidden from `/` menu (Claude-only background knowledge). Default `true`. Controls menu visibility only, not Skill-tool access |
| `allowed-tools` | Tools pre-approved (no permission prompt) while skill active; space/comma-separated or YAML list; does NOT restrict availability. Supports permission-rule syntax e.g. `Bash(git add *)`. Project-skill `allowed-tools` gated by workspace trust |
| `disallowed-tools` | Removes tools from pool while active; clears on next user message |
| `model` | Model override for rest of turn (same values as `/model`, or `inherit`) |
| `effort` | `low|medium|high|xhigh|max` |
| `context` | `fork` = run in forked subagent; skill body becomes the subagent prompt |
| `agent` | Subagent type for `context: fork` (`Explore`, `Plan`, `general-purpose`, or custom from `.claude/agents/`; default `general-purpose`) |
| `hooks` | Hooks scoped to skill lifecycle (same schema as settings hooks) |
| `paths` | Glob patterns limiting auto-activation to matching files (same format as rules `paths`) |
| `shell` | `bash` (default) or `powershell` for `!` injection blocks |

### String substitutions in body
`$ARGUMENTS`, `$ARGUMENTS[N]`, `$N` (0-based shorthand), `$name` (from `arguments`), `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}` (skill's own dir), `${CLAUDE_PROJECT_DIR}` (v2.1.196+, also works in `allowed-tools`). Escape literal `$` with `\$`. Args use shell-style quoting. If skill has no `$ARGUMENTS` but user passes args, `ARGUMENTS: <value>` is appended.

### Dynamic context injection (preprocessing, not model-executed)
- `` !`command` `` inline (only at line start or after whitespace) and ```` ```! ```` fenced blocks for multi-line. Output replaces placeholder before Claude sees content. Single pass, no recursion. Disable via `disableSkillShellExecution: true` setting.

### Size/budget limits
- **Keep SKILL.md under 500 lines** (explicit docs tip); move detail to supporting files.
- Skill listing context budget: **1% of context window** default (`skillListingBudgetFraction`, e.g. `0.02`; or `SLASH_COMMAND_TOOL_CHAR_BUDGET` env for fixed chars). Overflow → least-used skills' descriptions collapsed to bare names. `/doctor` reports truncation.
- Lifecycle: invoked skill content stays in context all session (never re-read). Compaction re-attaches most recent invocation of each skill: first **5,000 tokens each**, shared **25,000-token budget**, most-recent-first.
- Skill stacking: up to 6 skills in one message (`/a /b args`), v2.1.199+.

### Invocation matrix
| Frontmatter | User | Claude | Context |
|---|---|---|---|
| default | yes | yes | description always in context; full content on invoke |
| `disable-model-invocation: true` | yes | no | nothing until invoked |
| `user-invocable: false` | no | yes | description always in context |

### Permission control over skills
`Skill` deny rule disables all; `Skill(name)` exact / `Skill(name *)` prefix rules. `skillOverrides` setting (per-skill: `"on"|"name-only"|"user-invocable-only"|"off"`), written by `/skills` menu to `.claude/settings.local.json`; doesn't apply to plugin skills.

### Evaluation
`skill-creator` plugin (`/plugin install skill-creator@claude-plugins-official`): evals in `evals/evals.json` inside skill dir, `grading.json`, `benchmark.json`, blind A/B version comparison, description tuning (should/shouldn't-trigger prompts).

---

## 2. CLAUDE.md / MEMORY
**Source:** `01-getting-started/05-use-claude-code/01-memory.md` (authoritative). Best practices: `01-getting-started/05-use-claude-code/06-best-practices.md`. Decision framework: `01-getting-started/04-core-concepts/02-extend-claude-code.md`.

### Locations (load order broad→specific)
| Scope | Location |
|---|---|
| Managed policy | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux/WSL `/etc/claude-code/CLAUDE.md`; Windows `C:\Program Files\ClaudeCode\CLAUDE.md`; or `claudeMd` string key in managed-settings.json |
| User | `~/.claude/CLAUDE.md` |
| Project | `./CLAUDE.md` **or** `./.claude/CLAUDE.md` |
| Local | `./CLAUDE.local.md` (gitignore it) |

### Loading semantics
- All files **concatenate** (additive), never override. Order: filesystem root down to cwd; within a dir, `CLAUDE.local.md` appended after `CLAUDE.md`. Walks UP the tree from cwd (parents load in full at launch); subdirectory CLAUDE.md files load lazily when Claude reads files there.
- Delivered as a **user message after the system prompt**, not system prompt itself — advisory, not enforced. For enforcement use hooks; for system-prompt-level text use `--append-system-prompt`.
- Block-level HTML comments (`<!-- -->`) stripped before injection (free maintainer notes); preserved inside code blocks.
- Project-root CLAUDE.md survives `/compact` (re-read+re-injected); nested ones reload on next file access.
- `--add-dir` dirs: CLAUDE.md NOT loaded unless `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`.
- `claudeMdExcludes` setting (glob/abs paths vs absolute file paths, merges across scopes) skips files; managed files can't be excluded.

### Imports
- `@path/to/file` anywhere in CLAUDE.md; relative resolves against the importing file; recursion max **4 hops**; expanded at launch (imports do NOT save context). Backticks suppress import (`` `@README` `` literal). First external-import encounter shows an approval dialog. `@~/...` home paths work (share personal notes across worktrees). AGENTS.md interop: `@AGENTS.md` import or symlink `ln -s AGENTS.md CLAUDE.md`.

### `.claude/rules/` (project) and `~/.claude/rules/` (user)
- All `.md` files discovered recursively; symlinks OK (circulars handled). Rules without `paths` frontmatter load at launch with same priority as `.claude/CLAUDE.md`. User rules load before project rules.
- Path-scoped rules: YAML frontmatter `paths:` list of globs (`**/*.ts`, brace expansion `src/**/*.{ts,tsx}`); load only when Claude reads matching files (v2.1.198+ also via symlinked paths).

### Best-practice content rules (for generation)
- Target **under 200 lines** per CLAUDE.md; longer reduces adherence.
- Include: build/test commands Claude can't guess, style rules that differ from defaults, repo etiquette, architecture decisions, env quirks, gotchas. Exclude: anything inferable from code, standard conventions, API docs, frequently-changing info, "write clean code" platitudes.
- Concrete & verifiable ("Use 2-space indentation" not "format properly"). Markdown headers+bullets. Consistency: conflicting rules → arbitrary pick. Emphasis ("IMPORTANT", "YOU MUST") boosts adherence.
- Test: "Would removing this cause mistakes?" If a rule is a multi-step procedure → skill; path-specific → rule; must-always-happen → hook.
- `/init` generates starter CLAUDE.md (reads AGENTS.md, `.cursorrules`, `.devin/rules/`, `.windsurfrules`); `CLAUDE_CODE_NEW_INIT=1` enables interactive multi-phase flow that sets up CLAUDE.md + skills + hooks.

### Auto memory (Claude-written)
- On by default (v2.1.59+; `autoMemoryEnabled: false` or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`). Stored `~/.claude/projects/<project>/memory/` (keyed to git repo; shared across worktrees); `autoMemoryDirectory` setting relocates (trust-gated from project settings). `MEMORY.md` index loaded at session start — **first 200 lines or 25KB whichever first**; topic files loaded on demand. Subagents get own memory via agent `memory: user|project|local` field → `~/.claude/agent-memory/<name>/`, `.claude/agent-memory/<name>/`, `.claude/agent-memory-local/<name>/` (same 200-line/25KB MEMORY.md rule).

---

## 3. SETTINGS.JSON
**Source:** `04-configuration/01-settings-and-permissions/01-settings.md` (full key table). Permissions: `.../02-permissions.md`.

### Files & precedence (highest→lowest)
1. **Managed** (server-managed > MDM plist/registry > file `managed-settings.json` + `managed-settings.d/*.json` alphabetical merge > HKCU). File locations: macOS `/Library/Application Support/ClaudeCode/`, Linux `/etc/claude-code/`, Windows `C:\Program Files\ClaudeCode\`. `policyHelper` executable output beats all.
2. CLI args (`--settings <file-or-json>` merges)
3. `.claude/settings.local.json` (gitignored when Claude Code creates it)
4. `.claude/settings.json` (committed, team)
5. `~/.claude/settings.json` (user)
- Scalars override; **arrays concatenate+dedupe across scopes** (exceptions: `fallbackModel` — whole chain from highest scope; `availableModels` in managed).
- `$schema`: `https://json.schemastore.org/claude-code-settings.json`.
- Hot reload: most keys (incl. `permissions`, `hooks`, `apiKeyHelper`) apply live; `model` and `outputStyle` need restart/`/clear`. `ConfigChange` hook fires per change. User/project/local files validate strictly (whole file rejected on error); managed parse tolerantly (bad entry stripped).
- Other config in `~/.claude.json`: OAuth, user/local-scope MCP servers, per-project state (trust, allowed tools), caches; also `autoConnectIde`, `autoInstallIdeExtension`, `externalEditorContext`, `teammateDefaultModel`.

### Key settings for harness generation (selection from full table)
- `permissions`: `{allow, ask, deny, additionalDirectories, defaultMode, disableBypassPermissionsMode, skipDangerousModePermissionPrompt}`. `defaultMode` values: `default`(alias `manual` v2.1.200+), `acceptEdits`, `plan`, `auto` (ignored in project/local settings), `dontAsk`, `bypassPermissions`.
- `hooks`: see §4. `disableAllHooks: true` kills all hooks + custom statusline. `allowedHttpHookUrls` (URL allowlist, merges), `httpHookAllowedEnvVars`, `allowManagedHooksOnly` (managed only).
- `env`: object of env vars applied to every session + subprocesses.
- `model` (default model; `--model`/`ANTHROPIC_MODEL` override per session), `fallbackModel` (array, ≤3, no merge), `availableModels`, `effortLevel` (`low|medium|high|xhigh`), `alwaysThinkingEnabled`, `outputStyle`, `language`, `theme`, `editorMode`, `autoUpdatesChannel`, `cleanupPeriodDays` (default 30, min 1), `spinnerVerbs`, `spinnerTipsOverride`, `companyAnnouncements`.
- `statusLine`: `{type:"command", command:"~/.claude/statusline.sh", padding?, refreshInterval? (min 1s), hideVimModeIndicator?}`.
- `attribution`: `{commit, pr, sessionUrl}` (empty string hides; replaces deprecated `includeCoAuthoredBy`). Default commit trailer `Co-Authored-By: Claude <model> <noreply@anthropic.com>`; default PR `🤖 Generated with [Claude Code](...)`.
- `agent`: run the main thread as a named subagent (project default agent).
- Skills-related: `skillOverrides`, `skillListingBudgetFraction` (default 0.01), `skillListingMaxDescChars` (default 1536), `disableBundledSkills`, `disableSkillShellExecution`.
- Memory-related: `autoMemoryEnabled`, `autoMemoryDirectory`, `claudeMd` (managed only), `claudeMdExcludes`, `includeGitInstructions`.
- Plugins: `enabledPlugins` (`"name@marketplace": true/false`; project beats user; local opts out; a plugin with no entry uses its `defaultEnabled`), `extraKnownMarketplaces` (named entries `{source:{source:"github"|"git"|"directory"|"hostPattern"|"settings", ...}, autoUpdate?}`), managed-only `strictKnownMarketplaces` (direct source objects; `[]`=lockdown), `blockedMarketplaces`, `strictPluginOnlyCustomization` (`true` or subset of `["skills","agents","hooks","mcp"]` — blocks user+project sources for those surfaces), `pluginTrustMessage`, `disableSideloadFlags`.
- MCP: `enableAllProjectMcpServers`, `enabledMcpjsonServers`, `disabledMcpjsonServers`, managed `allowedMcpServers`/`deniedMcpServers`/`allowManagedMcpServersOnly`, `disableClaudeAiConnectors`.
- `sandbox`: `{enabled, autoAllowBashIfSandboxed (default true), excludedCommands, allowUnsandboxedCommands, filesystem:{allowWrite,denyWrite,denyRead,allowRead}, network:{allowedDomains,deniedDomains,allowUnixSockets,allowLocalBinding,httpProxyPort,...}, credentials:{files,envVars}}`. Sandbox path prefixes: `/`=absolute, `~/`, `./`/bare = relative to project root (project settings) or `~/.claude` (user settings) — **differs from Read/Edit rule syntax where `//`=absolute, `/`=settings-source-relative**.
- `worktree`: `{baseRef:"fresh"|"head", symlinkDirectories, sparsePaths, bgIsolation}`.
- `plansDirectory` (default `~/.claude/plans`), `autoCompactEnabled`, `fileCheckpointingEnabled`, `footerLinksRegexes` (user/managed only), `fileSuggestion`, `askUserQuestionTimeout`, `verbose`, `viewMode`, `tui`.

### Permission rule syntax (§ `02-permissions.md`)
- Format `Tool` or `Tool(specifier)`. Evaluation order: **deny → ask → allow, first match wins; specificity irrelevant**. Deny at any scope beats allow anywhere.
- Bare deny `Bash` removes tool from context entirely; scoped `Bash(rm *)` blocks matching calls.
- Bash: `*` glob at any position, spans spaces (`Bash(git * main)`); trailing ` *` enforces word boundary (`ls *` ≠ `lsof`); `:*` suffix = trailing wildcard. Compound commands: each subcommand must match independently (separators `&&`, `||`, `;`, `|`, `|&`, `&`, newlines). Wrappers stripped before match: `timeout,time,nice,nohup,stdbuf`, bare `xargs`. `watch/setsid/ionice/flock`, `find -exec/-delete` always prompt. Built-in read-only command set runs without prompt (not configurable; override via ask/deny rule).
- Read/Edit: gitignore semantics. `//path` abs, `~/path` home, `/path` relative to **settings source** (project root for project settings, `~/.claude` for user settings), `path`/`./path` cwd-relative. Bare filename matches at any depth (`Read(.env)` ≡ `Read(**/.env)`). Symlinks: allow needs both link+target to match; deny if either matches. Applies to file tools + recognized Bash file commands, NOT arbitrary subprocesses (use sandbox).
- `WebFetch(domain:example.com)`, wildcard `*.example.com` (subdomains only, not apex).
- MCP: `mcp__server`, `mcp__server__tool`; allow-rule tool-position globs only after literal `mcp__<server>__` prefix; deny/ask accept full globs (`*`, `mcp__*`).
- `Agent(AgentName)` gates subagents; `Skill(name)`/`Skill(name *)`; `Cd(pattern)` for `/cd`; param matching `Tool(param:value)` for deny/ask only (not for canonicalized fields like `command`/`file_path`).
- Workspace trust: project `.claude/settings.json` **allow rules and additionalDirectories apply only after trust dialog accepted**; deny/ask always apply. `settings.local.json` usually exempt (unless repo-committed).

---

## 4. HOOKS
**Source:** `05-reference/07-hooks-reference.md` (authoritative, 3100 lines). Guide: `02-build-with-claude-code/06-automation/01-automate-with-hooks.md`.

### Config schema (in any settings file, plugin `hooks/hooks.json`, or skill/agent frontmatter)
```json
{"hooks": {"<Event>": [{"matcher": "<pattern>", "hooks": [{"type":"command","command":"...","args":[],"if":"Bash(git *)","timeout":600,"async":true,"statusMessage":"...","once":true}]}]}}
```
3 levels: event → matcher group → handler array. All matching hooks run in parallel, deduped by command+args (command) or URL (http).

### Handler types (5)
- `command`: shell. `args` present = **exec form** (direct spawn, no shell, placeholders substituted per-arg); absent = shell form (`sh -c`/Git Bash/PowerShell; `shell: "bash"|"powershell"` field). `async: true` background; `asyncRewake` wakes Claude on exit 2.
- `http`: POST JSON to `url`; `headers` with env interpolation gated by `allowedEnvVars`. Non-2xx = non-blocking; must return 2xx+JSON to block.
- `mcp_tool`: `{server, tool, input}` with `${tool_input.file_path}`-style substitution from hook input.
- `prompt`: single LLM call; `prompt` with `$ARGUMENTS` placeholder; model defaults fast; responds `{"ok": true|false, "reason": "..."}`; `continueOnBlock` option.
- `agent`: experimental subagent verifier (Read/Grep/Glob, ≤50 turns, default timeout 60s), same `{ok}` schema.
- Timeouts: 600s default for command/http/mcp_tool (UserPromptSubmit 30s, MessageDisplay 10s, SessionEnd 1.5s budget), 30s prompt, 60s agent.
- `once: true` honored only in skill frontmatter hooks.
- `if` field: one permission rule, tool events only; best-effort (fails open on unparseable Bash).

### Events (complete list)
`SessionStart` (matchers startup|resume|clear|compact), `Setup` (init|maintenance; only with `--init-only`/`-p --init`/`-p --maintenance`), `UserPromptSubmit`, `UserPromptExpansion` (matcher=command name; fires on `/skill` typed path that bypasses PreToolUse), `PreToolUse`, `PermissionRequest`, `PermissionDenied` (auto-mode classifier only), `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Notification` (matchers permission_prompt|idle_prompt|auth_success|elicitation_*|agent_needs_input|agent_completed), `MessageDisplay`, `SubagentStart`/`SubagentStop` (matcher=agent type; plugin agents = `plugin:name`, colon forces regex path → anchor `^...$`), `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure` (matcher=error type), `TeammateIdle`, `InstructionsLoaded` (matcher=load_reason: session_start|nested_traversal|path_glob_match|include|compact), `ConfigChange` (matcher user_settings|project_settings|local_settings|policy_settings|skills; can block except policy), `CwdChanged`, `FileChanged` (matcher = literal filenames split on `|`, builds watch list), `WorktreeCreate` (replaces git worktree creation; must print worktree path), `WorktreeRemove`, `PreCompact`/`PostCompact` (manual|auto), `Elicitation`/`ElicitationResult`, `SessionEnd` (matcher = reason).

### Matcher semantics
`"*"`/`""`/omitted = all. Alnum+`_-`, spaces, `,`, `|` = exact string or `|`/`,`-separated list. Any other char = **unanchored JS regex** (`Edit.*` matches `NotebookEdit`; anchor with `^$`). MCP tools: `mcp__server__.*` (bare `mcp__server` is exact-match and matches nothing). Events without matcher support: UserPromptSubmit, PostToolBatch, Stop, TeammateIdle, TaskCreated/Completed, WorktreeCreate/Remove, MessageDisplay, CwdChanged.

### I/O protocol
- Input: JSON on stdin (command) / POST body (http). Common fields: `session_id, prompt_id, transcript_path, cwd, permission_mode, effort, hook_event_name` (+`agent_id`,`agent_type` in subagents; event-specific `tool_name`,`tool_input`,`tool_use_id`,`tool_response`...).
- **Exit 0** = success; stdout parsed as JSON output (only on exit 0). **Exit 2** = blocking error, stderr fed to Claude (per-event effects table; PreToolUse blocks call, Stop prevents stopping, UserPromptSubmit erases prompt...). **Exit 1/other** = non-blocking error. Only exit 2 blocks (except WorktreeCreate: any non-zero fails creation).
- JSON output universal fields: `continue` (false = stop entirely), `stopReason`, `suppressOutput`, `systemMessage`, `terminalSequence` (allowlisted OSC 0/1/2/9/99/777+BEL, v2.1.141+). Output strings capped 10,000 chars (spilled to file beyond).
- Decision patterns: top-level `decision:"block"`+`reason` (UserPromptSubmit, UserPromptExpansion, PostToolUse, PostToolUseFailure, PostToolBatch, Stop, SubagentStop, ConfigChange, PreCompact). PreToolUse: `hookSpecificOutput.{permissionDecision: allow|deny|ask|defer, permissionDecisionReason, updatedInput, additionalContext}` (deny>defer>ask>allow across hooks; deprecated top-level approve/block). PermissionRequest: `hookSpecificOutput.decision.{behavior: allow|deny, updatedInput, updatedPermissions, message, interrupt}`; `updatedPermissions` entries `{type: addRules|replaceRules|removeRules|setMode|addDirectories|removeDirectories, destination: session|localSettings|projectSettings|userSettings}`. PostToolUse: `updatedToolOutput` (must match tool output shape). `additionalContext` in `hookSpecificOutput` injects a system reminder (works on SessionStart/Setup/SubagentStart/UserPromptSubmit/PreToolUse/PostToolUse/PostToolBatch/Stop/SubagentStop...). SessionStart extras: `initialUserMessage`, `sessionTitle`, `watchPaths`, `reloadSkills`. Hooks that block must use permission system for hard guarantees (hook `if` fails open).
- SessionStart/Setup/CwdChanged/FileChanged get `CLAUDE_ENV_FILE` env var — append `export` lines there to persist env vars into session Bash commands.
- Path placeholders: `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` (also exported as env vars). Prefer exec form with these.
- Stop-hook loop protection: `stop_hook_active` input flag; hard cap of 8 consecutive blocks. Stop input includes `last_assistant_message`, `background_tasks[]`, `session_crons[]`.
- SessionStart/Setup support only `command`+`mcp_tool` types. 13 events support all 5 types (PreToolUse, PostToolUse, Stop, UserPromptSubmit, etc.).
- Locations: `~/.claude/settings.json` / `.claude/settings.json` / `.claude/settings.local.json` / managed / plugin `hooks/hooks.json` / skill+agent frontmatter. `/hooks` menu is read-only.

---

## 5. SUBAGENTS (`.claude/agents/`)
**Source:** `02-build-with-claude-code/01-agents-and-parallel-work/01-create-custom-subagents.md`. Also `05-reference/08-plugins-reference.md` (plugin agents).

- Markdown file, YAML frontmatter + body = subagent's **system prompt** (replaces default; subagent gets only this + env details, not full CC system prompt).
- Scope priority: managed settings `.claude/agents/` (1) > `--agents` CLI JSON (2) > project `.claude/agents/` (3) > `~/.claude/agents/` (4) > plugin `agents/` (5). Scanned recursively; identity = `name` field, not filename; same-scope duplicate names → only one loads (`/doctor` reports, v2.1.196+). Nested project dirs: closest to cwd wins (v2.1.178+). File watcher: live edits apply; new agents dir needs restart. v2.1.198+: `/agents` wizard removed — write files directly.

### Frontmatter (only `name` and `description` required)
| Field | Notes |
|---|---|
| `name` | lowercase+hyphens; hooks receive as `agent_type` |
| `description` | when Claude should delegate ("use proactively" encourages) |
| `tools` | allowlist (inherits all if omitted); `Agent(worker, researcher)` syntax restricts spawnable types (main-thread `--agent` only) |
| `disallowedTools` | denylist, applied before `tools`; MCP patterns `mcp__server`, `mcp__server__*`, `mcp__*` |
| `model` | `sonnet|opus|haiku|fable|<full-id>|inherit` (default inherit). Resolution: `CLAUDE_CODE_SUBAGENT_MODEL` env > per-invocation param > frontmatter > main model; checked against `availableModels` |
| `permissionMode` | `default|acceptEdits|auto|dontAsk|bypassPermissions|plan|manual`; ignored for plugin agents; parent bypassPermissions/acceptEdits/auto override |
| `maxTurns` | turn cap |
| `skills` | list preloaded FULL content at startup (can't preload `disable-model-invocation` skills); unlisted skills still invocable via Skill tool |
| `mcpServers` | name refs to existing servers or inline defs (same schema as .mcp.json; stdio/http/sse/ws); ignored for plugin agents |
| `hooks` | scoped to agent lifetime; `Stop` auto-converts to `SubagentStop`; ignored for plugin agents |
| `memory` | `user|project|local` → persistent `agent-memory/<name>/` dir; auto-enables Read/Write/Edit; MEMORY.md first 200 lines/25KB in system prompt |
| `background` | `true` = always background (v2.1.198+ background is default anyway) |
| `effort` | `low|medium|high|xhigh|max` |
| `isolation` | `worktree` = temp git worktree |
| `color` | `red|blue|green|yellow|purple|orange|pink|cyan` |
| `initialPrompt` | auto-submitted first user turn when run as main session (`--agent`) |
- Plugin agents: NO `hooks`/`mcpServers`/`permissionMode` (security). Support `name, description, model, effort, maxTurns, tools, disallowedTools, skills, memory, background, isolation`.
- Built-ins: `Explore` (read-only, skips CLAUDE.md+git status), `Plan` (same skips), `general-purpose` (all tools). Explore/Plan are one-shot (no resume). Custom subagent named `Explore` overrides built-in.
- Non-fork subagent startup context: own system prompt + delegation message + full CLAUDE.md hierarchy + git status (Explore/Plan skip both) + preloaded skills. Tools unavailable in subagents: AskUserQuestion, EnterPlanMode, ExitPlanMode (unless plan mode), ScheduleWakeup, WaitForMcpServers. Nesting to depth 5.
- Invocation: auto-delegate by description; `@agent-<name>` mention; `claude --agent <name>` or `"agent"` setting = run main thread as agent.
- Disable: `permissions.deny: ["Agent(Explore)"]`, `--disallowedTools`, `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1`, deny `Agent` tool entirely.

---

## 6. OUTPUT STYLES
**Source:** `04-configuration/02-model-and-responses/04-output-styles.md`.
- Markdown files: user `~/.claude/output-styles/`, project `.claude/output-styles/` (loads from every dir up to repo root; closest wins on clash, v2.1.178+), managed policy dir, plugin `output-styles/`.
- Frontmatter: `name` (defaults to filename), `description`, `keep-coding-instructions` (default **false** — leaving it off strips CC's built-in SWE instructions), `force-for-plugin` (plugin only — auto-applies while enabled, overrides user `outputStyle`).
- Instructions appended to END of system prompt; reminders re-inject during conversation. Selection: `outputStyle` setting (via `/config`, saved to `.claude/settings.local.json`); takes effect after `/clear`/restart. Built-ins: Default, Proactive, Explanatory, Learning. `/output-style` command removed in v2.1.91.
- NOT discovered from `--add-dir` dirs.

---

## 7. SLASH COMMANDS — CURRENT STATE
**Sources:** `05-reference/02-commands.md`, skills doc §Note, `06-agent-sdk/05-customize-behavior/02-slash-commands.md`.
- **Custom commands are MERGED into skills.** `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`, same mechanism, same frontmatter support. `.claude/commands/` files keep working; skills recommended (supporting files, invocation control, auto-load). Name clash: skill wins over command. Command name = filename without extension; subdirectory shows in description but doesn't change the name (SDK doc).
- Command frontmatter observed in SDK doc: `allowed-tools`, `description`, `model`, `argument-hint` — same set as skills.
- Built-in commands are separate (coded in CLI): `/init`, `/memory`, `/permissions`, `/hooks`, `/config`, `/mcp`, `/plugin`, `/skills`, `/agents` (now just prints reminder), `/statusline`, `/context`, `/compact`, `/clear`, `/rewind`, `/model`, `/effort`, `/doctor`, `/cd`, `/add-dir`, etc. Bundled **skills** (prompt-based, can be overridden by project skill of same name, removable via `disableBundledSkills`): `/code-review`, `/batch`, `/debug`, `/loop`, `/claude-api`, `/run`, `/verify`, `/run-skill-generator`, `/simplify`, `/fewer-permission-prompts`, `/dataviz`, `/design-sync`. Bundled **workflows**: `/deep-research`. A few built-ins exposed to the model through Skill tool: `/init`, `/review`, `/security-review`.
- MCP prompts appear as `/mcp__<server>__<prompt>`.

---

## 8. PLUGINS & MARKETPLACES
**Sources:** `05-reference/08-plugins-reference.md` (schema), `03-administration/05-plugin-distribution/01-plugin-marketplaces.md` (marketplace.json), `02-build-with-claude-code/04-plugins/02-create-plugins.md`.

### Plugin layout
`.claude-plugin/plugin.json` (manifest, optional — auto-discovery + dir name if absent). Components at plugin ROOT (never inside `.claude-plugin/`): `skills/` (dirs w/ SKILL.md), `commands/` (flat .md, legacy), `agents/`, `output-styles/`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`, `themes/`, `monitors/monitors.json`, `bin/` (added to Bash PATH), `settings.json` (only `agent` and `subagentStatusLine` keys honored), `scripts/`. Root `CLAUDE.md` is NOT loaded — plugins contribute context only via skills/agents/hooks.

### plugin.json fields
Required: `name` (kebab-case). Metadata: `$schema` (`https://json.schemastore.org/claude-code-plugin-manifest.json`), `displayName`, `version` (semver; omit → git SHA versioning = update on every commit), `description`, `author{name,email,url}`, `homepage`, `repository`, `license`, `keywords`, `defaultEnabled` (v2.1.154+). Component paths (must start `./`): `skills` (ADDS to default scan), `commands`/`agents`/`outputStyles`/`experimental.themes`/`experimental.monitors` (REPLACE defaults), `hooks`/`mcpServers`/`lspServers` (path|array|inline object, merge). `userConfig` (prompted at enable; fields `type: string|number|boolean|directory|file`, `title`, `description`, `sensitive`, `required`, `default`, `multiple`, `min/max`; substituted as `${user_config.KEY}`; exported `CLAUDE_PLUGIN_OPTION_<KEY>`). `channels`, `dependencies` (`[{name, version:"~2.1.0"}]`). Unrecognized fields ignored (warnings only; `--strict` for CI). Single-skill plugin: root `SKILL.md`, name from frontmatter `name`.
- Env/path vars: `${CLAUDE_PLUGIN_ROOT}` (install dir, changes per update), `${CLAUDE_PLUGIN_DATA}` (persistent → `~/.claude/plugins/data/<sanitized-id>/`), `${CLAUDE_PROJECT_DIR}`.
- Cache: marketplace plugins copied to `~/.claude/plugins/cache`; no `../` escapes; symlink rules (in-plugin preserved, in-marketplace dereferenced, outside skipped). Orphaned versions cleaned after 7 days.
- Install scopes: `user` (default, `~/.claude/settings.json`), `project` (`.claude/settings.json`), `local`, `managed`. CLI: `claude plugin init|install|uninstall|prune|enable|disable|update|list|details|validate|tag`.

### marketplace.json (`.claude-plugin/marketplace.json` at repo root)
Required: `name` (kebab-case; reserved names list exists), `owner{name, email?}`, `plugins[]`. Optional: `$schema`, `description`, `version`, `metadata.pluginRoot`, `allowCrossMarketplaceDependenciesOn`, `renames`. Plugin entry: required `name` + `source` (string `"./path"` relative | object `{source: github|git|url|npm|file|directory, ...}`), plus any plugin.json field, plus `category`, `tags`, `strict`, `relevance`, `defaultEnabled`.

---

## 9. MCP CONFIG
**Source:** `02-build-with-claude-code/02-mcp/02-reference.md`.
- `.mcp.json` (project root, committed): `{"mcpServers": {"<name>": {...}}}`. Server entry: stdio `{command, args, env, timeout?}`; http `{type:"http" (alias "streamable-http"), url, headers}`; sse `{type:"sse", url, headers}`; ws `{type:"ws", url, headers, headersHelper, timeout, alwaysLoad}`.
- Env expansion in `.mcp.json`: `${VAR}` and `${VAR:-default}` in command/args/env/url/headers; missing var w/o default = parse failure. `CLAUDE_PROJECT_DIR` needs `${CLAUDE_PROJECT_DIR:-.}` in project/user scope (set only in server env).
- Scopes: **local** (default; stored in `~/.claude.json` under project path), **project** (`.mcp.json`, trust-gated approval prompt; reset via `claude mcp reset-project-choices`), **user** (`~/.claude.json`). Precedence local > project > user > plugin > claude.ai connectors; whole entry wins, no field merge.
- `claude mcp add [--transport http|sse|stdio] [--scope local|project|user] [--env K=V] <name> [-- cmd args]`; `claude mcp add-json <name> '<json>'`.

---

## 10. WORKFLOWS (`.claude/workflows/*.js`)
**Source:** `02-build-with-claude-code/01-agents-and-parallel-work/04-dynamic-workflows.md`.
- Saved dynamic workflow = JS file with `export const meta = {name, description}` + top-level-await script body using `agent(prompt, {schema?, label?})` and `pipeline(list, fn)` primitives; each file becomes `/<name>` command. Locations: `.claude/workflows/` (project, closest dir wins v2.1.178+) or `~/.claude/workflows/` (personal); project beats personal on clash. Input via `args` global (structured). Saved from `/workflows` view (`s` key). Runtime: isolated, no user input mid-run, subagents run in `acceptEdits` inheriting tool allowlist, ≤16 concurrent agents, ≤1000 agents/run. Disable: `disableWorkflows: true` / `CLAUDE_CODE_DISABLE_WORKFLOWS=1`.

---

## 11. STATUSLINE
**Source:** `04-configuration/03-interface/04-statusline.md`.
- `statusLine: {type:"command", command: "<script or inline shell>", padding?, refreshInterval?, hideVimModeIndicator?}` in user or project settings. Script gets JSON on stdin; prints text (multi-line, ANSI colors, OSC 8 links OK). Runs after assistant messages/compact/permission-mode/vim changes, debounced 300ms. `COLUMNS`/`LINES` env vars carry terminal size (v2.1.153+).
- stdin JSON fields: `model.{id,display_name}`, `cwd`, `workspace.{current_dir,project_dir,added_dirs,git_worktree,repo{host,owner,name}}`, `cost.{total_cost_usd,total_duration_ms,total_api_duration_ms,total_lines_added,total_lines_removed}`, `context_window.{total_input_tokens,total_output_tokens,context_window_size,used_percentage,remaining_percentage,current_usage{input_tokens,output_tokens,cache_creation_input_tokens,cache_read_input_tokens}}`, `exceeds_200k_tokens`, `effort.level`, `thinking.enabled`, `rate_limits.{five_hour,seven_day}.{used_percentage,resets_at}`, `session_id`, `session_name`, `prompt_id`, `transcript_path`, `version`, `output_style.name`, `vim.mode`, `agent.name`, `pr.{number,url,review_state}`, `worktree.{name,path,branch,original_cwd,original_branch}`. Many fields conditionally absent/null.
- Plugin `settings.json` may set `subagentStatusLine`.

---

## 12. .claude DIRECTORY MAP (harness inventory)
**Source:** `01-getting-started/04-core-concepts/03-claude-directory.md` (file-reference table §1474).
Committed project harness surface: `CLAUDE.md` (root or `.claude/`), `.claude/rules/*.md`, `.claude/settings.json`, `.mcp.json` (root), `.worktreeinclude` (root), `.claude/skills/<name>/SKILL.md`, `.claude/commands/*.md`, `.claude/output-styles/*.md`, `.claude/agents/*.md`, `.claude/workflows/*.js`, `.claude/agent-memory/<name>/`. Not committed: `.claude/settings.local.json`, `CLAUDE.local.md`, `.claude/agent-memory-local/`. Global-only: `~/.claude.json`, `~/.claude/projects/<project>/memory/`, `keybindings.json`, `themes/*.json`.

---

## 13. DECISION FRAMEWORK (for the meta-skill's routing logic)
**Source:** `01-getting-started/04-core-concepts/02-extend-claude-code.md`.
- Trigger table: mistake twice → CLAUDE.md; repeated prompt → user-invocable skill; repeated playbook → skill; browser-copied data → MCP; symbol navigation → LSP plugin; context-flooding side task → subagent; must-happen-every-time → hook; second repo needs same setup → plugin.
- Layering: CLAUDE.md additive; skills/agents override by name (managed > user > project for skills; managed > CLI > project > user > plugin for agents); MCP by name local > project > user; hooks merge (all fire).
- Context cost: CLAUDE.md full every request; skills descriptions-only until invoked (`disable-model-invocation` = zero); MCP tool names only (tool search on by default); hooks zero unless output; subagents isolated.
- Guardrails belong in hooks/permissions, not prose; CLAUDE.md/skills are advisory.

## KEY FACTS
- Custom slash commands are merged into skills: .claude/commands/deploy.md and .claude/skills/deploy/SKILL.md both create /deploy with identical frontmatter support; skills win on name clash; skills add supporting files, invocation control, and auto-loading (source: 02-build-with-claude-code/03-skills/01-extend-claude-with-skills.md)
- SKILL.md frontmatter fields (all optional, description recommended): name, description, when_to_use, argument-hint, arguments, disable-model-invocation, user-invocable, allowed-tools, disallowed-tools, model, effort, context (fork), agent, hooks, paths, shell; description+when_to_use capped at 1,536 chars in listing; keep SKILL.md under 500 lines; skill listing budget = 1% of context window
- Skill command name comes from the DIRECTORY name (or filename for commands/*.md), NOT the frontmatter name field, except for plugin-root SKILL.md
- Skill body substitutions: $ARGUMENTS, $ARGUMENTS[N], $N, $name, ${CLAUDE_SESSION_ID}, ${CLAUDE_EFFORT}, ${CLAUDE_SKILL_DIR}, ${CLAUDE_PROJECT_DIR}; dynamic context injection via !`cmd` inline and ```! fenced blocks runs BEFORE Claude sees content
- CLAUDE.md locations: managed policy file, ~/.claude/CLAUDE.md, ./CLAUDE.md or ./.claude/CLAUDE.md, ./CLAUDE.local.md; all concatenate (never override); parents load at launch, subdirectories lazily; @path imports expand at launch with max 4 hops; HTML comments are stripped; target under 200 lines; delivered as user message not system prompt
- .claude/rules/*.md: discovered recursively, symlinks OK; rules without paths frontmatter load at launch like CLAUDE.md; paths: glob frontmatter makes them load only when Claude touches matching files; user rules ~/.claude/rules/ load before project rules
- settings.json precedence: managed > CLI args > .claude/settings.local.json > .claude/settings.json > ~/.claude/settings.json; scalars override, arrays concatenate+dedupe (exceptions fallbackModel, managed availableModels); JSON schema at https://json.schemastore.org/claude-code-settings.json; most keys hot-reload except model and outputStyle
- Permission rules: deny → ask → allow, first match wins regardless of specificity; bare-name deny removes tool from context; Read/Edit rules use gitignore semantics with //=absolute, ~/=home, /=settings-source-relative, bare=cwd-relative; project settings.json allow rules require workspace trust; Bash * spans spaces and each compound subcommand must match independently
- Hook config: {hooks: {Event: [{matcher, hooks: [{type: command|http|mcp_tool|prompt|agent, ...}]}]}}; matchers are exact strings/lists unless they contain regex chars (then unanchored JS regex); exit 0 = JSON output parsed, exit 2 = block with stderr fed to Claude, other codes non-blocking; PreToolUse decides via hookSpecificOutput.permissionDecision allow|deny|ask|defer + updatedInput; ~30 events total including SessionStart, PreToolUse, PostToolUse, Stop, UserPromptSubmit, PreCompact, FileChanged, WorktreeCreate
- Hooks can live in settings files, plugin hooks/hooks.json, and skill/agent YAML frontmatter (component-scoped, once: true only honored in skill frontmatter); exec form (args present) avoids shell quoting for ${CLAUDE_PROJECT_DIR}/${CLAUDE_PLUGIN_ROOT} placeholders
- Subagents: .claude/agents/*.md (project) and ~/.claude/agents/*.md (user); frontmatter requires name+description; optional tools, disallowedTools, model (default inherit), permissionMode, maxTurns, skills (preloads FULL content), mcpServers (inline or refs), hooks, memory (user|project|local), background, effort, isolation: worktree, color, initialPrompt; body = system prompt replacing the default; Explore/Plan skip CLAUDE.md and git status; plugin agents can't use hooks/mcpServers/permissionMode
- Output styles: ~/.claude/output-styles/ and .claude/output-styles/*.md; frontmatter name, description, keep-coding-instructions (default false = strips built-in SWE instructions), force-for-plugin; applied via outputStyle setting; appended to system prompt end; needs /clear or restart
- Plugin manifest .claude-plugin/plugin.json: only name required; components live at plugin root (skills/, commands/, agents/, hooks/hooks.json, .mcp.json, .lsp.json, output-styles/, bin/, monitors/); skills path field ADDS to default scan while commands/agents/outputStyles REPLACE; ${CLAUDE_PLUGIN_ROOT} changes on update, ${CLAUDE_PLUGIN_DATA} persists; marketplace.json requires name, owner{name}, plugins[{name, source}]
- .mcp.json format: {mcpServers: {name: {command,args,env} | {type: http|sse|ws, url, headers}}}; supports ${VAR} and ${VAR:-default} expansion in command/args/env/url/headers; scope precedence local > project > user > plugin > connectors, whole-entry wins
- statusLine setting: {type: 'command', command: path-or-inline, padding, refreshInterval, hideVimModeIndicator}; script receives rich session JSON on stdin (model, workspace, cost, context_window, effort, rate_limits, pr, worktree) and prints display text
- Auto memory: ~/.claude/projects/<project>/memory/MEMORY.md, first 200 lines or 25KB loaded per session; subagent memory via memory frontmatter → agent-memory/<name>/ dirs with same limit
- Saved workflows: .claude/workflows/*.js or ~/.claude/workflows/*.js, each file with export const meta = {name, description} + JS body using agent()/pipeline() becomes a /<name> command; project beats personal on clash
- Enforcement hierarchy for generation: CLAUDE.md/skills are advisory context; hooks and permission rules are the deterministic layer ('put guardrails in hooks'); permissions rules are enforced by the client regardless of model behavior
- Skill lifecycle: invoked content stays in context all session; compaction re-attaches first 5,000 tokens per skill within a 25k shared budget most-recent-first; skills can be stacked up to 6 per message (v2.1.199+)
- Managed lockdown keys that a harness generator should not fight: strictPluginOnlyCustomization (blocks user/project skills|agents|hooks|mcp), allowManagedHooksOnly, allowManagedPermissionRulesOnly, strictKnownMarketplaces, disableSkillShellExecution

## OPEN QUESTIONS
- Should the harness-creator target the classic .claude/commands/*.md format at all, or generate only .claude/skills/ (docs recommend skills; commands are legacy-but-supported)?
- Does the meta-skill need to generate plugin/marketplace packaging (for cross-repo distribution) or only in-repo harnesses (.claude/ + CLAUDE.md + settings.json)? The @skills-dir plugin path (.claude-plugin/plugin.json inside a skills folder) is a middle ground.
- Docs snapshot is versioned (~v2.1.200, mid-2026, includes fictional-sounding models like 'fable' and claude-sonnet-5); should generated harnesses pin/check minimum Claude Code versions for features like ${CLAUDE_PROJECT_DIR} in skills (v2.1.196+) or exact-match hyphen matchers (v2.1.195+)?
- Should generated settings.json write permissions/hooks to .claude/settings.json (team, trust-gated allow rules) vs .claude/settings.local.json (personal, applies without trust)? Trust-gating of project allow rules affects out-of-box behavior for cloned repos.
- The docs mention /init with CLAUDE_CODE_NEW_INIT=1 already does an interactive CLAUDE.md+skills+hooks setup — how should harness-creator differentiate from or build on the built-in /init flow?
