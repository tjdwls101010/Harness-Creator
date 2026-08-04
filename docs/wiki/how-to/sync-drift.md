# Synchronize harness drift

Use this guide when `.claude/harness-spec.md` and the harness files on disk no longer describe the same components.

## 1. Produce the audit report

Run the audit directly or invoke Harness Creator:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/audit_harness.py --path .
```

For machine-readable output:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/audit_harness.py --path . --json
```

The audit reports two existence-level drift directions:

- a component exists on disk but is absent from the spec;
- a spec row at `generated` or `validated` names a component that is missing on disk.

It does not compare the meaning of existing file contents against the spec.

## 2. Review each item before changing files

Treat divergence as evidence, not corruption. A file absent from the spec may be a teammate's intentional addition. A missing file may have been deliberately removed without updating its status.

For each item, choose one resolution:

- update the spec to reflect the current files;
- regenerate the file to match approved intent;
- mark the behavior `retired` when removal was deliberate;
- mark a proposed behavior `declined` when it should never be generated.

Default to preserving current files until the owner confirms otherwise.

## 3. Run sync mode

Invoke Harness Creator and select `sync`. The interaction should walk only the reported drift list rather than repeating the full goals interview.

Approve the resolution list before generation or spec edits.

## 4. Validate the reconciled state

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py --path .
```

Review the spec's change-history entry to confirm that it describes an external edit, a restoration, or a retirement accurately.

## 5. Next

Read [Harness spec reference](../reference/harness-spec.md) for status semantics, or [Extend a harness](extend-a-harness.md) to add a new behavior after the state is clean. Return to the [documentation index](../README.md).
