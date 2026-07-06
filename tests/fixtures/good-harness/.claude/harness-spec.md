# Harness Spec — example project

## Context
Node/TypeScript API, small team.

## Goals
Protect the database migration path and speed up routine review.

## Behavior inventory
| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | Never edit `.env` | hook+permission | `.claude/hooks/protect-files.sh` | generated |
| B2 | Security review on request | agent | `.claude/agents/security-reviewer.md` | generated |

## Component specs
- `.claude/skills/example-skill/` — example domain skill, triggers on "example task".
- `.claude/agents/security-reviewer.md` — read-only diff reviewer.
- `.claude/rules/db-migrations.md` — path-scoped migration rule.
- `.claude/workflows/example-workflow.js` — thin fan-out/verify example.

## Design rationale
Hooks pair with deny rules for hard guarantees (see references/hooks.md).

## Validation
Not yet run.

## Change history
- 2026-07-06: initial generation.
