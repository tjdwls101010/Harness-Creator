# Hooks and permissions

This is the authoring guide for the enforcement layer: the only layer in a generated harness that is deterministic rather than advisory. Read this before designing any hook or permission rule, and re-check the generated `settings.json` against the gotcha list here before declaring the component done. Full per-event schemas (input fields, decision channels, JSON examples) live in `references/hooks-events.md` — load that file once you know which event you're targeting. This file is the one you load first, on every hook-design task, because the principles and gotchas here apply regardless of which event you end up choosing.

Permissions are folded into this same file rather than split out on their own. A hook's guarantees and a permission rule's guarantees are two halves of one mechanism — a hook without a matching permission rule is often not actually enforcing anything — and both are decided and loaded at the same point in the generation flow, so there is no benefit to separating them the way hooks.md and hooks-events.md are separated by load timing.

## The hook eligibility test

Before writing a hook, ask: **must this never be violated?** If the answer is "it's fine if Claude usually gets it right," the item belongs in CLAUDE.md, a rule file, or a skill — not a hook. Route it back through the layer-routing framework in SKILL.md instead of reaching for a hook by default.

This test matters because hooks are not free. Every hook adds a process spawn to the relevant lifecycle point, which is latency the user pays on every matching event whether or not anything was actually wrong. A `PreToolUse` hook on `Bash` runs on every single shell command for the rest of the session. Beyond latency, a harness with hooks scattered across every plausible concern starts fighting the model instead of guiding it — legitimate edge cases the interview didn't anticipate get blocked alongside the genuine violations, and the user ends up fighting their own harness. Reserve hooks for the small set of points where determinism is worth that cost: protecting a path from ever being edited, guaranteeing a formatter always runs, blocking a category of command outright. Everything softer is advisory, and advisory belongs in a layer that's cheap to override when the 16th case you didn't think of shows up.

## Hard guarantees need a permission-rule pair, not a hook alone

A `PreToolUse` hook's `if` field looks like a filter, but it is best-effort: it fails open on Bash commands it can't parse, and the official Claude Code documentation itself says explicitly that hard allow/deny decisions belong in the permission system, not in a hook's `if` condition. A hook is therefore the wrong tool for a guarantee on its own.

