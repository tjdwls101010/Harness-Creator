# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] — 2026-08-24

Self-application. Four releases built one doctrine each — principle over rail, interface over document, write for the user rather than the developer, density. None of them ever asked whether the skill obeys all four itself. This one asks, across the whole surface at once, and the answer was no in five places. The doctrine was stated four times and the copies had already drifted apart from the code. Prose restated things a tool schema and a check message deliver on every use. Two headings announced sections that had moved. A document contradicted itself about whether its own central claim was verified. And the one thing a harness author most needs to decide — which of the four ways to run work in parallel — was not in the skill at all.

### Added

- **The four-way orchestration choice**, in `references/agents.md`, which now opens on it: subagents, agent view, agent teams, dynamic workflows. The discriminant is the one the docs already use — **who decides what runs next** — and the column this skill adds is what each choice makes the harness *contain*, because three of the four contain nothing. Agent teams had appeared exactly once before this, as an antipattern with no honest opposite; the section gives them one, along with the four costs an interview never volunteers, the largest being that teams do not isolate teammates in worktrees, so partitioned file ownership is a design act the harness owes the user.
- **Four prose-only rules became checks.** Project-scope `permissions.defaultMode: "auto"` (ignored outright, so the harness reads as configured and behaves as if it weren't). Path rules on tools that never consult one — `Write(docs/**)` parses, looks like it protects `docs/`, and protects nothing; an Error rather than a Warning because no valid alternative reading exists. The missing word boundary in `Bash(ls*)`, which turned out to be a message repair rather than a new check. And skill-frontmatter `hooks:` blocks, which had reached no validator at all.
- **A heading-with-no-body check** over every reference file. The defect it catches is invisible by construction: moving a paragraph out is a diff a reviewer sees, and the heading left behind is a diff nobody sees. Container headings are allowed to hand straight to a deeper one — they promise subsections and deliver them; what has no reading is a heading whose next heading is a sibling.

### Changed

- **`interview.md` and `re-entry.md` merged into one file, and `re-entry.md` deleted.** v2's D22 was two steps, and only one of them earned the headline: gating the load produced always-loaded 4,833 → 2,411 words, while splitting the file bought "a re-entry pass doesn't read interview prose" and cost a second copy of the status semantics plus a round trip back into the stages. Rewritten rather than concatenated — 74 claims extracted from the two originals, then a new document written against that list, so a fresh build and a re-entry read as two phases of one lifecycle instead of two documents.
- **The doctrine has one canonical statement again.** `skills.md` restated the rail-vs-principle litmus at greater length than the original and restated progressive disclosure in full; `claude-md-and-rules.md` restated the enforced-vs-advisory question `hooks.md` also asks; `workflows.md` quoted "the one sentence that governs every layer" without citing it. Each keeps its component-specific application and anchors to the canonical phrase.
- **A new filter, sharper than "is this mechanism prose?": does a runtime surface already deliver this on every use?** The surfaces are a tool's own schema, a bundled script's `--help`, and a check's failure message — none of which can drift from what they describe. `AskUserQuestion`'s mechanical limits and the workflow determinism ban went on that basis. Documentation of *silent* behaviour stays, because no surface delivers it.
- Reference prose is net smaller everywhere it was touched: `skills.md` 2,840 → 2,491, `e2e-testing.md` 3,523 → 3,467, `workflows.md` 2,203 → 2,180, `claude-md-and-rules.md` 2,795 → 2,764, `SKILL.md` 2,644 → 2,620.

### Fixed

- **`e2e-testing.md` contradicted itself** about whether headless permission handling was verified — a heading saying "unverified in this build", a paragraph reporting three confirmed runs, and a third paragraph saying "reasoned, not verified. Do not present it to the user as already confirmed." Three positions on one question, left behind when 0.4.0 added the confirmation without updating the prose around it. The boundary is now drawn once: the flag combination is settled, the reader's machine never is, and the date and run count live only in `run_e2e.py`'s docstring.
- **`skills.md` said a skill body over 400 lines earns a second file** while `MAX_SKILL_BODY_LINES` says 500 and `SKILL.md` says 500. Rather than correct the number, the sentence now defers to the check, whose message prints it — writing 500 into prose would have reproduced the exact defect being fixed.
- **Two headings in `agents.md` promised sections whose content had migrated into the frontmatter table below.**
- **A check that fired on a documented pattern.** The first implementation of the skill-hooks check warned whenever a skill hook used `${CLAUDE_PROJECT_DIR}`, which the docs describe as the intended way for a skill to reach a project-level script. Caught by the adversarial review and removed, along with the reference sentence that read as a ban on it.

### Known limitations

- **Sync mode costs about 3.6× more to enter than it did.** Before the merge it read `re-entry.md` alone, 1,094 words; it now reads the merged `interview.md`, 3,924. Nothing offsets this and it is not presented as an improvement — it is an **accepted trade**, taken because the alternative was two copies of the status table that can disagree, which is sync's own correctness problem. Frequency is not part of the argument: there is no invocation telemetry, so "sync is the rarest mode" is not measurable here. The merged file is still conditional, so the always-loaded budget is unaffected.
- **The claim-loss audit behind the merge is a floor, not a proof.** It anchors one string per claim, which cannot see a claim losing part of itself — the adversarial pass found two doing exactly that, and both were restored before release. A future merge should expect the same class of miss.
- **Prose and check messages still co-own the reason and the fix in several places this release did not touch** (`hooks.md`'s permission gotchas, the duplicate-agent-name warning, the `paths:`-less rule warning). The boundary that says prose keeps the decision and the finding carries the consequence was applied to what changed here, not swept across the package.
- Carried forward: the L5 full-interview dogfooding remains unrun, for the fourth release — `AskUserQuestion` does not exist in headless or subagent contexts, so no automated test can exercise the interview. Installing the plugin from a local directory path still copies gitignored files into the plugin cache (harmless; GitHub-source installs are unaffected).

## [0.4.0] — 2026-08-22

Interface. The last release made the skill's own `--help` output trustworthy; this one stops its prose from copying that output back out, and finds what the missing half had already broken. The doctrine ran in one direction — it constrained what may go *into* a signature and said nothing about prose restating one — so writing both broke no rule, and the skill was doing it. Two rows of its own script table were already wrong, one named a flag belonging to a different CLI, and four sentences elsewhere asserted behaviour the code contradicted. One of those four was a safety bug.

### Added

- **The interface boundary runs both ways, split on ownership.** The tool owns what is *valid*, what it does, and what it prints; the project owns when to reach for it, what it costs, and why it was chosen. Neither side restates the other, and a falsifiability test makes it operable on cases nobody enumerated: **if editing the tool would make the sentence false, the sentence belongs in the tool.** An earlier draft forbade prose from "asserting how a tool currently behaves" and was retired after a blind test showed it left "run this only with consent, it spends real tokens" writable nowhere — the other half forbids it in `--help`.
- **A pointer inherits its target's reader**, so it moves who pays rather than whether.
- **The bundled-script CLI self-description check** (unreleased since 2026-08-19): `validate_harness.py` parses `.claude/skills/*/scripts/**/*.py` with `ast` and errors on an `add_argument` or `add_parser` with no `help=`. The interface doctrine promises a benefit that only exists once `--help` is complete, and nothing taught or checked that.
- **A package-closure check for plugin-shipped skills.** A plugin installs as its own directory, so a pointer at a document elsewhere in the repo resolves for its author and nobody else. It warns rather than fails, because the same path can be a correct sentence about the *reader's* project — an adversarial pass built three correct plugins that collide, on `docs/architecture.md`, `.github/copilot-instructions.md` and `packages/web/CONTRIBUTING.md`.
- **Ablation, and the improve question that finds candidates for it.** Every arrow in the feedback-routing table ended in a repair or a promotion, so a harness that is improved often only grows. A stale *line* has no tell — a rule written to fight a model's old default reads exactly like one still fighting the current default, and the model changes while the harness doesn't. One rule at a time, restore it if something breaks, and record that in the spec so the next pass doesn't re-run the experiment. **Never a hook or a permission rule**: those layers exist because their failure is the one you cannot afford to observe.
- **An eviction rule for the two spec sections that grow every pass.** Change history keeps what a re-entering pass can still act on and folds the rest to a line each — except a pass that recorded someone else's edit, the only place the next pass learns this harness has other authors. Design rationale keeps decisions and rejected alternatives, drops the sentences defending them, and rewrites a superseded decision to its outcome rather than stacking the new one beneath it.
- **`--keep-isolated` on `run_e2e.py`**, for scenarios that grade generated files rather than the transcript.

### Verified

- **`run_e2e.py`'s headless permission handling works.** It had never been watched to succeed end to end, across four generations, and the script said so in the `--help` it prints to users. `--isolate` plus skip-permissions completed three scenarios on the first attempt, no auth failure, no permission stall. The caveat that survives is narrower and still true: auth is per-machine, so a machine this has not run on is a fresh question.

Alongside the doctrine work, the discoverability track that had been sitting unreleased:

- A canonical Diátaxis documentation set under `docs/wiki/`, with tutorials, how-to guides, reference, explanation, and compact navigation, plus a research-backed discoverability dossier covering positioning, documentation architecture, visual direction, community distribution, launch sequencing, and directional measurement.
- Repository-owned graphical abstracts, a verified archival copy of the original poster, support and security policies, Contributor Covenant 3.0, structured Issue Forms, and a pull-request template.
- Python 3.10 and 3.14 CI, pull-request internal-link validation, non-blocking pull-request plus weekly/manual external-link validation, and weekly Dependabot updates for GitHub Actions. Every action is pinned to an immutable commit SHA.

### Changed

- **`SKILL.md`'s script table lost its `Signature` column.** Judgment (`Run it when`) stays; the flags were a copy of `--help` that nothing checked, and two of five rows had gone wrong. The table now says to read `--help` on first use.
- **CLAUDE.md no longer points at `.claude/harness-spec.md`.** The rule against enumerating components rests on hand-maintained prose lists drifting — and the spec's Behavior inventory is one, with its own drift check. The pointer moved the drift one hop and put a working session on a maintenance document. A maintainer's way in is an HTML comment, stripped before injection. Fixed in all three places that carried it, including a linter message that recommended it.
- **805 words of reference prose removed** — table introductions, restatements of an example, a gotcha duplicating the frontmatter row three lines above it, and mechanism numbers no decision compares against. The test applied: does this change what the builder writes into a generated harness, or does during a pass?
- The always-loaded surface is **2,642 words**, inside the existing 2,650 budget. The first draft of the new doctrine measured 2,694; auditing it against this project's own list of shapes to cut found three of them in it, including a development-history anecdote — the exact thing this release forbids shipping.
- Rewrote the README around the discovery-to-install path, with the interview-driven positioning, recommended plugin install, secondary skills CLI install, deliberate layer comparison, validation boundaries, and canonical documentation map.
- Consolidated the tracked wiki from 34 files to 16, removing legacy pointer pages and grouping related maintenance, validation, reference, and design material into clearer reader paths.
- Updated contribution guidance for the current test, validation, CI, documentation, support, and security workflows; applied the approved repository metadata and security settings; and submitted Harness Creator to Anthropic's plugin directory for Claude Code, recording the review status and the downstream distribution gate.

### Fixed

- **Prose called isolation `run_e2e.py`'s default when `--isolate` is opt-in.** A reader who trusted it and dropped the flag would point a headless agent session at the user's real project. The `--help` was right the whole time; only the prose was wrong.
- **`test_hook.py` returned 0 whatever the hook did**, while `SKILL.md` used "passes `test_hook.py`" as a delivery gate. A hook exiting 1 — documented in this same package as the mistake that leaves a policy silently doing nothing — cleared it. Exit 2 is still a pass: a blocking hook exits 2 on the path it exists to block.
- **A skill or agent built the way the guides describe could not clear the lint.** Three reference files teach a nested `hooks:` block in frontmatter; the parser gave up on the whole file when it saw one, and the validator reported the component's auto-triggering as dead.
- **A plugin laid out the default way had every skill skipped, silently.** Discovery only knew `.claude/skills/`, while a plugin ships from `./skills` unless its manifest says otherwise — reported as a clean run.
- **`run_e2e.py --isolate` never deleted its project copy.** The variable naming the temp parent was assigned and never used, and a comment claimed the OS collects them; 48 copies and 8.8 GB had accumulated. The test file leaked one per run of its own.
- **Thirteen pointers led out of the shipped package** — decision-log codes nothing in the package defines, plan-document paths, and two `.tmp/` paths that are gitignored and therefore absent from every clone. One sat in a module docstring that `--help` prints to the end user.
- **The canonical fixture described a hook that does not exist**, `agents.md` claimed `tools:` enforces read-only while its own example keeps `Bash`, and the must-never recipe demonstrated an `Edit|Write` matcher that this package's own gotcha list calls incomplete. Generated harnesses are modelled on these.
- **Two holes in the pointer check**: a nested pointer was only verified one path segment deep, and a sentence-ending period was read as part of the filename — the second failing *correct* harnesses.
- **`--model`'s help promised the invoking session's model.** Nothing forwards it; the spawned `claude` applies its own default. Behavioural fidelity is the entire premise of e2e.

### Known limitations

- **The L5 full-interview dogfooding remains unrun**, for the third release. `AskUserQuestion` does not exist in headless or subagent contexts, so no automated test can exercise the interview; the runbook and a prepared target repo ship in `docs/plan/v3/`. This release was not held for it, which is a deliberate call and not an oversight.
- The claim that this release's doctrine reaches generated harnesses is checked by generation behaviour, not by the interview that produces it — three headless runs, all three deferring their bundled script's flag set to `--help` and none writing a signature table. What that does *not* cover is whether the interview elicits the right spec in the first place, which is the same gap as the item above.
- Carried forward: installing the plugin from a local directory path copies gitignored files into the plugin cache (harmless; GitHub-source installs are unaffected).

## [Unreleased]

Nothing yet.

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
