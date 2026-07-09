# Concepts

This page is the mental model. If you read only one wiki page before using harness-creator, read this one.

## What is a harness?

> **`ai-agent = ai-model + ai-harness`**

An AI agent is two things: the **model** (Claude's raw intelligence, which you don't control) and the **harness** (everything around it that shapes how it behaves in a specific project). The harness is made of seven kinds of thing in Claude Code:

- **`CLAUDE.md`** — advisory project context, injected every session
- **rules** — the same, but scoped to part of the file tree
- **skills** — procedures and knowledge that load on demand
- **hooks** — deterministic code that fires on lifecycle events
- **permissions** — hard allow/deny rules the client enforces
- **agents** — context-isolated subagents with their own tools and prompt
- **workflows** — fixed-shape multi-agent orchestrations

A harness is not a config file. It's the difference between Claude re-deriving your build command every session and Claude just knowing it; between Claude occasionally editing a file it should never touch and Claude being *unable* to; between a vague "please write tests" and a hook that won't let the turn end until they pass.

## Why building one by hand is hard

Two reasons.

**First, the mechanics are full of traps.** A representative sample of things that are true, non-obvious, and change what you'd write:

- A hook that exits `1` does **not** block anything — only exit `2` blocks. This inverts normal Unix convention and is the single most common hook mistake.
- A hook matcher containing any character outside a small set silently becomes an *unanchored regex* — so `Edit.*` also matches `NotebookEdit`.
- The built-in `Explore` and `Plan` subagents don't load `CLAUDE.md` at all, so your rules never reach them.
- An `@path` import in `CLAUDE.md` expands at launch and saves **no** context — it's not lazy-loading.
- A project's `allow` permission rules only take effect after the workspace is trusted.

None of these are guessable. You learn them by being burned. A harness built without them looks fine and quietly fails.

**Second, you have to ask the right questions about your own project** — what Claude keeps getting wrong here, what must never happen, how skilled the team is — and then make a judgment call about *where each answer belongs*. That judgment is the actual skill, and it's what harness-creator is built around.

## The core judgment: layer routing

Every requirement you have maps to exactly one layer, and picking the wrong layer is the most common way a harness underperforms. harness-creator makes the choice with three questions:

1. **Enforced or advisory?** Is it fine if Claude *usually* gets this right, or must it *never* fail? Advisory things go in prose (`CLAUDE.md`, rules, skills). Things that must never fail go in code (hooks + permissions), because prose has no enforcement power — a model can and occasionally will deviate from it.
2. **When does it need to load?** Every session → `CLAUDE.md`. Only in one part of the tree → a rule. Only when a specific job comes up → a skill. Only on a lifecycle event → a hook.
3. **What does it cost?** `CLAUDE.md` is paid on every request. A skill's description competes in a shared budget. A hook costs nothing until it produces output. An agent costs a routing decision every time it merely exists as an option.

A single requirement often splits across layers. "Always run tests before committing" becomes a **hook** (the guarantee) *plus* a one-line `CLAUDE.md` note explaining why that hook exists (so a block doesn't read as a mysterious failure). The full framework, with a routing table, is in **[The Layer-Routing Framework](Layer-Routing.md)**.

## The design philosophy (why the skill is written the way it is)

harness-creator generates harnesses, and it holds the harnesses it generates — and itself — to the same standard. These principles are the standard.

### Principle over rule ("conviction over compliance")

A rule tells the model *what* to do; a principle convinces it *why*. A convinced model handles the case its author never imagined — the sixteenth case that no rule enumerated. So every instruction is written as **what + a convincing why + a concrete picture**, and the litmus test is: *could a capable model re-derive this rule from the why alone?* If yes, it's a principle. If it only works for the cases you happened to list, it's a rail, and it will snap.

### Don't write what the model already knows

Re-teaching a capable model general coding sense doesn't just waste tokens — it buries the content that matters and signals distrust. The highest-value content is the **gotcha**: a domain trap that can't be derived from general competence, only learned by failing at it once. A harness built from generic preferences and no gotchas isn't worth generating.

### Progressive disclosure is an optimum, not a direction

Splitting content across files has a real cost: every file is a routing decision handed to a future reader. Split along a seam the reader recognizes instantly (which cloud provider? which template?) and the choice is obvious. Shatter the same material into topic-named fragments and the reader loads the wrong one, or doesn't know a needed one exists — a *silent* failure. So the split axis is **invocation pattern, not volume**. A file crossing some line count is not a reason to split it.

### Enforcement in code, advice in prose

`CLAUDE.md` is not a system prompt — it's advisory text injected after the system prompt, with no enforcement guarantee. Anything that must hold with zero exceptions is routed to a hook (deterministic) paired with a permission rule (client-enforced). Prose steers; code enforces. Confusing the two is how harnesses ship guarantees that aren't guarantees.

### Scripts are parameterized tools, not frozen snippets

A bundled script earns its place only if the model can compose with it — a CLI that takes arguments, not a one-shot snippet hard-coded for a single case. The four tools harness-creator ships are all parameterized CLIs for exactly this reason.

## How these ideas show up in practice

When harness-creator interviews you, it's applying "don't write what the model knows" (it won't ask about things it can read from your `package.json`). When it proposes a hook *and* a `CLAUDE.md` line for one requirement, it's applying "enforcement in code, advice in prose." When it keeps its own `SKILL.md` short and defers detail to reference files loaded per-component, it's applying progressive disclosure to itself. The skill practices what it generates.

## Next

- See the routing decision in full: **[The Layer-Routing Framework](Layer-Routing.md)**
- See the seven layers concretely: **[Generated Components](Generated-Components.md)**
- Just run it: **[Getting Started](Getting-Started.md)**