The practical implication: whenever the interview surfaces a "must never happen" item — protected file, forbidden command, dangerous directory — generate **both** a `PreToolUse` hook (for the rich feedback message Claude sees when it tries and fails, so it can adapt its approach) **and** a matching `permissions.deny` rule (for the guarantee that actually can't be bypassed, including in `bypassPermissions` mode). The hook without the deny rule is a suggestion with good error messages; the deny rule without the hook is a hard wall with a generic client-side message. Together they give Claude both the wall and the explanation for why it hit the wall.

## Where hook scripts live and how settings.json references them

Generate hook logic with any real complexity as a standalone file under `.claude/hooks/`, not as an inline one-liner buried in `settings.json`. A one-liner is fine for something as trivial as an `echo`, but the moment a hook needs to parse JSON, branch on a field, or check a path against a list, it needs to be a script you can read, test, and diff independently of the JSON that invokes it.

Reference that script from `settings.json` using **exec form** — an `args` array — with an absolute path anchored on `${CLAUDE_PROJECT_DIR}`, not a bare relative path and not shell form:

```json
{
  "type": "command",
  "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-files.sh",
  "args": []
}
```

Three reasons this specific shape, not something else: first, `${CLAUDE_PROJECT_DIR}` is what makes the hook resolve correctly regardless of the directory Claude Code happens to be `cwd`'d into when the hook fires — a relative path silently breaks the moment a subagent or a `cd` changes the working directory mid-session. Second, `args` being present (even as an empty array) is what switches Claude Code to exec form: no shell, no quoting rules, no risk of a path containing a space or an apostrophe breaking tokenization — the executable is resolved and spawned directly, and each `args` element passes through verbatim. Third, a real file under version control is diffable, testable in isolation with `echo '{...}' | ./script.sh`, and survives being read back by a future session in a way an inline shell string embedded in JSON does not.

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

This mechanism is a real way for a skill to self-enforce something automatically instead of just telling the model to remember to check it — but it isn't automatically the right call just because it's available. Eligibility still runs through the same test as any other hook: a `PostToolUse` hook that fires on every `Edit|Write` a skill's own generation process makes will fire on every incomplete mid-draft edit, not just on a finished component, which is exactly the over-firing failure mode the eligibility test above warns about — the fix for "the model might forget to validate" is usually a clearer instruction at the right checkpoint in the skill's own body, not a hook racing ahead of the model's own judgment about when a component is actually done.

## Every generated hook must be verified with test_hook.py before delivery

Do not consider a hook "generated" until `${CLAUDE_SKILL_DIR}/scripts/test_hook.py` has run against it and passed. A hook that looks correct by inspection can still fail for reasons that are invisible until you actually pipe JSON at it: `jq` not installed, the script not marked executable, a shell-profile `echo` polluting stdout ahead of the JSON, an exit code that doesn't match what you intended. This is a free, offline check — there is no reason to skip it, and skipping it is how a harness ships a hook that silently no-ops the first time it fires for real.

## Gotchas — the highest-density knowledge in this file

Everything below is a place where an already-capable model's default assumptions about hooks are wrong, usually because the mechanism inverts an expectation carried over from somewhere else (Unix exit codes, regex intuition, "surely a deny always wins"). Read all of them before generating any hook — a hook that trips one of these does not fail loudly; it silently does something other than what you designed it to do.

**Exit 1 does not block anything.** This is the single most common mistake, and it inverts ordinary Unix convention where a nonzero exit means failure. In Claude Code's hook contract, only **exit 2** blocks. Exit 1 (or any other nonzero code) is a *non-blocking* error: the action proceeds anyway, and the transcript shows a `<hook name> hook error` notice with the first line of stderr, easy to miss if you're not looking for it. If you write a hook intending to enforce a policy and it exits 1 on the violation path, the policy silently does nothing. The one documented exception is `WorktreeCreate`, where any nonzero exit — not just 2 — aborts worktree creation.

**Exit 0 + stdout JSON is the decision channel; exit 2 + stderr is the block channel; the two are mutually exclusive.** Claude Code only parses stdout as JSON when the hook exits 0. If you exit 2, any JSON you also happened to print to stdout is discarded — stderr is what Claude reads back as the block reason. Pick one shape per hook: either "exit 2, write the reason to stderr" for a hard block, or "exit 0, print a JSON decision object to stdout" for anything richer (allow/deny/ask, `updatedInput`, `additionalContext`). Mixing them — e.g. printing a `permissionDecision: "deny"` JSON object and then exiting 2 — throws away the JSON and falls back to the plain stderr-block behavior.

**An unanchored character in a matcher silently turns it into a regex.** A matcher containing only letters, digits, `_`, `-`, whitespace, `,`, or `|` is evaluated as an exact string (or a list of exact strings, if `,`- or `|`-separated). The instant it contains any other character, it becomes an **unanchored** JavaScript regex tested with `RegExp.prototype.test`, meaning it matches if the pattern appears *anywhere* in the string, not just as a whole-string match. `Edit.*` is the textbook trap: written by someone who thinks `.` means "match everything after Edit," it actually matches `NotebookEdit` too, because `NotebookEdit` contains `Edit` followed by anything (zero characters satisfies `.*`). If you actually want a regex, anchor it explicitly: `^Edit$`.

**MCP tool matchers need the trailing `.*`.** `mcp__server__.*` matches every tool from `server`. A bare `mcp__server` (no trailing wildcard) contains only exact-match characters, so it is compared as an exact literal string — and no tool is literally named `mcp__server`, so it matches nothing at all. This is a silent zero-match failure, not an error; a generated hook with this typo will simply never fire and give no indication why.

**`@file` references bypass `PreToolUse(Read)` entirely.** When a user types `@path/to/file` in a prompt, Claude Code expands and inlines the file's contents while building the prompt — no `Read` tool call happens, so no `PreToolUse` hook fires, regardless of matcher. A hook designed to gate file access by matching the `Read` tool has a hole exactly the size of every `@`-reference in every future prompt. Protect sensitive file contents with a `Read` **permission deny rule** instead — deny rules apply to `@`-references directly, independent of any tool call.

**A Bash-driven file edit doesn't trip an `Edit|Write` matcher.** Claude can modify a file via `Bash` (`sed -i`, `echo >> file`, a script that writes output) without ever calling the `Edit` or `Write` tool, so a `PostToolUse` hook matching `Edit|Write` never sees it. Compensate one of two ways: include `Bash` in the same matcher group and inspect the command inside the hook script, or add a `Stop`-time hook that runs `git status --porcelain` once per turn and reacts to any unexpected diff regardless of which tool produced it. The `Stop`-time approach is coarser (once per turn, not per edit) but catches every path; the `Bash`-inclusive approach is precise but requires parsing the command yourself.

**`PreToolUse` deny holds even under `bypassPermissions` mode — but a hook can never override a deny from any scope.** This cuts both ways and both directions matter. In the direction that helps you: a hook that returns `permissionDecision: "deny"` (or exits 2) blocks the tool call even in the strongest permission mode available, `bypassPermissions` — a user cannot escape a hook-enforced policy just by switching modes. In the direction that constrains you: the reverse never holds. A hook returning `"allow"` never overrides a `deny` or `ask` rule that already exists in *any* settings scope, including managed/enterprise settings. Hooks can only tighten what permissions already allow; they can never loosen a deny. Design accordingly — if you need a hook to auto-approve something, verify first that no deny rule anywhere would have blocked it regardless.

**Two `updatedInput`-mutating hooks on the same tool race.** When multiple `PreToolUse` hooks match the same tool call and more than one returns `updatedInput`, they all run in parallel and the **last one to finish wins** — non-deterministic, since "last to finish" depends on process scheduling, not declaration order. Never generate two input-rewriting hooks for the same tool. If two concerns both need to touch the same tool's input (e.g. one hook redacts secrets, another normalizes paths), combine them into a single hook script that does both, in a defined order you control.

**`Stop`-hook loop guards are mandatory, not optional polish.** A `Stop` hook that returns `decision: "block"` keeps Claude working — which is exactly the point for a validation gate — but if the condition it's checking never resolves, this becomes an infinite loop. Two things prevent that: the hook must read the `stop_hook_active` input field and treat `true` as "I already forced a continuation once; let it stop now" rather than blocking again unconditionally, and Claude Code itself caps consecutive `Stop`-hook blocks at **8** regardless of what the hook returns (overridable via `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`, `0` disables the cap — never generate a hook that relies on disabling it). Every `Stop`-hook you generate must check `stop_hook_active` in its own logic; don't rely on the 8-block cap alone to save you, because hitting that cap means the user's task didn't actually get validated, it just gave up.

**`additionalContext` must read as a fact, not a command.** Phrase it "This repo uses `bun test`," not "Run `bun test`." The reasoning is not stylistic: `additionalContext` is injected as an invisible system reminder, and text phrased as an out-of-band imperative instruction can trip Claude's own prompt-injection defenses — designed to catch exactly this shape of "instruction smuggled in through a non-user channel" — which causes the text to be surfaced to the user instead of silently trusted and acted on. A factual statement about project state reads as legitimate context; an imperative reads as a suspicious command sneaking in through a side channel.

**Default timeouts are wildly uneven, and mismatched expectations cause silent truncation.** Most hook types (`command`, `http`, `mcp_tool`) default to 600 seconds — ten minutes — which is generous enough that people stop thinking about it. Two events break that pattern hard: `UserPromptSubmit` lowers the default to **30 seconds** (because it blocks every single prompt from reaching Claude, so a slow hook stalls the whole session on every turn), and `SessionEnd` defaults to **1.5 seconds** — not 15, not 150, one and a half — because it runs during session teardown where the user is already trying to exit. A `SessionEnd` hook that shells out to something slow (a network call, a large file write) will silently get truncated well before it finishes unless you explicitly raise its `timeout` field or set `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`. Check the timeout column in hooks-events.md for the event you're generating; don't assume 600 seconds.

**Hook processes have no tty, and shell-profile stdout noise breaks JSON parsing.** Hooks run in their own session without a controlling terminal — they cannot write to `/dev/tty` (use `terminalSequence` in JSON output for desktop notifications instead). More insidious: if the hook runs in shell form (no `args`) and the shell sources a profile (`.bashrc`, `.zshrc`) that unconditionally echoes something on startup — a "Shell ready" banner, a version notice — that text lands on stdout *before* your hook's JSON, and Claude Code's JSON parser chokes on the combined output. Guard any profile echo with an interactive-shell check (`[[ $- == *i* ]]`) so it only fires in a real interactive terminal, never in the non-interactive shell a hook spawns.

**Several features are version-gated; generate for latest stable and comment the floor.** The `if` field requires Claude Code v2.1.85+; comma-separated matcher lists require v2.1.191+; hyphens inside an exact-match matcher set require v2.1.195+ (earlier, a hyphenated name like `code-reviewer` silently becomes an unanchored regex that also matches `senior-code-reviewer`); `defer` requires v2.1.89+; and more. The generation policy is: **assume latest stable Claude Code, and add a one-line comment noting the minimum version wherever you use a version-gated feature** — do not hedge every single hook against every possible older version, since that produces defensive, unreadable configuration for a problem most users don't have. `references/hooks-events.md` carries a version column per event for exactly this lookup.

## Permissions: the rules that make a hook's guarantee real

### Evaluation order: deny, then ask, then allow — first match wins regardless of specificity

Permission rules are evaluated in a fixed order — deny rules first, then ask rules, then allow rules — and the **first matching rule in that order decides the outcome**, no matter how specific a later rule is. A broad `Bash(aws *)` deny rule blocks even a call that also matches a narrow `Bash(aws s3 ls)` allow rule; the deny wins because deny is checked first, not because it's more specific. This means a deny rule can never carry an allowlist exception baked in as a separate, more-specific allow rule elsewhere — if you need an exception, it has to be carved out of the deny rule's own pattern. A deny rule in **any** settings scope — user, project, local, or managed — wins over an allow rule in any other scope; there is no scope-priority override for allow.

### Read/Edit rules use gitignore-style path syntax, and one rule governs a family of tools

`Read` and `Edit` permission rules follow gitignore pattern conventions, with four anchor forms: `//path` is an absolute path from the filesystem root; `~/path` is relative to the home directory; a single leading `/path` is relative to the **settings file's own project root** (so the exact same rule text resolves to a different location depending on which settings.json it's written in — project settings anchor at the project root, user settings anchor at `~/.claude/`); and a bare filename or `./path` matches relative to the current directory, with a bare filename like `.env` matching at any depth (equivalent to `**/.env`). Generate the anchor form deliberately — a rule meant to be absolute needs `//`, and writing a single `/` when you meant `//` is a common, silent mistake since both look like "absolute" to a human reader.

