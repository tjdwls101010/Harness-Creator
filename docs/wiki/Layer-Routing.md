# The Layer-Routing Framework

This is the core judgment the whole interview builds toward: for each thing you want, which layer should hold it? Every other decision in harness-creator exists to help fill one row of the routing table below correctly.

## The problem: right requirement, wrong layer

A harness is made of several layers — `CLAUDE.md`, rules, skills, hooks, permissions, agents, workflows (see [Generated Components](Generated-Components.md) for what each one is). Almost every requirement you have belongs in *exactly one* of them, and putting a requirement in the wrong layer is the single most common way a harness quietly underperforms.

The failure is never loud. Put a hard guarantee in `CLAUDE.md` and it reads as strong to a human ("never touch `legacy/`") but is mechanically just advisory text the model can deviate from. Put a session-wide fact in a skill and no session ever loads it when it needs it. Put a scoped convention in `CLAUDE.md` and it bloats the one file every request pays for. Each of these looks fine on disk and fails in a way you only notice later. Routing is the skill that prevents it.

## Three questions that route any requirement

For each behavior the interview surfaces, ask these in order. The answers name a layer directly.

1. **Enforced or advisory?** Is it fine if Claude *usually* gets this right, or must it *never* fail? The former is prose — `CLAUDE.md`, rules, skills. The latter is code — hooks and permissions. Prose has no enforcement power; a model can and occasionally will deviate from it.
2. **When does it load?** Every session → `CLAUDE.md`. Only in one part of the tree → a rule with a `paths:` glob. Only when a specific job comes up → a skill. Only on a lifecycle event → a hook.
3. **What does it cost?** `CLAUDE.md` content is paid on every request. A skill's `description` sits in a shared listing budget (~1% of context) whether or not the skill is ever used. A hook costs nothing unless it produces output. An agent costs a routing decision every time it merely exists as an option. Cheaper isn't better — but a requirement that doesn't justify its cost in the cheapest adequate layer probably doesn't belong in the harness at all.

## The routing table

Get this into muscle memory. Each row is one shape of requirement, the layer it routes to, and why.

| What you want to hold | Layer | Why this layer |
|---|---|---|
| A fact or constraint relevant to nearly every request — build commands, an architecture decision, a "this rule exists" notice | `CLAUDE.md` | Loaded every session. Past ~200 lines adherence drops, so the bar for a line here is "does literally every session need this." |
| A rule that only matters in one part of the tree — a migration convention under `src/db/**` | `.claude/rules/*.md` + a `paths:` glob | Loads only when a matching file is touched, keeping `CLAUDE.md` from bloating with things most sessions never need. |
| A procedure, domain playbook, or reference needed only when a specific job comes up | a skill | Triggers on its `description`; the body loads only then. Skill count is a real cost, so consolidate related behaviors rather than defaulting to one skill per requested behavior. |
| Something that must happen — or must never happen — every time, no exceptions | a hook, paired with a `permissions` rule | Advisory layers have no enforcement power; a model can and occasionally will deviate. A hook fires deterministically regardless of what the model decides; the permission rule is what actually can't be bypassed. |
| A specific tool, command, or path that must be blocked or force-approved | `permissions.allow` / `permissions.deny` | Enforced by the client itself, independent of model behavior. |
| A context-hungry, read-heavy role where only the conclusion matters back in the main thread — research, review, QA | `.claude/agents/*.md` | Isolates context and lets you restrict tools and system prompt per role. Agent count is a real cost — generate only roles the interview actually showed a need for. |
| An orchestration whose *shape* is fixed and repeats — same steps, only the arguments change, meant to be a one-button `/name` | `.claude/workflows/*.js` | Determinism is the point. Keep it thin: skeleton in the script, judgment in the agent prompts. |
| Large parallel work whose shape is different every time it comes up | Natural-language guidance in `CLAUDE.md` or a skill | A fixed file for a variable-shaped task becomes a flexibility tax; on-the-fly composition guided by a principle beats a rigid template. |

