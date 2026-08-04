# Harness Creator documentation

Harness Creator helps Claude Code users design, generate, validate, and maintain a project-specific harness through a structured interview. Start with the first tutorial if you have not run it before.

## Start here

- [Overview](Overview.md) — what Harness Creator does, who it is for, and what it deliberately does not do.
- [Create your first harness](tutorials/first-harness.md) — install the plugin and reach a validated first result.

## Tutorials

- [Create your first harness](tutorials/first-harness.md) — learn the complete new-project flow.
- [Improve an existing harness](tutorials/improve-an-existing-harness.md) — learn the audit and re-entry model by fixing a real friction point.

## How-to guides

- [Install and update](how-to/install-and-update.md) — choose one installation path, update it, or remove it.
- [Extend a harness](how-to/extend-a-harness.md) — add a new need without rebuilding what already works.
- [Synchronize drift](how-to/sync-drift.md) — reconcile `.claude/harness-spec.md` with files on disk.
- [Validate a harness](how-to/validate-a-harness.md) — run the deterministic structural validator.
- [Test hooks](how-to/test-hooks.md) — exercise matchers, exit codes, and hook outputs locally.
- [Run E2E validation](how-to/run-e2e-validation.md) — run an optional behavioral scenario with informed consent.
- [Troubleshoot](how-to/troubleshooting.md) — resolve common installation, routing, validation, and cache problems.

## Reference

- [Generated components](reference/generated-components.md) — the seven possible harness layers.
- [CLI](reference/cli.md) — exact commands and options for the bundled Python tools.
- [Interview and re-entry](reference/interview-and-reentry.md) — stages, approval gates, modes, and statuses.
- [Harness spec](reference/harness-spec.md) — schema and lifecycle of `.claude/harness-spec.md`.
- [Support, compatibility, and limitations](reference/support-compatibility-and-limitations.md) — supported environment and honest boundaries.
- [FAQ](reference/faq.md) — concise answers to recurring questions.

## Explanation

- [Why harnesses](explanation/why-harnesses.md) — why project-specific context and controls matter.
- [Layer routing](explanation/layer-routing.md) — how authority, load timing, and cost select a layer.
- [Architecture](explanation/architecture.md) — exact technical flow and repository structure.
- [Progressive disclosure](explanation/progressive-disclosure.md) — why context should load at the moment it becomes relevant.
- [Principles and verified boundaries](explanation/principles-and-verified-boundaries.md) — the division between judgment and deterministic control.

## Project routes

- [Contributing](../../CONTRIBUTING.md)
- [Support](../../SUPPORT.md)
- [Security](../../SECURITY.md)
- [Code of Conduct](../../CODE_OF_CONDUCT.md)
- [License](../../LICENSE)
