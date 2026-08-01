# Verified Claude Code mechanics — 2026-08-01 sweep

Every fact below was read from a live doc page on 2026-08-01 against Claude Code **v2.1.220**.
This file exists because the repo's CLAUDE.md requires every mechanic the skill asserts to trace to a
primary source, and because `.tmp/docs_claude/` (snapshot ~2026-07-05) is now provably stale.

Columns in the status marks:
**✓ CONFIRMS** — the shipped skill already says this correctly, cite this row when re-verifying.
**⚠ CORRECTS** — the shipped skill says something wrong or imprecise here.
**+ NEW** — the shipped skill has no equivalent statement.

---

## A. Compaction and the always-loaded budget

| # | Fact | Source | Status |
|---|---|---|---|
| A1 | Auto-compaction re-attaches **the most recent invocation of each skill after the summary, keeping the first 5,000 tokens of each**. Re-attached skills share a combined **25,000-token** budget, filled most-recently-invoked first, so older skills can be dropped entirely. | `/docs/en/skills` §Skill content lifecycle | ✓ CONFIRMS `skills.md:68` |
| A2 | **Implication A1 does not state, and neither does the skill:** content past the first 5,000 tokens of a SKILL.md does not survive compaction. SKILL.md is currently ~2,185 words ≈ 2,900 tokens. That is the real ceiling on the always-loaded surface, and it is a cliff, not a gradient. | derived from A1 | + NEW |
| A3 | A reference file pulled in with Read is an ordinary tool result in the transcript. It is summarized away by compaction and is **not** re-attached. So a fact stated only in a reference is lost after compaction; the same fact in SKILL.md is not. | derived from A1 | + NEW — this is the justification for deliberate SKILL.md/reference duplication |
| A4 | Project-root CLAUDE.md **survives compaction**: Claude re-reads it from disk and re-injects it. | `/docs/en/memory` §Instructions seem lost after `/compact` | ✓ CONFIRMS `skills.md:68` |
| A5 | **Nested subdirectory CLAUDE.md files are NOT re-injected** after compaction; they reload only the next time Claude reads a file in that subdirectory. | same | + NEW — breaks `claude-md-and-rules.md:44`'s monorepo advice when combined with `skills.md:68` |
| A6 | Skill listing budget = **1% of the model's context window**. On overflow, Claude Code "drops descriptions starting with the skills you **invoke least**". Per-entry cap 1,536 chars. | `/docs/en/skills` §skill listing | ✓ CONFIRMS `skills.md:44`, `skills.md:52`; ⚠ CORRECTS "least-**recently**-invoked" → "invoked least" |
| A7 | Budget levers: `skillListingBudgetFraction` (e.g. `0.02`), `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`. | same | + NEW |
| A8 | `skillOverrides: {"<name>": "name-only" \| "off"}` — the middle remedy between keeping a skill and deleting it: it lists without a description, freeing listing budget. Written to `.claude/settings.local.json`; plugin skills unaffected. | `/docs/en/skills` §Override skill visibility | + NEW — `skills.md:44` offers only consolidate-or-keep |
| A9 | Auto memory: **the first 200 lines OR 25KB of `MEMORY.md`, whichever comes first, load at the start of every conversation.** Topic files load on demand. | `/docs/en/memory` §How it works | + NEW |
| A10 | CLAUDE.md target: "**target under 200 lines per CLAUDE.md file.** Longer files consume more context and reduce adherence." | `/docs/en/memory` §Write effective instructions | ✓ CONFIRMS `claude-md-and-rules.md:11` — the number is Anthropic's own, not invented |
| A11 | Official skill guidance: "**Keep SKILL.md under 500 lines.** Move detailed reference material to separate files." | `/docs/en/skills` | ⚠ CORRECTS `SKILL.md:86` — the shipped split principle ("split only when the model branches") is narrower than official guidance, which licenses staged reference files |

## B. Auto memory

