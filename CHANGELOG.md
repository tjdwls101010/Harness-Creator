# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] — 2026-08-04

Doctrine. The skill taught two filters for what earns its tokens and left a hole between them: nothing screened the sentences that *justify* a claim. A generator following both faithfully wrote a one-clause rule under three sentences of argument — and every harness this skill produces inherited that shape. This release closes the hole and then applies it to the skill's own surface.

### Added

- **The filter extended to the why.** `SKILL.md` now screens justification the same way it screens claims, and names the five shapes that go: restating what you just said, arguing for it, spelling out a consequence the reader computes anyway, giving the negative case equal weight when the positive implies it, and narrating what the next paragraph will do. Named, because a model cannot recognize "cut the persuasion" in its own prose without them.
- **The parameter space as a teaching surface, and its link to compression.** An argument that takes three named values teaches the three cases by existing; prose moved into a signature is not shortened, it is relocated to a surface re-read for free.
- **References need not be prose.** A failing test, a schema, a rubric, or a function in another codebase pins a target more precisely than a paragraph describing it — and the runnable ones fail loudly when the target moves, where a paragraph goes quietly stale.
- **A check's failure message is an interface too**, read at exactly the moment it matters and free otherwise.
- **`hook_event.py`** — look up one hook event's schema (`--event PreToolUse`, 432 words) instead of reading all thirty (3,777). Its `--event` choices are generated from the file, so the signature doubles as the authoritative event list; several of these events postdate common training data, and a model that cannot see them enumerated refuses to author one as nonexistent.

### Fixed

- **`validate_harness.py` no longer fails correct harnesses on a valid `model:`.** It enumerated model ids, so the documented alias `fable` and the id `claude-opus-5` both drew "unrecognized" while `claude-opus-4-8` passed. It now checks shape — a documented alias, or any `claude-` prefixed id — so it cannot go wrong on its own as models ship.
- **`Setup` hook triggers were documented wrong.** The event router listed `--init-only`/`--init`/`--maintenance` as three equivalent flags; the latter two do nothing without `-p`. A generator reading only that file — the one it is told to read first, on every hook task — would wire a `Setup` hook that never fires.
- **`SessionEnd` was ordered before `Elicitation`** in the router while the schema reference called its own list authoritative. The docs agree with the schema reference.
- **Workflow permission rules now carry their reason.** The skill told the generator to write matching `permissions.allow` entries and never to record why, so they read as ordinary convenience allowances on disk — and the next person tightening permissions deletes them, leaving a workflow that stalls mid-run on a prompt nobody is watching.

### Changed

- **Three lint findings gained a consequence clause**, on the theory that a check's message is read exactly when it matters: the 500-line skill guideline now says why 500, a malformed `paths:` glob says the rule will never fire, and a missing spec says drift detection reports nothing in either direction.
- **Three others deliberately did not.** The docs do not say what happens when an `@import` target is missing, or when subagent frontmatter fails to parse, or when a `model:` value is simply a typo. Writing a plausible consequence would have put an invented mechanic in a linter whose entire value is that its gotchas are real; a test now asserts those messages stay bare.
- **The skill's own prose was compressed against the new filter.** Total words 30,712 → 30,072 (−2.1%); words trapped in paragraphs of 110 or more, 9,476 → 7,861 (−17.0%). The gap between those two numbers is the change: these files did not get shorter, they stopped arguing.
- **The always-loaded budget rose from 2,500 to 2,650 words**, deliberately, rather than cutting the new doctrine to fit. 2,500 was a target set while *removing* an unconditional file load; the mechanic is the 5,000-token compaction ceiling, which did not move and still sits over a thousand words away. This project also teaches that a number stripped of its reason is a rail wearing a digit, so holding one after its justification changed would have been the skill failing its own test.


### Known limitations

- **The claim that this release's doctrine reaches generated harnesses is not end-to-end verified.** The doctrine is present in `SKILL.md` and the skill's own prose was compressed against it, both checked mechanically. Whether a *generated* harness comes out shorter-paragraphed with its reasons attached in a clause can only be answered by running the interview to completion, and `AskUserQuestion` does not exist in headless or subagent contexts, so no automated test can do it. The runbook and a prepared target repo ship in `docs/plan/v3/`; the run itself is outstanding.
- Carried forward from 0.2.0: the interview cannot be end-to-end tested for the same reason, and installing the plugin from a local directory path copies gitignored files into the plugin cache (harmless; GitHub-source installs are unaffected).

## [0.2.0] — 2026-08-03

Correctness and context. Twelve defects are fixed — including one that made a correct harness fail the skill's own delivery gate — and the context a session pays for before its first prompt is cut in half. Every product mechanic asserted by the skill was re-verified against live documentation, because the previous release shipped one that was wrong.

### Breaking