## Why enforcement has to be code, not prose

The first routing question carries the most weight, so it is worth being precise about *why* prose can never enforce.

`CLAUDE.md` content is delivered as a user message injected after the system prompt. It is not the system prompt, and Claude Code makes no enforcement guarantee about it — Claude reads it and tries to comply the same way it tries to comply with anything else in the conversation, and two contradictory instructions get resolved arbitrarily rather than by any override rule. This is why "always" and "never" language reads as strong to a human but is mechanically just advisory. Anything that must hold with zero exceptions — blocking a dangerous command, refusing to touch a path, guaranteeing a lint step runs — does not belong in this layer at all.

Enforcement lives in exactly two places, and they work as a pair:

- A **hook** fires deterministically on a lifecycle event regardless of what the model decides, and can hand back a rich feedback message so Claude can adapt its approach after being blocked.
- A **`permissions.deny` rule** is enforced by the client, holds even under `bypassPermissions` mode, and cannot be bypassed by model behavior.

Generate both for a "must never happen" item. The hook without the deny rule is a suggestion with good error messages — its own `if` filter is best-effort and fails open on input it can't parse. The deny rule without the hook is a hard wall with a generic client-side message. Together they give Claude both the wall and the explanation for why it hit the wall. (One nuance worth knowing: in auto permission mode a separate classifier reads your `CLAUDE.md` text directly, so a prose prohibition there measurably steers its decisions — but it is still not a guarantee on its own, which is why the deny rule is what does the actual work.)

## Worked examples

Routing is easier to feel than to state. Three requirements, run through the three questions.

### "Always run tests before committing" — splits across layers

Enforced or advisory? This must never fail, so it routes to **code**. The guarantee is a hook — a `Stop`-time gate that runs the suite and keeps the turn going with a `decision: "block"` until tests pass (guarded against infinite looping by reading `stop_hook_active`). But a bare block reads as a mysterious failure, so add **one** `CLAUDE.md` line explaining that the hook exists and why. That single requirement now lives in two layers: the hook is the enforcement, and the prose line is the explanation so the block isn't confusing. This split — a guarantee in code plus a one-line note in prose — is the canonical shape, not an exception.

### "Never let Claude touch `.env`" — hook plus permission deny

A protected path is a textbook "must never happen every time." Route it to a hook (for the adaptive feedback message) *and* a matching deny rule (for the guarantee):

```json
{
  "permissions": {
    "deny": ["Edit(.env)", "Read(.env)"]
  }
}
```

Two things to know here. First, an `Edit` deny rule also governs `Write` and `NotebookEdit`, so one rule covers the whole file-mutating family — no need for three. Second, blocking *reads* needs the `Read` deny rule specifically, not a `PreToolUse(Read)` hook: when a user types `@.env` in a prompt, Claude Code inlines the file's contents while building the prompt with no `Read` tool call at all, so a read-gating hook never fires — but the deny rule applies to `@`-references directly. This is exactly the kind of routing choice a prose "please don't read `.env`" line cannot make.

### A migration convention that only applies under `src/db/**` — a scoped rule

Advisory this time — it steers behavior, it doesn't guarantee anything — so it stays in **prose**. But it only matters when someone is editing database migrations, and paying for it in `CLAUDE.md` on every unrelated request is waste. That answers question 2: a `.claude/rules/*.md` file with a `paths: ["src/db/**"]` glob, which loads only when a matching file is touched. The `paths:` frontmatter is load-bearing — a rule file without it loads at launch with the same priority as `CLAUDE.md` itself, so you'd have paid the cost you were trying to avoid.

## See also

- **[Generated Components](Generated-Components.md)** — what each of the seven layers actually is
- **[The Interview & Spec](The-Interview.md)** — how routing decisions get made and recorded, stage by stage
- **[Concepts](Concepts.md)** — the mental model this framework sits inside

The full design rationale behind these routing rules lives in [`docs/plan/`](../plan/), the design-rationale record.
