# Frequently asked questions

This page answers common questions about installing, running, and evaluating Harness Creator.

## 1. Is a harness just `CLAUDE.md`?

No. `CLAUDE.md` is one possible layer. A project may also need path-scoped rules, on-demand skills, hooks, permissions, agents, workflows, and a persisted spec. Harness Creator generates only the layers justified by identified needs.

## 2. Does “complete” mean all seven layers?

No. Complete does not mean every layer. It means every identified need has a deliberate home, and no layer is generated without a reason.

## 3. Which installation should I use?

Use the Claude Code plugin for normal use, the skills CLI when you want only the skill, and the symlink for local development. Keep only one active. See [Install and update](../how-to/install-and-update.md).

## 4. Why is the plugin invocation namespaced?

Plugin skills are namespaced by plugin name, so the invocation is `/harness-creator:harness-creator`. A skills CLI or symlink installation uses `/harness-creator`.

## 5. Will Harness Creator overwrite my existing `.claude/` setup?

It begins with an audit, chooses a re-entry mode, records proposed changes in the spec, and requires approval before generation. Review the diff before committing. Sync mode defaults to treating unexpected files as potentially intentional rather than deleting them.

## 6. What is `.claude/harness-spec.md` for?

It records goals, behavior inventory, routing, component details, rationale, validation evidence, statuses, and change history. Future runs use it to extend, improve, and reconcile the harness without reconstructing intent from files.

## 7. Does validation prove the harness works?

Structural validation proves only the contracts it checks. Hook tests provide stronger evidence for command-hook matching and output behavior. Optional E2E scenarios provide behavioral evidence for one approved case, not a universal guarantee.

## 8. Why are hooks separate from instructions?

Instructions guide model behavior. A non-negotiable block requires deterministic control such as a hook or permission. The model choosing to obey prose is different from the harness preventing an action.

## 9. Why not put every instruction in `CLAUDE.md`?

Root `CLAUDE.md` loads in every session. Narrow procedures and path-specific rules consume context even when irrelevant and can conflict with other instructions. Skills and scoped rules load closer to the task that needs them.

## 10. Can the interview run headlessly?

Not end to end. It relies on interactive decisions, and the required question surface is unavailable in headless and subagent contexts. The repository does not claim automated coverage for that interaction.

## 11. Does E2E validation cost tokens?

Yes. `run_e2e.py` starts a real headless Claude Code session. It runs only with user consent and should use a specific scenario, an isolated copy, and an explicit result directory.

## 12. Why did an update not appear?

Plugin installs use a cache. Update the marketplace and plugin, then run `/reload-plugins` or start a new session. Contributors should use the symlink for immediate source changes.

## 13. Does Harness Creator require third-party Python packages?

No. The bundled scripts target Python 3.10+ and use the standard library only.

## 14. How do I report a problem?

Use [SUPPORT.md](../../../SUPPORT.md). Bugs, feature requests, and documentation issues have dedicated Issue Forms. Security vulnerabilities must use private vulnerability reporting.

## 15. Next

Read [Support, compatibility, and limitations](support-compatibility-and-limitations.md) for the full boundary, or return to the [documentation index](../README.md).
