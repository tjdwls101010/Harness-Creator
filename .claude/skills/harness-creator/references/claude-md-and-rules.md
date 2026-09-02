# CLAUDE.md and rules

This is the authoring guide for the first, most-loaded layer of any harness. Read it the moment a CLAUDE.md line or a rule becomes a candidate in routing, and re-check the generated output against it before declaring the component done.

## What CLAUDE.md actually is

CLAUDE.md content is delivered as a user message injected after the system prompt — it is not the system prompt, and Claude Code makes no enforcement guarantee about it. Claude reads it and tries to comply, the same way it tries to comply with anything else in the conversation, but a determined or confused model can still deviate, and two contradictory instructions get resolved arbitrarily rather than by any override rule. This is why "always/never" language in CLAUDE.md reads as strong to a human but is mechanically just advisory text.

A guarantee — blocking a dangerous command, refusing to touch a path, a lint step that always runs — is not carried by CLAUDE.md; hooks and permissions make behaviour non-optional, and the eligibility test in `references/hooks.md` decides which items earn that (its second question is the one that can come back negative). What CLAUDE.md carries about a guarantee is its *reason*: one line saying why a block is about to happen turns a confusing refusal into an expected one, and under auto mode that line also steers the classifier (loading semantics, below). The rule lives in the deny; the why lives here.

## Target length: ~200 lines

Longer CLAUDE.md files measurably reduce adherence — important rules get lost in the noise, so a complete but bloated file performs worse than a shorter, sharper one. Target under 200 lines per file. The one exception: a monorepo root CLAUDE.md that still overflows after path-specific content has gone into `.claude/rules/*.md`, because what remains is genuinely cross-cutting. Try the split first.

Apply this same eligibility test line by line while drafting: "would removing this line cause Claude to make a mistake?" If not, cut it. A rule Claude already follows correctly without being told is dead weight that pushes real rules further down.

## Pointer policy: never enumerate what the filesystem already tracks

Do not list the project's skills, agents, or hooks by name inside CLAUDE.md. The filesystem is the single source of truth for what components exist; a hand-maintained inventory in CLAUDE.md immediately starts drifting the moment someone adds, renames, or removes a component, and nobody remembers to update the prose list. This exact pattern — full registries of every skill and agent spelled out in CLAUDE.md — goes stale within a few iterations, actively misleading the model about what's available.

Instead, CLAUDE.md holds two kinds of content: trigger rules (when to reach for a capability, stated as a condition, not a name-dump) and core facts (build commands, architecture, environment gotchas). It does not announce what exists, because the client already does — a skill reaches the listing through its own `description`, agents arrive as a list, a hook speaks when it fires, a rule loads when its path matches. The line "`.claude/hooks/no-raw-sql.sh` blocks an edit that adds raw SQL" is not an inventory entry: it is the reason a block will happen, stated before it happens, which is a trigger rule. An inventory is a list of names with no condition attached; a reader who needs that lists `.claude/skills/`, which is always correct.

Don't redirect that job to `.claude/harness-spec.md` either. A pointer inherits its target's reader, and the spec's reader is a maintainer: it carries design rationale and an inventory hand-maintained enough to need its own drift check. A working session sent there pays for all of that to answer a question it never had. A maintainer who wants the way in gets it from an HTML comment, which costs nothing (see the loading semantics below).

## Content eligibility test

