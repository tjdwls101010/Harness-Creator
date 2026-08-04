# harness-creator

This repo builds `harness-creator`, a meta-skill that designs, generates, and validates Claude Code harnesses (CLAUDE.md, rules, skills, hooks, permissions, agents, workflows) for other projects through a structured interview.

## Where things live

- The skill itself: [.claude/skills/harness-creator/](.claude/skills/harness-creator/) — `SKILL.md` is the orchestrator, `references/` holds per-component authoring guides, `scripts/` holds the Python CLIs it calls.
- The binding implementation spec: [docs/plan/](docs/plan/), one directory per generation with the newest last — start at the highest-numbered one's `00-overview.md`, which carries that generation's decision log and says which earlier decisions it revises. Earlier generations stay as written; they are the citation record, not a live spec. If you change a decision, edit the newest generation's plan and record why.
- Self-test fixtures for the scripts: `tests/fixtures/` at the repo root, not inside the skill — anything under the skill directory ships to plugin users, so dev-only fixtures stay outside it.
- Local reference snapshots the plan was researched against: `.tmp/docs_claude/` and `.tmp/skill-creator/` — gitignored, not part of this repo's own history.

## Working on this repo

- This repo is dogfooding its own output shape: `.claude/skills/harness-creator/` is simultaneously (a) a project skill for this repo and (b) the plugin's skill component (`.claude-plugin/plugin.json`'s `skills` field points here). Don't duplicate the skill elsewhere.
- Daily development loop is the symlink, not the plugin install: `~/.claude/skills/harness-creator` → this repo's skill directory. Edits are reflected immediately in a fresh session. Only install the plugin via the local marketplace when smoke-testing the distribution path itself, and uninstall it afterward — running both at once double-registers the skill under two different names (bare `harness-creator` vs. `harness-creator:harness-creator`).
- No mid-sentence hard line-wraps in any markdown written here (SKILL.md, references, this file, generated harness output). Line breaks only at sentence/list/paragraph boundaries — hard wraps break Edit-tool string matching and pollute diffs, and renderers soft-wrap anyway.
- Every claim the skill makes about Claude Code mechanics (hook exit codes, matcher syntax, CLAUDE.md loading semantics, etc.) must be checked against `.tmp/docs_claude/` or `docs/plan/research/` before being written into a reference file — this skill's entire value is gotcha density, and a wrong gotcha is worse than no gotcha.
