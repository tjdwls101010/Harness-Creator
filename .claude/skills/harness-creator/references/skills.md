# Generating skills

You are generating a SKILL.md (and possibly `references/` and `scripts/`) for someone else's project. This file is what you follow while doing that. The authoring doctrine it applies lives in SKILL.md; what's here is the part that only makes sense once the target is a skill — triggering, the listing budget, bundled scripts, and the traps specific to how Claude Code implements skills.

## What "Conviction over compliance" looks like in a skill body

SKILL.md states the rule; this is the picture of it. Compare:

> **Rail:** "Never query the `subscriptions` table by `created_at`."
> **Principle:** "The `subscriptions` table is append-only — every plan change inserts a new row rather than updating the old one. The row you want is the one with the highest `version`, not the newest `created_at`; a query ordered by `created_at` silently returns a stale plan on any account that has ever changed tiers."

The rail bans one query shape. The principle explains the table's actual shape, so the model also gets joins, aggregates, and migration scripts right — cases the rail never listed. When you're tempted to enumerate a scenario for every case you can think of, that's the signal to step back: state the principle once, make it vivid with 2-3 real cases, and stop.

## The gotcha filter also decides whether the skill should exist

"Don't write what a capable model already knows" (SKILL.md) filters content everywhere; on a skill it additionally decides existence. What survives it is knowledge the model has no way to already have — this project's conventions, a proprietary workflow, a decision already made (the exact command, the schema a script depends on), and above all the gotcha. So while interviewing, listen for the sentence that starts "oh, and one thing that always trips people up..." — that sentence is the skill's entire reason to exist. A skill built from a user's general preferences and no gotchas isn't worth generating; if the interview surfaces none, say so and suggest a CLAUDE.md line instead.

## Progressive disclosure is an optimum, not a direction

A skill loads in three stages: metadata (name + description) is in context every session; the SKILL.md body loads once the skill triggers; bundled `references/` and `scripts/` load only when a step actually reaches them. This staging exists because irrelevant text degrades the model even when the tokens are technically free — a long body buries its own key instructions where attention thins. So the question for every piece of content you're about to write is not "is this useful?" but "is this needed on *every* path through the skill?" Needed every time it triggers → SKILL.md body. Needed only on some paths (a schema used at one step, a framework-specific variant, a deep worked example) → `references/`.

