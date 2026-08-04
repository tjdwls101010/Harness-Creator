# Support, compatibility, and limitations

This reference defines the supported environment, maintenance expectations, and known boundaries of Harness Creator.

## 1. Runtime compatibility

| Surface | Compatibility |
|---|---|
| Claude Code | Current Claude Code plugin and skill surfaces; product mechanics can change and should be checked against current docs |
| Python | 3.10 or later; CI covers 3.10 and 3.14 |
| Python dependencies | Standard library only |
| Git | Required for the normal project and distribution workflow |
| Operating system | Scripts are written for portable Python; generated hooks may be platform-specific by project choice |

Harness Creator itself is distributed as a Claude Code skill through a plugin marketplace and the skills CLI. It does not run as a standalone interactive Python application.

## 2. Support policy

Maintenance and user support are best effort. There is no response, resolution, or release SLA. Use [SUPPORT.md](../../../SUPPORT.md) to choose the appropriate route.

Security support applies to the latest tagged release only and is also best effort. Report vulnerabilities through GitHub private vulnerability reporting, not a public issue.

## 3. Structural validation boundary

`validate_harness.py` checks deterministic structure: syntax, known fields, references, paths, component discovery, selected cross-file relationships, drift, and instruction budget.

It cannot prove natural-language trigger quality, model adherence, usefulness of generated content, correctness of arbitrary hook business logic, or success of a real task.

## 4. Interview automation boundary

The full interview relies on interactive user decisions. `AskUserQuestion` is unavailable in headless and subagent contexts, so the interview is not covered by an automated end-to-end test. It is verified through interactive use and the resulting spec, not by claiming a headless test that does not exist.

## 5. E2E runner boundary

`run_e2e.py` records a real headless Claude Code session for separate grading. Its headless permission handling has not been broadly confirmed across environments. `--isolate` copies the target project but is not a security sandbox. Treat early runs as validation of both the harness and runner assumptions.

## 6. Drift boundary

Audit and validation can find files missing from the spec and generated/validated spec rows missing from disk. They do not compare the meaning of existing component content against its rationale.

## 7. Installation cache behavior

Plugin installations are copied into Claude Code's plugin cache. Editing a checkout does not update the cached plugin. Contributors should use the development symlink and remove the plugin during editing.

Only one of the plugin, skills CLI, and symlink paths should be active at a time.

## 8. Generated security-sensitive components

Hooks, permissions, agents, and workflows can execute commands or alter tool access. Review them before committing. A generated file is not trusted merely because its structure validates.

## 9. External services

Harness Creator runtime does not require a hosted service from this repository. Plugin marketplaces and skills.sh are distribution surfaces; their availability is outside the project's control.

## 10. Next

Use [Troubleshooting](../how-to/troubleshooting.md) for a concrete problem, [FAQ](faq.md) for recurring questions, or [SUPPORT.md](../../../SUPPORT.md) for issue routing. Return to the [documentation index](../README.md).
