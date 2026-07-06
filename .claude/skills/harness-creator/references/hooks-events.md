# Hook events — full reference

This file enumerates all 30 hook events Claude Code supports, verified against the primary source (`07-hooks-reference.md`). Load this file once you already know which event you're targeting — for picking the right event in the first place, use the one-line router table in `references/hooks.md`, which also carries the design principles and gotchas that apply regardless of event. This file is pure lookup: trigger timing, matcher support, input fields, decision channel, typical use, and version caveats, per event.

The 30 events, in lifecycle order: `SessionStart`, `Setup`, `InstructionsLoaded`, `UserPromptSubmit`, `UserPromptExpansion`, `MessageDisplay`, `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Notification`, `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`, `ConfigChange`, `CwdChanged`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `Elicitation`, `ElicitationResult`, `SessionEnd`. This ordering matches the primary source's own event table and is the count and enumeration to treat as authoritative — see the note at the bottom of this file if any other document you encounter states a different number.

Every event also receives the common input fields on top of what's listed per event below: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, and where applicable `prompt_id` (v2.1.196+), `permission_mode`, `effort` (tool-context events only), plus `agent_id`/`agent_type` inside subagents. These are omitted from the per-event "key input fields" column below to keep it focused on what's actually distinctive about that event.

## The 8 high-traffic events, expanded

### SessionStart

**Trigger timing.** Fires when a session begins or when it resumes — every session, so keep hooks on this event fast.

**Matcher.** Supported. Filters on how the session started: `startup` (new session), `resume` (`--resume`/`--continue`/`/resume`), `clear` (`/clear`), `compact` (after compaction).

**Key input fields.** `source` (mirrors the matcher value), optional `model` (not guaranteed present — check before reading), optional `agent_type`, optional `session_title`.

**Decision channel.** Context-only, no blocking. Plain stdout is added directly as context — the only events besides `Setup`/`UserPromptSubmit`/`UserPromptExpansion` where that's true. JSON output additionally supports `hookSpecificOutput.additionalContext`, `initialUserMessage` (first turn in `-p` mode), `sessionTitle` (startup/resume only), `watchPaths` (seeds the `FileChanged` watch list), and `reloadSkills` (re-scans skill/command directories after the hook completes, so a hook that installs a skill makes it available in the same session). Exit 2 shows stderr to the user only (as of v2.1.199 — earlier versions wrote it to the debug log only); Claude never sees it.

**Typical use.** Load development context (recent commits, open issues, current branch) at the start of every session; sync a shared skills repo and request `reloadSkills`; set up `CLAUDE_ENV_FILE` exports.

**Version caveats.** SessionStart exit-2 visibility to the transcript requires v2.1.199+.

**Example input:**
```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../.claude/projects/.../00893aaf.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "SessionStart",
  "source": "startup",
  "model": "claude-sonnet-5"
}
```

