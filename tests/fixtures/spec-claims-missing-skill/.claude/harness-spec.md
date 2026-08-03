# Harness Spec — spec-vs-disk drift fixture

## Context
Fixture for the "in spec but not on disk" drift direction (B6).

## Goals
Exercise every status value against the on-disk set.

## Behavior inventory
| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | A skill that really exists | skill | `.claude/skills/real-skill/` | generated |
| B2 | A skill generation never finished | skill | `.claude/skills/ghost-skill/` | generated |
| B3 | An agent something deleted | agent | `.claude/agents/ghost-agent.md` | validated |
| B4 | Approved but not yet built | skill | `.claude/skills/not-yet/` | approved |
| B5 | Surfaced, not yet approved | hook | `.claude/hooks/maybe.sh` | proposed |

## Component specs
- `.claude/skills/real-skill/` — the only component with a file behind it.

## Design rationale
Rows B4 and B5 must NOT be reported: `proposed` and `approved` are intent, not
artifacts, so a harness mid-interview would otherwise report drift constantly.

## Validation
None.

## Change history
- Created as a regression fixture.
