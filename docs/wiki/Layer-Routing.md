# The Layer-Routing Framework

This is the core judgment the whole interview builds toward: for each thing you want, which layer should hold it? Every other decision in harness-creator exists to help fill one row of the routing table below correctly.

## The problem: right requirement, wrong layer

A harness is made of several layers — `CLAUDE.md`, rules, skills, hooks, permissions, agents, workflows (see [Generated Components](Generated-Components.md) for what each one is). Almost every requirement you have belongs in *exactly one* of them, and putting a requirement in the wrong layer is the single most common way a harness quietly underperforms.

The failure is never loud. Put a hard guarantee in `CLAUDE.md` and it reads as strong to a human ("never touch `legacy/`") but is mechanically just advisory text the model can deviate from. Put a session-wide fact in a skill and no session ever loads it when it needs it. Put a scoped convention in `CLAUDE.md` and it bloats the one file every request pays for. Each of these looks fine on disk and fails in a way you only notice later. Routing is the skill that prevents it.

## Four questions that route any requirement

For each behavior the interview surfaces, ask these in order. The answers name a layer directly.

1. **Enforced or advisory?** Is it fine if Claude *usually* gets this right, or must it *never* fail? The former is prose — `CLAUDE.md`, rules, skills. The latter is code — hooks and permissions. Prose has no enforcement power; a model can and occasionally will deviate from it.
2. **When does it load?** Every session → `CLAUDE.md`. Only in one part of the tree → a rule with a `paths:` glob. Only when a specific job comes up → a skill. Only on a lifecycle event → a hook.
3. **Who needs it, and who writes it?** Every clone of the repo, or only this one machine? Written by a person, or by Claude at runtime? A fact only one developer needs — a local port number, a personal shortcut — belongs in `CLAUDE.local.md` (gitignored, deterministic, theirs alone), not in the shared `CLAUDE.md` every teammate pays to load. This is also where auto memory's `MEMORY.md` gets ruled *out* as a destination: it's advisory and non-deterministic ("Claude doesn't save something every session — it decides what's worth remembering"), so anything the developer needs to be reliably present does not belong there.
4. **What does it cost?** The always-loaded bill is `CLAUDE.md` *plus* every rule without `paths:` *plus* every `@import` expanded *plus* the first 200 lines of auto memory's `MEMORY.md` — all paid on every request. A skill's `description` sits in a shared listing budget (~1% of context) whether or not the skill is ever used. A hook costs nothing unless it produces output. An agent costs a routing decision every time it merely exists as an option. Cheaper isn't better — but a requirement that doesn't justify its cost in the cheapest adequate layer probably doesn't belong in the harness at all.

## The routing table

The full table — one row per layer, with the "why this layer" reasoning — lives in a single place now: `SKILL.md`'s **"The layer-routing framework"** section, in [`.claude/skills/harness-creator/SKILL.md`](../../.claude/skills/harness-creator/SKILL.md). It used to be duplicated here (and a third time in `docs/plan/02-skill-design.md`), and the three copies drifted out of sync with each other — this page and `SKILL.md` disagreed about which layer's guarantee survives `bypassPermissions` mode. Rather than re-fix three copies every time the routing logic changes, this page now points at the one that's actually loaded into every session and therefore has to stay correct: `SKILL.md` itself.

In short, the layers it routes to are `CLAUDE.md`, `CLAUDE.local.md`, `.claude/rules/*.md`, skills, hooks (paired with a permission rule), `permissions.allow`/`permissions.deny`, `.claude/agents/*.md`, `.claude/workflows/*.js`, and — for large, variable-shaped parallel work — natural-language fan-out guidance instead of a fixed file. Read `SKILL.md` for the reasoning behind each.

## Why enforcement has to be code, not prose

The first routing question carries the most weight, so it is worth being precise about *why* prose can never enforce.

`CLAUDE.md` content is delivered as a user message injected after the system prompt. It is not the system prompt, and Claude Code makes no enforcement guarantee about it — Claude reads it and tries to comply the same way it tries to comply with anything else in the conversation, and two contradictory instructions get resolved arbitrarily rather than by any override rule. This is why "always" and "never" language reads as strong to a human but is mechanically just advisory. Anything that must hold with zero exceptions — blocking a dangerous command, refusing to touch a path, guaranteeing a lint step runs — does not belong in this layer at all.

Enforcement lives in exactly two places, and they work as a pair — and, worth knowing precisely, both of them individually hold even under `bypassPermissions` mode, the strongest permission mode available:

- A **hook** fires deterministically on a lifecycle event regardless of what the model decides, and can hand back a rich feedback message so Claude can adapt its approach after being blocked. A `PreToolUse` hook that exits `2` blocks the tool call *before* Claude Code ever evaluates permission rules — so this one holds under `bypassPermissions` too, on its own, with no deny rule required.
- A **`permissions.deny` rule** is enforced by the client, holds even under `bypassPermissions` mode, and cannot be bypassed by model behavior.

Generate both anyway for a "must never happen" item — the hook without the deny rule is a suggestion with good error messages (its own `if` filter is best-effort and fails open on input it can't parse), and each is a single point of failure on its own. Together they give Claude both the wall and the explanation for why it hit the wall. The exact reference for this — including the reverse rule, that a hook's own `"allow"` can never override a deny rule from any scope — is `references/hooks.md` in the skill itself. (One nuance worth knowing: in auto permission mode a separate classifier reads your `CLAUDE.md` text directly, so a prose prohibition there measurably steers its decisions — but it is still not a guarantee on its own, which is why the hook/deny pair is what does the actual work.)

## Worked examples

Routing is easier to feel than to state. Three requirements, run through the four questions.

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
