# Harness Creator discoverability overhaul

This dossier records the approved discovery, documentation, trust, installation, and measurement strategy for Harness Creator. It is an implementation record, not product runtime guidance.

## Goal

Help Claude Code users move through a clear sequence:

1. Discover the repository.
2. Understand what Harness Creator does.
3. Verify that its claims and maintenance practices are credible.
4. Install it through one supported path.
5. Reach a useful first run.

Success is directional evidence of qualified interest, not a predetermined star count.

## Immutable product boundary

Everything under `.claude/skills/harness-creator/` is frozen for this overhaul. The existing skill body, references, scripts, runtime behavior, frontmatter, and Korean trigger examples are not changed.

## Contents

- [Research and benchmarks](01-research-and-benchmarks.md)
- [Positioning and messaging](02-positioning-and-messaging.md)
- [Documentation architecture](03-documentation-architecture.md)
- [Visual brief](04-visual-brief.md)
- [Community and distribution](05-community-and-distribution.md)
- [Launch and measurement](06-launch-and-measurement.md)
- [Implementation checklist](07-implementation-checklist.md)
- [Metrics log](metrics-log.md)

## Decision status

The positioning, file set, visual direction, community surfaces, CI scope, repository metadata, and staged distribution sequence in this dossier are approved. Live repository settings and external submissions remain post-merge actions and require the gates described in the distribution plan.
