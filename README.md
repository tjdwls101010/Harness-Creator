# harness-creator

A meta-skill for [Claude Code](https://claude.com/claude-code) that designs, generates, validates, and maintains a complete Claude Code harness for a project.

`ai-agent = model + ai-harness`. A harness is the CLAUDE.md, rules, skills, hooks, permissions, agents, and workflows that shape how Claude works in a given repo. Building a good one by hand means knowing dozens of non-obvious gotchas (hook exit codes, matcher syntax, CLAUDE.md loading semantics, and more) and asking yourself the right interview questions. harness-creator runs that interview, routes each thing you want to the right layer, generates the files, and validates them before calling itself done.

## What it does

Call it (`/harness-creator` or a natural-language request like "set up a harness for this project") and it will:

1. Audit any existing `.claude/` setup and figure out whether this is a new build, an extension, an improvement, or a drift-sync.
2. Interview you in stages — goals, behavior inventory, layer routing, component detail, validation plan — with a spec document (`.claude/harness-spec.md`) as the running source of truth.
3. Generate the components, running a deterministic lint (`validate_harness.py`) until it passes with zero errors.
4. Offer hook unit tests (free) and, with your consent, an end-to-end validation pass using headless Claude sessions.

See [.claude/skills/harness-creator/SKILL.md](.claude/skills/harness-creator/SKILL.md) for the full operating loop and layer-routing framework, and [docs/plan/](docs/plan/) for the design rationale behind every decision.

## Install

**Option A — plugin (recommended for using it in other projects):**

```bash
claude plugin marketplace add tjdwls101010/Harness-Creator
claude plugin install harness-creator@harness-creator
```

The skill is namespaced under the plugin, so it's invoked as `/harness-creator:harness-creator` (auto-trigger via natural language works the same either way).

**Option B — symlink (recommended if you're developing this repo itself):**

```bash
ln -s /path/to/harness-creator/.claude/skills/harness-creator ~/.claude/skills/harness-creator
```

Edits to the skill are reflected immediately in a fresh session — no plugin cache to refresh. Invoked as bare `/harness-creator`. Don't run both install paths at once on the same machine: the same skill would register under two different names.

## Status

v0.1.0 — implementation complete against [docs/plan/06-milestones.md](docs/plan/06-milestones.md) (M0–M5): the plugin/marketplace path and the symlink dev path both verified working, all 8 reference files and 4 scripts written and self-tested (78 passing unit tests against hand-built fixture harnesses), the skill dogfooded end to end against a real project (audit → interview → generate → validate → re-entry check). The plan itself was written and adversarially reviewed in a separate planning session before implementation began.

Two things a fresh user should know going in: `run_e2e.py`'s headless permission handling (`--isolate` + `--dangerously-skip-permissions`) is a documented best guess, not empirically confirmed in an authenticated environment — the implementation sandbox that built it couldn't log in a spawned `claude` process to test it, so treat your first real e2e run as the actual verification. And installing the plugin from a **local directory path** (as opposed to the real GitHub source) copies the raw filesystem, including anything gitignored — harmless but worth knowing if you're testing from a local checkout.
