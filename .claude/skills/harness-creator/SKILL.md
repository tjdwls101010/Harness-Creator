---
name: harness-creator
description: >
  Design, generate, validate, and maintain a complete Claude Code harness
  (CLAUDE.md, rules, skills, hooks, permissions, agents, workflows) for a project
  through a structured interview. Use when the user wants to create or set up a
  harness / CLAUDE.md / skills / hooks for a project, improve or extend an
  existing .claude/ setup, or asks how Claude should be configured to work on
  their codebase. Also triggers on Korean requests like "하네스 만들어줘",
  "하네스 구성해줘", "클로드 세팅해줘".
---

# harness-creator

## What a harness is, and what this skill does

`ai-agent = model + ai-harness`. A harness — CLAUDE.md, rules, skills, hooks, permissions, agents, workflows — is the layer that adds capability to a model without touching its judgment. A good one tells Claude what this project needs and why, then gets out of the way; a bad one either says nothing (so Claude re-derives the same context every session) or tries to hard-code every case (so Claude fights the harness the moment reality doesn't match what its author anticipated).

This skill runs the loop that builds one: audit what already exists, interview the user until their goals are concrete component specs, generate the components, validate them mechanically, and offer deeper end-to-end testing. It never guesses at requirements it could instead ask about, and it never declares a harness done until `validate_harness.py` says so.

## Operating loop

```
Invocation
 └─ Phase 0. Audit (always, before anything else)
     ├─ python "${CLAUDE_SKILL_DIR}/scripts/audit_harness.py" --path . → existing component inventory
     ├─ check .claude/harness-spec.md
     ├─ scout the codebase (build system, language, test runner, team-size signals)
     └─ branch: new / extend (new asks) / improve (fix existing problems) / sync (resolve spec-vs-disk drift)
        audit_harness.py's "suggested mode" is a hint, not a verdict — for extend vs. improve
        specifically, ask the user directly (see references/interview.md's re-entry variants).
 └─ Phase 1-N. Interview (load references/interview.md)
     └─ each stage ends by updating the spec, then a user approval gate
 └─ Generate (load references/<component>.md, only after the spec is approved)
     ├─ warn the user once that the first .claude/ write will prompt (protected path, see Hard lines)
     ├─ generate components (a large harness can fan out generation across a dynamic workflow — optional,
     │   see references/workflows.md for when that's worth it vs. just writing files directly)
     └─ python "${CLAUDE_SKILL_DIR}/scripts/validate_harness.py" --path . → fix until zero errors
 └─ Offer validation (load references/e2e-testing.md)
     ├─ hooks: scripts/test_hook.py — free, always recommend it
     └─ e2e: only with the user's consent (it spends real tokens) — compose a dynamic workflow on the
        spot from the spec's Validation scenarios, or fall back to sequential subagents if workflows
        aren't available
 └─ Wrap-up
     ├─ record what happened in the spec's Change history
     ├─ update CLAUDE.md's pointers if needed (never enumerate components — see references/claude-md-and-rules.md)
     └─ propose a commit
```

Flexibility (this loop is a map, not rails): skip a stage whose answer you already have, compress everything into one pass for a simple ask ("just a CLAUDE.md and two hooks"), and for "just build it" take the minimum needed to fill Goals and hard constraints before proceeding. The one thing that never gets skipped is the spec-approval gate — the spec is the record of what was agreed, and generating without it means there's nothing to audit against on the next invocation.

All script invocations in this skill and its references use `${CLAUDE_SKILL_DIR}/scripts/...` — never a bare relative path. The working directory is the target project, not this skill's own directory, and a plugin install runs these scripts from the plugin cache, not from a repo checkout — a relative path breaks in both cases.

## The layer-routing framework

This is the core judgment call the whole interview builds toward: for each thing the user wants, which layer should hold it? Get this table into muscle memory — everything else in this skill exists to help you fill in one row of it correctly.

| What it is | Layer | Why |
|---|---|---|
| A project fact or constraint relevant to nearly every request (build commands, an architecture decision, "this rule exists" notices) | CLAUDE.md | Loaded every session. Past ~200 lines, adherence drops — the bar for a line here is "does literally every session need this." |
| A rule that only matters in one part of the tree (a migration convention under `src/db/**`) | `.claude/rules/*.md` + `paths:` glob | Loads only when a matching file is touched — keeps CLAUDE.md from bloating with things most sessions never need. |
| A procedure, domain playbook, or reference material needed only when a specific job comes up | skill | Triggers on `description`; body loads only then. This is a repeated-prompt turned into an on-demand asset. |
| Something that must happen (or never happen) every time, no exceptions | hook, paired with a `permissions` rule | Advisory layers have no enforcement power — a model can and occasionally will deviate. A hook fires deterministically regardless of what the model decides; pair it with a permission rule because a hook's own `if` filter is best-effort and fails open on unparseable input (see references/hooks.md). |
| A specific tool, command, or path that must be blocked or force-approved | `permissions.allow` / `permissions.deny` | Enforced by the client itself, independent of model behavior. |
| A context-hungry, read-heavy role where only the conclusion matters back in the main thread (research, review, QA) | `.claude/agents/*.md` | Isolates context and lets you restrict tools/system-prompt per role — but agent count is a real cost (see references/agents.md), generate only roles the interview actually demonstrated a need for. |
| An orchestration whose *shape* is fixed and repeats — same steps, only the arguments change, meant to be a one-button `/name` | `.claude/workflows/*.js` | Determinism is the point here. Keep it thin: skeleton in the script, judgment in the agent prompts (see references/workflows.md and D12). |
| Large parallel work whose shape is different every time it comes up | Natural-language guidance in CLAUDE.md/a skill ("fan this out with a workflow: find → verify → synthesize") | A fixed file for a variable-shaped task becomes a flexibility tax. On-the-fly composition, guided by a principle, beats a rigid template here. |

How to apply it, in three questions: **enforced or advisory** — is it fine if Claude usually gets it right, or must it never fail? The former is prose (CLAUDE.md/rules/skills), the latter is code (hooks/permissions). **When does it load** — every session, only on a path, only on demand, only on an event? That answer names the layer directly. **What does it cost** — CLAUDE.md content is paid every request, a skill's description sits in a shared listing budget (~1% of context), a hook costs nothing unless it produces output, an agent costs a routing decision every time it exists as an option. A single request often splits across layers: "always run tests before committing" is a hook (the guarantee) plus one CLAUDE.md line explaining why that hook exists (so a block doesn't read as confusing).

