# CLAUDE.md and rules

This is the authoring guide for the first, most-loaded layer of any harness. Read this before drafting a project's CLAUDE.md or any `.claude/rules/*.md` file, and re-check the generated output against it before declaring the component done.

## What CLAUDE.md actually is

CLAUDE.md content is delivered as a user message injected after the system prompt — it is not the system prompt, and Claude Code makes no enforcement guarantee about it. Claude reads it and tries to comply, the same way it tries to comply with anything else in the conversation, but a determined or confused model can still deviate, and two contradictory instructions get resolved arbitrarily rather than by any override rule. This is why "always/never" language in CLAUDE.md reads as strong to a human but is mechanically just advisory text.

The practical consequence for you as the generator: anything that must hold with zero exceptions — blocking a dangerous command, refusing to touch a path, guaranteeing a lint step runs — does not belong in CLAUDE.md. Route it to a hook (deterministic, fires on the lifecycle event regardless of what the model decides) paired with a `permissions.deny` rule where applicable (enforced by the client, not the model). CLAUDE.md's job is to carry facts and steer behavior; hooks and permissions are the layer that makes behavior non-optional. When you're deciding where an interview answer belongs, ask "does this need to be true every single time, or is it fine if Claude usually gets it right?" — the former routes away from this file entirely.

## Target length: ~200 lines

Longer CLAUDE.md files measurably reduce adherence — the model has more text to track and important rules get lost in the noise, so a file that is technically complete but bloated can perform worse than a shorter, sharper one. Target under 200 lines per file. The one stated exception: a monorepo root CLAUDE.md that still overflows after you've already split path-specific content into `.claude/rules/*.md` may legitimately exceed 200 lines, because at that point the remaining content is all genuinely cross-cutting and there's nowhere left to push it. Don't reach for that exception as a shortcut — try the split first.

Apply this same eligibility test line by line while drafting: "would removing this line cause Claude to make a mistake?" If not, cut it. A rule Claude already follows correctly without being told is dead weight that pushes real rules further down.

## Pointer policy: never enumerate what the filesystem already tracks

Do not list the project's skills, agents, or hooks by name inside CLAUDE.md. The filesystem is the single source of truth for what components exist; a hand-maintained inventory in CLAUDE.md immediately starts drifting the moment someone adds, renames, or removes a component, and nobody remembers to update the prose list. This exact pattern — full registries of every skill and agent spelled out in CLAUDE.md — goes stale within a few iterations, actively misleading the model about what's available.

Instead, CLAUDE.md should hold three kinds of content: trigger rules (when to reach for a capability, stated as a condition, not a name-dump), core facts (build commands, architecture, environment gotchas), and a single pointer to `.claude/harness-spec.md` for anyone who wants the full picture of what the harness contains and why. If a future reader needs to know exactly which skills exist, they list the `.claude/skills/` directory — that is always correct, unlike prose.

## Content eligibility test

