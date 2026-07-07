# Getting Started

Install harness-creator, invoke it in a project, and walk through your first end-to-end run — audit, interview, generate, validate, wrap-up. This page assumes you already know [what a harness is](Concepts.md); if not, start there.

## Prerequisites

- **Claude Code** — harness-creator is a skill that runs inside it.
- **Python 3.10+** — the four bundled scripts are standard-library-only, so there is nothing to `pip install`.
- **git** — the wrap-up step proposes a commit, and re-entry audits work against your history.

## Install

There are two install paths. They differ only in how you invoke the skill and how edits propagate; the behavior is identical once running. Pick one — running both on the same machine at once double-registers the skill under two different names.

### Option A — plugin (recommended for using it across your projects)

```bash
claude plugin marketplace add tjdwls101010/Harness-Creator
claude plugin install harness-creator@harness-creator
```

Invoked as `/harness-creator:harness-creator` (the plugin namespaces the slash command). Updates arrive via `claude plugin update`.

### Option B — symlink (recommended if you're hacking on this repo)

```bash
ln -s /path/to/harness-creator/.claude/skills/harness-creator ~/.claude/skills/harness-creator
```

Invoked as bare `/harness-creator`. Edits to the skill are reflected immediately in a fresh session — there is no plugin cache to refresh.

## How to invoke

From inside the project you want a harness for, either type the slash command for your install path, or just describe what you want in natural language — auto-triggering works the same either way:

> "Set up a Claude Code harness for this project."

The skill also auto-triggers on requests to improve or extend an existing `.claude/` setup, or on questions about how Claude should be configured for your codebase. Korean requests trigger it too (for example, "하네스 만들어줘").

## Your first run, end to end

The skill runs a five-part loop. Expect it to ask questions and to gate on your approval before writing anything — it never guesses at a requirement it could ask about, and every decision is recorded in a spec file so the next invocation has something to audit against.

1. **Audit** — before anything else, it inventories any existing `.claude/` setup, checks for a `.claude/harness-spec.md`, and scouts your codebase (build system, language, test runner, team-size signals). From that it picks a mode: a new build, an **extend**, an **improve**, or a **sync** (see [Re-entry Modes](Re-entry-Modes.md)). On a clean project this is a new build.
2. **Interview** — a staged conversation: goals & pain points → behavior inventory → layer routing → component detail → validation plan. Structured multiple-choice questions are used to converge among known options; open dialogue is used to explore goals where the option space isn't known yet. Each stage ends by updating `.claude/harness-spec.md` and pausing at an approval gate. The spec-approval gate is never skipped — it's the written record of what you agreed to. See [The Interview & Spec](The-Interview.md).
3. **Generate** — only after the spec is approved. For each behavior, it routes to the right layer (see [Layer-Routing](Layer-Routing.md)), loads the matching authoring reference, and writes the files: some subset of `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, hooks + permissions in `.claude/settings.json`, `.claude/agents/`, and `.claude/workflows/`. It then runs `validate_harness.py` and fixes findings until it exits with zero errors — a harness is not called done until that passes.
4. **Offer validation** — hook unit tests via `test_hook.py` are free and run against any generated hook. A deeper end-to-end pass, which spawns real headless sessions and grades their transcripts, spends real tokens and only runs with your explicit consent. See [Validation & Testing](Validation.md).
5. **Wrap-up** — one final whole-harness `validate_harness.py` pass, a change-history entry in the spec, any needed `CLAUDE.md` pointer updates, and a proposed commit.

You stay in control the whole way. When in doubt it asks rather than assumes, and the spec is your written record of everything that was decided.

## The protected-path prompt

The first time the skill writes anything under `.claude/`, Claude Code will prompt you to approve it. This is expected: `.claude/` is a **protected path**, and that safety check runs before any allow-rule you might have configured — so no permission setting can pre-clear it. The skill warns you this prompt is coming before it starts generating.

When it appears, choose the option to **allow Claude to edit its own settings for this session**. That approves the subsequent `.claude/` writes for the rest of the session, so you approve once rather than on every file. Approving it for the session is the normal, intended flow.

## Verifying the install worked

- **Plugin install:** `claude plugin details harness-creator` should report `Skills (1) harness-creator`.
- **Either path:** start a fresh session in any project and type `/` — the harness-creator command should appear (as `/harness-creator` for the symlink, `/harness-creator:harness-creator` for the plugin). A natural-language request like "set up a harness for this project" should also trigger it.
- **The scripts:** run `python3 /path/to/harness-creator/.claude/skills/harness-creator/scripts/validate_harness.py --path .` against any project — a clean exit code 0 confirms the Python toolchain is wired up. See [The Scripts](Scripts.md) for what each one does.

## Next

- [The Interview & Spec](The-Interview.md) — a closer look at the staged conversation you just met.
- [Layer-Routing](Layer-Routing.md) — the decision at the heart of what the skill generates.
- [Re-entry Modes](Re-entry-Modes.md) — what happens the second time you run it on a project that already has a harness.
