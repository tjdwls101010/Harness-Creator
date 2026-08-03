# Harness Spec — bare-name convention fixture

## Context
Fixture for B9: a spec that refers to its components by bare name.

## Goals
Prove the two scripts agree, and that a bare name is a nudge rather than a
false "isn't mentioned" report.

## Behavior inventory
| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | Does the bare-named thing | skill | bare-named | generated |

## Component specs
- bare-named — referred to without backticks or a repo-relative path.

## Design rationale
The component is genuinely present and genuinely described. Reporting it as
missing would be a false positive on a correct harness.

## Validation
None.

## Change history
- Created as a regression fixture.
