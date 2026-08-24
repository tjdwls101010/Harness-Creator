# Reddit project-showcase copy

This document records the current Reddit route and keeps reusable copy for both the active Megathread path and a possible future feed post. Recheck the community rules immediately before publishing, and preserve the timing gates in [Community and distribution](05-community-and-distribution.md).

## Submission outcome

- A Showcase feed submission was routed away from the subreddit feed because the submitting account did not meet the current minimum of 50 total karma.
- This was an account-eligibility gate, not a rejection of the project or its copy.
- The moderator response explicitly invited the project to the [Built with Claude Project Showcase Megathread](https://www.reddit.com/r/ClaudeAI/comments/1sly3jm/built_with_claude_project_showcase_megathread/).
- Do not repeatedly resubmit the feed post. Use the Megathread comment below while the account remains below the feed-post threshold.
- No successful public submission or permalink is recorded yet.

## Current target

- Community: `r/ClaudeAI`
- Surface: Built with Claude Project Showcase Megathread
- Format: comment; no post title or flair is required
- Disclosure: the commenter is the project maintainer

## Megathread comment

**Harness Creator — an interview-driven harness creator for Claude Code**

I built Harness Creator after repeatedly running into the same configuration problem: the hard part was not writing another `CLAUDE.md`, but deciding where each project need should live.

It audits the repository and existing Claude Code setup, interviews the user about goals and non-negotiable constraints, routes each need to an appropriate layer, generates only the approved components, and validates their structure.

Possible layers include `CLAUDE.md`, scoped rules, skills, hooks and permissions, agents, workflows, and a persisted `.claude/harness-spec.md`. The design rule is:

> Complete does not mean every layer. It means every identified need has a deliberate home, and no layer is generated without a reason.

Structural validation checks schemas, paths, references, hooks, permissions, imports, drift, and always-loaded context budget. It does not claim to prove Claude's behavior in every task; hook tests and optional consent-gated E2E scenarios are separate evidence.

GitHub: https://github.com/tjdwls101010/Harness-Creator

skills.sh: https://www.skills.sh/tjdwls101010/harness-creator/harness-creator

MIT licensed. Independent project; not an Anthropic product or endorsement. I am the maintainer, and I would especially value feedback on the layer-routing model and where the interview feels too long.

## Future feed-post variant

Keep this version for a later feed submission only if the account meets the current karma requirement and the subreddit still permits the format.

### Title

I built an interview-driven harness creator for Claude Code — it audits first, then generates only justified layers

### Body

I kept running into the same Claude Code configuration problem: the hard part was not writing another `CLAUDE.md`. It was deciding where each project need should live.

A fact needed in most sessions may belong in `CLAUDE.md`. A path-specific convention may belong in a scoped rule. A reusable procedure may be better as a skill. A boundary that must not fail may need a hook, permission, or test instead of stronger prose.

I built **Harness Creator**, an open-source Claude Code plugin and skill that works through that decision with you rather than starting from a fixed template.

Its workflow is:

1. **Audit** the repository and any existing Claude Code setup.
2. **Interview** the user about goals, pain points, and non-negotiable constraints.
3. **Route** every identified need to a deliberate Claude Code layer.
4. **Generate** only the components approved in the spec.
5. **Validate** deterministic structure, then offer separate hook testing and optional behavioral E2E evidence.

The seven possible layers are `CLAUDE.md`, rules, skills, hooks and permissions, agents, workflows, and `.claude/harness-spec.md`. A project can use any subset.

The main design rule is:

> Complete does not mean every layer. It means every identified need has a deliberate home, and no layer is generated without a reason.

The generated spec records the behavior inventory, selected layer, rationale, status, and validation evidence. That makes later `extend`, `improve`, and `sync` runs a comparison against approved intent rather than a fresh guess.

The validation boundary is intentionally explicit. Structural validation checks schemas, paths, references, hooks, permissions, imports, drift, and always-loaded context budget. It does **not** claim to prove that Claude will behave correctly in every future task. Hook tests and consent-gated E2E scenarios provide different, narrower kinds of evidence.

Recommended Claude Code plugin installation:

```bash
claude plugin marketplace add tjdwls101010/Harness-Creator
claude plugin install harness-creator@harness-creator
```

Then run:

```text
/harness-creator:harness-creator
```

GitHub: https://github.com/tjdwls101010/Harness-Creator

skills.sh: https://www.skills.sh/tjdwls101010/harness-creator/harness-creator

The project is MIT licensed and independent; it is not an Anthropic product or endorsement.

I would especially value feedback on three things:

- Does the layer-routing model match how you configure Claude Code today?
- Where would the interview feel too long or ask for information the repository already contains?
- Which structural checks or hook-test cases would make the result easier to trust?

Disclosure: I am the maintainer of Harness Creator.

### Alternate titles

- How should a Claude Code project choose between CLAUDE.md, rules, skills, hooks, agents, and workflows?
- I open-sourced a Claude Code tool that interviews you before generating a project harness

## Pre-publish checklist

- Use the Megathread comment path while the account is below the feed-post karma threshold.
- Confirm the [Megathread](https://www.reddit.com/r/ClaudeAI/comments/1sly3jm/built_with_claude_project_showcase_megathread/) remains open and still accepts project comments.
- Confirm the GitHub and skills.sh links resolve.
- Capture the pre-channel metrics snapshot before commenting.
- Do not publish before the distribution plan's Reddit timing gate opens unless the maintainer explicitly changes that plan.
- Do not request votes, imply Anthropic affiliation, or add unsupported performance claims.
- After publishing, record the comment permalink, time, metrics snapshot, and qualitative feedback in `metrics-log.md`.
