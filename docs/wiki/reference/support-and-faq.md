# Support, compatibility, and FAQ

This reference collects the supported environment, known boundaries, maintenance expectations, and recurring questions for Harness Creator users.

## 1. Compatibility and support

| Surface | Compatibility |
|---|---|
| Claude Code | Current plugin and skill surfaces; mechanics can change and should be checked against current documentation |
| Python | 3.10 or later; CI covers 3.10 and 3.14 |
| Python dependencies | Standard library only |
| Git | Required for the normal project and distribution workflow |
| Operating system | Scripts are portable Python; generated hooks may be platform-specific by project choice |

Harness Creator is a Claude Code skill distributed through a plugin marketplace and the skills CLI. It is not a standalone interactive Python application.

Maintenance and user support are best effort. There is no response, resolution, or release SLA. Security support applies to the latest tagged release only and is also best effort. Use [SUPPORT.md](../../../SUPPORT.md) for the appropriate route and GitHub private vulnerability reporting for security issues.

## 2. Validation and automation boundaries

### 2.1. Structural validation

`validate_harness.py` checks deterministic structure: syntax, known fields, references, paths, component discovery, selected cross-file relationships, drift, and instruction budget.

It cannot prove natural-language trigger quality, model adherence, usefulness of generated content, correctness of arbitrary hook business logic, or success of a real task.

### 2.2. Interactive interview

The complete interview relies on interactive user decisions. The required question surface is unavailable in headless and subagent contexts, so the project does not claim automated end-to-end coverage for that interaction.

### 2.3. Behavioral E2E

`run_e2e.py` records a real headless Claude Code session for separate grading. Its headless permission handling has not been broadly confirmed across environments. `--isolate` copies the target project but is not a security sandbox.

### 2.4. Drift detection

Audit can find files missing from the spec and `generated` or `validated` rows missing from disk. It does not compare the meaning of existing component content against its rationale.

## 3. Operational boundaries

Plugin installations are copied into Claude Code's cache. Editing a checkout does not update the cached plugin. Contributors should use the development symlink and remove the plugin during editing. Only one of the plugin, skills CLI, and symlink paths should be active at a time.

Hooks, permissions, agents, and workflows can execute commands or alter tool access. Review them before committing. A generated file is not trusted merely because its structure validates.

Harness Creator runtime does not require a hosted service from this repository. Plugin marketplaces and skills.sh are distribution surfaces whose availability is outside the project's control.

## 4. Frequently asked questions

### 4.1. Is a harness just `CLAUDE.md`?

No. `CLAUDE.md` is one possible layer. A project may also need path-scoped rules, on-demand skills, hooks, permissions, agents, workflows, and a persisted spec. Harness Creator generates only the layers justified by identified needs.

### 4.2. Does “complete” mean all seven layers?

No. Complete does not mean every layer. It means every identified need has a deliberate home, and no layer is generated without a reason.

### 4.3. Which installation should I use?

Use the Claude Code plugin for normal use, the skills CLI when you want only the skill, and the symlink for local development. Keep only one active. See [Install and update](../how-to/install-and-update.md).

### 4.4. Why is the plugin invocation namespaced?

Plugin skills are namespaced by plugin name, so the invocation is `/harness-creator:harness-creator`. A skills CLI or symlink installation uses `/harness-creator`.

### 4.5. Will Harness Creator overwrite my existing setup?

It begins with an audit, chooses a re-entry mode, records proposed changes in the spec, and requires approval before generation. Sync mode treats unexpected files as potentially intentional rather than deleting them automatically. Review the diff before committing.

### 4.6. What is `.claude/harness-spec.md` for?

It records goals, behavior inventory, routing, component details, rationale, validation evidence, statuses, and change history. Future runs can extend, improve, or reconcile the harness without reconstructing intent from files.

### 4.7. Does validation prove the harness works?

Structural validation proves only the contracts it checks. Hook tests provide stronger evidence for selected command-hook inputs. Optional E2E scenarios provide behavioral evidence for one approved case, not a universal guarantee.

### 4.8. Why are hooks separate from instructions?

Instructions guide model behavior. A non-negotiable block requires a deterministic control such as a hook or permission. Choosing to follow prose is different from the harness preventing an action.

### 4.9. Why not put every instruction in `CLAUDE.md`?

Root `CLAUDE.md` loads in every session. Narrow procedures and path-specific rules consume context when irrelevant and can conflict with other guidance. Skills and scoped rules load closer to the task that needs them.

### 4.10. Can the interview run headlessly?

Not end to end. It relies on interactive decisions, and the required question surface is unavailable in headless and subagent contexts.

### 4.11. Does E2E validation cost tokens?

Yes. `run_e2e.py` starts a real headless Claude Code session. Use a specific scenario, an isolated copy, an explicit result directory, and informed consent.

### 4.12. Why did an update not appear?

Refresh the marketplace and plugin, then run `/reload-plugins` or start a new session. Contributors should use the development symlink for immediate source changes.

### 4.13. Does Harness Creator require third-party Python packages?

No. The bundled scripts target Python 3.10+ and use the standard library only.

### 4.14. How do I report a problem?

Use [SUPPORT.md](../../../SUPPORT.md). Bugs, feature requests, and documentation issues have dedicated Issue Forms. Report vulnerabilities privately.

## 5. Next

Use [Troubleshooting](../how-to/troubleshooting.md) for a concrete failure, [CLI reference](cli.md) for exact commands, or [Harness reference](harness.md) for component and spec contracts. Return to the [documentation index](../README.md).
