# Harness Spec — harness-creator

This repo is its own first user. The spec below tracks the harness that ships from here — the `harness-creator` skill and its bundled references and scripts — using the same template the skill generates for any other project.

## Context

Python 3.10+ (stdlib only, no third-party dependencies) plus authored markdown. The deliverable is a Claude Code skill distributed as a plugin, so everything under `.claude/skills/harness-creator/` ships to users and everything outside it does not. Tests are plain `unittest` files run directly (`for f in tests/test_*.py; do python3 "$f"; done`); there is no CI. Single maintainer.

The binding design record is `docs/plan/` (v1, D1-D12) as revised by `docs/plan/v2/` (D13-D24) and by the implementation session's D25-D28 in `docs/plan/v2/00-overview.md`.

## Goals

- Ship a meta-skill that designs, generates, and validates a complete harness for another project through a structured interview.
- Hold the always-loaded surface — what enters context on every invocation before the first prompt — under 2,650 words, because past roughly 5,000 tokens (~3,750 words) content is dropped silently at compaction rather than degrading. The 5,000-token ceiling is the product fact; 2,650 is the self-imposed margin, raised from v2's 2,500 when v3 added the compression doctrine (see Design rationale).
- Never assert a product mechanic the live docs don't support. A wrong gotcha is worse than no gotcha, and this skill's entire value is gotcha density.
- Never let the skill claim an enforcement that doesn't exist. Hard line 1 forbids it, and the v2 audit found five violations of it.

## Behavior inventory

| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | Orchestrate the audit → interview → generate → validate loop | skill | `.claude/skills/harness-creator/SKILL.md` | validated |
| B2 | Author CLAUDE.md and rules, incl. scope axis and auto memory | skill | `.claude/skills/harness-creator/references/claude-md-and-rules.md` | validated |
| B3 | Author skills: triggering, near-misses, listing budget | skill | `.claude/skills/harness-creator/references/skills.md` | validated |
| B4 | Author hooks, permissions, protected paths, workspace trust | skill | `.claude/skills/harness-creator/references/hooks.md` | validated |
| B5 | Per-event hook interface reference | skill | `.claude/skills/harness-creator/references/hooks-events.md` | validated |
| B6 | Author subagents: tools, memory, what skips CLAUDE.md | skill | `.claude/skills/harness-creator/references/agents.md` | validated |
| B7 | Author dynamic workflows, thin-script doctrine | skill | `.claude/skills/harness-creator/references/workflows.md` | validated |
| B8 | Run the interview: five stages, gates, spec template | skill | `.claude/skills/harness-creator/references/interview.md` | validated |
| B9 | Re-entry: extend, improve, and the full sync procedure | skill | — | retired |
| B10 | Second-tier e2e validation and feedback routing | skill | `.claude/skills/harness-creator/references/e2e-testing.md` | validated |
| B11 | Inventory an existing harness and detect spec-vs-disk drift | skill | `.claude/skills/harness-creator/scripts/audit_harness.py` | validated |
| B12 | Deterministic lint + always-loaded budget report | skill | `.claude/skills/harness-creator/scripts/validate_harness.py` | validated |
| B13 | Exercise a generated hook before it is called delivered | skill | `.claude/skills/harness-creator/scripts/test_hook.py` | validated |
| B14 | Launch a headless session for an e2e scenario | skill | `.claude/skills/harness-creator/scripts/run_e2e.py` | validated |
| B15 | Shared discovery, frontmatter parsing, import parsing | skill | `.claude/skills/harness-creator/scripts/harness_common.py` | validated |
| B19 | Look up one hook event's schema instead of all thirty | skill | `.claude/skills/harness-creator/scripts/hook_event.py` | validated |
| B16 | Repo conventions for working on this codebase | CLAUDE.md | `CLAUDE.md` | validated |
| B17 | A pre-commit hook enforcing the no-hard-wrap rule | hook | — | declined |
| B18 | A rule scoped to `docs/plan/**` | rule | — | declined |

