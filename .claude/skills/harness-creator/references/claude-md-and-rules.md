# CLAUDE.md and rules

This is the authoring guide for the first, most-loaded layer of any harness: what CLAUDE.md can and cannot carry, what earns a line in it, where a personal fact goes instead, and the loading semantics that decide whether a rule arrives at all.

## What CLAUDE.md actually is

CLAUDE.md content is delivered as a user message injected after the system prompt — it is not the system prompt, and Claude Code makes no enforcement guarantee about it. Claude reads it and tries to comply, the same way it tries to comply with anything else in the conversation, but a determined or confused model can still deviate, and two contradictory instructions get resolved arbitrarily rather than by any override rule. This is why "always/never" language in CLAUDE.md reads as strong to a human but is mechanically just advisory text.

A guarantee — blocking a dangerous command, refusing to touch a path, a lint step that always runs — is not carried by CLAUDE.md; hooks and permissions make behaviour non-optional, and the eligibility test in `references/hooks.md` decides which items earn that (its second question is the one that can come back negative). Which of the two carries it depends on what the prohibition is made of: one a permission rule can name — a tool, a command pattern, a path — belongs in `permissions.deny`, and one that needs a judgement about content, or has to happen at a moment rather than to a call (a lint step that always runs, a commit message shape), belongs in the hook, which is code and can look. What CLAUDE.md carries either way is the *reason*: one line saying why a block is about to happen turns a confusing refusal into an expected one, and under auto mode that line also steers the classifier (loading semantics, below). The enforcement lives in the layer that can express it; the why lives here.

## Target length: ~200 lines

Longer CLAUDE.md files measurably reduce adherence — important rules get lost in the noise, so a complete but bloated file performs worse than a shorter, sharper one. Target under 200 lines per file. The one exception: a monorepo root CLAUDE.md that still overflows after path-specific content has gone into `.claude/rules/*.md`, because what remains is genuinely cross-cutting. Try the split first.

Apply this same eligibility test line by line while drafting: "would removing this line cause Claude to make a mistake?" If not, cut it. A rule Claude already follows correctly without being told is dead weight that pushes real rules further down.

## Pointer policy: never enumerate what the filesystem already tracks

What is banned is the bare inventory: a list of component names with no condition attached, hand-maintained in CLAUDE.md. It drifts the moment someone adds, renames or removes a component, and then actively misleads the model about what is available — and it buys nothing, because the client already announces existence: a skill reaches the listing through its own `description`, agents arrive as a list, a rule loads when its path matches.

Naming a component is fine, and sometimes necessary, when the line changes what the session does: a condition for reaching a capability, what a block will cost, why an enforcement exists. "`.claude/hooks/no-raw-sql.sh` blocks an edit that adds raw SQL" earns its line — a hook speaks only when it fires, so without that line the first refusal is a surprise. The test is not whether a name appears but whether removing the line would change a session: a condition, a cost or a reason survives it, a registry entry does not.

Don't redirect that job to `.claude/harness-spec.md` either. A pointer inherits its target's reader, and the spec's reader is a maintainer: it carries design rationale and an inventory hand-maintained enough to need its own drift check. A working session sent there pays for all of that to answer a question it never had. A maintainer who wants the way in gets it from an HTML comment, which costs nothing (see the loading semantics below).

## Content eligibility test

Everything in CLAUDE.md must be something Claude cannot infer by reading the code: non-default build and test commands ("run a single test file with `npm test -- path/to/file`, not the full suite"), style rules that diverge from the language's own defaults, architecture decisions invisible in the code structure ("auth tokens are validated in the gateway, not in each service"), environment quirks (required env vars, a local service that must be running). Generic engineering advice ("write clean code") fails the test, and so does an interview answer that describes what the code already shows. A personal sandbox URL or your own test credentials pass it and still don't belong here — real facts, but yours rather than the team's; the scope axis below is where they go.

### The line worth keeping is the one that contradicts a default, not the one that repeats it

The test above catches lines that **duplicate** a default. The opposite case is where the best lines live: one that **contradicts** a sensible default. The check is *"delete this line — would Claude get it wrong?"* For a line fighting a default the answer is a clean yes, and nothing in a codebase announces a decision made by *not* doing something — no docstrings on internal helpers, tests colocated against the ecosystem convention, an old API surface kept because a consumer pins it.

