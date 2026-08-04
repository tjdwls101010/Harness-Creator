# Validate a harness

Use this guide to run Harness Creator's deterministic structural checks against a target repository.

## 1. Run the default check

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py --path /path/to/target-project
```

Exit codes:

| Code | Meaning |
|---:|---|
| `0` | No structural errors; warnings may still be present |
| `1` | At least one error, or a warning under `--strict` |
| `2` | The validator could not run because the path or arguments were invalid |

## 2. Use strict mode in automation

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py --path . --strict
```

Strict mode turns warnings into failures. Use it when the project's warning policy is settled; the default Harness Creator generation loop requires zero errors but can surface warnings for user judgment.

## 3. Request JSON

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py --path . --json
```

Use JSON when another script needs to group findings by severity or location.

## 4. Interpret the result

The validator covers structural contracts including settings shape, hook definitions, permission tokens, referenced scripts, rules, skills, agents, workflows, imports, spec/file existence drift, and always-loaded instruction budget.

A clean result does not establish:

- that a skill triggers on the right natural-language requests;
- that Claude follows advisory guidance in every situation;
- that a hook's business logic is correct for all inputs;
- that a workflow produces a useful outcome;
- that a behavioral E2E scenario passes.

Use [Test hooks](test-hooks.md) for command hooks and [Run E2E validation](run-e2e-validation.md) for consent-gated behavioral evidence.

## 5. Resolve findings

Fix errors at the reported location rather than suppressing the validator. For warnings, decide whether the condition is intentional and record that reasoning in the harness spec when it affects design.

Run the same command again after every fix until the exit code is zero.

## 6. Next

Look up all flags in the [CLI reference](../reference/cli.md), or use [Troubleshooting](troubleshooting.md) for recurring failures. Return to the [documentation index](../README.md).
