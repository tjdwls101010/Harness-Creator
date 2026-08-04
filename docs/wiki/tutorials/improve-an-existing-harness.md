# Improve an existing harness

This tutorial shows how to turn one observed problem in an existing Claude Code harness into a focused, validated change.

## 1. Choose one real friction point

Start from observed behavior, not a speculative redesign. Useful examples include:

- a skill triggers for unrelated requests;
- a rule is repeatedly ignored;
- `CLAUDE.md` contains a long procedure that is irrelevant to most sessions;
- a hook fires but does not block as intended;
- the spec and the files disagree.

Commit or stash unrelated work before continuing.

## 2. Run Harness Creator again

Use the same installation path as the original run. For the plugin path:

```text
/harness-creator:harness-creator
```

Phase 0 audits the current harness and reads `.claude/harness-spec.md` when present. If the files are structurally valid and match the spec, the audit cannot infer whether you want to add or improve behavior; state that you want `improve` mode.

## 3. Describe the failure as evidence

Give the smallest reproducible description:

```text
The release skill triggers for ordinary changelog questions. It should trigger only when I ask to prepare or publish a release.
```

Include the prompt that exposed the problem, the behavior you observed, and the desired behavior. Avoid prescribing the fix unless the layer is itself part of the requirement.

## 4. Review the proposed target

Improve mode routes the symptom to the surface that owns it. A trigger miss usually targets a skill description. A correct trigger followed by a bad procedure targets the skill body. A repeatedly ignored non-negotiable rule may need to move from prose to a hook or permission.

Ask the interview to explain why the proposed layer has enough authority and what additional context cost it introduces.

## 5. Approve the delta

The updated spec should preserve existing approved behaviors and add a change-history entry for this run. Review only the proposed delta, but verify that no unrelated status or rationale changed.

Approve generation when the failure, target component, and validation evidence are all explicit.

## 6. Validate the change

Run structural validation:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py --path .
```

Then use the evidence appropriate to the failure:

- trigger problem: try realistic should-trigger and near-miss prompts in a fresh session;
- hook problem: use `test_hook.py` before a live session;
- context problem: inspect the always-loaded budget report;
- behavioral problem: run an approved E2E scenario in an isolated copy.

## 7. Compare before and after

The improvement is successful when the original failure no longer occurs and existing behavior still satisfies the spec. Record the evidence in the spec's Validation section instead of relying on memory.

## 8. Next

Use [Maintain an existing harness](../how-to/maintain-a-harness.md) when the next change is a new need or the audit reports file/spec disagreement. Return to the [documentation index](../README.md).
