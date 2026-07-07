# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-07-07

First public release. harness-creator is usable end to end: it audits, interviews, generates, validates, and maintains a complete Claude Code harness for a target project.

### Added

- **The `harness-creator` skill** (`SKILL.md`) — the orchestrator that runs the audit → interview → generate → validate → wrap-up loop, with the layer-routing framework inline.
- **Eight reference guides** (`references/`) loaded on demand while generating each component type: `claude-md-and-rules.md`, `skills.md`, `hooks.md`, `hooks-events.md` (all 30 hook events), `agents.md`, `workflows.md`, `interview.md`, `e2e-testing.md`.
- **Four command-line tools** (`scripts/`, Python 3.10+ standard library only):
  - `validate_harness.py` — deterministic lint for a generated harness (settings/hooks, permissions, skills, agents, workflows, rules, CLAUDE.md, spec drift).
  - `audit_harness.py` — Phase 0 inventory, spec-vs-disk drift detection, and a new/extend/improve/sync mode suggestion.
  - `test_hook.py` — unit-tests a hook without a live session, reproducing matcher evaluation and explaining each exit code's meaning.
  - `run_e2e.py` — launches a headless `claude -p` session and parses its transcript for grading.
- **Re-entrancy**: four modes (new / extend / improve / sync) branched from an audit of the existing `.claude/` setup.
- **A persisted spec** (`.claude/harness-spec.md`) as the single source of truth for what a harness contains and why.
- **Two-tier validation**: a free, always-run deterministic lint, plus a consent-gated end-to-end pass over real headless sessions.
- **Distribution**: installable as a Claude Code plugin (`claude plugin marketplace add tjdwls101010/Harness-Creator`) or via a symlink for local development.
- **78 unit tests** (`tests/`, standard-library `unittest`) against fixture harnesses.
- **Documentation**: this README, a `docs/wiki/` handbook, and the design-rationale record in `docs/plan/`.

### Known limitations

- `run_e2e.py`'s headless permission handling (`--isolate` + `--dangerously-skip-permissions`) is built from documented behavior but was not empirically confirmed in the build environment — treat the first real end-to-end run as the actual verification.
- The interview cannot be end-to-end tested (`AskUserQuestion` is unavailable in headless and subagent contexts); it is validated by manual dogfooding.
- Installing the plugin from a **local directory path** (rather than the GitHub source) copies gitignored files into the plugin cache — harmless, and it does not affect GitHub-source installs.

[0.1.0]: https://github.com/tjdwls101010/Harness-Creator/releases/tag/v0.1.0
