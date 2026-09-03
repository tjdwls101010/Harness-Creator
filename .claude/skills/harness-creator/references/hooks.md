# Hooks and permissions

This is the authoring guide for the enforcement layer: the only layer in a generated harness that is deterministic rather than advisory. It covers the eligibility test that decides the route, the gotchas to re-check the generated `settings.json` against, and permission rules. Per-event schemas (input fields, decision channels, JSON examples) live in `references/hooks-events.md`; take one event's worth with `hook_event.py --event <Event>` once you know which event you're targeting.

## The hook eligibility test

Before writing a hook, ask: **must this never be violated?** If the answer is "it's fine if Claude usually gets it right," the item belongs in CLAUDE.md, a rule file, or a skill — not a hook. Route it back through the layer-routing framework in SKILL.md instead of reaching for a hook by default.

That question can't do the work alone, because asked whether something matters, people say yes. Ask a second one that can come back negative: **what does a violation cost, and is something already catching it?** CI, a review, or a type checker already catching it means the hook only moves the failure earlier and bills every tool call for the privilege; cheap to undo means the same. What's left — expensive or irreversible *and* uncaught downstream — is the set worth generating. "We'd fix it in review" is the signal to route back to prose.

Hooks are not free. Every hook is a process spawn on every matching event whether or not anything was wrong — a `PreToolUse` hook on `Bash` runs on every shell command for the rest of the session — and a harness with hooks on every plausible concern blocks the edge cases the interview didn't anticipate alongside the violations. Reserve hooks for the points where determinism is worth that: protecting a path from ever being edited, guaranteeing a formatter always runs, blocking a category of command outright.

## A hook blocks the calls it receives; a deny rule decides which calls exist

Both halves are hard, and they fail in different places. A `PreToolUse` hook that returns `permissionDecision: "deny"` or exits 2 blocks the call before any permission-mode check, in every mode including `bypassPermissions` and `dontAsk` — a user cannot escape it by switching modes. What is best-effort is not the block but the *reach*: the `if` field takes permission-rule syntax to narrow which calls spawn the hook, and when Claude Code can't tell which commands a Bash input will run it spawns the hook regardless of the pattern, which is why the docs say to express a hard allow or deny as a permission rule rather than an `if`. Reach fails in other ways too — an `@file` reference never becomes a `Read` call, `disableAllHooks` or a missing `jq` takes the hook out, and a hook that errors exits nonzero-but-not-2, which does not block.

So for an item that passed the eligibility test — expensive or irreversible, uncaught downstream: a protected file, a forbidden command, a dangerous directory — generate **both** a `PreToolUse` hook, for the feedback Claude reads when it tries and fails and can adapt to, **and** a matching `permissions.deny` rule, which the client evaluates on every call with no script to reach or fail. Pair them only where permission grammar can express the same restriction — a tool, a command pattern, a path. A guarantee about an event or a state rather than a call — `PostToolUse`, `TaskCompleted`, `Stop`, `ConfigChange`, `PreCompact` — has no permission rule that says the same thing, and stands alone.

## Where hook scripts live and how settings.json references them

Generate hook logic with any real complexity as a standalone file under `.claude/hooks/`, not as an inline one-liner in `settings.json`: the moment a hook parses JSON, branches on a field, or checks a path against a list, it needs to be a script you can read, test with `echo '{...}' | ./script.sh`, and diff independently of the JSON that invokes it.

Reference that script from `settings.json` using **exec form** — an `args` array — with an absolute path anchored on `${CLAUDE_PROJECT_DIR}`, not a bare relative path and not shell form:

```json
{
  "type": "command",
  "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-files.sh",
  "args": []
}
```

`${CLAUDE_PROJECT_DIR}` makes the hook resolve regardless of the directory Claude Code is `cwd`'d into when it fires — a relative path breaks silently the moment a subagent or a `cd` moves the working directory. `args` being present, even empty, switches Claude Code to exec form: no shell, no quoting, the executable is spawned directly and each `args` element passes through verbatim, so a path with a space or an apostrophe cannot break tokenization.

