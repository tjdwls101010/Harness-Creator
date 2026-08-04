# Overview

This page introduces Harness Creator for Claude Code users who want a project-specific setup without becoming experts in every extension surface first.

## 1. The problem

Claude Code can read a repository, but durable project behavior lives across several surfaces with different costs and authority. A fact in `CLAUDE.md` is always present. A path-scoped rule loads only for matching work. A skill holds a procedure. A hook or permission can block an action. An agent isolates context. A workflow fixes an execution shape.

Putting everything in one file wastes context and creates conflicting instructions. Generating every possible layer creates maintenance work without evidence that the layer is needed. Leaving a hard boundary as prose makes it advisory when the project requires enforcement.

## 2. What Harness Creator does

Harness Creator runs a five-part loop:

1. Audit the repository and any existing harness.
2. Interview the user about goals and non-negotiable constraints.
3. Route each identified need to a deliberate layer.
4. Generate only the approved components and persist the rationale.
5. Validate structure and offer optional behavioral end-to-end testing.

The implementation is a Claude Code skill packaged as a plugin. Its Python scripts use only the standard library and can also be run directly.

## 3. Who it is for

Harness Creator is for Claude Code users who:

- want consistent project behavior but do not know which Claude Code surface should own each need;
- already have a `.claude/` setup and need to extend, improve, or reconcile it;
- want deterministic checks separated from advisory instructions;
- want an inspectable spec explaining why each generated component exists.

You do not need to know hook event names, permission syntax, skill frontmatter, or workflow structure before the interview. The skill uses repository facts where it can and asks you only for choices that require intent.

## 4. What you receive

The generated result can contain any subset of seven layers: `CLAUDE.md`, rules, skills, hooks and permissions, agents, workflows, and `.claude/harness-spec.md`.

Complete does not mean every layer. It means every identified need has a deliberate home, and no layer is generated without a reason.

Structural validation is part of the default loop. Optional behavioral E2E validation is a separate, consent-gated activity because it uses a real Claude Code session and may consume tokens or execute generated behavior.

## 5. How it differs by category

| Category | Main tradeoff |
|---|---|
| Manual configuration | Direct control, but the user owns discovery, routing, syntax, and maintenance |
| Static template | Fast start, but assumptions are fixed before the project is inspected |
| Component collection | Reusable pieces, but the user still assembles and validates the system |
| Harness Creator | More guided interaction in exchange for project-specific routing and a persisted rationale |

Harness Creator does not promise that one structure fits every repository. The interview exists because the correct layer depends on the project's facts, the user's intent, and the cost of a violation.

## 6. Non-goals

Harness Creator does not:

- replace Claude Code or change the underlying model;
- generate every supported component by default;
- claim that deterministic lint proves behavioral correctness;
- silently overwrite an existing harness without an approved plan;
- make an external service, marketplace, or hosted control plane part of runtime use;
- remove the need to review security-sensitive hooks and permissions.

## 7. Next

Continue with [Create your first harness](tutorials/first-harness.md), or read [Why harnesses](explanation/why-harnesses.md) for the underlying mental model. Return to the [documentation index](README.md).
