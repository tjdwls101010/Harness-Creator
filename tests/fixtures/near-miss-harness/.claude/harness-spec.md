# Harness Spec — near-miss harness

## Context
False-positive fixture. Every shape here looks like one of the four checks v6
added and is in fact correct, so a finding raised against this fixture is a
false positive by construction.

## Component specs
- `.claude/settings.json` — a project `defaultMode` that is allowed, a path rule
  on a tool that does consult one, a bare tool-level deny, and a Bash prefix
  rule that already carries its word boundary.
- `.claude/skills/deploy-guard/` — a skill whose frontmatter `hooks:` block is
  correct, including a command path resolved against the skill's own directory
  and a `once: true` handler, which is honored in this position and nowhere else.
  It also carries a quoted event key and a `${CLAUDE_PROJECT_DIR}` command: the
  first is valid YAML the narrow reader has to accept rather than decline, and
  the second is the documented way for a skill to reach a project-level script.
