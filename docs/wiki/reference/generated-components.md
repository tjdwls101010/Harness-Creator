# Generated components

This reference describes the seven layers Harness Creator can generate and the contract each layer serves.

## 1. Completeness

Complete does not mean every layer. It means every identified need has a deliberate home, and no layer is generated without a reason.

The harness spec is the inventory of those decisions. A layer can be absent because no need routes to it.

## 2. `CLAUDE.md`

Use `CLAUDE.md` for project facts, build commands, layout, and team conventions relevant to most sessions. Root content is always loaded, so every line has recurring context cost.

Avoid long task procedures and narrow directory-specific rules here. Route those to skills or path-scoped rules.

## 3. Rules

Use `.claude/rules/*.md` for constraints and conventions. A `paths` frontmatter field can scope a rule so it loads only when matching files are touched.

Rules remain model instructions. They are not deterministic enforcement.

## 4. Skills

Use `.claude/skills/<name>/SKILL.md` for reusable procedures and specialized knowledge that should load on demand. The name and description participate in discovery; the full body loads when invoked.

References and scripts belong inside a skill when they are needed only by that procedure. A skill description must distinguish both intended triggers and close near-misses.

## 5. Hooks and permissions

Use hooks for lifecycle-triggered actions such as checking, transforming, recording, or blocking. Use permissions to define tool access boundaries.

Command, HTTP, and MCP-tool handlers execute deterministically once their hook event fires. Prompt and agent hook handlers still use model judgment. Event-specific input, matcher, output, and blocking contracts matter.

Prose can explain a boundary; a hook or permission is required when the boundary must be enforced.

## 6. Agents

Use `.claude/agents/*.md` for focused roles that benefit from their own context window, tool policy, or model choice. Only the result returns to the parent session.

Isolation has a coordination cost. Do not create an agent when a skill in the main conversation is sufficient.

## 7. Workflows

Use `.claude/workflows/*.js` for repeatable orchestration with a stable execution shape. A workflow should remain thin: code controls sequencing, concurrency, and data transfer while agents retain judgment inside their assigned work.

Permissions required by unattended workflow steps must be explicit so execution does not stall on an unseen prompt.

## 8. Harness spec

Use `.claude/harness-spec.md` as the persisted source of truth for context, goals, behavior inventory, component specifications, rationale, validation evidence, and change history.

The spec is always present in a Harness Creator result because it records why other layers exist or were declined.

## 9. Routing summary

| Need | Default destination |
|---|---|
| Fact needed in most sessions | `CLAUDE.md` |
| File-scoped convention | Rule with `paths` |
| Reusable procedure | Skill |
| Non-negotiable block or automatic check | Hook or permission |
| Isolated specialist context | Agent |
| Fixed orchestration | Workflow |
| Decision and lifecycle record | Harness spec |

## 10. Next

Read [Layer routing](../explanation/layer-routing.md) for the decision logic or [Harness spec](harness-spec.md) for the persisted schema. Return to the [documentation index](../README.md).