## Hooks can also live in a skill's or agent's own frontmatter

Settings.json isn't the only place a hook can be declared. A skill or agent's own frontmatter can carry a `hooks:` field in the exact same event/matcher/handler shape used everywhere else in this file, scoped to that component's own active lifetime — it starts working when the skill or agent becomes active and is cleaned up when it finishes, without ever touching the target project's `settings.json`:

```yaml
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

One field here has no settings.json equivalent: `once: true` on a handler makes it run once per session and then remove itself — but this is honored **only** for hooks declared in skill frontmatter; the same field on an agent-frontmatter hook or a settings.json hook is silently ignored. If you're generating a skill that needs a check to fire on its first activation only (a one-time environment sanity check, say), skill frontmatter with `once: true` is the only place that behavior exists at all.

Command paths here resolve relative to the skill's own directory, not `${CLAUDE_PROJECT_DIR}` — a different convention from every settings.json recipe in this file, so don't copy a `${CLAUDE_PROJECT_DIR}`-anchored command into a skill's frontmatter unchanged. The substitutions actually documented as available inside a hook's `command` field are `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, and `${CLAUDE_PLUGIN_DATA}` — `${CLAUDE_SKILL_DIR}` is a convention for referencing scripts from a skill's own *body* text (what the model reads and acts on), not a substitution Claude Code performs inside a hook's execution environment; treat it as unverified in a `command` field until you've confirmed otherwise against a real run.

The eligibility test still applies: a `PostToolUse` hook on every `Edit|Write` a skill's own process makes fires on every mid-draft edit, not only on a finished component — the fix for "the model might forget to validate" is a clearer instruction at the right checkpoint in the skill body, not a hook racing the model's judgment about when a component is done.

A hook that looks correct by inspection can still fail for reasons invisible until JSON is actually piped at it — `jq` not installed, the script not executable, a shell-profile `echo` ahead of the JSON, an exit code other than the one intended — which is what `test_hook.py` exists to surface before the hook fires for real.

## Gotchas

Each of these inverts an expectation carried over from somewhere else (Unix exit codes, regex intuition, "surely a deny always wins"), and a hook that trips one does not fail loudly; it silently does something other than what you designed.

**Exit 1 does not block anything.** This is the single most common mistake, and it inverts ordinary Unix convention where a nonzero exit means failure. In Claude Code's hook contract, only **exit 2** blocks. Exit 1 (or any other nonzero code) is a *non-blocking* error: the action proceeds anyway, and the transcript shows a `<hook name> hook error` notice with the first line of stderr, easy to miss if you're not looking for it. If you write a hook intending to enforce a policy and it exits 1 on the violation path, the policy silently does nothing. The one documented exception is `WorktreeCreate`, where any nonzero exit — not just 2 — aborts worktree creation.

**Exit 0 + stdout JSON is the decision channel; exit 2 + stderr is the block channel; the two are mutually exclusive.** Claude Code only parses stdout as JSON when the hook exits 0. If you exit 2, any JSON you also happened to print to stdout is discarded — stderr is what Claude reads back as the block reason. Pick one shape per hook: either "exit 2, write the reason to stderr" for a hard block, or "exit 0, print a JSON decision object to stdout" for anything richer (allow/deny/ask, `updatedInput`, `additionalContext`). Mixing them — e.g. printing a `permissionDecision: "deny"` JSON object and then exiting 2 — throws away the JSON and falls back to the plain stderr-block behavior.

**An unanchored character in a matcher silently turns it into a regex.** A matcher containing only letters, digits, `_`, `-`, whitespace, `,`, or `|` is evaluated as an exact string (or a list of exact strings, if `,`- or `|`-separated). The instant it contains any other character, it becomes an **unanchored** JavaScript regex tested with `RegExp.prototype.test`, meaning it matches if the pattern appears *anywhere* in the string, not just as a whole-string match. `Edit.*` is the textbook trap: written by someone who thinks `.` means "match everything after Edit," it actually matches `NotebookEdit` too, because `NotebookEdit` contains `Edit` followed by anything (zero characters satisfies `.*`). If you actually want a regex, anchor it explicitly: `^Edit$`.