**Example output:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Current branch: feat/auth-refactor\nUncommitted changes: src/auth.ts\nActive issue: #4211 Migrate to OAuth2",
    "sessionTitle": "auth-refactor"
  }
}
```

Only `command` and `mcp_tool` hook types are supported on this event — `http`, `prompt`, and `agent` are not. `CLAUDE_ENV_FILE` is available here for persisting env vars into later Bash commands.

---

### UserPromptSubmit

**Trigger timing.** Fires when the user submits a prompt, before Claude processes it. Runs on every single prompt, so a slow hook here stalls the whole turn.

**Matcher.** Not supported — fires on every prompt unconditionally.

**Key input fields.** `prompt` (the submitted text).

**Decision channel.** Both a top-level `decision` and context injection are available. `decision: "block"` rejects and erases the prompt (exit 2 is equivalent). `reason` is shown to the user, not added to context. `hookSpecificOutput.additionalContext` injects an invisible system reminder alongside the prompt. Plain stdout is also added as visible context (shown in the transcript, unlike `additionalContext`). `sessionTitle` names the session from prompt content. `suppressOriginalPrompt` (with `block`) omits the original prompt text from the user-facing block message. This hook **cannot rewrite or replace the prompt** — only inject alongside it or block it outright.

**Typical use.** Validate or reject certain prompt shapes; inject environment state relevant to every turn (current deploy target, active feature flag); auto-title sessions from prompt content.

**Version caveats.** Default timeout for `command`/`http`/`mcp_tool` is lowered to **30 seconds** here (vs. 600s elsewhere) — a stuck hook blocks the entire turn. A timed-out hook's output, including `additionalContext`, is silently discarded pre-v2.1.196; from v2.1.196 the transcript names the hook and the timeout that fired.

**Example input:**
```json
{
  "session_id": "abc123",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "Write a function to calculate the factorial of a number"
}
```

**Example output (block):**
```json
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "My additional context here"
  }
}
```

---

### PreToolUse

**Trigger timing.** Fires after Claude has constructed a tool call's parameters, before the call executes. The main enforcement point — this is where a call can be stopped before anything happens.

**Matcher.** Supported, filters on tool name: `Bash`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `WebFetch`, `WebSearch`, `AskUserQuestion`, `ExitPlanMode`, or any `mcp__<server>__<tool>` name.

**Key input fields.** `tool_name`, `tool_input` (schema varies per tool — e.g. Bash: `command`/`description`/`timeout`/`run_in_background`; Edit: `file_path`/`old_string`/`new_string`/`replace_all`; Write: `file_path`/`content`), `tool_use_id`.

**Decision channel.** `hookSpecificOutput.permissionDecision`: `"allow"` (skip the prompt — except for MCP tools flagged `requiresUserInteraction`, v2.1.199+), `"deny"` (block, reason shown to Claude), `"ask"` (force a prompt, labeled with the hook's source scope), `"defer"` (`-p` mode only, v2.1.89+, pauses with `stop_reason: "tool_deferred"` for an SDK wrapper to resume — only works for single-tool-call turns). Precedence across multiple hooks: `deny` > `defer` > `ask` > `allow`. `updatedInput` replaces the **entire** tool input object (include unchanged fields, not just the ones you're modifying) — ignored when `permissionDecision` is `defer`. `additionalContext` adds context next to the tool result, also ignored under `defer`. Exit 2 = deny (equivalent to `permissionDecision: "deny"`).

**Typical use.** Block a dangerous command outright; redirect to a preferred tool ("use `rg` not `grep`"); redact or rewrite arguments before execution; auto-approve `AskUserQuestion`/`ExitPlanMode` in headless mode by echoing back `updatedInput` with an `answers` object.

**Version caveats.** `defer` requires v2.1.89+. The `requiresUserInteraction` strictness on MCP tools requires v2.1.199+. Deprecated top-level `decision`/`reason` (`"approve"`/`"block"`) map to `allow`/`deny` but `hookSpecificOutput.permissionDecision` is current.

**Example input:**
```json
{
  "session_id": "abc123",
  "cwd": "/Users/...",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test" }
}
```

**Example output:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Destructive command blocked by hook"
  }
}
```

Gotcha reminder (full detail in hooks.md): `@file` references never trigger this event at all, since no tool call happens for them.

---

### PostToolUse

**Trigger timing.** Fires immediately after a tool call **succeeds**. The tool has already run — this event cannot prevent anything, only react.

**Matcher.** Supported, same tool-name values as `PreToolUse`.