Everything in CLAUDE.md must be something Claude cannot infer by reading the code. Concretely, this includes: build and test commands (especially when they're non-default, e.g. "always run a single test file with `npm test -- path/to/file`, not the full suite"), style rules that diverge from the language's own defaults, architecture decisions that aren't visible from the code structure alone ("auth tokens are validated in the gateway, not in each service"), and environment quirks (required env vars, a local service that must be running). Note what is *not* on that list: a personal sandbox URL, your own test credentials, the path where you happen to keep a scratch checkout. Those are real facts Claude needs, but they are yours rather than the team's — see the scope axis below for where they go. Do not include generic software-engineering advice ("write clean code," "handle errors properly") — a competent model already knows this, and stating it wastes a line without changing behavior.

When generating a harness, everything you put in CLAUDE.md should be traceable to something the interview surfaced that genuinely can't be recovered by reading the repo. If an interview answer is really just describing what the code already shows, that's a signal the answer doesn't need a CLAUDE.md line at all.

### The line worth keeping is the one that contradicts a default, not the one that repeats it

The test above catches instructions that **duplicate** what the model already does. It does not catch the opposite case, and the opposite case is where the highest-value lines live: an instruction that **contradicts** a sensible default. Ask "if I deleted this line, would Claude get it wrong?" — for a line fighting a default, the answer is a clean yes, and that is exactly what earns its tokens. A project that wants no docstrings on internal helpers, or that wants tests colocated when the ecosystem convention is a `tests/` tree, or that wants an older API surface kept because a downstream consumer pins it, has to say so; nothing in the codebase announces a decision that was made by *not* doing something.

Write these as intent, not prohibition. "Don't add docstrings" holds only the case its author listed and snaps on the first variant — a type comment, a module header — that wasn't enumerated. "Internal helpers under `src/lib/` are deliberately undocumented; the public API in `src/api/` carries full docs, and that split is what tells a reader which surface is stable" lets the model re-derive the rule for a case nobody wrote down. The same shape applies to any harness layer, not just CLAUDE.md.

One caution when you write one of these: a default you're contradicting is a moving target. Say what the project wants and why, and avoid pinning the sentence to a description of current model behavior that will read as false in a year.

## Write concretely and verifiably

Every instruction should be checkable, not aspirational. "Use 2-space indentation" is verifiable — you can look at a file and confirm it's true or false. "Format code properly" is not — there's no way to check compliance, so the model has nothing concrete to aim for and reviewers have nothing concrete to check against. Apply this test to every line you generate: could someone glance at the codebase and confirm this rule is (or isn't) being followed? If not, sharpen it until they can.

Emphasis markers like "IMPORTANT" or "YOU MUST" measurably raise compliance on the line they're attached to, but this effect saturates and then reverses: a file where every third line is shouted stops reading as prioritized and starts reading as noise, and the model can no longer tell which of the ten "IMPORTANT"s is the one that actually matters this session. Reserve emphasis for the handful of rules where getting it wrong is genuinely costly, and let the rest read as plain, confident statements.

## The scope axis: who needs this, and who writes it

"Does this belong in CLAUDE.md?" has a second half that the eligibility test above doesn't ask: **is this fact true for every clone of the repo, or only on this developer's machine?** Get it wrong in the generous direction and a shared, version-controlled file that every teammate pays for on every request fills up with one person's sandbox URLs. There are four places a durable fact can live, and they differ on two axes — who it's for, and who writes it.

| | You write it | Claude writes it |
|---|---|---|
| **Everyone gets it** | `CLAUDE.md`, `.claude/rules/` — committed, reviewed, shared | *(nothing — Claude never authors a shared file on its own)* |
| **Only this machine** | `CLAUDE.local.md` — gitignored, deterministic, yours | **auto memory** — `MEMORY.md` plus topic files, machine-local |

`CLAUDE.local.md` sits at the project root, loads alongside `CLAUDE.md` and immediately after it, and is the documented home for "your sandbox URLs, preferred test data." When the interview surfaces a fact that is real but personal, route it here and say why: it keeps the team's always-loaded budget clean, and it keeps a teammate from inheriting a URL that only resolves on someone else's laptop. Add it to `.gitignore` in the same pass. One caveat for anyone using git worktrees: a gitignored `CLAUDE.local.md` exists only in the worktree where it was created, so a fact that should follow the developer everywhere is better written once in their home directory and imported with `@~/.claude/my-notes.md`.

**Auto memory is the surface to know about but never to depend on.** Claude writes it itself — build commands it worked out, debugging insights, preferences it noticed — into `~/.claude/projects/<project>/memory/`, and the first 200 lines or 25KB of `MEMORY.md` (whichever comes first) load into every conversation. So it is a second always-loaded instruction surface carrying the same *kind* of content this file routes to CLAUDE.md, which is exactly why it belongs in the budget question. Three properties make it a destination you must not route requirements to:

- **It is nondeterministic.** "Claude doesn't save something every session. It decides what's worth remembering." A fact Claude *must* have cannot be filed somewhere that may or may not record it.
- **It can be switched off entirely** — `autoMemoryEnabled: false` in any settings scope, or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`. Nothing load-bearing may assume it exists.
- **It is machine-local and never travels.** Not committed, not shared across machines or cloud environments, and not loaded into subagents unless a subagent declares its own `memory` field.

The practical use for a generator is subtractive: auto memory is a reason *not* to spend a shared CLAUDE.md line on something Claude will pick up on its own after one correction. It is never the answer to "where should this requirement live."

During Phase 0, it's worth reading the project's `MEMORY.md` if it exists — it is the most honest available record of what Claude has repeatedly needed here, which makes it interview material of unusually high quality. Read it, don't script it: the directory-slug encoding isn't documented, and it's the user's private notes.

## Interoperating with AGENTS.md and other agents' rule files

Claude Code reads `CLAUDE.md`, **not `AGENTS.md`**. A repo that already has `AGENTS.md`, `.cursorrules`, or `.github/copilot-instructions.md` is not a repo with a working Claude harness, and the fix is not to copy the content across — a parallel body of instructions drifts the moment either side is edited, and then two agents disagree about the same project. Make `@AGENTS.md` the first line of `CLAUDE.md` and add Claude-specific guidance below it, or symlink one to the other when there's nothing Claude-specific to add.

Treat those files as the best interview material in the repo. Someone already did the work of writing down what an agent needs to know here; the interview's job is to ask what's missing or stale, not to re-elicit it from scratch.

## Loading semantics — the gotchas that break naive assumptions

These behaviors are not what most people expect from "a config file Claude reads," and each one has a direct implication for how you generate or advise on CLAUDE.md.

- **Loaded once at session start, not live.** A project's CLAUDE.md (and any already-loaded rule) is read when a session begins; editing it mid-session has no effect until `/clear`, `/compact`, or a restart. You author harnesses before the sessions that use them, so this rarely bites you — but when you edit an existing CLAUDE.md in a live improve/sync pass, tell the user to restart before trusting that the change took effect.
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

## A good vs. bad CLAUDE.md, side by side

**Bad** — enumerates components (goes stale immediately) and states unverifiable, uncheckable advice:

```markdown
# Project

We have the following skills: deploy, review-pr, migrate-db, seed-fixtures,
generate-report, sync-schema.

Our agents: security-reviewer, perf-auditor, doc-writer.

## Style
Write clean, maintainable code. Follow best practices. Be consistent.

## Testing
Test your changes before committing.
```

Every claim here is either a list that will drift the first time someone adds a skill, or advice too vague to check against actual behavior.

**Good** — points at the filesystem instead of listing it, and states only what the code can't tell you:

```markdown
# Project

See `.claude/harness-spec.md` for the full harness inventory and design
rationale.

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
`src/db/`. A PreToolUse hook blocks commits containing raw SQL strings;
this line exists so you know why that hook fires before you hit it.
```

Notice the last block: the hook does the actual enforcement, and the CLAUDE.md line exists only to explain *why*, so the model isn't confused when the hook blocks it. That's the correct division of labor between this layer and the enforcement layer.

Notice two things this file does **not** say, both of which a first draft usually contains. It never summarizes the stack — `package.json` already answers "what is this project," and a line restating it is pure cost. And it doesn't restate the formatting rules the linter enforces; it points at the linter instead, because a rule with a mechanical enforcer already has a better home than prose. Everything that survived is something the repo genuinely cannot tell you: which port, how long the suite takes, where auth actually lives, and why a hook is about to block you.