Write them as intent, not prohibition: "don't add docstrings" snaps on the first variant nobody enumerated (a type comment, a module header), while "internal helpers under `src/lib/` are deliberately undocumented — the split from `src/api/` is what tells a reader which surface is stable" survives it. And say what the project wants rather than what the model currently does, which dates.

## Write concretely and verifiably

Every instruction should be checkable: "Use 2-space indentation" can be confirmed true or false by looking at a file; "Format code properly" cannot, so the model has nothing concrete to aim for and a reviewer nothing to check. Could someone glance at the codebase and confirm this rule is being followed? If not, sharpen it until they can.

Emphasis markers like "IMPORTANT" or "YOU MUST" raise compliance on the line they're attached to, and the effect saturates and reverses when every third line is shouted — the model can no longer tell which "IMPORTANT" matters this session. Reserve emphasis for the handful of rules where getting it wrong is costly.

## The scope axis: who needs this, and who writes it

The eligibility test asks whether a fact is derivable. It doesn't ask the second question: **true for every clone, or only on this machine?** Answer it generously and a file the whole team pays for on every request fills with one person's sandbox URLs.

| | Authored and reviewed | Accumulated by Claude |
|---|---|---|
| **Everyone gets it** | `CLAUDE.md`, `.claude/rules/` — committed, reviewed, shared. A file generated through this skill lands here: Claude drafts, the user approves, git records it | *(no surface: nothing Claude writes on its own initiative is shared, which is why the row below never answers a team requirement)* |
| **Only this machine** | `CLAUDE.local.md` — gitignored, deterministic, yours | **auto memory** — `MEMORY.md` + topic files |

`CLAUDE.local.md` sits at the project root and loads right after `CLAUDE.md`; it's the documented home for "your sandbox URLs, preferred test data." Route personal facts there and gitignore it in the same pass. Worktree caveat: a gitignored file exists only in the worktree that created it, so a fact that should follow the developer belongs in their home directory, imported as `@~/.claude/my-notes.md`.

**Auto memory is the surface to know about and never to depend on.** Claude writes it into `~/.claude/projects/<project>/memory/`, and `MEMORY.md`'s first 200 lines or 25KB (whichever comes first) load every conversation — a second always-loaded surface holding the same *kind* of content this file routes to CLAUDE.md, which is why it belongs in the budget. But it is nondeterministic by design ("Claude doesn't save something every session. It decides what's worth remembering"), can be switched off entirely (`autoMemoryEnabled: false`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`), and never travels — not committed, not across machines, not into subagents unless one declares its own `memory` field. So it is never the answer to "where should this requirement live." Its use to a generator is subtractive: a reason not to spend a shared line on something Claude learns after one correction.

## Interoperating with AGENTS.md and other agents' rule files

Claude Code reads `CLAUDE.md`, **not `AGENTS.md`**. So `AGENTS.md`, `.cursorrules` and `.github/copilot-instructions.md` are not loaded as instructions no matter how good they are — a repo can look thoroughly briefed and hand Claude nothing — and copying the content across makes two bodies of instructions that drift the moment either is edited. Make `@AGENTS.md` the first line of `CLAUDE.md` and add Claude-specific guidance below it, or symlink when there is nothing Claude-specific to add. Those files are the best interview material in the repo: someone already wrote down what an agent needs to know here, so ask what's missing or stale rather than re-eliciting it.

## Loading semantics — the gotchas that break naive assumptions

