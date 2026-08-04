# CLI reference

This reference lists the bundled Python 3.10+ command-line tools. All use only the Python standard library.

Commands below assume a Harness Creator checkout at `/path/to/Harness-Creator`.

## 1. `audit_harness.py`

Inventory an existing harness, compare spec and disk, report hygiene findings, and suggest a re-entry mode.

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/audit_harness.py \
  --path TARGET [--json]
```

| Option | Meaning |
|---|---|
| `--path PATH` | Target repository root; required |
| `--json` | Emit machine-readable JSON |

The audit exits zero unless the target path is invalid. Findings are evidence for a mode decision, not a pass/fail gate.

## 2. `validate_harness.py`

Run deterministic structural validation and the always-loaded budget report.

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py \
  --path TARGET [--json] [--strict]
```

| Option | Meaning |
|---|---|
| `--path PATH` | Target repository root; required |
| `--json` | Emit findings as JSON |
| `--strict` | Treat warnings as failures |

Exit `0` means no errors, exit `1` means errors or strict warnings, and exit `2` means invocation failure.

## 3. `hook_event.py`

Look up one hook event from the bundled source-of-truth table without loading the full reference.

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/hook_event.py \
  [--event EVENT] [--list]
```

`--list` prints supported event names. `--event` prints the selected event's schema and contract.

## 4. `test_hook.py`

Resolve and execute command hooks against realistic input, or inspect matching without execution.

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/test_hook.py \
  [--settings FILE] [--command COMMAND] [--event EVENT] [--tool TOOL] \
  [--input FILE] [--input-field k=v] [--matrix] [--json]
```

| Option | Meaning |
|---|---|
| `--settings FILE` | Read hooks from a settings file |
| `--command COMMAND` | Test one command handler directly |
| `--event EVENT` | Hook event name |
| `--tool TOOL` | Representative tool name; defaults to `Bash` |
| `--input FILE` | JSON input fixture |
| `--input-field k=v` | Override a sample input field; repeatable |
| `--matrix` | Print matcher results without executing handlers |
| `--json` | Emit machine-readable results |

## 5. `run_e2e.py`

Launch a headless Claude Code session and record artifacts for separate grading.

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/run_e2e.py \
  --project TARGET [--prompt TEXT | --prompt-file FILE] [--model MODEL] \
  [--timeout SECONDS] [--out DIR] [--json] \
  [--permission-mode MODE] [--isolate]
```

| Option | Meaning |
|---|---|
| `--project PATH` | Target project; required |
| `--prompt TEXT` | Inline scenario prompt |
| `--prompt-file FILE` | Read scenario prompt from a file |
| `--model MODEL` | Claude model ID or alias |
| `--timeout SECONDS` | Run timeout; default 300 |
| `--out DIR` | Artifact directory; otherwise a temporary directory |
| `--json` | Also print the summary as JSON |
| `--permission-mode MODE` | Pass a Claude Code permission mode |
| `--isolate` | Copy the project before running |

Read [Behavioral E2E validation](../how-to/validate-a-harness.md#4-behavioral-e2e-validation) before using this command. It can consume tokens and its headless permission behavior is not a universal safety guarantee.

## 6. Internal helper

`harness_common.py` provides shared parsing and discovery logic to the CLIs. It is not a user-facing command.

## 7. Next

Use [Validate a harness](../how-to/validate-a-harness.md) for structural, hook, and E2E evidence, or [Maintain an existing harness](../how-to/maintain-a-harness.md) for extension and drift work. Return to the [documentation index](../README.md).