| # | Fact | Source | Status |
|---|---|---|---|
| B1 | Two mechanisms carry knowledge across sessions: CLAUDE.md (you write, instructions and rules) and auto memory (Claude writes, learnings and patterns). Both load into every session. | `/docs/en/memory` §CLAUDE.md vs auto memory | + NEW |
| B2 | Location `~/.claude/projects/<project>/memory/`, containing `MEMORY.md` (index) plus topic files. `<project>` derives from the git repository, so all worktrees share one directory. | same §Storage location | + NEW |
| B3 | **Machine-local. "Files are not shared across machines or cloud environments."** Never committed, never travels with the repo. | same | + NEW — this is the routing boundary vs CLAUDE.md |
| B4 | On by default. Off via `autoMemoryEnabled: false` (any settings scope) or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Relocatable with `autoMemoryDirectory`. | same §Enable or disable | + NEW — nothing load-bearing may depend on memory existing |
| B5 | `autoMemoryDirectory` set in project settings is honored **only after workspace trust is accepted** — the same gate that governs hooks. | same | + NEW |
| B6 | The main conversation's auto memory is **not** loaded into subagents (forks excepted). A subagent gets its own only via the `memory` frontmatter field. | `/docs/en/sub-agents` §What loads at startup | + NEW |
| B7 | After a `MEMORY.md` write, Claude Code measures it against the 200-line/25KB read limits and errors if over, because everything past the limit is dropped on next load. Frontmatter and block HTML comments are stripped before measuring (v2.1.211+). | `/docs/en/memory` | + NEW |

## C. CLAUDE.md and rules — discovery and loading

| # | Fact | Source | Status |
|---|---|---|---|
| C1 | A project CLAUDE.md may live at **either `./CLAUDE.md` or `./.claude/CLAUDE.md`**. Both load. | `/docs/en/memory` §Set up a project CLAUDE.md | ⚠ **BUG** — `validate_harness.py:402` and `audit_harness.py:38` each hardcode `root/"CLAUDE.md"` only |
| C2 | `CLAUDE.local.md` loads alongside `CLAUDE.md`, appended after it within each directory. | same | + NEW — invisible to both scripts |
| C3 | All discovered files **concatenate**; there is no override. Root-down ordering; within a directory, `CLAUDE.local.md` comes after `CLAUDE.md`. | same §How CLAUDE.md files load | ✓ CONFIRMS `claude-md-and-rules.md:40` |
| C4 | Rules are discovered **recursively** in `.claude/rules/`, including subdirectories like `frontend/`. | `/docs/en/memory` §Set up rules | ⚠ **BUG** — `harness_common.py:282` uses a non-recursive glob |
| C5 | A rule with no `paths:` frontmatter is "loaded at launch with the same priority as `.claude/CLAUDE.md`". | same §Path-specific rules | ✓ CONFIRMS `claude-md-and-rules.md:43` |
| C6 | `paths` glob budget: a rule's **whole `paths` list shares one budget of 1,000 expanded patterns and 4 MiB**. Each brace group multiplies (`{a,b}/{c,d}/*.{ts,tsx}` → 8). A pattern that would exceed the budget is used **unexpanded**, and its literal braces match no files. | same | + NEW |
| C7 | Glob `[` starts a bracket expression. An unreadable one (`photos [2024/**`) matches nothing; escape as `\[`. Before v2.1.207 one invalid pattern made Read fail for every file the rule was evaluated against. | same | + NEW |
| C8 | `@path` imports expand at launch; max 4 hops; parsing skips code spans and fenced blocks; **the extensionless form `@README` works**. | same §Import additional files | ✓ CONFIRMS `claude-md-and-rules.md:41`; ⚠ **BUG** — `_AT_IMPORT_RE` at `validate_harness.py:38` misses extensionless targets and fires on any `word@word.tld` in prose |
| C9 | An import in a **project** memory file whose path resolves outside the working directory is "external": a one-time approval dialog lists them, and **declining disables them permanently with no repeat dialog**. User-scope imports skip the dialog. | same | + NEW |
| C10 | Block-level HTML comments are stripped before injection but stay visible to a human and to the Read tool. | same | ✓ CONFIRMS `claude-md-and-rules.md:42` |
| C11 | Claude Code reads `CLAUDE.md`, **not `AGENTS.md`**. Documented interop: make `@AGENTS.md` the first line of CLAUDE.md, or symlink. `/init` also reads Cursor and Copilot rule files. | same §AGENTS.md | + NEW |
| C12 | `claudeMdExcludes` (glob, any settings layer, arrays merge) skips specific CLAUDE.md files. Managed-policy CLAUDE.md cannot be excluded. | same §Exclude specific CLAUDE.md files | + NEW |
| C13 | Managed settings may carry a `claudeMd` key with inline org-wide content; honored only in managed/policy scope. | same §Deploy organization-wide CLAUDE.md | + NEW |
| C14 | User rules at `~/.claude/rules/` apply to **every project** and load before project rules. | same §User-level rules | + NEW — `audit_harness.py`'s user-scope conflict check reads only `~/.claude/CLAUDE.md` |
| C15 | CLAUDE.md is "delivered as a user message after the system prompt, not as part of the system prompt itself… there's no guarantee of strict compliance." | same §Troubleshoot | ✓ CONFIRMS `claude-md-and-rules.md:7` |