**MCP tool matchers need `__.*`.** `mcp__server__.*` matches every tool from `server`; a bare `mcp__server` is exact-match characters only, so it is compared as a literal tool name no tool has and matches nothing, with no indication why. Permission rules are a different grammar — there a bare `mcp__server` does mean the whole server — so a matcher is not a rule you can copy across.

**`@file` references bypass `PreToolUse(Read)` entirely.** When a user types `@path/to/file` in a prompt, Claude Code expands and inlines the file's contents while building the prompt — no `Read` tool call happens, so no `PreToolUse` hook fires, regardless of matcher. A hook designed to gate file access by matching the `Read` tool has a hole exactly the size of every `@`-reference in every future prompt. Protect sensitive file contents with a `Read` **permission deny rule** instead — deny rules apply to `@`-references directly, independent of any tool call.

**A Bash-driven file edit doesn't trip an `Edit|Write` matcher — but a path *rule* reaches further than the matcher does.** Claude can modify a file via `Bash` (`sed -i`, `echo >> file`, a script that writes) without calling `Edit` or `Write`, so a `PostToolUse` hook on `Edit|Write` never sees it. The permission layer does not have that hole in the same shape: `Edit`/`Read` deny rules are applied to the file commands Claude Code recognizes inside Bash — `cat`, `head`, `tail`, `sed` — and lose the path only to a subprocess it cannot read through, a Python or Node script that opens the file itself. Match each compensation to which of the two gaps it closes: `Bash` in the matcher plus a command scan inside the hook script narrows the hook's blind spot at the cost of parsing shell text yourself; a `git status --porcelain` check at `Stop`, or a `FileChanged` hook, reacts after the write instead of preventing it and sees only what its own scope covers (a repo diff misses ignored files and anything outside the worktree); and OS-level sandbox filesystem rules are the only form that binds a subprocess the permission layer can't read.

**`PreToolUse` deny holds even under `bypassPermissions` mode — but a hook can never override a deny from any scope.** This cuts both ways and both directions matter. In the direction that helps you: a hook that returns `permissionDecision: "deny"` (or exits 2) blocks the tool call even in the strongest permission mode available, `bypassPermissions` — a user cannot escape a hook-enforced policy just by switching modes. In the direction that constrains you: the reverse never holds. A hook returning `"allow"` never overrides a `deny` or `ask` rule that already exists in *any* settings scope, including managed/enterprise settings. Hooks can only tighten what permissions already allow; they can never loosen a deny. A hook that exits 2 stops the tool call **before** permission rules are evaluated, which is why no allow rule in any scope or mode can override it — and why a hook meant to auto-approve something has to check first that no deny rule would have blocked it anyway.

**Two `updatedInput`-mutating hooks on the same tool race.** When multiple `PreToolUse` hooks match the same tool call and more than one returns `updatedInput`, they all run in parallel and the **last one to finish wins** — non-deterministic, since "last to finish" depends on process scheduling, not declaration order. Never generate two input-rewriting hooks for the same tool. If two concerns both need to touch the same tool's input (e.g. one hook redacts secrets, another normalizes paths), combine them into a single hook script that does both, in a defined order you control.

**`Stop`-hook loop guards are mandatory, not optional polish.** A `Stop` hook that returns `decision: "block"` keeps Claude working — which is exactly the point for a validation gate — but if the condition it's checking never resolves, this becomes an infinite loop. Two things prevent that: the hook must read the `stop_hook_active` input field and treat `true` as "I already forced a continuation once; let it stop now" rather than blocking again unconditionally, and Claude Code itself caps consecutive `Stop`-hook blocks at **8** regardless of what the hook returns (overridable via `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`, `0` disables the cap — never generate a hook that relies on disabling it). Every `Stop`-hook you generate must check `stop_hook_active` in its own logic; don't rely on the 8-block cap alone to save you, because hitting that cap means the user's task didn't actually get validated, it just gave up.