But splitting has a cost that points the opposite direction: every reference file is a routing decision you're handing to a future invocation of the model — *which file do I open for this?* Split along a seam the model can recognize instantly and the answer is obvious. Shatter the same material into a dozen topic-named fragments and the model spends judgment deciding what to read, and sometimes doesn't know a needed fragment exists at all. That failure is silent: nothing signals that the model routed wrong, so it just quietly does a worse job. This is why the split axis is **invocation pattern, not volume**. "This file feels long, let's move a section out" is the wrong test and produces exactly this failure mode; "does the model choose between variants of this file depending on what it's doing" is the right one. A skill that covers three cloud providers earns `references/{aws,gcp,azure}.md` because the model picks exactly one per invocation. A skill that covers one procedure does not earn a second file just because the body got long — inline it, and cut something else instead if length is truly a problem. (`validate_harness.py` warns past a body-length guideline and its message carries the number, so you don't have to hold one.)

**A skill that will be packaged has to be self-contained, and the interview's Deployment question is when you learn that.** A plugin installs as its own directory: the repo it was written in does not come along, so a line sending the reader to a design doc elsewhere in that repo resolves for its author and for nobody else. This is where the split axis stops being only about attention — material a packaged skill genuinely needs belongs in its own `references/`, and material it merely cites belongs cited by public source rather than by local path. A project skill is under no such constraint; it lives in the repo it points into.

When you generate a multi-file skill for someone else's project, ask specifically: on any given invocation, does the model actually choose a branch, or would it need all these files together anyway? If the answer is "together," that's evidence they should be one file, regardless of resulting length.

## description is the only trigger mechanism

The frontmatter `description` (plus `when_to_use`, which is appended to it) is the entire signal Claude uses to decide whether to load a skill at all. A "When to use this skill" section written into the body does nothing for triggering — the body only loads *after* the decision to trigger has already been made. Every triggering-relevant fact belongs in `description`.

Current models under-trigger: they skip a skill that would have helped rather than load one that turns out unneeded. The asymmetry in cost is not symmetric either — a skill that loads when marginally unneeded costs a little context; a skill that stays dark when it was actually needed costs the entire skill. So when generating a description, lean deliberately toward triggering. Weak: "How to build a dashboard for internal data." Strong: "How to build a dashboard for internal data. Use whenever the user mentions dashboards, metrics, or displaying company data — even if they never say 'dashboard.'" The second version names the underlying intent, not just the surface keyword, because a real user asking for this will often describe the need without naming the thing.

Equally important, and easy to skip under time pressure: describe the **near-misses** — requests that sound adjacent but should route elsewhere. A skill for "deploy to production" should note in its description that routine `git push` or local test runs are out of scope, if another skill or plain judgment already covers those; without that boundary language, an eagerly-tuned description starts stealing triggers from its neighbors, and the failure is just as silent as under-triggering because nothing tells you which skill actually ran. When you generate several skills for one project in the same session, read their descriptions against each other before finishing — that's the moment to catch two skills quietly competing for the same request.

## Scripts must be parameterized, never frozen

A bundled script earns its place only if the model can compose with it: a CLI that takes arguments (`validate.py --path <dir> --strict`) or importable helpers it assembles for the task at hand. The trap is the frozen script — no arguments, one hardcoded purpose, written for the exact case in front of you. It cannot be reused, so the instant the task shifts the model rewrites it from scratch, and the bundle bought the project nothing while still costing a file to maintain. Write the parameterized version even if the immediate ask looks one-shot — a one-shot script is a sign the content belongs inline as an instruction, not as a script at all.

Parameterized is necessary but not sufficient — the parameters have to describe themselves. An argument declared without `help=` prints as a bare flag name in `--help`, so the model opens the source to learn what it takes and the interface reverts to the document it was meant to replace. Give every argument a `help=` and the parser a `description=`; where a parameter's space is closed, `choices=` teaches the cases by existing.

## Skill count is itself a cost

The interview should look for consolidation, not default to one skill per requested behavior. Every skill's description sits in a shared listing whose entire budget is about 1% of the context window (configurable, but that's the default every project starts from). That budget is spent on every session regardless of whether any skill triggers. Add skills one at a time and each new description silently taxes every other skill's share; once the listing overflows the budget, the descriptions of the skills you invoke *least* collapse to bare names — no description at all — which quietly disables their ability to auto-trigger without ever producing an error. This is why, during the interview, three related behaviors a user asks for in three separate breaths (e.g. "a skill for opening PRs," "a skill for checking CI status," "a skill for merging when green") are a prompt to ask whether they're really one skill with three steps rather than three skills with three descriptions eating the same budget. Consolidate when the behaviors share a trigger context and a user would think of them as one job; keep them separate only when they trigger from genuinely different situations, because forcing unrelated triggers into one description makes that description vaguer and worse at triggering for either job.

## Frontmatter fields worth a judgment call

| Field | What it decides | When to set it |
|---|---|---|
| `description` | The only trigger signal (see above). Combined with `when_to_use`, truncated at 1,536 characters in the skill listing — put the triggering-critical clause first, not last. | Always write deliberately; never leave to the body's first paragraph. |
| `disable-model-invocation` | `true` removes the skill from auto-triggering (and from the context budget entirely) — only `/name` invokes it. | Side-effecting actions the user must time themselves: deploys, sending a message, committing. Never for something Claude deciding on its own would be a convenience, not a risk. |
| `user-invocable` | `false` hides it from the `/` menu; Claude can still trigger it. | Background domain knowledge that isn't an action a user would ever type as a command. |
| `allowed-tools` | Pre-approves specific tools while the skill is active, cutting permission-prompt friction. Does not restrict the tool pool otherwise. | A skill whose steps reliably need the same one or two tools (e.g. `Bash(git commit *)` for a commit skill) — pair it with the tools the skill's own instructions actually call. |
| `context: fork` + `agent:` | Runs the skill body as the subagent's *entire prompt* instead of inline — isolates context, but only makes sense when the body is an actionable task, not reference guidance. Pair it with `allowed-tools` so the forked run doesn't stall on a permission prompt mid-flight. | Research- or review-shaped work that should not consume the main conversation's context. Never for a skill whose content is "use these conventions" with no task verb. Targeting the built-in `Explore` or `Plan` agent means the body must be self-contained about project facts — those two skip CLAUDE.md (see references/agents.md). |
| `paths` | Restricts auto-activation to when the model is working with matching files. | A skill that's only relevant to one part of a monorepo (mirrors `rules` glob semantics). |
| `hooks` | Declares hooks scoped to this skill's own active lifetime, same event/matcher/handler shape as settings.json (see references/hooks.md's "Hooks can also live in a skill's or agent's own frontmatter"). Command paths resolve relative to the skill's own directory, not `${CLAUDE_PROJECT_DIR}`. Uniquely supports `once: true` per handler (runs once per session, then removes itself — not honored anywhere else). | Only when a check genuinely needs to be enforced, not just remembered — and only after checking it won't over-fire on the skill's own intermediate, mid-draft tool calls (see references/hooks.md's eligibility test). |