Everything in CLAUDE.md must be something Claude cannot infer by reading the code. Concretely, this includes: build and test commands (especially when they're non-default, e.g. "always run a single test file with `npm test -- path/to/file`, not the full suite"), style rules that diverge from the language's own defaults, architecture decisions that aren't visible from the code structure alone ("auth tokens are validated in the gateway, not in each service"), and environment quirks (required env vars, a local service that must be running). Note what is *not* on that list: a personal sandbox URL, your own test credentials, the path where you happen to keep a scratch checkout. Those are real facts Claude needs, but they are yours rather than the team's — see the scope axis below for where they go. Do not include generic software-engineering advice ("write clean code," "handle errors properly") — a competent model already knows this.

When generating a harness, everything you put in CLAUDE.md should be traceable to something the interview surfaced that genuinely can't be recovered by reading the repo. If an interview answer is really just describing what the code already shows, that's a signal the answer doesn't need a CLAUDE.md line at all.

### The line worth keeping is the one that contradicts a default, not the one that repeats it

The test above catches lines that **duplicate** a default. The opposite case is where the best lines live: one that **contradicts** a sensible default. The check is *"delete this line — would Claude get it wrong?"* For a line fighting a default the answer is a clean yes, and nothing in a codebase announces a decision made by *not* doing something — no docstrings on internal helpers, tests colocated against the ecosystem convention, an old API surface kept because a consumer pins it.

Write them as intent, not prohibition, and the reason is the rail argument again: "don't add docstrings" snaps on the first variant nobody enumerated (a type comment, a module header), while "internal helpers under `src/lib/` are deliberately undocumented — the split from `src/api/` is what tells a reader which surface is stable" survives the case you didn't think of. Say what the project wants and why; don't pin the sentence to a description of current model behavior, which dates.

## Write concretely and verifiably

Every instruction should be checkable: "Use 2-space indentation" can be confirmed true or false by looking at a file; "Format code properly" cannot, so the model has nothing concrete to aim for and a reviewer nothing to check. Could someone glance at the codebase and confirm this rule is being followed? If not, sharpen it until they can.

Emphasis markers like "IMPORTANT" or "YOU MUST" raise compliance on the line they're attached to, and the effect saturates and reverses when every third line is shouted — the model can no longer tell which "IMPORTANT" matters this session. Reserve emphasis for the handful of rules where getting it wrong is costly.

## The scope axis: who needs this, and who writes it

The eligibility test asks whether a fact is derivable. It doesn't ask the second question: **true for every clone, or only on this machine?** Answer it generously and a file the whole team pays for on every request fills with one person's sandbox URLs.

| | You write it | Claude writes it |
|---|---|---|
| **Everyone gets it** | `CLAUDE.md`, `.claude/rules/` — committed, reviewed, shared | *(nothing on its own initiative — a shared file Claude writes through this skill is the user writing it, at their request, and reviewed)* |
| **Only this machine** | `CLAUDE.local.md` — gitignored, deterministic, yours | **auto memory** — `MEMORY.md` + topic files |

`CLAUDE.local.md` sits at the project root and loads right after `CLAUDE.md`; it's the documented home for "your sandbox URLs, preferred test data." Route personal facts there and gitignore it in the same pass. Worktree caveat: a gitignored file exists only in the worktree that created it, so a fact that should follow the developer belongs in their home directory, imported as `@~/.claude/my-notes.md`.

**Auto memory is the surface to know about and never to depend on.** Claude writes it into `~/.claude/projects/<project>/memory/`, and `MEMORY.md`'s first 200 lines or 25KB (whichever comes first) load every conversation — a second always-loaded surface holding the same *kind* of content this file routes to CLAUDE.md, which is why it belongs in the budget. But it is nondeterministic by design ("Claude doesn't save something every session. It decides what's worth remembering"), can be switched off entirely (`autoMemoryEnabled: false`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`), and never travels — not committed, not across machines, not into subagents unless one declares its own `memory` field. So it is never the answer to "where should this requirement live." Its use to a generator is subtractive: a reason not to spend a shared line on something Claude learns after one correction.

Reading `MEMORY.md` during the audit (SKILL.md's K1) is by hand, not by script: the slug encoding is undocumented and these are private notes.

## Interoperating with AGENTS.md and other agents' rule files

Claude Code reads `CLAUDE.md`, **not `AGENTS.md`**. A repo with `AGENTS.md`, `.cursorrules`, or `.github/copilot-instructions.md` has no working Claude harness yet, and copying the content across makes two bodies of instructions that drift the moment either is edited. Make `@AGENTS.md` the first line of `CLAUDE.md` and add Claude-specific guidance below it, or symlink when there is nothing Claude-specific to add. Those files are the best interview material in the repo: someone already wrote down what an agent needs to know here, so ask what's missing or stale rather than re-eliciting it.

## Loading semantics — the gotchas that break naive assumptions

Each of these has a direct implication for how you generate or advise on CLAUDE.md.

- **Loaded once at session start, not live.** A project's CLAUDE.md (and any already-loaded rule) is read when a session begins; editing it mid-session has no effect until `/clear`, `/compact`, or a restart. You author harnesses before the sessions that use them, so this rarely bites you — but when you edit an existing CLAUDE.md in a live session, tell the user to restart before trusting that the change took effect.
- **All CLAUDE.md files concatenate; there is no override.** Managed policy, user (`~/.claude/CLAUDE.md`), project, and local files are all appended into context together, ordered broad-to-specific, with no mechanism for a more-specific file to supersede a broader one. If the user-level file says "always use tabs" and the project file you're generating says "use 2-space indentation," both are in context and the model may pick either arbitrarily. During the audit phase, always check whether `~/.claude/CLAUDE.md` exists and read it — a generated project CLAUDE.md that silently conflicts with the user's personal file is a bug you introduced, not a pre-existing condition.
- **`@path` imports expand at launch and save no context.** `@README.md` pulls the full file into context at session start, every session, exactly as if you'd pasted it into CLAUDE.md directly — imports are a readability and organization convenience, not a lazy-loading mechanism. If you want to reference a file's existence in prose without importing its content, wrap the mention in backticks (`` `@README.md` ``); outside backticks, the `@` syntax always expands. Recursive imports are capped at 4 hops.
- **Block-level HTML comments are stripped before injection.** `<!-- like this -->` never reaches the model's context — it's removed at load time, though it stays visible to a human opening the file directly. This is free real estate for maintainer notes ("this section encodes a workaround for the old build system, revisit when upgraded") that cost zero tokens.
- **Rules need `paths:` frontmatter to actually lazy-load.** A file dropped in `.claude/rules/` without a `paths:` key loads at launch with the exact same priority as CLAUDE.md itself — splitting content into `rules/` buys you nothing if you forget the frontmatter. Only a `paths:` glob list makes a rule conditional, loading only when Claude reads a file matching the pattern. Globs support brace expansion, e.g. `src/**/*.{ts,tsx}` for both extensions in one line. Always generate `paths:` on rule files unless the rule is deliberately meant to be global (in which case, ask whether it should just be in CLAUDE.md instead).
- **Subdirectory CLAUDE.md vs. `rules/`: pick by shape, not preference.** A CLAUDE.md placed inside a subdirectory (e.g. `packages/api/CLAUDE.md`) lazy-loads only when Claude reads a file inside that directory — it's directory-scoped ownership, naturally suited to a team or package that wants its own self-contained conventions file living alongside its code. A `rules/*.md` file with a `paths:` glob is centrally located but can target a pattern that cuts across many directories (e.g. every `*.test.ts` file regardless of which package it's in). In a monorepo, default to subdirectory CLAUDE.md when a single directory owns a coherent set of conventions, and default to `rules/` when the same rule needs to apply to a scattered pattern of files across the tree.
- **Compaction does not restore all of these equally, and the split cuts across the monorepo advice above.** After a compaction, the project-root CLAUDE.md is re-read from disk and re-injected, and a rule without `paths:` comes back with it. A **subdirectory CLAUDE.md is not re-injected** — it reloads only the next time Claude reads a file in that directory — and a `paths:`-scoped rule behaves the same way. So on a long session in a monorepo, the conventions that were governing `packages/api/` silently stop governing it after a compaction, until something happens to touch that directory again. This is the one case where the previous bullet's advice needs a caveat: if a rule genuinely must never be absent, its home is the root CLAUDE.md or an unscoped rule, and you pay the always-loaded cost on purpose. Directory-scoped placement is right for conventions whose worst case is "re-derived a bit later," not for the ones a mistake is expensive on.

| Surface | Survives compaction? |
|---|---|
| Project-root `CLAUDE.md`, `CLAUDE.local.md` | Yes — re-read from disk and re-injected |
| Rule without `paths:` | Yes — loads at launch, same as root CLAUDE.md |
| Subdirectory `CLAUDE.md` | **No** — until Claude next reads a file there |
| Rule with `paths:` | **No** — until a matching file is read again |
| A boundary stated only in conversation | **No** — and it isn't stored as a rule at all |

- **The auto-mode classifier reads CLAUDE.md directly.** When a project runs in auto permission mode, a separate classifier model reviews each action and decides whether it looks safe, and that classifier's input includes the generated CLAUDE.md text. This means a prohibition written in CLAUDE.md prose ("never modify files under `legacy/`") isn't purely advisory in auto mode — it measurably steers the classifier's allow/block decisions, even though it's still not a hard guarantee on its own. For anything that must be durably blocked, pair the CLAUDE.md prose with a matching `permissions.deny` rule: the deny rule is what actually can't be bypassed, and the CLAUDE.md text is what makes the classifier's default behavior already point the right way before the deny rule even has to fire.

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

Everything that survived is something the repo cannot tell you itself: which port, how long the suite takes, where auth actually lives, the invariant the query builder protects, and why a hook is about to block you.