**`additionalContext` must read as a fact, not a command.** "This repo uses `bun test`," not "Run `bun test`": it is injected as an invisible system reminder, and an out-of-band imperative is the exact shape Claude's prompt-injection defenses catch, so it gets surfaced to the user instead of acted on.

**Default timeouts are wildly uneven, and mismatched expectations cause silent truncation.** Most hook types (`command`, `http`, `mcp_tool`) default to 600 seconds — ten minutes — which is generous enough that people stop thinking about it. Three events depart from that, and the last one departs in kind, not just in magnitude:

- `UserPromptSubmit` — **30 seconds**, because it blocks every prompt from reaching Claude, so a slow hook stalls the session on every turn.
- `MessageDisplay` — **10 seconds**, because it sits in the render path.
- `SessionEnd` — **1.5 seconds, and it is a budget shared across all `SessionEnd` hooks, not a per-hook default.** This is the one whose mechanism differs from every other event. Raising a per-hook `timeout` raises the shared budget to match, up to 60 seconds; `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` overrides it in milliseconds. A timeout set on a *plugin-provided* hook does not raise the budget.

So a `SessionEnd` hook that shells out to anything slow gets truncated during teardown, and a second `SessionEnd` hook eats into the same budget rather than getting its own.

**Hook processes have no tty, and shell-profile stdout noise breaks JSON parsing.** Hooks cannot write to `/dev/tty` (use `terminalSequence` in JSON output for desktop notifications). In shell form (no `args`), a profile (`.bashrc`, `.zshrc`) that echoes on startup lands that text on stdout *before* the hook's JSON and the parser chokes; guard profile echoes with `[[ $- == *i* ]]`, or use exec form.

**Several features are version-gated; generate for latest stable and comment the floor.** The `if` field needs v2.1.85+; comma-separated matcher lists v2.1.191+; hyphens inside an exact-match matcher v2.1.195+ (earlier, `code-reviewer` silently became an unanchored regex that also matched `senior-code-reviewer`); `defer` v2.1.89+. Assume latest stable and add a one-line comment naming the floor where you use a gated feature — hedging every hook against every older version produces configuration nobody can read. `hooks-events.md` carries a version column per event.

## Permissions: the rules that make a hook's guarantee real

### Evaluation order: deny, then ask, then allow — first match wins regardless of specificity

Permission rules are evaluated in a fixed order — deny rules first, then ask rules, then allow rules — and the **first matching rule in that order decides the outcome**, no matter how specific a later rule is. A broad `Bash(aws *)` deny rule blocks even a call that also matches a narrow `Bash(aws s3 ls)` allow rule; the deny wins because deny is checked first, not because it's more specific. This means a deny rule can never carry an allowlist exception baked in as a separate, more-specific allow rule elsewhere — if you need an exception, it has to be carved out of the deny rule's own pattern. A deny rule in **any** settings scope — user, project, local, or managed — wins over an allow rule in any other scope; there is no scope-priority override for allow.

### Read/Edit rules use gitignore-style path syntax, and one rule governs a family of tools

`Read` and `Edit` permission rules follow gitignore pattern conventions, with four anchor forms: `//path` is an absolute path from the filesystem root; `~/path` is relative to the home directory; a single leading `/path` is relative to the **settings file's own project root** (so the exact same rule text resolves to a different location depending on which settings.json it's written in — project settings anchor at the project root, user settings anchor at `~/.claude/`); and a bare filename or `./path` matches relative to the current directory, with a bare filename like `.env` matching at any depth (equivalent to `**/.env`). Generate the anchor form deliberately — a rule meant to be absolute needs `//`, and writing a single `/` when you meant `//` is a common, silent mistake since both look like "absolute" to a human reader.