- **Loaded once at session start, not live.** A project's CLAUDE.md (and any already-loaded rule) is read when a session begins; editing it mid-session has no effect until `/clear`, `/compact`, or a restart. You author harnesses before the sessions that use them, so this rarely bites you — but when you edit an existing CLAUDE.md in a live session, tell the user to restart before trusting that the change took effect.
- **All CLAUDE.md files concatenate; there is no override.** Managed policy, user (`~/.claude/CLAUDE.md`), project, and local files are all appended into context together, ordered broad-to-specific, with no mechanism for a more-specific file to supersede a broader one. If the user-level file says "always use tabs" and the project file you're generating says "use 2-space indentation," both are in context and the model may pick either arbitrarily — a conflict you introduce, not a pre-existing one, so read the user-level file the audit names before writing over its subject.
- **`@path` imports expand at launch and save no context.** `@README.md` pulls the full file into context at session start, every session, exactly as if you'd pasted it into CLAUDE.md directly — imports are a readability and organization convenience, not a lazy-loading mechanism. If you want to reference a file's existence in prose without importing its content, wrap the mention in backticks (`` `@README.md` ``); outside backticks, the `@` syntax always expands. Recursive imports are capped at 4 hops.
- **Block-level HTML comments are stripped before injection.** `<!-- like this -->` never reaches the model's context — it's removed at load time, though it stays visible to a human opening the file directly. This is free real estate for maintainer notes ("this section encodes a workaround for the old build system, revisit when upgraded") that cost zero tokens.
- **Rules need `paths:` frontmatter to actually lazy-load.** A file dropped in `.claude/rules/` without a `paths:` key loads at launch with the exact same priority as CLAUDE.md itself — splitting content into `rules/` buys you nothing if you forget the frontmatter. Only a `paths:` glob list makes a rule conditional, loading only when Claude reads a file matching the pattern. Globs support brace expansion, e.g. `src/**/*.{ts,tsx}` for both extensions in one line. Always generate `paths:` on rule files unless the rule is deliberately meant to be global (in which case, ask whether it should just be in CLAUDE.md instead).
- **Subdirectory CLAUDE.md vs. `rules/`: pick by the shape of what the rule covers.** A `packages/api/CLAUDE.md` lazy-loads when Claude reads a file in that directory — directory-scoped ownership, for a package with its own conventions. A `rules/*.md` with a `paths:` glob is central but can target a pattern scattered across the tree (every `*.test.ts`, whichever package it's in).
- **Compaction does not restore the two the same way.** The project-root CLAUDE.md is re-read from disk and re-injected, and a rule without `paths:` comes back with it; a subdirectory CLAUDE.md and a `paths:`-scoped rule do not, reloading only when a matching file is next read. So in a long monorepo session the conventions governing `packages/api/` silently stop governing it after a compaction. Scope by cost, then: directory placement suits conventions whose worst case is "re-derived a bit later," and a rule that must never be absent goes in the root file or an unscoped rule, paying the always-loaded price on purpose.

| Surface | Survives compaction? |
|---|---|
| Project-root `CLAUDE.md`, `CLAUDE.local.md` | Yes — re-read from disk and re-injected |
| Rule without `paths:` | Yes — loads at launch, same as root CLAUDE.md |
| Subdirectory `CLAUDE.md` | **No** — until Claude next reads a file there |
| Rule with `paths:` | **No** — until a matching file is read again |
| A boundary stated only in conversation | **No** — and it isn't stored as a rule at all |

- **The auto-mode classifier reads CLAUDE.md directly.** In auto mode a classifier model reviews each action, and its input includes the CLAUDE.md text — so a prose prohibition ("never modify files under `legacy/`") steers allow/block decisions there rather than being purely advisory. It is still not a guarantee: what the prose buys is a classifier already pointing the right way before the paired deny rule has to fire.

## A good CLAUDE.md, concretely

What survives the rules above states only what the code can't tell you:

```markdown
# Project

<!-- Harness inventory and design rationale: .claude/harness-spec.md -->

## Build & test
- `npm run dev` starts both API (port 3001) and frontend (port 5173).
- Run a single test file: `npm test -- path/to/file.test.ts`. The full
  suite takes ~6 minutes; avoid it unless asked explicitly.

## Style
- API handlers live in `src/api/routes/`, one file per resource.
- Formatting is `npm run lint`'s job, not yours — run it, don't hand-match it.

## Architecture
- Auth tokens are validated in the gateway (`src/gateway/auth.ts`), not in
  individual route handlers — do not add per-route auth checks.

## IMPORTANT
Never write raw SQL in route handlers — use the Knex query builder in
`src/db/`, because it is the only layer that knows every tenant query must
carry the `tenant_id` scope; a raw string bypasses that and leaks rows
across tenants. `.claude/hooks/no-raw-sql.sh` blocks an edit that would add
one, through `Bash` as well as `Edit`; this line exists so you know why
before you hit it.
```