## Five gotchas you cannot derive from general skill-writing sense

These are the traps that are specific to how Claude Code implements skills — not general writing advice, and not things a capable model already knows.

**The invocable command name comes from the directory, not `name`.** `name` in frontmatter is a display label only. A skill at `.claude/skills/deploy-staging/SKILL.md` is invoked as `/deploy-staging` regardless of what `name` says — set `name: Deploy to Staging` for a nicer listing and the command is still `/deploy-staging`. The directory name *is* the interface contract; naming it sloppily (`skill1`, `helper`) breaks discoverability in a way no frontmatter fix can repair without moving the whole directory.

**A broken frontmatter YAML doesn't break the skill — it breaks auto-triggering, silently.** If the YAML between the `---` markers fails to parse, Claude Code still loads the body with empty metadata: `/skill-name` keeps working by direct invocation, but there is no `description` for Claude to match against, so the skill simply never auto-triggers again and nothing errors to say so. This is exactly the kind of silent failure a lint pass has to catch.

**`/compact` doesn't re-inject the skill listing.** A skill that never triggered before the compaction boundary is gone from the model's awareness for the rest of that session, as completely as if it didn't exist. So for any behavior the harness truly cannot afford to lose over a long session, back it with a one-line trigger rule in CLAUDE.md — that file is re-read at session start and untouched by compaction.

**`` !`command` `` is preprocessing, not something the model executes.** The backtick-wrapped syntax runs a shell command before the skill content is ever sent to the model; the command's stdout replaces the placeholder in the text, so what the model actually receives is the literal output, never the command itself and never a live tool call it could reason about. This is the right mechanism for injecting session-start state ("Current branch: `` !`git branch --show-current` ``") because it guarantees freshness without spending a tool-use turn — but it also means the model cannot conditionally decide not to run it; it always runs when the skill loads.

**SKILL.md edits take effect immediately within the current session — CLAUDE.md edits do not** (see `references/claude-md-and-rules.md`). That makes SKILL.md the fast iteration surface during the generate loop: draft, test-trigger it in the same session, revise. A CLAUDE.md edit in the same pass needs the user told to restart before they trust it.

## A well-structured skill, concretely

A skill for filing well-formed bug reports against a project's issue tracker, where the project has several distinct issue templates:

```
file-bug-report/
├── SKILL.md                    — triggers, the decision of which template applies, the procedure
├── references/
│   ├── template-crash.md       — fields + example for a crash/exception report
│   ├── template-regression.md  — fields + example for "used to work, now doesn't"
│   └── template-feature.md     — fields + example for a feature request
└── scripts/
    └── file_issue.py           — CLI: file_issue.py --template crash --title "..." --body-file f.md
```

SKILL.md stays short: trigger conditions, the one gotcha that matters here ("this tracker's 'priority' field is required at creation time and can't be changed after — ask up front"), which template to open, and where the script is. Each `references/template-*.md` holds one report type and nothing about the others, because a single invocation needs exactly one. The split follows the branch the model actually takes. With only one template, the right shape would be zero reference files and the template inlined — a routing decision that saves no reading is pure cost.