Critically, an `Edit` rule also governs `Write` and `NotebookEdit` — you don't need three separate rules for the three file-mutating tools, one `Edit` rule covers the family. Symmetrically, a `Read` rule also governs `Grep`, `Glob`, and IDE-shared file context. When the interview surfaces "never let Claude touch `.env`," one `Edit(.env)` deny rule (plus, if read access should also be blocked, one `Read(.env)` deny rule) is the complete answer — don't generate redundant per-tool rules.

### Project allow rules are gated on workspace trust; deny/ask are not

A project's `.claude/settings.json` **allow** rules only take effect after the user has accepted the workspace-trust dialog for that directory — until then, Claude Code reads the rules but does not apply them. Deny and ask rules have no such gate; they apply immediately regardless of trust, since they only restrict, never grant. This asymmetry is the direct explanation for a specific, otherwise-confusing bug report: "I cloned the repo, the committed settings.json has an allow rule for `npm test`, but Claude still prompts me for it." The rule is real and correctly written; it just hasn't taken effect yet because the workspace hasn't been trusted in this environment. State this explicitly in any harness documentation you generate that ships allow rules in project settings, so a fresh clone doesn't read as a broken harness.

### Only narrow allow rules are worth generating — broad ones get dropped in auto mode

When a session enters auto mode, Claude Code automatically suspends broad allow rules that grant arbitrary code execution: a blanket `Bash(*)` or `PowerShell(*)`, wildcarded interpreters like `Bash(python*)`, package-manager run commands, and `Agent` allow rules. Narrow rules like `Bash(npm test)` carry over untouched. The practical consequence for a generator: **a broad allow rule has no durable value** in a harness that might ever run under auto mode — it works in `default`/`acceptEdits` mode and silently stops covering anything the moment the user switches to auto. Generate narrow, specific allow rules (`Bash(npm test)`, `Bash(git status)`) rather than broad ones (`Bash(*)`), both because narrow rules are what the interview should actually be surfacing (specific, named, safe commands) and because narrow rules are the only kind guaranteed to keep working across every permission mode.

