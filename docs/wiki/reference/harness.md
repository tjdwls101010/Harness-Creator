# Harness reference

This reference defines the seven possible harness layers and the persisted `.claude/harness-spec.md` contract that records why each layer exists.

## 1. Completeness

Complete does not mean every layer. It means every identified need has a deliberate home, and no layer is generated without a reason.

The harness spec inventories those decisions. A layer can be absent because no need routes to it, and a considered component can remain recorded as `declined`.

## 2. Harness layers

### 2.1. `CLAUDE.md`

Use `CLAUDE.md` for project facts, build commands, layout, and team conventions relevant to most sessions. Root content is always loaded, so every line has recurring context cost.

### 2.2. Rules

Use `.claude/rules/*.md` for constraints and conventions. A `paths` frontmatter field can load a rule only when matching files are touched. Rules remain model instructions rather than deterministic enforcement.

### 2.3. Skills

Use `.claude/skills/<name>/SKILL.md` for reusable procedures and specialized knowledge that should load on demand. The name and description participate in discovery; the full body loads when invoked.

### 2.4. Hooks and permissions

Use hooks for lifecycle-triggered checks, transformations, records, or blocks. Use permissions for tool-access boundaries. Command, HTTP, and MCP-tool handlers execute deterministically after their event fires; prompt and agent handlers still use model judgment.

Prose can explain a boundary. A hook or permission is needed when the boundary must be enforced.

### 2.5. Agents

Use `.claude/agents/*.md` for focused roles that need an isolated context window, tool policy, or model choice. Isolation has coordination cost, so do not create an agent when a skill in the main conversation is sufficient.

### 2.6. Workflows

Use `.claude/workflows/*.js` for repeatable orchestration with a stable execution shape. Code controls sequencing, concurrency, and data transfer while agents retain judgment inside their assigned work.

### 2.7. Harness spec

Use `.claude/harness-spec.md` as the persisted source of truth for context, goals, behavior inventory, component specifications, rationale, validation evidence, and change history. It is present in every Harness Creator result.

## 3. Required spec sections

| Section | Content |
|---|---|
| Context | Project stack, commands, layout, team facts, and interview calibration |
| Goals | Desired outcomes, preserving the user's precise wording where useful |
| Behavior inventory | Stable ID, need, layer, component path, and status |
| Component specs | Trigger, scope, inputs, outputs, authority, and failure policy |
| Design rationale | Why the selected layer fits and why alternatives were rejected |
| Validation | Approved scenarios, latest evidence, and outcome |
| Change history | Date, mode, and summary for every Harness Creator pass |

A behavior row uses this stable shape:

```markdown
| id | behavior/knowledge/constraint | layer | component | status |
|---|---|---|---|---|
| B1 | Know the test command in every session | CLAUDE.md | `CLAUDE.md` | validated |
```

Do not renumber existing IDs merely to make the table contiguous.

## 4. Status lifecycle

The common forward path is:

```text
proposed → approved → generated → validated
```

| Status | Meaning | Claims a file exists? |
|---|---|---|
| `proposed` | Identified but not approved | No |
| `approved` | Approved intent awaiting generation | No |
| `generated` | A component was written | Yes |
| `validated` | The component passed its recorded checks | Yes |
| `declined` | Considered and deliberately not built | No |
| `retired` | Previously present and deliberately removed | No |

Only a missing file for a `generated` or `validated` row is existence-level drift.

## 5. Component specifications

Record enough detail to regenerate or inspect a component without inventing missing intent:

- skill: intended triggers, near-misses, purpose, references, scripts, and output contract;
- hook: event, matcher, handler type, input fields, allow/block behavior, output channel, and failure policy;
- agent: role, tools, model policy, input/output contract, and isolation reason;
- workflow: phases, dependencies, shared artifacts, permissions, and stop conditions;
- rule: paths, advisory constraint, and reason it belongs outside root context.

## 6. Evidence, drift, and history

Record structural checks, hook tests, and behavioral E2E as separate evidence levels. Include the command or scenario, date, outcome, and evidence location. Structural validation must not be labeled as behavioral proof.

Audit detects component existence disagreement in both directions. It does not compare the semantic contents of an existing file with the spec. A clean drift report therefore means paths and statuses align, not that every component behaves as described.

Append one change-history entry per run with the date, mode (`new`, `extend`, `improve`, or `sync`), and a concise description. Describe external edits and spec corrections honestly.

## 7. Routing summary

| Need | Default destination |
|---|---|
| Fact needed in most sessions | `CLAUDE.md` |
| File-scoped convention | Rule with `paths` |
| Reusable procedure | Skill |
| Non-negotiable block or automatic check | Hook or permission |
| Isolated specialist context | Agent |
| Fixed orchestration | Workflow |
| Decision and lifecycle record | Harness spec |

## 8. Next

Read [Layer routing](../explanation/layer-routing.md) for the decision method, [Interview and re-entry](interview-and-reentry.md) for the lifecycle, or [Maintain an existing harness](../how-to/maintain-a-harness.md) for drift reconciliation. Return to the [documentation index](../README.md).