## D. Permissions, protected paths, auto mode

| # | Fact | Source | Status |
|---|---|---|---|
| D1 | **`.claude` is a protected directory** (except `.claude/worktrees`). `.mcp.json` and `.claude.json` are protected files. Also protected: `.git`, `.vscode`, `.idea`, `.husky`, `.devcontainer`, shell rc files, `.npmrc`/`bunfig.toml`, `.pre-commit-config.yaml`, and more. | `/docs/en/permission-modes` §Protected paths | + NEW |
| D2 | **`permissions.allow` rules do NOT pre-approve protected-path writes.** "The safety check runs before Claude Code evaluates allow rules… an entry such as `Edit(.claude/**)` … does not change the per-mode outcome." | same | + NEW — this is the fix a generator would reach for, and it does nothing |
| D3 | Per-mode outcome for a protected-path write: `default`/`acceptEdits` → **prompted**; `plan` → prompted (allowed with bypass available; routed to the classifier with auto mode available, v2.1.218+); `auto` → **classifier**; `dontAsk` → **denied**; `bypassPermissions` → allowed. | same | + NEW — `SKILL.md:39` says only "will prompt" |
| D4 | In modes that prompt, the `.claude/` write prompt offers **"Yes, and allow Claude to edit its own settings for this session"**. | same | + NEW — the one actionable detail `SKILL.md:39` is missing |
| D5 | **`defaultMode: "auto"` is ignored in `.claude/settings.json` and `.claude/settings.local.json`** — "Claude Code v2.1.142 and later ignore `auto` from those files so a repository cannot grant itself auto mode. Move it to `~/.claude/settings.json`." | same §auto mode | + NEW — harness-creator generates project settings.json |
| D6 | On entering auto mode, broad allow rules granting arbitrary code execution are **dropped**: blanket `Bash(*)`/`PowerShell(*)`, wildcarded interpreters (`Bash(python*)`), package-manager run commands, and `Agent` allow rules. Narrow rules like `Bash(npm test)` carry over; dropped rules return on leaving auto mode. | same | ✓ CONFIRMS `hooks.md:110` |
| D7 | The auto-mode classifier "sees user messages, tool calls, and **your CLAUDE.md content**. Tool results are stripped." | same | ✓ CONFIRMS `claude-md-and-rules.md:45` |
| D8 | Under auto mode, **a subagent's `permissionMode` frontmatter is ignored** — every subagent action goes through the classifier with the parent's rules. | same §How auto mode handles subagents | ⚠ REFINES `agents.md:64` |
| D9 | Boundaries stated in conversation are re-read from the transcript on each classifier check, so **compaction can lose them**. "For a hard guarantee, add a deny rule instead." | same §Boundaries you state in conversation | + NEW — an independent restatement of the advisory-vs-enforced doctrine |
| D10 | **`Write(path)` rules are not matched by file permission checks — only `Edit(path)` rules are**, and an Edit rule covers all file-editing tools. | `/docs/en/permissions` | ✓ CONFIRMS `hooks.md:102`'s first half; + NEW that a `Write(...)` rule silently does nothing |
| D11 | Workspace trust gates project `permissions.allow` **and `permissions.additionalDirectories`**. `deny`/`ask` are unaffected. `.claude/settings.local.json` also goes through the check when the repository could have supplied it (committed to git, or `.claude` is a symlink). | `/docs/en/permissions` §Project allow rules and workspace trust | ✓ CONFIRMS `hooks.md:104-106`; + NEW on `additionalDirectories` and the committed-local-settings case |
| D12 | A blocking hook takes precedence over allow rules: "A hook that exits with code 2 stops the tool call **before permission rules are evaluated**." | `/docs/en/permissions` | ⚠ REFINES `hooks.md:78` |
| D13 | Settings path anchoring: project settings anchor `/path` at the project root; local settings at the original cwd; user settings at `~/.claude/path`. | `/docs/en/permissions` | ✓ CONFIRMS `hooks.md:100` |

## E. Subagents

