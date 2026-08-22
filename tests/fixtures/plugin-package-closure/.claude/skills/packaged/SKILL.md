---
name: packaged
description: >
  Fixture skill for the package-closure check. Use when exercising
  validate_harness.py against a plugin-packaged skill.
---

# Packaged

Target-project paths — these name files in the repo this skill is *run against*,
which is what it exists to build, so none of them are pointers into its own
package: `.claude/settings.json`, `.claude/rules/*.md`, `CLAUDE.md`, a monorepo's
`packages/api/CLAUDE.md`, another tool's `.github/copilot-instructions.md`, a
vendored `node_modules/some-pkg/README.md`, generated output in `dist/index.md`,
and wherever the reader keeps `docs/notes.md`. None of those resolve here, which
is exactly why they are talking about somewhere else.

Real pointers, which resolve inside the package: references/real.md and
scripts/tool.py.

Leaks — both resolve in this repo and travel nowhere: the rationale is in
docs/design/notes.md and the decision log is in notes/internal-decisions.md.
