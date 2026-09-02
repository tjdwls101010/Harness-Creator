# Harness Spec — hook and permission shapes

## Context
Fixture: one positive case per shape check.

## Goals
Each of V02, V03, V04, V05 and V15 fires exactly once here.

## Behavior inventory
| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | Stop gate | hook | `.claude/hooks/gate.sh` | generated |
| B2 | MCP logger | hook | `.claude/hooks/log.sh` | generated |

## Component specs
- `.claude/hooks/gate.sh` — Stop gate without a loop guard.
- `.claude/hooks/log.sh` — logger on a matcher that matches nothing.

## Design rationale
Fixture.

## Validation
Fixture.

## Change history
- 2026-09-02: created.
