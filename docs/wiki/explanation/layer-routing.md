# Layer routing

This explanation shows how Harness Creator selects a deliberate home for each identified need.

## 1. Three axes

Routing evaluates three primary axes:

| Axis | Question |
|---|---|
| Authority | Is this advice, a reusable procedure, or a non-negotiable control? |
| Load timing | Is it needed in most sessions, only for matching files, or only for one task? |
| Cost | What recurring context, coordination, execution, and maintenance cost does the layer add? |

A fourth practical question checks whether an existing tool already enforces the requirement. A second control may be redundant rather than safer.

## 2. Start with the need, not the component

The interview first writes a behavior, knowledge item, or constraint in user terms. “Generate a security agent” is a proposed implementation. “Review authentication changes without filling the main session with dependency traces” is a need that can be evaluated.

Starting from needs prevents the available Claude Code surfaces from dictating the inventory.

## 3. Route by authority

Advisory facts and principles belong in model context. Reusable multi-step procedures belong in skills. Non-negotiable behavior needs a deterministic control when one is available and justified.

The key distinction is not “important versus unimportant.” It is whether the project can accept model interpretation at the moment of action.

## 4. Route by load timing

| Timing | Likely layer |
|---|---|
| Needed in almost every session | Root `CLAUDE.md` |
| Needed when matching paths are touched | Path-scoped rule or subdirectory context |
| Needed for a named procedure | Skill |
| Needed at a lifecycle event | Hook |
| Needed in a side task with isolated context | Agent |
| Needed in a fixed multi-step execution | Workflow |

Loading later is useful only when the routing path is reliable. Splitting one procedure across many references can save context but create a silent failure when the pointer is missed.

## 5. Account for cost

Every layer has more than token cost:

- root context consumes tokens on every session;
- a skill needs discoverable trigger metadata;
- a hook adds executable code and event-specific failure modes;
- an agent adds isolation and handoff overhead;
- a workflow adds orchestration and permission requirements;
- duplication adds drift.

The right layer is the least costly one that still has enough authority and reliable timing.

## 6. Record declines

When a layer is considered and rejected, the spec records `declined` with the reason. This is part of completeness: deliberate absence is different from an overlooked need.

## 7. Escalate from evidence

Improve mode applies routing in reverse. If advisory context repeatedly fails for a costly boundary, the evidence may justify escalation to a hook or permission. If an always-loaded procedure wastes context, move it to a skill. If an agent adds handoff noise without useful isolation, collapse it back into the main flow.

## 8. Next

Look up each destination in [Harness reference](../reference/harness.md) or see the implementation flow in [Architecture](architecture.md). Return to the [documentation index](../README.md).