### Compound commands need every sub-command matched, and a trailing wildcard enforces a word boundary

Claude Code parses shell compound-command separators (`&&`, `||`, `;`, `|`, `|&`, `&`, newlines) and requires **each sub-command independently** to match an allow rule before the whole compound command is approved without a prompt — a rule like `Bash(npm test)` does not implicitly bless `npm test && rm -rf build` just because the first half matches. When generating allow rules meant to smooth over a specific workflow, remember the workflow's compound commands need every clause covered, not just the first one visible in the interview transcript.

Separately: a trailing `*` preceded by a space, as in `Bash(ls *)`, enforces a **word boundary** — it requires the prefix to be followed by a space or end-of-string, so `Bash(ls *)` matches `ls -la` but does **not** match `lsof`, even though `lsof` starts with the same three characters. Writing `Bash(ls*)` with no space removes that boundary and matches both. This is an easy rule to get backwards when generating allowlists quickly — always include the space before the trailing `*` unless you specifically intend a prefix match with no word boundary.

## The router: which event for which job

Full schema for every event lives in `references/hooks-events.md`. This table is only for picking the right event fast — one line each, purpose-first, so you can scan for the job you're trying to do and jump straight to that event's section in hooks-events.md for the input/output details.

| Event | One-line purpose |
|---|---|
| `SessionStart` | Inject context or set up environment when a session begins or resumes. |
| `Setup` | One-time preparation on `--init-only`/`--init`/`--maintenance`, outside normal session start. |
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
| `Stop` | Keep the main agent working past its natural stop — the validation-gate event. |
| `StopFailure` | Log/alert on an API-error turn ending. No decision control at all. |
| `TeammateIdle` | Gate an agent-team teammate going idle, same shape as `Stop`. |
| `ConfigChange` | Audit or block a settings/skill file change mid-session (not `policy_settings`). |
| `CwdChanged` | React to `cd` — reload env vars via `CLAUDE_ENV_FILE`, update `FileChanged` watch list. |
| `FileChanged` | React to a watched file changing on disk (direnv-style patterns). |
| `WorktreeCreate` | Replace git-worktree creation with another VCS. Must return a path or creation fails. |
| `WorktreeRemove` | Clean up after a non-git `WorktreeCreate`. |
| `PreCompact` | Block compaction, or let it proceed. |
| `PostCompact` | React after compaction completes — log the summary, refresh external state. |
| `SessionEnd` | Cleanup/logging on session end. Very short default timeout — see gotchas above. |
| `Elicitation` | Answer an MCP server's mid-task input request programmatically, skipping the dialog. |
| `ElicitationResult` | Observe or override the user's elicitation response before it reaches the MCP server. |

