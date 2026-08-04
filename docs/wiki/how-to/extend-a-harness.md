# Extend a harness

Use this guide when the current harness works and you want to add a new project behavior without redoing the original design.

## 1. Prepare the repository

Commit or stash unrelated changes. Confirm that `.claude/harness-spec.md` exists and that the current harness validates:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py --path .
```

If the validator reports drift or structural errors, resolve those before adding a new behavior.

## 2. Invoke Harness Creator

Use the invocation for your active install path. For the plugin:

```text
/harness-creator:harness-creator
```

Tell the audit that this is an `extend` run and state only what is new:

```text
Extend the existing harness so release preparation follows the repository's release checklist.
```

## 3. Review the delta inventory

The interview should preserve existing goals and add numbered items for the new need. Check that the proposed route answers:

- Does the information need to be present in most sessions?
- Is it a reusable procedure that should load on demand?
- Does it require deterministic enforcement?
- Does it benefit from isolated context or a fixed orchestration shape?

Reject a proposal that creates a layer without a concrete need.

## 4. Approve and generate

Approve the delta after the spec names the component, rationale, status, and validation evidence. Generation should update only the new or directly affected components plus the spec change history.

Inspect the diff:

```bash
git diff --stat
git diff
```

## 5. Validate the extension

Repeat structural validation. If the extension adds a hook, run the matching hook test. If it adds a skill, try both realistic trigger prompts and close near-misses in a fresh Claude Code session.

Record the result in the spec's Validation section before committing.

## 6. Next

Use [Improve an existing harness](../tutorials/improve-an-existing-harness.md) for a behavior that is already present but wrong, or [Synchronize drift](sync-drift.md) when the spec and disk disagree. Return to the [documentation index](../README.md).