- **`audit_harness.py --json`: `inventory.claude_md` is now an array, not an object.** A project CLAUDE.md can live at `./CLAUDE.md` *or* `./.claude/CLAUDE.md`, and `./CLAUDE.local.md` loads alongside either, so a single slot could not represent reality. If you read `inventory.claude_md.lines`, read `inventory.claude_md[0].lines` — or iterate, which is the point of the change. An absent CLAUDE.md is now `[]` rather than `null`.

### Fixed

- **`@import` detection no longer rejects correct harnesses.** `maintainer: ops@acme.com` was read as an import of `acme.com` and `react@18.2.0` as an import of `18.2.0`, each raising an error and a non-zero exit — so a CLAUDE.md that named a maintainer or pinned a version could never satisfy `validate_harness.py`. Import parsing now skips fenced blocks and code spans, requires a path boundary, and supports the documented extensionless `@README` form. Relative targets resolve against the importing file rather than the repo root, and `@~/…` imports are recognized as external rather than reported missing.
- **A project using `.claude/CLAUDE.md` is no longer reported as having no harness.** Both scripts hardcoded `./CLAUDE.md`, which fed the mode suggestion and classified an established harness as `new`.
- **Rules and agents are discovered recursively.** A nested `.claude/rules/frontend/style.md` without `paths:` loads at launch but was invisible to the linter, the inventory, and the drift check.
- **Spec drift is detected in both directions.** The audit only reported components on disk that the spec omitted; it now also reports spec rows whose `status` claims a file that isn't there, and `in_spec_not_on_disk` is present in `--json` whether or not a spec exists.
- **The workflow syntax check accepts top-level `return`**, which the workflow runtime supports and which the skill's own examples use — it was reported as a syntax error.
- **`SessionEnd`'s 1.5-second timeout is documented correctly** as a budget shared across all `SessionEnd` hooks, not a per-hook default; two reference files also disagreed about which event had the shortest timeout.
- Wrap-up now validates *after* the edits it is meant to check, rather than before them.
- Dead-link checking covers a skill's pointers written as prose, markdown links, or `${CLAUDE_SKILL_DIR}` invocations — previously only backtick-wrapped forms in one file, one pointer out of thirty-two.
- Three dangling cross-references and an unclosed code fence.

### Added

- **An always-loaded budget report**, printed on every `validate_harness.py` run: CLAUDE.md plus expanded `@imports` plus every rule without `paths:`, with an explicit list of the surfaces it cannot count (user scope, ancestor directories, auto memory, managed policy).
- **Three lint warnings**, each with a fixture proving it stays quiet on correct input: generic advice anchored to whole sentences, a deny rule that swallows an allow rule, and a catch-all `paths:` glob.
- **`references/re-entry.md`** — the extend/improve/sync modes and the full drift-resolution procedure, loaded only when re-entering an existing harness.
- **Auto memory and the personal-vs-team scope axis.** The routing framework now asks who needs a fact and who writes it, with `CLAUDE.local.md` as the destination for per-developer facts; auto memory enters the budget model but is explicitly never a routing destination, being nondeterministic and disableable.
- **Mechanics whose absence leaves a generated harness silently inert**: what workspace trust gates beyond allow rules, why `Edit(.claude/**)` cannot pre-approve a protected-path write, that `defaultMode: "auto"` is ignored in project settings, that `Write(path)` permission rules are never consulted, and that enabling a subagent's `memory` re-enables `Read`/`Write`/`Edit`.
- **A compaction survival matrix** — root CLAUDE.md and unscoped rules are re-injected, subdirectory CLAUDE.md and `paths:`-scoped rules are not — which qualifies the monorepo guidance in the same file.
- `declined` and `retired` spec statuses, so a harness records what was deliberately not built.
- This repository now carries its own `.claude/harness-spec.md`.

### Changed

- **The always-loaded surface is 4,833 → 2,411 words.** `SKILL.md` instructed an unconditional load of `interview.md`, so the split between them bought nothing; Phase 0 now branches by mode and the sync path never opens the interview file.
- Principles are stated once rather than elaborated, and examples no longer carry domain narrative that pulled generated components toward the example's subject matter.

### Known limitations

- Headless authentication propagated correctly during this release's verification, but `run_e2e.py`'s permission handling remains a documented best guess rather than a broad confirmation.
- The interview still cannot be end-to-end tested; `AskUserQuestion` does not exist in headless or subagent contexts.
- A generated harness does not yet mention that workflow agents run in `acceptEdits` mode and inherit the session allowlist, though the reference prose covers it.

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

[Unreleased]: https://github.com/tjdwls101010/Harness-Creator/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/tjdwls101010/Harness-Creator/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/tjdwls101010/Harness-Creator/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/tjdwls101010/Harness-Creator/releases/tag/v0.1.0