**Key input fields.** `tool_name`, `tool_input` (the arguments that were sent), `tool_response` (the tool's structured result — schema varies per tool, e.g. Write → `{filePath, success}`), `tool_use_id`, `duration_ms`.

**Decision channel.** Top-level `decision: "block"` + `reason` adds the reason next to the (still-visible) original output — it does not hide the original. `additionalContext` adds context alongside the result. `updatedToolOutput` **replaces** what Claude sees — must match the tool's own output schema for built-in tools or it is silently ignored; MCP tool output is unvalidated so anything goes there. `updatedMCPToolOutput` is the MCP-specific equivalent (prefer `updatedToolOutput`, which covers both). Exit 2 shows stderr to Claude but cannot undo the tool's real-world effect — files already written stay written.

**Typical use.** Run a formatter or linter after every edit; redact secrets from command output before Claude reads it; log every tool result for auditing.

**Version caveats.** None specific to this event beyond the general exec-form/version notes in hooks.md.

**Example input:**
```json
{
  "session_id": "abc123",
  "cwd": "/Users/...",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": { "file_path": "/path/to/file.txt", "content": "file content" },
  "tool_response": { "filePath": "/path/to/file.txt", "success": true },
  "tool_use_id": "toolu_01ABC123...",
  "duration_ms": 12
}
```

**Example output (replace output):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Additional information for Claude",
    "updatedToolOutput": { "stdout": "[redacted]", "stderr": "", "interrupted": false, "isImage": false }
  }
}
```

Redaction pattern to remember: `PreToolUse.updatedInput` for outbound (before the tool runs), `PostToolUse.updatedToolOutput` for inbound (before Claude sees the result). Use `PreToolUse` if you actually need to prevent the effect, not just hide it afterward.

---

### Stop

**Trigger timing.** Fires when the main agent finishes responding — not on a user interrupt, and not on an API error (that fires `StopFailure` instead). This is the validation-gate event: the one place you can force Claude to keep working after it believes it's done.

**Matcher.** Not supported — fires on every stop.

**Key input fields.** `stop_hook_active` (`true` when Claude Code is already continuing because of an earlier `Stop`-hook block — **must check this to avoid an infinite loop**), `last_assistant_message` (Claude's final response text, so you don't have to parse the transcript file), `background_tasks` (array of in-flight shell/subagent/workflow/etc. tasks, v2.1.145+), `session_crons` (array of scheduled wakeups, v2.1.145+, distinguishes "actually done" from "paused waiting on background work").

**Decision channel.** Top-level `decision: "block"` + required `reason` prevents stopping and feeds `reason` to Claude as its next instruction. `hookSpecificOutput.additionalContext` is the non-error variant — same effect (conversation continues) but labeled "Stop hook feedback" in the transcript rather than showing as a hook error. Both paths go through the same loop protection: the `stop_hook_active` field plus a built-in cap of **8 consecutive blocks** (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` to override, `0` disables — don't rely on disabling it). Exit 2 = block, equivalent to `decision: "block"`.

**Typical use.** Verify tests pass, lint is clean, or a build artifact exists before letting the turn end; nudge Claude to keep working toward a stated goal (the `/goal` command is a built-in shortcut for exactly this pattern).

**Version caveats.** `background_tasks`/`session_crons` require v2.1.145+.

**Example input:**
```json
{
  "session_id": "abc123",
  "cwd": "/Users/...",
  "hook_event_name": "Stop",
  "stop_hook_active": false,
  "last_assistant_message": "I've completed the refactoring. Here's a summary...",
  "background_tasks": [],
  "session_crons": []
}
```

**Example output:**
```json
{
  "decision": "block",
  "reason": "Must be provided when Claude is blocked from stopping"
}
```

---

### SubagentStart

**Trigger timing.** Fires when a subagent is spawned via the Agent tool, before its first prompt.

**Matcher.** Supported, filters on agent type: built-in names (`general-purpose`, `Explore`, `Plan`), a custom subagent's frontmatter `name`, or a plugin-scoped name like `my-plugin:reviewer`. The colon in a plugin-scoped name forces the matcher onto the regex path, so anchor it: `^my-plugin:reviewer$`.

**Key input fields.** `agent_id`, `agent_type`.

**Decision channel.** Context-only — cannot block subagent creation. `hookSpecificOutput.additionalContext` is injected into the **subagent's own context**, before its first prompt (not the parent session's context). Exit 2 shows stderr in the subagent's own transcript only, never the parent's.