## Component specs

Each reference file is loaded only when the matching component type is being generated; `SKILL.md` is the sole always-loaded surface, and `interview.md` loads at Phase 1 rather than during Phase 0's audit. That gating is what keeps the always-loaded surface at one file; the numbers behind it are in Change history.

The five CLIs are plain-argument, stdlib-only, and invoked as `${CLAUDE_SKILL_DIR}/scripts/<name>.py` so they work from a plugin cache as well as a checkout.

## Design rationale

**The always-loaded budget is 2,650 words, and the rule is: audit the draft before touching the budget.** v3 raised it from 2,500 rather than cut half of four new pieces of doctrine to fit — measured, those paragraphs yielded about 51 words to whole-clause deletion, and paraphrase-shortening was rejected outright because that is where meaning dilutes. The number was never the mechanic (that is the 5,000-token compaction ceiling, still about 1,100 words away), and holding one after its justification changed is the rail-wearing-a-digit failure this skill warns about. v5 then added the boundary's second direction and did *not* need another raise: the draft measured 2,694, an audit against this skill's own list of shapes to cut found three of them in it — a mirror clause the previous sentence implied, a sentence defending the claim, and a development-history anecdote, which is the very thing v5 forbids shipping — and it landed at 2,642. The first draft of new doctrine reliably contains the shapes the doctrine names. v3's density metric moved the right way too: words trapped in paragraphs of 110 or more went 788 → 580.

Doctrine lives in `SKILL.md` rather than `references/skills.md` because a pass that generates only CLAUDE.md or only hooks never opens that file, and because auto-compaction re-attaches the skill body while a reference read is summarized away.

Worth naming for whoever revises this next: tabulating a short passage *costs* words, because table pipes and the separator row count — `SKILL.md`'s four-question paragraph went 198 → 203 as a table. Bullets discretize just as well and run about five words per item cheaper.

**hooks-events.md stays markdown, with a query script in front of it.** The access pattern is lookup — one event of thirty, about 8% of the file — and markdown's unit of access is the whole file. `hook_event.py --event <Event>` turns 3,777 words into roughly 200-430.

A binary store (SQLite) was considered and declined — not for the usual objections, which are weak here (textconv gives real diffs, edits are rare, nobody opens it by hand), but for auditing: the operation that matters is re-checking against live Claude Code docs, which is two documents read side by side, and the v3 audit that caught two factually wrong router rows worked exactly that way. The direction is asymmetric too — markdown converts to a database with one script, a database with history does not convert back.

The one thing a binary store buys that a script cannot is enforcement: it makes reading the whole file unavailable. Unmeasured, so L5 observes it — if a generated hook pass reads `hooks-events.md` whole despite the script existing, the enforcement argument wins and this should be revisited. v5 removed one reason it might: the file's own header said "Load this file", contradicting the router that sends the reader to `hook_event.py`.

**The interface boundary splits on ownership, not on forbidding assertions about behavior.** v5's first draft forbade prose from asserting how a tool currently behaves; a blind re-derivability test — the rule alone, five cases, no context — showed that left "run this only with consent, it spends real tokens" writable nowhere, since the other half forbids it in `--help`. Ownership leaves no such gap.

**Package closure warns rather than fails**, because a path that resolves here and not in the package is a leak *or* a correct sentence about the reader's project that collides with a path here — an adversarial pass built three correct plugins that collide, on `docs/architecture.md`, `.github/copilot-instructions.md` and `packages/web/CONTRIBUTING.md`. Nothing distinguishes them, so this repo runs `--strict` to enforce closure on itself. Keying it on `.gitignore` was tried and reverted: a plugin repo's `.gitignore` describes its own build products, the sentences describe the reader's.

**The plan's literal leak patterns were rejected as shipped rules.** `docs/plan/`, `.tmp/` and `\bD[0-9]{1,2}\b` are facts about this repo; a user's skill pointing at its own `docs/plan/` is correct. They live in `tests/test_skill_surface.py` as regression pins instead, alongside the other repo-specific pins.

