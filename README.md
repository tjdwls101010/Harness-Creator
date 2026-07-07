<div align="center">

# harness-creator

**A meta-skill for [Claude Code](https://claude.com/claude-code) that designs, generates, validates, and maintains a complete harness for your project — through a structured interview.**

[![Version](https://img.shields.io/badge/version-0.1.0-blue)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%20skill-8A63D2)](https://claude.com/claude-code)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

</div>

---

## The idea in one line

> **`ai-agent = model + ai-harness`**

The *model* is fixed — you get Claude's intelligence out of the box. What actually determines how well Claude works in **your** repo is the **harness**: the `CLAUDE.md`, rules, skills, hooks, permissions, agents, and workflows that tell it what this project needs and quietly keep it on the rails.

A good harness is worth a lot. But building one by hand means knowing dozens of non-obvious mechanics — which hook exit code actually blocks (it's not the one you'd guess), when a matcher silently becomes a regex, why an `@path` import doesn't save context, which subagents skip your `CLAUDE.md` entirely — *and* asking yourself the right interview questions about your own project. Most people never get there, and the harnesses that do get built tend to rot.

**harness-creator** is the meta-layer that does it for you. You invoke it in a project; it interviews you, routes each thing you want to the right layer, generates the files, and refuses to call itself done until a deterministic linter passes with zero errors.

## Table of contents

- [What it produces](#what-it-produces)
- [Install](#install)
- [Quickstart](#quickstart)
- [How it works](#how-it-works)
- [The tools it ships with](#the-tools-it-ships-with)
- [Project layout](#project-layout)
- [Documentation](#documentation)
- [Status & limitations](#status--limitations)
- [Design philosophy](#design-philosophy)
- [Contributing](#contributing)
- [License](#license)

## What it produces

harness-creator can generate any subset of the seven harness layers, choosing each one deliberately rather than by default:

| Layer | What it's for |
|---|---|
| **`CLAUDE.md`** | Project facts and constraints relevant to nearly every session. |
| **`.claude/rules/*.md`** | Rules scoped to part of the tree via a `paths:` glob — loaded only when a matching file is touched. |
| **`.claude/skills/`** | Procedures, playbooks, and domain knowledge that load on demand. |
| **hooks + permissions** | The *enforcement* layer — deterministic guarantees for things that must (or must never) happen. |
| **`.claude/agents/*.md`** | Context-isolated subagents for read-heavy roles (research, review, QA). |
| **`.claude/workflows/*.js`** | Fixed-shape, repeatable orchestrations run as a one-button `/command`. |
| **`.claude/harness-spec.md`** | A persisted spec — the single source of truth for what the harness contains and why. |

The heart of the skill is a **layer-routing framework**: for each behavior you want, it asks *is this enforced or advisory? when does it need to load? what does it cost?* — and those three answers name the layer. See **[The Layer-Routing Framework](docs/wiki/Layer-Routing.md)**.

## Install

### Option A — plugin (recommended for using it across your projects)

```bash
claude plugin marketplace add tjdwls101010/Harness-Creator
claude plugin install harness-creator@harness-creator
```

Invoked as `/harness-creator:harness-creator` (or just describe what you want in natural language — auto-triggering works the same).

### Option B — symlink (recommended if you're hacking on this repo)

```bash
ln -s /path/to/harness-creator/.claude/skills/harness-creator ~/.claude/skills/harness-creator
```

Invoked as bare `/harness-creator`. Edits are reflected immediately in a fresh session — no plugin cache to refresh. Don't run both install paths on the same machine at once; the skill would register under two different names.

**Requirements:** Claude Code, Python 3.10+ (for the bundled scripts — standard library only, no dependencies to install), and git.

## Quickstart

From inside the project you want a harness for:

```
/harness-creator:harness-creator
```

or just:

> "Set up a Claude Code harness for this project."

What happens next:

1. **Audit** — it inventories any existing `.claude/` setup and decides whether this is a new build, an extension, an improvement, or a drift-sync.
2. **Interview** — a staged conversation (goals → behavior inventory → layer routing → component detail → validation plan), using structured questions to converge and open dialogue to explore. A running spec (`.claude/harness-spec.md`) records every decision.
3. **Generate** — it writes the components, running its linter until zero errors.
4. **Validate** — it offers free hook unit-tests and, with your consent, an end-to-end pass over real headless sessions.
5. **Wrap up** — it records the change history, updates pointers, and proposes a commit.

You stay in control the whole way: it asks before it assumes, and the spec is a written record of everything you agreed to.

## How it works

```
Invocation
 └─ Phase 0. Audit           inventory .claude/, detect drift, pick a mode
 └─ Phase 1–N. Interview     staged questions, each gated on your approval, spec updated as you go
 └─ Generate                 load the right reference per component, write files, lint to zero errors
 └─ Offer validation         hook unit tests (free) + optional end-to-end run (with consent)
 └─ Wrap-up                  change history, pointer updates, propose a commit
```

The skill body stays small (~110 lines) and loads deeper guidance only when it's needed — one reference file per component type, at the moment it generates that component. This is **progressive disclosure**: split by *when content is needed*, not by volume. Read more in **[Concepts](docs/wiki/Concepts.md)**.

## The tools it ships with

Four parameterized command-line tools (Python 3.10+, standard library only) that the skill drives — and that you can run yourself:

| Tool | What it does |
|---|---|
| [`validate_harness.py`](.claude/skills/harness-creator/scripts/validate_harness.py) | Deterministic lint of a harness: hooks, permissions, skills, agents, workflows, rules, `CLAUDE.md`, spec drift. Exits non-zero on any error. |
| [`audit_harness.py`](.claude/skills/harness-creator/scripts/audit_harness.py) | Inventories an existing harness, reports spec-vs-disk drift, and suggests a re-entry mode. |
| [`test_hook.py`](.claude/skills/harness-creator/scripts/test_hook.py) | Unit-tests a hook without a live session — reproduces matcher evaluation and explains what each exit code actually means. |
| [`run_e2e.py`](.claude/skills/harness-creator/scripts/run_e2e.py) | Launches a headless `claude -p` session and parses its transcript for grading. |

See **[The Scripts](docs/wiki/Scripts.md)** for full usage.

## Project layout

```
Harness-Creator/
├── .claude-plugin/           # plugin + marketplace manifests
├── .claude/skills/harness-creator/
│   ├── SKILL.md              # the orchestrator
│   ├── references/           # 8 per-component authoring guides (loaded on demand)
│   └── scripts/              # 4 CLIs + a shared helper module
├── docs/
│   ├── plan/                 # design-rationale record (decisions + research)
│   └── wiki/                 # this project's handbook
├── tests/                    # 78 stdlib unittest cases + fixture harnesses
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

## Documentation

The full handbook lives in **[`docs/wiki/`](docs/wiki/Home.md)**:

- **[Concepts](docs/wiki/Concepts.md)** — what a harness is and the mental model behind the skill
- **[Getting Started](docs/wiki/Getting-Started.md)** — install and your first run, step by step
- **[The Interview & Spec](docs/wiki/The-Interview.md)** — how the staged interview works
- **[The Layer-Routing Framework](docs/wiki/Layer-Routing.md)** — the decision at the heart of the skill
- **[Generated Components](docs/wiki/Generated-Components.md)** — the seven layers in detail
- **[The Scripts](docs/wiki/Scripts.md)** — the four command-line tools
- **[Validation & Testing](docs/wiki/Validation.md)** — the two-tier validation model
- **[Re-entry Modes](docs/wiki/Re-entry-Modes.md)** — new / extend / improve / sync
- **[Architecture & Internals](docs/wiki/Architecture.md)** — how the repo is wired and dogfoods itself
- **[FAQ & Troubleshooting](docs/wiki/FAQ.md)**

The **design rationale** — the twelve binding decisions and the research behind every gotcha — is preserved separately in [`docs/plan/`](docs/plan/).

## Status & limitations

v0.1.0 is complete and dogfooded end to end, but a few things are worth knowing going in:

- **End-to-end permission handling is a documented best guess.** `run_e2e.py`'s headless permission flow (`--isolate` + `--dangerously-skip-permissions`) was built from documented behavior but never confirmed in the build environment (a spawned `claude` process couldn't authenticate there). Treat your first real e2e run as the actual verification.
- **The interview can't be auto-tested.** `AskUserQuestion` doesn't exist in headless/subagent contexts, so the interview flow is validated by manual use, not automated e2e.
- **Local-path plugin installs copy gitignored files** into the plugin cache (harmless; the GitHub-source install is clean).

See the **[FAQ](docs/wiki/FAQ.md)** for the full list and workarounds.

## Design philosophy

A few principles shaped every file in this repo, and they're worth stating because they're unusual:

- **Preserve the model's intelligence; add capability, don't cage it.** Define purpose and direction clearly, but don't hard-code the method — a rule with no reasoning behind it snaps on the first case its author didn't foresee.
- **Principle over rule.** Explain *why* a choice is good so the model can re-derive it. The litmus test: could a capable model reconstruct the rule from the reasoning alone?
- **Don't write what the model already knows.** The tokens worth spending are the **gotchas** — the traps you only learn by being burned once.
- **Progressive disclosure is a trade-off, not a default.** Split a file only when the reader genuinely branches at that seam; over-splitting causes silent routing failures.
- **Enforcement belongs in code, advice belongs in prose.** Anything that must never be violated is a hook or a permission rule, not a hopeful sentence in `CLAUDE.md`.

More in [Concepts](docs/wiki/Concepts.md) and [`docs/plan/`](docs/plan/).

## Contributing

Contributions are welcome — see **[CONTRIBUTING.md](CONTRIBUTING.md)**. The short version: develop via the symlink, run `validate_harness.py` and the test suite before a PR, keep the scripts dependency-free, and verify every Claude Code mechanic against a primary source before you write it down.

## License

[MIT](LICENSE) © 2026 seongjin

## Acknowledgments

Built on [Claude Code](https://claude.com/claude-code) and its extension surfaces. The gotcha inventory that gives the skill its value was researched against the official Claude Code documentation; the reasoning behind each decision is preserved in [`docs/plan/`](docs/plan/).
