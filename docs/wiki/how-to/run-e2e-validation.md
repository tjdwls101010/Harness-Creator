# Run behavioral E2E validation

Use this guide only after structural validation passes and the user has approved a real Claude Code scenario, token use, and possible execution effects.

## 1. Understand the boundary

`run_e2e.py` launches `claude -p`, records `transcript.jsonl` and `summary.json`, and leaves grading to a separate reviewer against the harness spec. It does not prove correctness by itself.

Headless permission handling remains a documented best estimate rather than a broadly verified guarantee. Treat the first run in your environment as validation of the runner itself. Prefer read-only prompts until that behavior is understood.

## 2. Define one scenario

Write a prompt with an observable expected result. Tie the expectation to a spec item:

```text
When asked to modify an existing migration, Claude should refuse the edit and explain that migrations are append-only.
```

Avoid vague scenarios such as “the harness should work well.”

## 3. Use an isolated copy

Run against a disposable or clean target project. `--isolate` copies the project to a temporary directory before the headless session:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/run_e2e.py \
  --project /path/to/target-project \
  --prompt-file scenario.txt \
  --isolate \
  --out e2e-results/migration-boundary
```

`--isolate` prevents writes from touching the original project, but it is not a security sandbox. Review the prompt, hooks, permissions, and available tools before running.

## 4. Control the run

Useful options include `--model`, `--timeout`, `--permission-mode`, `--json`, and `--out`. Do not pass `--dangerously-skip-permissions` casually; the runner may imply it for isolation unless an explicit permission mode is supplied, as described in its help and source comments.

Stop the run if it accesses unexpected resources or if the permission behavior differs from the approved scenario.

## 5. Grade the evidence

Review both artifacts:

- `transcript.jsonl` for the actual sequence of messages and tools;
- `summary.json` for run metadata and parse results.

Compare evidence against the spec's expected scenario. Record pass, failure, or inconclusive status with a reason. A transcript that merely mentions the rule is not evidence that an enforcement hook blocked the action.

## 6. Route failures

- Wrong or missed trigger: revise the skill description.
- Correct trigger, wrong procedure: revise the skill body or reference.
- Advisory rule ignored: strengthen context or move a non-negotiable boundary to deterministic control.
- Hook failed to block: inspect event, matcher, handler, exit code, and output channel.
- Runner behavior unclear: mark the scenario inconclusive rather than claiming the harness failed.

## 7. Next

Use [Improve an existing harness](../tutorials/improve-an-existing-harness.md) to route a confirmed failure. Return to [Validate a harness](validate-a-harness.md) or the [documentation index](../README.md).