One rule covers a family: an `Edit` rule also governs `Write` and `NotebookEdit`, a `Read` rule also governs `Grep`, `Glob`, and IDE-shared file context, and both are applied to the file commands Claude Code recognizes in Bash. So "never let Claude touch `.env`" is one `Edit(.env)` deny, plus a `Read(.env)` deny if reading is out too — not one rule per tool. What that pair does *not* reach is a subprocess Claude Code can't read through (see the Bash gotcha above), so write the rules for the tools and the recognized commands, and decide separately whether the remaining path needs a hook's command scan or a sandbox. Write the family's rule under the family's name — `Edit(docs/**)`, not `Write(docs/**)`, and `Read(docs/**)`, not `Glob(docs/**)` — because only `Edit(path)` and `Read(path)` are consulted. A bare `Write` deny with no path is a different thing and works: it matches at the tool level.

### Workspace trust gates what the repo *grants*, and gates it in two different strengths

**Trust gates what a repo *grants*, never what it *restricts*** — deny and ask rules are live on a clone nobody has trusted, because restricting needs no permission. But "granted" splits into two gates with different keys, and generating as if there were one is how a harness reads as working while half of it is off:

- **The exact folder must be trusted.** `permissions.allow` and `additionalDirectories`, a project subagent's frontmatter hooks (v2.1.218+ — the agent still runs, hookless), a repository `@skills-dir` plugin, `extraKnownMarketplaces`, and a subagent's inline `mcpServers`. Trusting a parent does not reach a nested project here.
- **Trusting the folder *or a parent* is enough.** Hooks in settings files, the `env` block and helpers like `apiKeyHelper`, a project skill's own frontmatter hooks, a project `statusLine`, and `autoMemoryDirectory`.
- **Never gated at all.** A project skill's `allowed-tools`, in any session. And user-level subagents in `~/.claude/agents/`, because the user wrote those.

The direction that surprises a generator is `claude -p` and the SDK, which never show the trust dialog: there the *second* group runs — project hooks fire, the `env` block applies — while the first is dropped, allow rules included, with one warning on stderr. That is the CI shape, so a harness whose smooth path depends on project allow rules stalls in the pipeline on prompts it never sees locally, while the hooks it also ships enforce as normal. Say which half a fresh clone gets in what you generate, or a guarantee looks like it's holding when it isn't; a skipped subagent hook says so only in a debug log.

Two edges: `.claude/settings.local.json` is normally exempt as the user's own file, but goes through the gate when the repo could have supplied it (committed, or `.claude` is a symlink); and a `--add-dir` folder needs trusting separately rather than inheriting the workspace's grant.

### Protected paths: `.claude/` writes can't be pre-approved, and one mode refuses them outright

`.claude` is protected (except `.claude/worktrees`), along with `.git`, `.vscode`, `.idea`, `.husky`, `.devcontainer`, `.mcp.json`, `.claude.json`, shell rc files, `.npmrc`, `.pre-commit-config.yaml`, and others — treat the list as open, not exhaustive.

**The safety check runs before allow rules are evaluated, so `Edit(.claude/**)` does nothing.** That is precisely the repair a generator reaches for when a user complains about the prompt, and it is a no-op that looks like a fix.

| Mode | Protected-path write |
|---|---|
| `default`, `acceptEdits` | Prompted |
| `plan` | Prompted (allowed where bypass is available; classifier where auto mode is) |
| `auto` | Routed to the classifier |
| `dontAsk` | **Denied** |
| `bypassPermissions` | Allowed |

Design around the `dontAsk` row: it's the CI mode, so a harness that writes into `.claude/` during setup works on a laptop and silently fails in the pipeline. In the prompting modes, the `.claude/` prompt offers **"Yes, and allow Claude to edit its own settings for this session."**

### Only narrow allow rules are worth generating — broad ones get dropped in auto mode

When a session enters auto mode, Claude Code suspends broad allow rules that grant arbitrary code execution — `Bash(*)`, `PowerShell(*)`, wildcarded interpreters like `Bash(python*)`, package-manager run commands, `Agent` allow rules — while narrow rules like `Bash(npm test)` carry over. So a broad allow rule has no durable value: generate the narrow, named, safe commands the interview surfaced, which are also the only kind that keeps working across every permission mode.

