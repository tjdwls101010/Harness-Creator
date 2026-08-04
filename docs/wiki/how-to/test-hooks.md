# Test hooks

Use this guide to exercise a command hook's matching and output behavior before trusting it in a live Claude Code session.

## 1. Test from settings

Choose the hook event and representative tool:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/test_hook.py \
  --settings .claude/settings.json \
  --event PreToolUse \
  --tool Bash \
  --input-field command="git status"
```

The tool finds matching groups, builds realistic event input, executes command handlers, and explains the effect of exit code, standard output, and standard error.

## 2. Inspect the matcher matrix

Before executing any handler:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/test_hook.py \
  --settings .claude/settings.json \
  --matrix
```

Review broad, overlapping, or unexpected matches. A matcher can become an unanchored regular expression when it contains characters outside the exact-list form.

## 3. Test one command directly

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/test_hook.py \
  --command .claude/hooks/protect-migrations.sh \
  --event PreToolUse \
  --tool Edit \
  --input sample-event.json
```

Use a checked-in or temporary JSON fixture containing the event shape the hook expects. Do not include secrets in fixtures.

## 4. Test both sides of the boundary

Every blocking hook needs at least:

- one input that must be allowed;
- one input that must be blocked;
- one close boundary case;
- one malformed or missing-field case when the hook accepts external input.

Confirm the actual effect, not just the process exit. For most blocking hook events, exit `2` uses standard error as the reason. Exit `1` is a hook failure and normally does not mean “deny.” Event-specific output contracts still apply.

## 5. Re-run structural validation

After changing a hook or settings file:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py --path .
```

## 6. Next

Use [Run E2E validation](run-e2e-validation.md) only if a real session is needed to test the interaction. See [CLI reference](../reference/cli.md) for every hook-test option. Return to the [documentation index](../README.md).
