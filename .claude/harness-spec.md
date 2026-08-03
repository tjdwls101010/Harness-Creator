# Harness Spec — harness-creator

This repo is its own first user. The spec below tracks the harness that ships from here — the `harness-creator` skill and its bundled references and scripts — using the same template the skill generates for any other project.

## Context

Python 3.10+ (stdlib only, no third-party dependencies) plus authored markdown. The deliverable is a Claude Code skill distributed as a plugin, so everything under `.claude/skills/harness-creator/` ships to users and everything outside it does not. Tests are plain `unittest` files run directly (`for f in tests/test_*.py; do python3 "$f"; done`); there is no CI. Single maintainer.

The binding design record is `docs/plan/` (v1, D1-D12) as revised by `docs/plan/v2/` (D13-D24) and by the implementation session's D25-D28 in `docs/plan/v2/00-overview.md`.

## Goals

- Ship a meta-skill that designs, generates, and validates a complete harness for another project through a structured interview.
- Hold the always-loaded surface — what enters context on every invocation before the first prompt — under 2,500 words, because past roughly 5,000 tokens content is dropped silently at compaction rather than degrading.
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
| B9 | Re-entry: extend, improve, and the full sync procedure | skill | `.claude/skills/harness-creator/references/re-entry.md` | validated |
| B10 | Second-tier e2e validation and feedback routing | skill | `.claude/skills/harness-creator/references/e2e-testing.md` | validated |
| B11 | Inventory an existing harness and detect spec-vs-disk drift | skill | `.claude/skills/harness-creator/scripts/audit_harness.py` | validated |
| B12 | Deterministic lint + always-loaded budget report | skill | `.claude/skills/harness-creator/scripts/validate_harness.py` | validated |
| B13 | Exercise a generated hook before it is called delivered | skill | `.claude/skills/harness-creator/scripts/test_hook.py` | validated |
| B14 | Launch a headless session for an e2e scenario | skill | `.claude/skills/harness-creator/scripts/run_e2e.py` | validated |
| B15 | Shared discovery, frontmatter parsing, import parsing | skill | `.claude/skills/harness-creator/scripts/harness_common.py` | validated |
| B16 | Repo conventions for working on this codebase | CLAUDE.md | `CLAUDE.md` | validated |
| B17 | A pre-commit hook enforcing the no-hard-wrap rule | hook | — | declined |
| B18 | A rule scoped to `docs/plan/**` | rule | — | declined |

## Component specs

Each reference file is loaded only when the matching component type is being generated; `SKILL.md` is the sole always-loaded surface, and `interview.md` and `re-entry.md` are gated behind the Phase 0 mode branch. That gating is the point of the v2 revision — it took the always-loaded surface from 4,833 words to under 2,500.

The four CLIs are plain-argument, stdlib-only, and invoked as `${CLAUDE_SKILL_DIR}/scripts/<name>.py` so they work from a plugin cache as well as a checkout.

## Design rationale

**B17 declined.** The no-hard-wrap rule is real and load-bearing (hard wraps break Edit's exact-string matching), but it's stated in `CLAUDE.md` and in `SKILL.md`, and a violation is cosmetic and trivially reversible. By this skill's own second hook-eligibility question — what does a violation cost, and is something already catching it — this doesn't clear the bar. Revisit only if it actually recurs.

**B18 declined.** A `paths:`-scoped rule for `docs/plan/**` would load only when those files are read, but the one thing worth saying there ("plan docs are the binding design record; record deviations") is already one line in `CLAUDE.md`, and splitting it out buys a routing decision with no saved reading.

**No `.claude/settings.json`.** This repo ships no project permissions or hooks. Project allow rules are gated on workspace trust, so committing them here would mostly generate confusion on a fresh clone for no benefit at this size.

**Dev-only files stay outside the skill directory.** `tests/` and `docs/` are at the repo root because everything under `.claude/skills/harness-creator/` is distributed to plugin users.

## Validation

Mechanical, run on every change:

```bash
python3 .claude/skills/harness-creator/scripts/validate_harness.py --path . --strict
for f in tests/test_*.py; do python3 "$f"; done
```

The test suite doubles as the regression record for the v2 audit's bug list: `tests/test_skill_surface.py` pins the always-loaded budget, the guardrail facts that must survive future trimming, and the prose bugs (B2/B5/B7/B8/B10 in the v2 numbering); `tests/test_validate_harness.py` and `tests/test_audit_harness.py` cover the script bugs.

Interview behavior itself cannot be validated this way — `AskUserQuestion` does not exist in headless or subagent contexts — so the interview is verified by dogfooding against a real project.

## Change history

- **2026-08-03 — improve.** v2 context-engineering revision, eight workstreams. Fixed twelve defects (a linter that failed correct harnesses on `@import` false positives; a Wrap-up that validated before the edits it checked; a dead-link check covering 1 of 32 pointers; a wrong SessionEnd timeout gotcha; three dangling pointers; an unclosed code fence; a drift direction the audit had declined; a dropped `--json` key; single-location CLAUDE.md discovery; non-recursive rules and agents; a literal `${CLAUDE_SKILL_DIR}` in a workflow prompt; a syntax gate that rejected top-level `return`). Added auto memory and the personal/team scope axis, six silent-failure mechanics, and the always-loaded budget report. Gated `interview.md` behind a real mode branch and moved the sync procedure into a new `re-entry.md`, taking always-loaded from 4,833 to 2,411 words. Created this spec.