### `defaultMode: "auto"` is ignored in the settings file this skill writes

A repository cannot grant itself auto mode. Since v2.1.142, Claude Code **ignores `permissions.defaultMode: "auto"`** when it appears in `.claude/settings.json` or `.claude/settings.local.json`; the session starts in `default` with no error and no warning. Only `~/.claude/settings.json` (or managed settings) can set it.

This matters here more than most gotchas because project `settings.json` is a file this skill generates. If the interview lands on "I don't want to be prompted constantly," writing `defaultMode: "auto"` into the project settings produces a harness that appears configured and behaves exactly as if it weren't. Route that request to the user's own settings and say so in the spec's Design rationale; `acceptEdits` and `plan` are honored in project settings and are the values worth generating there.

### Compound commands need every sub-command matched, and a trailing wildcard enforces a word boundary

Claude Code splits compound commands on `&&`, `||`, `;`, `|`, `|&`, `&` and newlines and requires **each sub-command independently** to match an allow rule — `Bash(npm test)` does not bless `npm test && rm -rf build`. An allow rule meant to smooth a workflow has to cover every clause of that workflow's commands, not the first one visible in the transcript.

A trailing `*` preceded by a space, as in `Bash(ls *)`, enforces a **word boundary**: it matches `ls -la` and not `lsof`, where `Bash(ls*)` matches both. Include the space unless a bare prefix match is what you mean.

## The router: which event for which job

One line per event, purpose-first, for picking the event; then `hook_event.py --event <Event>` for that event's schema from `references/hooks-events.md`.

| Event | One-line purpose |
|---|---|
| `SessionStart` | Inject context or set up environment when a session begins or resumes. |
| `Setup` | One-time preparation for CI or scripts. Never on normal startup. |
| `InstructionsLoaded` | Observe when CLAUDE.md or a rules file loads — audit/logging only, no decision control. |
| `UserPromptSubmit` | Inject context alongside a prompt, or block the prompt before Claude sees it. |
| `UserPromptExpansion` | Catch the direct `/skillname` path that bypasses `PreToolUse` on the Skill tool. |
| `MessageDisplay` | Rewrite what's rendered on screen only — transcript and Claude's view are untouched. |
| `PreToolUse` | Allow, deny, ask, defer, or rewrite a tool call before it executes. The main enforcement point. |
| `PermissionRequest` | Answer a permission dialog programmatically, including persisting new allow rules. |
| `PermissionDenied` | React when auto mode's classifier denies a call; can tell the model it may retry. |
| `PostToolUse` | Feed back or replace what Claude sees after a tool succeeds — can't undo the tool's real effect. |
| `PostToolUseFailure` | Add context after a tool call fails. |
| `PostToolBatch` | Inject context once after a whole parallel batch resolves, or stop the loop. |
| `Notification` | React to a Claude Code notification (permission prompt, idle, etc.) — side effects only. |
| `SubagentStart` | Inject context into a subagent before its first prompt. |
| `SubagentStop` | Keep a subagent working past its natural stop, same shape as `Stop`. |
| `TaskCreated` | Enforce naming/content rules on task creation, or roll it back. |
| `TaskCompleted` | Gate task completion on a condition (tests passing, lint clean). |
| `Stop` | Keep the main agent working past its natural stop — the validation-gate event. Before generating one, check whether `/goal` already does the job: it keeps Claude working across turns until a stated condition is met, with no hook to write, loop-guard, or maintain. |
| `StopFailure` | Log/alert on an API-error turn ending. No decision control at all. |
| `TeammateIdle` | Gate an agent-team teammate going idle, same shape as `Stop`. |
| `ConfigChange` | Audit or block a settings/skill file change mid-session (not `policy_settings`). |
| `CwdChanged` | React to `cd` — reload env vars via `CLAUDE_ENV_FILE`, update `FileChanged` watch list. |
| `DirectoryAdded` | Observe a directory added by `/add-dir` or the SDK — notification only, output discarded. |
| `FileChanged` | React to a watched file changing on disk (direnv-style patterns). |
| `WorktreeCreate` | Replace git-worktree creation with another VCS. Must return a path or creation fails. |
| `WorktreeRemove` | Clean up after a non-git `WorktreeCreate`. |
| `PreCompact` | Block compaction, or let it proceed. |
| `PostCompact` | React after compaction completes — log the summary, refresh external state. |
| `PreModelSwitch` | Block or allow a model switch before it applies; matches on the model switched *to*. |
| `PostModelSwitch` | React after the model changed, including changes Claude Code makes itself. |
| `Elicitation` | Answer an MCP server's mid-task input request programmatically, skipping the dialog. |
| `ElicitationResult` | Observe or override the user's elicitation response before it reaches the MCP server. |
| `SessionEnd` | Cleanup/logging on session end. Very short default timeout — see gotchas above. |