## Authoring philosophy

Conviction over compliance: every instruction you write into a generated component is what + a convincing why + a concrete picture, and the test is whether the why alone would let the model re-derive the rule and handle a case you didn't think to enumerate. A rule with no reason attached is a rail — it holds exactly the cases its author listed and snaps on the sixteenth one that wasn't. Don't write what a capable model already knows; the content that's actually worth its tokens is the **gotcha** — a domain trap nobody could have derived from general competence, only from having been burned by it once. Progressive disclosure is an optimum, not a default — split a file only when the model genuinely branches at that seam (which cloud provider, which template); splitting by volume alone produces a routing decision with no payoff and sometimes a silently-missed fragment. Numbers need their justification and their exception in the same breath. Every one of these threads is covered in depth, with the exact product-specific gotchas verified against primary sources, in `references/` — load the file for whatever component you're about to generate before you generate it, every time, even if you've generated that component type before in this session.

**No mid-sentence hard-wrapping.** Line breaks in every file you write — this skill's own files and everything you generate for a target project — fall only at sentence, list-item, or paragraph boundaries, never in the middle of a sentence to fit a column width. Hard wraps break a future Edit tool's exact-string matching and pollute diffs; renderers soft-wrap on their own, so there's no display benefit to doing it manually.

## Interview protocol, summarized

Five stages for a fresh build: goals & pain points → behavior inventory → layer routing → component detail → validation plan, each ending in an update to `.claude/harness-spec.md` and a gate. Re-entry (extend/improve/sync) shrinks or reframes the early stages — full detail, the exact AskUserQuestion operating rules, worked example questions, and the spec template are in `references/interview.md`; load it before Phase 1 of any invocation. Two operating rules worth internalizing here because they shape every stage: use AskUserQuestion for convergence among options you already know, and ordinary conversation for divergence (goals, pain points) where the option space isn't known yet — and never ask a question whose answer the codebase already shows you; state the finding instead.

## Scripts

All four live in `scripts/` and are plain-argument Python 3.10+ CLIs (stdlib only) — call them with `${CLAUDE_SKILL_DIR}/scripts/<name>.py`, not a bare relative path.

| Script | Run it when | Signature |
|---|---|---|
| `audit_harness.py` | Always, first, before any interview | `--path <target-repo> [--json]` |
| `validate_harness.py` | Immediately after generating or editing any component | `--path <target-repo> [--json] [--strict]` |
| `test_hook.py` | Right after generating any hook, before calling it delivered | `--settings <path> --event <Event> [--tool <Tool>] [--input-field k=v ...]` or `--command <script> --event <Event> [--input <file>]`, plus `--matrix` for match-only inspection |
| `run_e2e.py` | Only with explicit user consent, during the validation stage | `--project <path> --prompt "..." [--model] [--timeout] [--out] [--isolate]` |

`run_e2e.py`'s headless permission handling is a documented best guess (`--isolate` + `--dangerously-skip-permissions`), not empirically confirmed — see references/e2e-testing.md before the first real run and say so to the user.

## Hard lines

1. **Never advertise a component you haven't actually generated.** Every pointer this skill or its output writes — a reference to a script, a skill, a file — must resolve to a real file. `validate_harness.py` checks this mechanically; that check existing is not a substitute for you checking it yourself before claiming a component is done.
2. **A generated harness is not finished until `validate_harness.py` exits 0 (errors).** A checklist that isn't mechanically enforced doesn't get enforced — this is the direct fix for the failure mode a prior harness-generation project (referred to internally as revfactory) fell into: a review checklist that existed on paper and was never actually run.
3. **`.claude/harness-spec.md` and the actual files must never drift apart silently.** Every generation or edit updates the spec in the same pass; `audit_harness.py`'s drift check exists to catch the times this slips, not to be the only thing keeping them in sync.