**Typical use.** Inject role-specific guidance into a subagent that the parent session's CLAUDE.md doesn't reach (built-in Explore/Plan agents don't load CLAUDE.md at all — this hook is one of the three ways to compensate, per `references/agents.md`).

**Version caveats.** None specific.

**Example input:**
```json
{
  "session_id": "abc123",
  "cwd": "/Users/...",
  "hook_event_name": "SubagentStart",
  "agent_id": "agent-abc123",
  "agent_type": "Explore"
}
```

**Example output:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "Follow security guidelines for this task"
  }
}
```

---

### SubagentStop

**Trigger timing.** Fires when a subagent finishes responding.

**Matcher.** Supported, same agent-type values as `SubagentStart`.

**Key input fields.** `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path` (the subagent's own transcript, nested under a `subagents/` folder — distinct from `transcript_path`, which is always the main session), `last_assistant_message` (the subagent's final response text), plus `background_tasks`/`session_crons` scoped to the **parent** session (v2.1.145+).

**Decision channel.** Same shape as `Stop`: `decision: "block"` + `reason` keeps the subagent running with `reason` as its next instruction; `hookSpecificOutput.additionalContext` is the non-error variant. To inject into the **parent** session after the subagent returns, this event is the wrong tool — use a `PostToolUse` hook matched on the `Agent` tool instead, since `SubagentStop`'s context only reaches the subagent, which is about to vanish.

**Typical use.** Force a subagent to keep working until it actually produces the deliverable it was asked for, rather than stopping early.

**Version caveats.** `background_tasks`/`session_crons` require v2.1.145+. Note: agent frontmatter that declares a `Stop` hook is automatically converted to `SubagentStop`, since that's the event that actually fires when a subagent completes.

**Example input:**
```json
{
  "session_id": "abc123",
  "cwd": "/Users/...",
  "hook_event_name": "SubagentStop",
  "stop_hook_active": false,
  "agent_id": "def456",
  "agent_type": "Explore",
  "agent_transcript_path": "~/.claude/projects/.../abc123/subagents/agent-def456.jsonl",
  "last_assistant_message": "Analysis complete. Found 3 potential issues...",
  "background_tasks": [],
  "session_crons": []
}
```

---

### PreCompact

**Trigger timing.** Fires before Claude Code runs a compaction pass.

**Matcher.** Supported: `manual` (`/compact`), `auto` (context window nearly full).

**Key input fields.** `trigger` (mirrors the matcher), `custom_instructions` (the text the user passed to `/compact`; empty for `auto`).

**Decision channel.** Top-level `decision: "block"`, or exit 2, blocks compaction. Effect depends on why it was triggered: for a proactive `auto` compaction, Claude Code simply skips it and the conversation continues uncompacted; for an `auto` compaction that's recovering from a context-limit API error already returned, blocking means the underlying error surfaces and the request fails outright — blocking in that specific case doesn't avoid the problem, it just changes how it manifests.

**Typical use.** Prevent compaction at a moment where losing detail would be actively harmful (mid-way through a delicate multi-step operation) — but be aware of the auto/error-recovery caveat above before relying on this to always be safe.

**Version caveats.** None specific.

**Example input:**
```json
{
  "session_id": "abc123",
  "cwd": "/Users/...",
  "hook_event_name": "PreCompact",
  "trigger": "manual",
  "custom_instructions": ""
}
```

---

## The remaining 22 events — dense reference

| Event | Trigger timing | Matcher | Key input fields | Decision channel | Typical use | Version caveats |
|---|---|---|---|---|---|---|
| `Setup` | Only on `claude --init-only`, or `--init`/`--maintenance` with `-p`. Never fires on normal startup. | `init`, `maintenance` (which flag triggered it) | `trigger` | Cannot block. Exit 2 (or any nonzero) shows stderr to user only. `additionalContext` via JSON only — plain stdout goes to debug log, unlike `SessionStart`. | One-time dependency install or scheduled cleanup triggered explicitly from CI/scripts. | `command`/`mcp_tool` only. Has `CLAUDE_ENV_FILE`. |
| `InstructionsLoaded` | CLAUDE.md or a `.claude/rules/*.md` file loads — at session start (eager) and again on lazy loads mid-session. | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` (the `load_reason`) | `file_path`, `memory_type` (User/Project/Local/Managed), `load_reason`, `globs` (present only for `path_glob_match`), `trigger_file_path`, `parent_file_path` | None. Exit code ignored; async, observability-only. | Audit/compliance logging of what instructions were actually loaded and when. | None specific. |
| `UserPromptExpansion` | A user-typed `/command` or MCP prompt expands into a prompt, before reaching Claude. Covers the path `PreToolUse` on the `Skill` tool misses — typing `/skillname` directly never calls the Skill tool. | Command name (leave empty for every prompt-type command) | `expansion_type` (`slash_command`\|`mcp_prompt`), `command_name`, `command_args`, `command_source`, `prompt` | Top-level `decision: "block"` + `reason` blocks the expansion. `additionalContext` adds context. Exit 2 = block. | Require an approval file before `/deploy` runs; append a checklist as context for a specific review skill. | None specific. |
| `MessageDisplay` | While assistant message text streams to the screen, once per batch of newly completed lines (once per full message in `-p`/SDK mode). | Not supported — fires for every text-bearing assistant message. | `turn_id`, `message_id`, `index`, `final`, `delta` (new text since last batch) | `hookSpecificOutput.displayContent` replaces the **rendered** text only — transcript and what Claude sees keep the original. No blocking. | Strip markdown for plain-text display; redact secrets/hostnames from what's shown on screen. | Default timeout 10s (shortest of any event). |
| `PermissionRequest` | A permission dialog is about to be shown to the user. Distinct from `PreToolUse`, which fires regardless of permission status. | Tool name, same values as `PreToolUse` | `tool_name`, `tool_input` (no `tool_use_id`), optional `permission_suggestions` (would-be "always allow" entries) | `hookSpecificOutput.decision.behavior` (`allow`/`deny`) — deny/ask rules still apply even if the hook says `allow`. `updatedInput` (allow only, re-evaluated against rules), `updatedPermissions` (allow only — can persist rules to `session`/`localSettings`/`projectSettings`/`userSettings`), `message`/`interrupt` (deny only). Exit 2 = deny. Does **not** fire in `-p` mode — use `PreToolUse` there instead. | Auto-approve a specific low-risk prompt (e.g. `ExitPlanMode`) on the user's behalf; persist a permission rule so the user isn't asked again. | `setMode` to `bypassPermissions` only works if bypass was already available at launch; never persisted as `defaultMode`. |
| `PermissionDenied` | Auto mode's classifier denies a tool call. Does **not** fire for a manual denial, a hook block, or a matching deny rule — auto mode only. | Tool name, same values as `PreToolUse` | `tool_name`, `tool_input`, `tool_use_id`, `reason` (classifier's explanation) | `hookSpecificOutput.retry: true` tells the model it may retry — the denial itself is not reversed. Exit code/stderr ignored entirely. | Log classifier denials; auto-retry a call the classifier blocked for a fixable reason. | None specific. |
| `PostToolUseFailure` | A tool call fails (throws or returns a failure result). | Tool name, same values as `PreToolUse` | `tool_name`, `tool_input`, `error`, `is_interrupt` (optional), `duration_ms` | `additionalContext` only. Exit 2 shows stderr to Claude (tool already failed either way). | Give Claude corrective guidance right after a failure; log/alert on failures. | None specific. |
| `PostToolBatch` | Once after a full batch of parallel tool calls resolves, before the next model call. `PostToolUse` fires per-tool (concurrently on a parallel batch); this fires once for the whole batch. | Not supported | `tool_calls` array of `{tool_name, tool_input, tool_use_id, tool_response}` — `tool_response` here is the **serialized** content the model sees, a different shape from `PostToolUse`'s structured object | `additionalContext` injects once before the next model call. `decision: "block"` or `continue: false` stops the agentic loop before the next model call. Exit 2 = stop the loop. | Inject context that depends on the whole set of tools that just ran, not any single one (e.g. "these files are all part of the ledger module — run pytest before finishing"). | None specific. |
| `Notification` | Claude Code sends a notification. | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed` | `message`, optional `title`, `notification_type` | None — side effects only (can't block/modify). | Desktop notification when Claude needs input; forward to an external alerting service. | `agent_needs_input`/`agent_completed` require v2.1.198+, agent-view only. |
| `TaskCreated` | A task is being created via `TaskCreate`. | Not supported | `task_id`, `task_subject`, optional `task_description`, `teammate_name`, `team_name` (deprecated) | Exit 2 rolls back creation with stderr fed back as feedback. JSON `{"continue": false, "stopReason": "..."}` stops the teammate entirely. | Enforce a naming convention (e.g. require a ticket-number prefix) before a task is allowed to exist. | None specific. |
| `TaskCompleted` | A task is marked completed, either explicitly via `TaskUpdate` or implicitly when a teammate finishes its turn with in-progress tasks. | Not supported | Same shape as `TaskCreated` | Exit 2 prevents completion with stderr fed back. JSON `{"continue": false, "stopReason": "..."}` stops the teammate entirely. | Require tests/lint to pass before a task can close. | None specific. |
| `StopFailure` | The turn ends due to an API error (rate limit, auth failure, etc.) instead of a normal `Stop`. | `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `unknown` | `error`, optional `error_details`, `last_assistant_message` (here, the **API error string**, not Claude's own text — unlike `Stop`/`SubagentStop`) | None at all — output and exit code are fully ignored. | Logging/alerting on API-level failures only. | None specific. |
| `TeammateIdle` | An agent-team teammate is about to go idle after finishing its turn. | Not supported | `teammate_name`, `team_name` (deprecated) | Exit 2 keeps the teammate working with stderr as feedback. JSON `{"continue": false, "stopReason": "..."}` stops it entirely. | Require a build artifact to exist, or lint to be clean, before a teammate is allowed to go idle. | None specific. |
| `ConfigChange` | A settings file, managed policy, or skill file changes during a session. | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` | `source`, optional `file_path` | Top-level `decision: "block"` or exit 2 prevents the change from applying to the running session — **except** `policy_settings`, which can never be blocked (audit only, by design). | Security audit log of config changes; block an unauthorized project-settings edit mid-session. | None specific. |
| `CwdChanged` | The working directory changes (e.g. Claude runs `cd`). | Not supported | `old_cwd`, `new_cwd` | `watchPaths` replaces the dynamic `FileChanged` watch list. No blocking. | direnv-style reactive environment management paired with `FileChanged`. | Has `CLAUDE_ENV_FILE`. |
| `FileChanged` | A watched file changes on disk. | **Dual-purpose**: split on `\|` into literal filenames to watch (not a regex — `^\.env` would watch a file literally named `^\.env`), and the same value filters which hook groups run against the changed file's basename using normal matcher rules | `file_path`, `event` (`change`\|`add`\|`unlink`) | `watchPaths` updates the dynamic watch list. No blocking. | Reload env vars when `.env`/`.envrc` changes on disk. | Has `CLAUDE_ENV_FILE`. Uses a narrower exact-match matcher set (letters/digits/`_`/`\|` only) than most events. |
| `WorktreeCreate` | A worktree is being created (`--worktree` or subagent `isolation: "worktree"`). Replaces the default `git worktree` behavior entirely. | Not supported | `name` (slug identifier for the new worktree) | **Not** the usual allow/block model — the hook must return the absolute path to the created worktree. Command hooks print it on stdout (redirect everything else to stderr); HTTP hooks use `hookSpecificOutput.worktreePath`. **Any** nonzero exit (not just 2) or a missing path fails creation. | Use SVN, Perforce, or Mercurial instead of git for isolated working copies. | `.worktreeinclude` is not processed when this hook is configured — copy `.env` etc. yourself inside the hook. |
| `WorktreeRemove` | A worktree is being removed (session exit or subagent finish). | Not supported | `worktree_path` | None — can't block. Failures logged in debug mode only. | Cleanup counterpart to a custom `WorktreeCreate` (remove the SVN/Perforce checkout, archive changes). | None specific. |
| `PostCompact` | After a compaction completes. | `manual`, `auto` (same as `PreCompact`) | `trigger`, `compact_summary` | None — can't affect the result, only react to it. | Log the generated summary; refresh external state that depended on the pre-compaction context. | None specific. |
| `SessionEnd` | The session terminates. | `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other` (the `reason`) | `reason` | None — can't block termination. | Cleanup tasks, session-statistics logging, saving state. | Default timeout **1.5 seconds** (shortest of any event by nearly two orders of magnitude) — auto-raised to the highest per-hook timeout configured, up to 60s; override via `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`. |
| `Elicitation` | An MCP server requests user input mid-task (form or URL-based auth). | MCP server name | `mcp_server_name`, `message`, optional `mode` (`form`\|`url`), `url`, `elicitation_id`, `requested_schema` | `hookSpecificOutput.action` (`accept`\|`decline`\|`cancel`) + `content` (form values, `accept` only) answers programmatically, skipping the dialog. Exit 2 = deny. | Auto-supply credentials or form answers for a known, trusted MCP server flow. | None specific. |
| `ElicitationResult` | After the user responds to an elicitation, before the response reaches the MCP server. | MCP server name, same values as `Elicitation` | `mcp_server_name`, `action`, `content`, `mode`, `elicitation_id` | `hookSpecificOutput.action`/`content` overrides the user's response. Exit 2 blocks the response (becomes `decline`). | Redact or override form values before they're sent to the server. | None specific. |

## A note on the "30 events" count

This file enumerates exactly the 30 events listed in the primary source's own event table (`.tmp/docs_claude/05-reference/07-hooks-reference.md`, the "Hook lifecycle" section) and cross-checked against that same source's per-event sections later in the document, plus the parallel table in `01-automate-with-hooks.md`. Both tables list the identical 30 names in the identical order. If a future re-sync of the primary source shows a different count — a new event added, one renamed or removed — re-derive this file's event list from that source's own table rather than trusting the number "30" as a fixed fact; the number is a description of the source's current contents, not an independent constant.
