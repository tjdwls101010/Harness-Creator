# Why harnesses

This explanation develops the mental model behind project-specific Claude Code configuration.

## 1. General capability is not project context

A model can reason about code without knowing which command this repository uses for tests, which directories are generated, which migrations are append-only, or which release steps the team has agreed to follow.

Those facts and constraints are neither model weights nor one-off user prompts. They belong to the environment surrounding the model: the harness.

The heuristic `ai-agent = ai-model + ai-harness` makes that division visible. It is not a literal definition of every agent system. It is a reminder that project outcomes depend on both general capability and the context, procedures, tools, and controls supplied around it.

## 2. A harness is a system of surfaces

Claude Code offers several ways to influence or control behavior. They are not interchangeable:

- `CLAUDE.md` keeps high-frequency project context present;
- rules can narrow guidance by path;
- skills load reusable procedures on demand;
- hooks and permissions add deterministic control;
- agents isolate context and tool policy;
- workflows encode repeatable orchestration;
- the harness spec records intent and lifecycle.

A good harness is not the largest collection of these files. It is the smallest set that gives every identified need enough context and authority.

## 3. The routing problem

Consider “database migrations are append-only.” Three implementations carry different meanings:

1. A sentence in `CLAUDE.md` advises Claude in every session.
2. A path-scoped rule presents the constraint only near migration work.
3. A hook rejects an edit to an existing migration.

The first two preserve model judgment but can be missed. The third enforces a boundary but requires executable logic and maintenance. The correct destination depends on whether exceptions exist, how costly a violation is, and whether another control already catches it.

This is why Harness Creator interviews before generating. The repository can reveal file layout and commands; only the user can define intent and non-negotiable boundaries.

## 4. Why persist a spec

Configuration files record implementation. They usually do not record rejected alternatives or the user's reason for a decision. Without that rationale, a later maintainer cannot tell whether an absent hook was overlooked or deliberately declined.

`.claude/harness-spec.md` keeps the behavior inventory, routing, rationale, status, validation evidence, and change history. Re-entry becomes a comparison against approved intent rather than a fresh guess.

## 5. What validation can establish

Structural validation can prove that known schemas, paths, references, and cross-file contracts are internally consistent. Hook tests can exercise a particular deterministic control. A behavioral E2E scenario can provide evidence for one real interaction.

No single check proves universal behavior. A trustworthy harness names the level of evidence rather than collapsing all three into “validated.”

## 6. Next

Read [Layer routing](layer-routing.md) for the decision method or [Principles and verified boundaries](principles-and-verified-boundaries.md) for the judgment/enforcement split. Return to the [documentation index](../README.md).
