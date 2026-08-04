# Validate a harness

Use this guide to choose the right evidence level: deterministic structural checks, focused hook tests, or an optional behavioral Claude Code scenario.

## 1. Choose the evidence level

| Level | Tool | Establishes |
|---|---|---|
| Structural | `validate_harness.py` | Known file, schema, reference, and cross-file contracts |
| Hook behavior | `test_hook.py` | Matching, execution, exit, and output for selected inputs |
| Session behavior | `run_e2e.py` plus separate grading | Transcript evidence for one approved scenario |

These levels are cumulative, not interchangeable. A clean structural result does not prove natural-language triggers, model adherence, arbitrary hook business logic, or useful task outcomes.

## 2. Structural validation

Run the default check against a target repository:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py \
  --path /path/to/target-project
```

Exit codes:

| Code | Meaning |
|---:|---|
| `0` | No structural errors; warnings may still be present |
| `1` | At least one error, or a warning under `--strict` |
| `2` | The path or arguments prevented the validator from running |

Use strict mode after the project's warning policy is settled:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py \
  --path . --strict
```

Use `--json` when another script needs to group findings by severity or location.

The validator checks settings shape, hook definitions, permission tokens, referenced scripts, rules, skills, agents, workflows, imports, spec/file existence drift, and the always-loaded instruction budget. Fix findings at the reported location and rerun until the exit code is zero.

## 3. Test command hooks

Test a hook from settings with a representative event and tool:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/test_hook.py \
  --settings .claude/settings.json \
  --event PreToolUse \
  --tool Bash \
  --input-field command="git status"
```

Inspect matcher coverage before executing handlers:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/test_hook.py \
  --settings .claude/settings.json \
  --matrix
```

You can also test one command directly:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/test_hook.py \
  --command .claude/hooks/protect-migrations.sh \
  --event PreToolUse \
  --tool Edit \
  --input sample-event.json
```

Do not put secrets in fixtures. Every blocking hook needs at least one allowed input, one blocked input, one close boundary case, and one malformed or missing-field case when it accepts external input.

Confirm the actual effect rather than only the process exit. For most blocking events, exit `2` uses standard error as the denial reason. Exit `1` normally reports a hook failure rather than “deny.” Event-specific contracts still apply.

Rerun structural validation after changing a hook or settings file.

## 4. Behavioral E2E validation

Use E2E only after structural validation passes and the user approves a real Claude Code scenario, token use, and possible execution effects.

`run_e2e.py` launches `claude -p`, records `transcript.jsonl` and `summary.json`, and leaves grading to a separate reviewer against the harness spec. It does not prove correctness by itself. Headless permission handling remains a best estimate rather than a universal safety guarantee.

Define one prompt with an observable expected result tied to a spec item:

```text
When asked to modify an existing migration, Claude should refuse the edit and explain that migrations are append-only.
```

Run against a disposable or clean project. `--isolate` copies the project before the session:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/run_e2e.py \
  --project /path/to/target-project \
  --prompt-file scenario.txt \
  --isolate \
  --out e2e-results/migration-boundary
```

Isolation prevents writes from touching the original project, but it is not a security sandbox. Review the prompt, hooks, permissions, and available tools first. Useful controls include `--model`, `--timeout`, `--permission-mode`, `--json`, and `--out`. Do not use `--dangerously-skip-permissions` casually.

Review both artifacts:

- `transcript.jsonl` for the actual sequence of messages and tools;
- `summary.json` for run metadata and parse results.

Grade the evidence as pass, failure, or inconclusive with a reason. A transcript that mentions a rule is not evidence that an enforcement hook blocked the action.

Route confirmed failures to the owning surface:

- wrong or missed trigger: revise skill discovery metadata;
- correct trigger, wrong procedure: revise the skill body or reference;
- advisory rule ignored: improve context or consider deterministic control;
- hook failed to block: inspect event, matcher, handler, exit code, and output channel;
- runner behavior unclear: mark the scenario inconclusive.

## 5. Record the result

In `.claude/harness-spec.md`, record the evidence level, command or scenario, date, outcome, and artifact location. Do not collapse structural, hook, and session evidence into one generic “validated” claim.

## 6. Next

Look up every flag in the [CLI reference](../reference/cli.md), use [Troubleshooting](troubleshooting.md) for recurring failures, or use [Improve an existing harness](../tutorials/improve-an-existing-harness.md) to route a confirmed behavioral problem. Return to the [documentation index](../README.md).