**No CLAUDE.md pointer at this file.** The pointer policy forbids an inventory because a hand-maintained prose list drifts — and this file's Behavior inventory is one, with its own drift check. The pointer moved the drift one hop and put a working session on a maintenance document. A maintainer's way in is an HTML comment, which is stripped before injection.

**Reference gotchas are kept by what the builder does with them, not by whether they are true.** The test: does this paragraph change what the builder writes into a generated harness, or what it does during a pass? A paragraph describing how Claude Code behaves for the *end user* of a finished harness, with no consequent instruction, is background. Applying it removed 805 words (2.8%) across six files — table introductions, three "notice that..." restatements of an example, a gotcha that duplicated the frontmatter row above it, and mechanism numbers no decision compares against.

An independent classification pass proposed 2,153 words; roughly two thirds were rejected on judgment. Fourteen were `hooks-events.md`, which is `hook_event.py`'s data source and costs nothing until queried. The rest were one recurring error worth naming for the next pass: **splitting a claim from the reason that makes it re-derivable.** "Trust gates what a repo grants" was proposed for cutting because the instruction it justifies sits in the next line — but that line without this one says *say what*. Cut the sentence that argues; keep the sentence the instruction is derived from.

**B17 declined.** The no-hard-wrap rule is real and load-bearing (hard wraps break Edit's exact-string matching), but it is stated in `CLAUDE.md` and `SKILL.md`, and a violation is cosmetic and trivially reversible — it fails this skill's own hook-eligibility test. Revisit only if it recurs.

**B18 declined.** A `paths:`-scoped rule for `docs/plan/**` would load only when those files are read, but the one thing worth saying there is already one line in `CLAUDE.md`, and splitting it out buys a routing decision with no saved reading.

**No `.claude/settings.json`.** This repo ships no project permissions or hooks. Project allow rules are gated on workspace trust, so committing them here would mostly generate confusion on a fresh clone for no benefit at this size.

**Dev-only files stay outside the skill directory.** `tests/` and `docs/` are at the repo root because everything under `.claude/skills/harness-creator/` is distributed to plugin users.

## Validation

Mechanical, run on every change:

```bash
python3 -m unittest discover -s tests -q
python3 .claude/skills/harness-creator/scripts/validate_harness.py --path . --strict
python3 .claude/skills/harness-creator/scripts/audit_harness.py --path .
```

The test suite doubles as the regression record for the v2 audit's bug list: `tests/test_skill_surface.py` pins the always-loaded budget, the guardrail facts that must survive future trimming, and the prose bugs (B2/B5/B7/B8/B10 in the v2 numbering); `tests/test_validate_harness.py` and `tests/test_audit_harness.py` cover the script bugs.

### Behavioural verification of the interface doctrine (2026-08-22)

`validate_harness.py` cannot judge whether prose copied an interface, so v5's central claim was checked by generation behaviour instead: three headless sessions (`run_e2e.py --isolate`, `claude` 2.1.239), same prompt, against a small Node project — "build one skill for our fixed-width invoice export, with a bundled script that validates a file against it." 33/15/33 turns, $5.30 total.

**PASS, 3/3.** Every run triggered the skill, produced a harness that lints 0 errors / 0 warnings, and produced a script whose `--help` carries every argument (so the D43 check holds — the interface really does hold the information). No run wrote a signature table, and every run deferred the flag set to `--help` explicitly. Run 3 stated the reason back: *"`--help` for the flags and `--print-schema` for the column-entry vocabulary; both are emitted by the script, so neither can drift from what it accepts."*

What they did do, and it is the doctrine working rather than failing: each named two or three individual flags, always with a *when* attached — run 2's *"`--help` documents the rest; the flags worth knowing exist are `--columns-json` (validate against a proposed or older table) and `--line-ending` (pin LF or CRLF when the finance side requires one)"* is the ownership split applied exactly. The one wobble to watch is run 1, which restated the script's exit-code contract and one flag's output shape inline — tool-owned facts that had drifted back into prose. If that recurs, suspect the canonical example before tightening the doctrine.

**This run also closes v1's risk R3.** `run_e2e.py`'s headless permission handling had never been watched to succeed end to end across four generations, and `SKILL.md` still said so. `--isolate` plus skip-permissions worked on the first attempt, three times, with no auth failure and no permission stall.

Interview behavior itself cannot be validated this way — `AskUserQuestion` does not exist in headless or subagent contexts — so the interview is verified by dogfooding against a real project.

## Change history

Older passes are folded to one line each; the current generation stays in full. See `references/interview.md` for the rule.

- **2026-08-03 — improve (v2).** Context-engineering revision across eight workstreams: fixed twelve defects, added auto memory and the personal/team scope axis, six silent-failure mechanics, and the always-loaded budget report, and gated `interview.md` behind a real mode branch — always-loaded went 4,833 → 2,411 words. Created this spec.
- **2026-08-04 — improve (v3).** Extended the "don't write what the model knows" filter to cover justification, naming the five shapes that go; added the parameter space as a teaching surface, references-need-not-be-prose, and a check's failure message as an interface; added `hook_event.py`. Raised the word budget 2,500 → 2,650. Released as `v0.3.0`.
- **2026-08-19 — improve (v4).** Added the bundled-script CLI self-description check: `validate_harness.py` now parses `.claude/skills/*/scripts/**/*.py` with `ast` and errors on an `add_argument` or `add_parser` without `help=`. The interface doctrine had promised a benefit that only arrives when `--help` is complete, and nothing taught or checked that.
- **2026-08-22 — improve (v5).** The interface doctrine ran in one direction only — it constrained what may go into a signature and said nothing about prose copying one back out — so writing both broke no rule, and this skill was doing it.
  - **Doctrine.** The boundary now splits on ownership (the tool owns what is valid, what it does, what it prints; the project owns when to reach for it, what it costs, why it was chosen) with a falsifiability test attached: if editing the tool would make the sentence false, the sentence belongs in the tool. Added "a pointer inherits its target's reader."
  - **Applied to itself.** Deleted `SKILL.md`'s `Signature` column (two of five rows were already wrong, and one listed a flag belonging to the `claude` CLI); corrected Hard line 1's claim about what the pointer check covers; removed a Wrap-up line enumerating findings the linter already prints. 2,642 words, under budget, no raise.
  - **Four false statements about code, one a safety bug.** Prose called isolation `run_e2e.py`'s default when `--isolate` is opt-in — a reader trusting it would point a headless agent session at the user's real project. The canonical fixture described a raw-SQL hook that does not exist; `agents.md` claimed `tools:` enforces read-only while its own example keeps `Bash`; the must-never recipe demonstrated an `Edit|Write` matcher its own gotcha list calls incomplete.
  - **Thirteen pointers out of the package**, worst of them two `.tmp/` paths — gitignored, absent from every clone, one of them in a module docstring that `--help` prints. Added a package-closure check for plugin-shipped skills, and fixed two real holes in the pointer check (nested paths were only checked one segment deep; a sentence-ending period was read as part of the filename, failing correct harnesses).
  - **Removed the CLAUDE.md → this-file pointer**, on all three surfaces that carried it, including a linter message that recommended it.
  - **Gave this file an eviction rule** for the two sections that grow every pass, and applied it: inherited Design rationale went 709 → ~465 words with no claim lost, and v2-v4 above are folded to a line each.
  - **Cut 805 words of reference prose** that described Claude Code's runtime behavior without changing what a builder writes or does.
  - **Behavioural verification, 3/3** — the interface claim confirmed by generation rather than by lint, and the same runs closed v1's risk R3 after four generations.
  - Verified by two independent audits (`gpt-5.6-sol`, blank-slate and adversarial), which found the unsatisfiable-pair defect in the first doctrine draft and three correct plugins the closure check would have failed. Both changed the design.