## Three recipes

The `settings.json` entry plus the matcher/exit-code logic that makes it work. Adapt paths and matchers to what the interview surfaced; don't ship these verbatim.

### Recipe 1 — block edits to a protected path

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-files.sh",
            "args": []
          }
        ]
      }
    ]
  },
  "permissions": {
    "deny": ["Edit(.env)", "Edit(package-lock.json)"]
  }
}
```

`protect-files.sh` branches on `tool_name`: for `Bash` it scans `tool_input.command`, for everything else it matches `tool_input.file_path` against a protected-pattern list, and either way `exit 2` with a stderr reason on a match, `exit 0` otherwise. Generate both halves, per the pairing principle above.

`Bash` is in the matcher rather than left to the interview because the deny rules and the hook cover different reaches, and the write nobody covered is the one that lands: the rules bind the file tools and the Bash commands Claude Code recognizes, and the hook's own command scan is what stands in front of the rest. A `Stop`-time `git status --porcelain` scan is the wrong shape for a *must-never* — it notices after the write landed, and it bills every turn. What the command scan costs instead is precision: it is a substring scan over shell text, not a shell parser, so it over-blocks a command that merely mentions a protected name. Err in that direction, and keep the deny rules, which don't depend on a script guessing right. If the path must be unreachable to a subprocess neither layer reads — a script that opens the file itself — that is a sandbox filesystem rule, not a hook.

### Recipe 2 — post-edit auto-formatter

`PostToolUse` on `Edit|Write` (same JSON shape as Recipe 1) pointing at `format.sh`, which reads `tool_input.file_path`, formats that one file, and **exits 0 whether or not anything changed**. This is a side effect, not a gate, so it never exits 2 and needs no permission-rule pair — nothing is being blocked. If the formatter is slow enough to matter, add `"async": true`, remembering async hooks can't return decisions.

### Recipe 3 — Stop-time validation gate

`Stop` (no matcher — it isn't a tool event) pointing at `check-tests.sh`, which reads `stop_hook_active` from stdin first and exits 0 immediately if it's `true` (loop guard — see the gotcha above); otherwise it runs the test suite, and if tests fail, prints a JSON object with `decision: "block"` and a `reason` describing what's failing, then exits 0 (JSON decision channel, not the exit-2 channel, since `Stop` reads the top-level `decision` field rather than relying on exit code alone for this event). No permission-rule pair is needed here — a `Stop` hook isn't blocking a *tool call*, it's keeping the turn going, so there's no allow/deny rule that would express the same guarantee more strongly.

**Price this one before generating it.** `Stop` is a once-per-turn event, so unlike a `PreToolUse` hook that only wakes on a matching tool, this cost lands on *every* turn — including the turns where Claude answered a question and touched nothing. `async: true` makes a hook non-blocking, but Claude Code then ignores its output completely — no stdout, no JSON parsing, no exit codes — so an async `Stop` hook cannot block, which is the entire point of this recipe. (`asyncRewake: true` is a middle path: it runs in the background and wakes Claude on exit 2, which suits a slow check that should interrupt later rather than gate now.) Either scope the check to something cheap, gate it inside the script on whether any relevant file actually changed this turn, or accept the per-turn cost deliberately.