| # | Fact | Source | Status |
|---|---|---|---|
| E1 | "Explore and Plan **skip your CLAUDE.md files and the parent session's git status**… Every other built-in and custom subagent loads both." and "**There is no frontmatter field or per-agent setting to change which agents skip them.**" | `/docs/en/sub-agents` §What loads at startup | ✓ CONFIRMS `agents.md:25` verbatim — load-bearing, do not cut |
| E2 | A user or project subagent named `Explore` overrides the built-in and keeps its own `model` field. | same | ✓ CONFIRMS `agents.md:30` |
| E3 | `skills:` preloads the **full content** of each named skill at startup. | same | ✓ CONFIRMS `agents.md:37` |
| E4 | The subagent's system prompt **replaces** the default Claude Code system prompt entirely. | same | ✓ CONFIRMS `agents.md:15` |
| E5 | `memory: user\|project\|local` — `project` scope creates a **version-controlled `.claude/agent-memory/<name>/`**, and enabling memory **automatically enables Read, Write, and Edit**. | same §Enable persistent memory | + NEW — collides with the read-only-reviewer shape `agents.md:71`/`:77` makes load-bearing |
| E6 | Output style does not reach a non-fork subagent. A subagent's context window is sized by **its own** model, not the parent's. | same | + NEW |
| E7 | Concurrent subagent limit **20** (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, v2.1.217+); ultracode sessions exempt. Explore and Plan are one-shot, return no agent ID, and cannot be resumed. | same | + NEW |
| E8 | `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1` removes the two built-ins entirely. | same | + NEW |

## F. Corrections to shipped gotchas

| # | What the skill says | What is true | Action |
|---|---|---|---|
| F1 | `hooks.md:86` / `hooks-events.md:330`: "`SessionEnd` **defaults to** 1.5 seconds". | 1.5 s is a **budget shared across all SessionEnd hooks**, not a per-hook default timeout — a different mechanism from every other event. Raising a per-hook `timeout` raises the shared budget to match, up to 60 s. | Rewrite both sites. A wrong gotcha is worse than none (repo CLAUDE.md). |
| F2 | `hooks.md:86`: "**Two** events break the 600 s pattern." | **Three**: `UserPromptSubmit` 30 s, `MessageDisplay` 10 s, `SessionEnd` 1.5 s shared. | Rewrite so the count and the enumeration cannot disagree. |
| F3 | `hooks.md:86` sends the reader to "the timeout column in hooks-events.md". | That table has seven columns; none is a timeout column, and `UserPromptSubmit` is not in the table at all. | Inline the three numbers; drop the pointer. |
| F4 | `SKILL.md:111` Hard line 1: "`validate_harness.py` checks this mechanically." | The dead-link check matches only **backtick-wrapped** `references/x`/`scripts/x` and is called **only with SKILL.md's text**. Twelve of SKILL.md's thirteen concrete reference pointers are bare; reference-to-reference pointers are never scanned; `${CLAUDE_SKILL_DIR}/scripts/...` never matches. The hard line's own headline direction — spec advertises a component that is not on disk — is checked by **nothing**. | Either narrow the claim or widen the check. See `01-changes.md` W7. |
| F5 | `interview.md:103`, `:132`: `audit_harness.py` "parses" the spec's sections and `status` column and "can report precisely which behaviors are unresolved". | It does a substring scan of the raw spec text, one direction only (`audit_harness.py:157-161`), and its own comment at `:165-170` explicitly declines the other direction. `status` is never read (zero occurrences). | See `01-changes.md` W7 — this is a fork, not a wording fix. |
| F6 | `e2e-testing.md:50` passes `${CLAUDE_SKILL_DIR}` inside a **workflow agent prompt**. | The substitution happens in a skill's own markdown body and in `allowed-tools` Bash rules — not in a workflow script's prompt strings and not in a subagent's shell environment. It would expand to empty. | Resolve the absolute path in the composing session and interpolate it as a literal. |
| F7 | `SKILL.md:39` "the first `.claude/` write will prompt (protected path, see Hard lines)". | Hard lines says nothing about protected paths. And the outcome is per-mode (D3), an `Edit(.claude/**)` allow rule does nothing (D2), and the useful detail is the session-scoped approval option (D4). | Rewrite with D2/D3/D4; fix the cross-reference. |

## G. Sourcing note

Some rows above were first surfaced by reading the bundled setup-checkup skill's prompt out of the installed
binary during this planning session. **Every one of them was then re-verified against a public doc page, and
only the public citation is recorded here.** The shipped skill must not name that command or any other Claude
Code UI command (owner decision **D14** in `../00-overview.md` §3.1), and no text from it may be reproduced:
this repo ships as an open-source plugin. The binary was a lead; the docs are the source.
