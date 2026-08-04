# Maintain an existing harness

Use this guide to add a new behavior or reconcile drift without redesigning parts of the harness that already work.

## 1. Audit the current state

Commit or stash unrelated changes, then run the audit:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/audit_harness.py --path .
```

Add `--json` when another tool needs the result. The audit inventories the current harness and reports two existence-level drift directions:

- a component exists on disk but is absent from `.claude/harness-spec.md`;
- a `generated` or `validated` spec row names a component that is missing on disk.

It does not compare the meaning of an existing file with the spec. Treat every difference as evidence to review, not corruption to delete automatically.

Run structural validation before extending a harness:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py --path .
```

Resolve existing structural errors before adding new behavior.

## 2. Add a new behavior

Invoke Harness Creator through the one installation path currently active. For the plugin:

```text
/harness-creator:harness-creator
```

Choose `extend` mode and state only what is new:

```text
Extend the existing harness so release preparation follows the repository's release checklist.
```

Review the proposed delta against three questions:

- When must the information load?
- Does the project need advice, a reusable procedure, or deterministic enforcement?
- What context, execution, coordination, and maintenance cost does the layer add?

Reject a proposal that creates a component without a concrete need. Approve the delta only after the spec names the behavior, layer, component, rationale, status, and validation evidence.

## 3. Reconcile spec and disk drift

Choose `sync` mode when the audit finds a disagreement between the spec and disk. The interaction should walk only the drift list rather than repeating the goals interview.

For each item, choose one deliberate resolution:

- update the spec to describe an intentional file;
- regenerate a missing file from approved intent;
- mark deliberately removed behavior `retired`;
- mark a proposed behavior that should never be generated `declined`.

Default to preserving current files until the owner confirms otherwise. A file absent from the spec may be a teammate's intentional addition, and a missing file may have been removed deliberately without a status update.

## 4. Review the proposed change

Generation should touch only the new or directly affected components, the behavior inventory, and change history. Inspect the complete delta:

```bash
git diff --stat
git diff
```

Verify that unrelated statuses and rationale remain unchanged. For sync work, confirm that the change-history entry distinguishes an external edit, restoration, spec correction, or retirement accurately.

## 5. Validate and record the result

Repeat structural validation after generation. If the delta changes a hook, test both allowed and blocked inputs. If it changes skill discovery, try realistic triggers and close near-misses in a fresh Claude Code session.

Record the command or scenario, date, outcome, and evidence location in the spec's Validation section before committing.

## 6. Next

Use [Improve an existing harness](../tutorials/improve-an-existing-harness.md) when behavior is present but wrong, [Validate a harness](validate-a-harness.md) for the evidence workflow, or [Harness reference](../reference/harness.md) for spec and status contracts. Return to the [documentation index](../README.md).
