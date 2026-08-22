---
name: packaged
description: >
  Fixture skill for the package-closure check. Use when exercising
  validate_harness.py against a plugin-packaged skill.
---

# Packaged

Legitimate outside paths — these name files in the *target* project, which is
what this skill exists to build, so none of them are pointers into its own
package: `.claude/settings.json`, `.claude/rules/*.md`, `CLAUDE.md`, a monorepo's
`packages/api/CLAUDE.md`, and another tool's `.github/copilot-instructions.md`.

Real pointers, which resolve inside the package: references/real.md and
scripts/tool.py.

Leaks — both resolve on the author's machine and nowhere else: the rationale is
in docs/design/notes.md and the source snapshot is under .tmp/snapshot/api.md.