## Three recipes

Each recipe below is deliberately dense: the `settings.json` entry plus a one-line note on the matcher/exit-code logic that makes it work. Adapt paths and matchers to what the interview actually surfaced — don't ship these verbatim.

### Recipe 1 — block edits to a protected path

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
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

`protect-files.sh` reads `tool_input.file_path` from stdin, checks it against a protected-pattern list, and `exit 2` with a stderr reason on a match, `exit 0` otherwise — this is the belt. The `permissions.deny` block is the suspenders: even if the hook script has a bug, or a permission mode change bypasses the hook layer somehow, the deny rule holds on its own, including under `bypassPermissions`. Generate both, per the hard-guarantee principle above. Note the matcher covers `Edit|Write` but not `Bash` — if the interview flagged that Claude sometimes edits files via shell redirection in this project, add `Bash` to the matcher and inspect the command in the script, or add a `Stop`-time `git status --porcelain` scan as a backstop.

### Recipe 2 — post-edit auto-formatter

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/format.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

`format.sh` reads `tool_input.file_path`, runs the project's formatter against just that file (e.g. `npx prettier --write "$FILE"`), and exits 0 whether or not formatting changed anything — this is not a gate, it's a side effect, so there's no reason to ever exit 2 here. No matching permission rule is needed because nothing is being blocked; this recipe is pure automation, not enforcement. If the formatter is slow enough to matter, add `"async": true` so it runs in the background rather than blocking the next tool call, keeping in mind async hooks can't return decisions.

### Recipe 3 — Stop-time validation gate

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-tests.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

`check-tests.sh` reads `stop_hook_active` from stdin first and exits 0 immediately if it's `true` (loop guard — see the gotcha above); otherwise it runs the test suite, and if tests fail, prints a JSON object with `decision: "block"` and a `reason` describing what's failing, then exits 0 (JSON decision channel, not the exit-2 channel, since `Stop` reads the top-level `decision` field rather than relying on exit code alone for this event). No permission-rule pair is needed here — a `Stop` hook isn't blocking a *tool call*, it's keeping the turn going, so there's no allow/deny rule that would express the same guarantee more strongly. The loop guard plus the built-in 8-consecutive-block cap are what keep this safe from becoming an infinite loop if the tests never pass.
