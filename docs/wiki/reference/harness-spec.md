# Harness spec reference

This reference describes `.claude/harness-spec.md`, the persisted decision record generated and maintained by Harness Creator.

## 1. Purpose

Files reveal what exists. The spec also records why it exists, what was declined, what evidence was approved, and how the harness changed over time. Audit, re-entry, drift detection, and maintenance depend on that record.

## 2. Required sections

| Section | Content |
|---|---|
| Context | Project stack, commands, layout, team facts, and interview calibration |
| Goals | Desired outcomes, preferably preserving the user's precise wording |
| Behavior inventory | ID, need, layer, component path, and status |
| Component specs | Trigger, scope, inputs, outputs, authority, and failure policy per component |
| Design rationale | Why the selected layer fits and why alternatives were rejected |
| Validation | Approved scenarios, latest evidence, and outcome |
| Change history | Date, mode, and summary for every Harness Creator pass |

## 3. Behavior inventory

A stable row shape is:

```markdown
| id | behavior/knowledge/constraint | layer | component | status |
|---|---|---|---|---|
| B1 | Know the test command in every session | CLAUDE.md | `CLAUDE.md` | validated |
```

IDs remain stable across later runs. Do not renumber existing behaviors to make the table visually contiguous.

## 4. Status transitions

The common forward path is:

```text
proposed → approved → generated → validated
```

`declined` records a considered need that should not be generated. `retired` records a component deliberately removed later. Keeping these rows prevents the same decision from being rediscovered and debated on every run.

## 5. Component specifications

Record enough information to regenerate or inspect a component without inventing missing intent. Examples:

- skill: intended triggers, near-misses, body purpose, references, scripts, output contract;
- hook: event, matcher, handler type, input fields, allow/block behavior, output channel, failure policy;
- agent: role, tools, model policy, input/output contract, isolation reason;
- workflow: phases, dependencies, shared artifacts, permissions, stop conditions;
- rule: paths, advisory constraint, and reason it belongs outside root context.

## 6. Validation evidence

Separate structural checks, hook tests, and behavioral E2E. Record the command or scenario, date, outcome, and evidence location. Do not label structural validation as behavioral proof.

## 7. Drift semantics

The audit detects component existence disagreement in both directions. It does not compare the semantic contents of an existing file with the spec. A clean drift report therefore means paths and statuses align, not that every component still behaves as described.

## 8. Change history

Append one entry per run with the date, mode (`new`, `extend`, `improve`, or `sync`), and a concise description. Identify external edits honestly; do not describe a spec correction as though Harness Creator restored a file when it did not.

## 9. Next

Read [Interview and re-entry](interview-and-reentry.md) for the lifecycle or [Synchronize drift](../how-to/sync-drift.md) for the reconciliation procedure. Return to the [documentation index](../README.md).
