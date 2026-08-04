# Create your first harness

This tutorial takes a first-time user from installation to a structurally validated harness in a real project.

## 1. Before you begin

You need Claude Code, Git, and Python 3.10 or later. Work in a project whose Claude Code configuration you are allowed to change.

Keep only one Harness Creator installation active. If you previously installed it through the skills CLI or created a development symlink, remove that installation before using the plugin path in this tutorial.

Commit or stash unrelated work so the generated diff is easy to inspect.

## 2. Install the plugin

Add the repository marketplace:

```bash
claude plugin marketplace add tjdwls101010/Harness-Creator
```

Install Harness Creator:

```bash
claude plugin install harness-creator@harness-creator
```

Start a fresh Claude Code session in the target project. A fresh session ensures the installed skill is present in the available-skill catalog.

## 3. Start the interview

Invoke the namespaced skill:

```text
/harness-creator:harness-creator
```

If slash commands are inconvenient, use a natural-language request:

```text
Create a Claude Code harness for this project.
```

Harness Creator first runs a read-only audit. For a project without existing Claude Code configuration, the suggested mode should be `new`.

## 4. Describe the desired change

Answer the opening question in terms of project outcomes, not Claude Code components. For example:

```text
Claude should know the test command and repository layout in every session.
Changes to database migrations must be append-only.
Release preparation should follow the same checklist each time.
```

The interview turns this prose into a behavior inventory. It then proposes a layer for each item. Review the reasoning, especially the distinction between advisory context and a boundary that must be enforced.

## 5. Approve the spec

The skill writes the proposed decisions to `.claude/harness-spec.md` and asks for approval before generating components.

Check that:

- every goal you named appears in the inventory;
- each need has a plausible layer;
- declined components remain recorded rather than disappearing;
- the validation plan describes evidence you recognize;
- no component is present merely because Claude Code supports it.

Ask for corrections before approving. Generation begins only after explicit approval.

## 6. Inspect the generated result

After generation, review the working tree:

```bash
git status --short
git diff -- . ':!.claude/harness-spec.md'
git diff -- .claude/harness-spec.md
```

The exact file set depends on your interview. A small first harness may contain only `CLAUDE.md`, one rule or skill, and the spec.

## 7. Verify structural validation

Harness Creator runs its validator before completing. You can repeat the check yourself from the target repository:

```bash
python3 /path/to/Harness-Creator/.claude/skills/harness-creator/scripts/validate_harness.py --path .
```

A clean result means the generated files satisfy the validator's structural contracts. It does not prove behavior in every future task.

If the harness includes command hooks, continue with [Test hooks](../how-to/test-hooks.md). If you approved behavioral scenarios, read [Run E2E validation](../how-to/run-e2e-validation.md) before spending tokens.

## 8. Record the result

Commit the generated harness only after reviewing it. Keep `.claude/harness-spec.md` with the other files; future `extend`, `improve`, and `sync` runs depend on its rationale and status history.

## 9. Next

Learn how later runs work in [Improve an existing harness](improve-an-existing-harness.md), or look up the exact state model in [Interview and re-entry](../reference/interview-and-reentry.md). Return to the [documentation index](../README.md).
