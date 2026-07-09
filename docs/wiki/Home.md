# harness-creator — Handbook

Welcome. This handbook explains what harness-creator is, the ideas behind it, and how to use it for your own projects.

> **New here?** Read [Concepts](Concepts.md) for the mental model, then [Getting Started](Getting-Started.md) to run it.

harness-creator is a meta-skill for [Claude Code](https://claude.com/claude-code). Given a project, it runs a structured interview and then designs, generates, validates, and maintains a complete **harness** for it — the `CLAUDE.md`, rules, skills, hooks, permissions, agents, and workflows that shape how Claude works in that repo.

The guiding equation:

> **`ai-agent = ai-model + ai-harness`**

You can't change the model. The harness is the part you *can* shape — and building a good one by hand takes a lot of hard-won knowledge about how Claude Code actually behaves. harness-creator packages that knowledge and the interview that turns your goals into concrete components.

## Pages

### Understand it
- **[Concepts](Concepts.md)** — what a harness is, and the design philosophy behind the skill
- **[The Layer-Routing Framework](Layer-Routing.md)** — the core decision: which layer holds each thing you want
- **[Generated Components](Generated-Components.md)** — the seven layers, in detail

### Use it
- **[Getting Started](Getting-Started.md)** — install and your first run
- **[The Interview & Spec](The-Interview.md)** — how the staged conversation works
- **[Re-entry Modes](Re-entry-Modes.md)** — new / extend / improve / sync
- **[Validation & Testing](Validation.md)** — how a generated harness is checked
- **[The Scripts](Scripts.md)** — the four command-line tools you (and the skill) can run

### Go deeper
- **[Architecture & Internals](Architecture.md)** — how the repo is wired, packaging, and how it dogfoods itself
- **[FAQ & Troubleshooting](FAQ.md)** — limitations, caveats, and fixes

## A note on how this project is written

Every file here follows a few deliberate rules: explain *why* a choice is good rather than just listing rules, spend words on the non-obvious gotchas instead of what a capable reader already knows, and keep enforcement in code while keeping advice in prose. If a page feels dense, that's on purpose — the density is around the things that actually change what you build. The full design rationale and the research behind each gotcha live in [`docs/plan/`](../plan/) in the repository.
