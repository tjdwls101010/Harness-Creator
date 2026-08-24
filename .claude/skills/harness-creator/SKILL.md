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

`ai-agent = ai-model + ai-harness`. A harness — CLAUDE.md, rules, skills, hooks, permissions, agents, workflows — adds capability to a model without touching its judgment. A bad one either says nothing (so Claude re-derives the same context every session) or hard-codes every case (so Claude fights it the moment reality doesn't match what its author anticipated).

This skill runs the loop that builds one: audit, interview until goals are concrete component specs, generate, validate mechanically, offer end-to-end testing. It never guesses at a requirement it could ask about, and never declares a harness done until `validate_harness.py` says so.

## Operating loop

```
Invocation
 └─ Phase 0. Audit (always, before anything else)
     ├─ python "${CLAUDE_SKILL_DIR}/scripts/audit_harness.py" --path . → existing component inventory
     ├─ check .claude/harness-spec.md
     ├─ scout the codebase (build system, language, test runner, team-size signals) and, if it
     │   exists, read this project's auto-memory MEMORY.md — it's the most honest record of what
     │   Claude has repeatedly needed here, so it's interview material, not a component to track
     └─ branch on mode. audit_harness.py's "suggested mode" is a hint, not a verdict: it can tell
        new from not-new, but extend and improve look identical on disk, so ask the user directly.
        The mode picks the opening question, not a different file.
 └─ Phase 1-N. Interview (load references/interview.md, which covers all four modes; sync alone
   │  runs no stages, only the drift list the audit above produced)
     ├─ each stage ends by updating the spec, then a user approval gate
     └─ behavior inventory specifically: skill count is a real cost (see the layer-routing table below) —
        weigh consolidation into the inventory decision itself, not as an afterthought once Generate starts
 └─ Generate (load references/<component>.md for EVERY component type in this pass — an agent, a workflow,
   │  and a skill in one pass means three separate reference loads, never one file's principles stretched
   │  by analogy over another component type — only after the spec is approved)
     ├─ warn the user once that the first .claude/ write hits a protected path: it prompts in most modes
     │   and is refused outright under dontAsk, and no allow rule can pre-approve it (see the protected
     │   paths section in references/hooks.md)
     ├─ generate components (a large harness can fan out generation across a dynamic workflow — optional,
     │   see references/workflows.md for when that's worth it vs. just writing files directly)
     ├─ python "${CLAUDE_SKILL_DIR}/scripts/validate_harness.py" --path . → fix until zero errors
     └─ any hook generated OR wired this pass (a new hook script, or a settings.json edit that points at
        one) → python "${CLAUDE_SKILL_DIR}/scripts/test_hook.py" must pass first (see references/hooks.md).
        validate_harness.py cannot check this for you — it has no way to know a hook was exercised
 └─ Offer validation (load references/e2e-testing.md)
     └─ e2e: only with the user's consent (it spends real tokens) — compose a dynamic workflow on the
        spot from the spec's Validation scenarios, or fall back to sequential subagents if workflows
        aren't available
 └─ Wrap-up (in this order — the validation has to come after the edits it's meant to check)
     ├─ record what happened in the spec's Change history
     ├─ update CLAUDE.md's pointers if needed (never enumerate components — see references/claude-md-and-rules.md);
     │   if this changes what harness-spec.md should say, fold it back into the Change-history update
     ├─ python "${CLAUDE_SKILL_DIR}/scripts/validate_harness.py" --path . → one more whole-harness
     │   pass, because the two bullets above edit files this lints. Fix what it finds first.
     └─ propose a commit
```

This loop is a map, not rails: skip a stage whose answer you already have, and compress the whole thing into one pass for a simple ask. The spec-approval gate is the one step that never gets skipped — without it there's nothing to audit against next time.

## The layer-routing framework

The core judgment call the whole interview builds toward: for each thing the user wants, which layer should hold it? Everything else in this skill exists to help you fill in one row of this table correctly.

| What it is | Layer | Why |
|---|---|---|
| A project fact or constraint relevant to nearly every request (build commands, an architecture decision, "this rule exists" notices) | CLAUDE.md | Loaded every session. Past ~200 lines, adherence drops — the bar for a line here is "does literally every session need this" (see references/claude-md-and-rules.md). |
| A rule that only matters in one part of the tree (a migration convention under `src/db/**`) | `.claude/rules/*.md` + `paths:` glob | Loads only when a matching file is touched — keeps CLAUDE.md from bloating with things most sessions never need (see references/claude-md-and-rules.md). |
| A procedure, domain playbook, or reference material needed only when a specific job comes up | skill | Triggers on `description`; body loads only then. This is a repeated-prompt turned into an on-demand asset — but skill count is a real cost (see references/skills.md), so consolidate related behaviors during the interview rather than defaulting to one skill per requested behavior. |
| Something that must happen (or never happen) every time, no exceptions | hook, paired with a `permissions` rule | Advisory layers have no enforcement power — a model can and occasionally will deviate. A hook fires deterministically regardless of what the model decides; pair it with a permission rule because a hook's own `if` filter is best-effort and fails open on unparseable input (see references/hooks.md). |
| A specific tool, command, or path that must be blocked or force-approved | `permissions.allow` / `permissions.deny` | Enforced by the client itself, independent of model behavior (see the permissions section in references/hooks.md). |
| A context-hungry, read-heavy role where only the conclusion matters back in the main thread (research, review, QA) | `.claude/agents/*.md` | Isolates context and lets you restrict tools/system-prompt per role — but agent count is a real cost (see references/agents.md), generate only roles the interview actually demonstrated a need for. |
| An orchestration whose *shape* is fixed and repeats — same steps, only the arguments change, meant to be a one-button `/name` | `.claude/workflows/*.js` | Determinism is the point here. Keep it thin: skeleton in the script, judgment in the agent prompts (see references/workflows.md). |
| Large parallel work whose shape is different every time it comes up | Natural-language guidance in CLAUDE.md/a skill ("fan this out with a workflow: find → verify → synthesize") | A fixed file for a variable-shaped task becomes a flexibility tax. On-the-fly composition, guided by a principle, beats a rigid template here. |

How to apply it, in four questions:

- **Enforced or advisory** — is it fine if Claude usually gets it right, or must it never fail? The former is prose (CLAUDE.md/rules/skills), the latter is code (hooks/permissions).
- **When does it load** — every session, only on a path, only on demand, only on an event? That answer names the layer directly.
- **Who needs it, and who writes it** — every clone or only this machine; you or Claude at runtime? A fact only this developer needs goes in `CLAUDE.local.md` (gitignored, deterministic, theirs), not in the CLAUDE.md their whole team pays for.
- **What does it cost** — the always-loaded bill is CLAUDE.md *plus* every rule without `paths:` *plus* every `@import` expanded *plus* the first 200 lines of auto memory's `MEMORY.md`, all paid on every request; a skill's description sits in a shared listing budget (~1% of context); a hook costs nothing unless it produces output; an agent costs a routing decision every time it exists as an option.

A single request often splits across layers: "always run tests before committing" is a hook (the guarantee) plus one CLAUDE.md line explaining why that hook exists (so a block doesn't read as confusing).

## Authoring philosophy

Conviction over compliance: every instruction you write into a generated component is what + a convincing why + a concrete picture, and the test is whether the why alone would let the model re-derive the rule and handle a case you didn't think to enumerate. A rule with no reason attached is a rail — it holds exactly the cases its author listed and snaps on the sixteenth one that wasn't.

Don't write what a capable model already knows; the content that's actually worth its tokens is the **gotcha** — a domain trap nobody could have derived from general competence, only from having been burned by it once. The same filter runs on the why: keep the clause that makes the rule re-derivable, cut the sentences that argue for it. Conviction is whether a reason is present, not how far it runs, and the sentences doing the talking bury the gotcha beside them. The shapes that go: restating the claim you just made, arguing for it, spelling out a consequence the reader computes anyway, giving the negative case equal weight when the positive implies it, and narrating what the next paragraph is about to do.

Progressive disclosure is an optimum, not a default — the seam that pays is one where the model genuinely branches (which cloud provider, which template, which mode), because then each invocation reads one file instead of all of them. Volume alone is a weaker reason but not a non-reason: official guidance is to keep a SKILL.md under 500 lines and move detailed reference material out, so a body that has outgrown that gets split even if the branch is soft. What never pays is splitting a file the model will always read in full anyway — that buys a routing decision with no saved reading, and sometimes a silently-missed fragment.

A reference does not have to be prose. A failing test, a schema, a rubric, or a function in another codebase pins a target more precisely than a paragraph describing it, in a language the model reads natively — and the runnable ones fail loudly when the target moves, where a paragraph just goes quietly stale. When the interview surfaces "here's what good looks like," ask whether the answer is a file that already exists.

Numbers need their justification and their exception in the same breath. Every one of these threads is covered in depth in `references/` — load the file for whatever component you're about to generate before you generate it, every time, even if you've generated that component type before in this session.

**Prefer an interface over an instruction where one exists.** Some behaviors don't need to be told to Claude at all — the thing Claude operates can be shaped so the wrong move isn't available. An interface is re-read from the tool's own signature on every use: every session, after every compaction, inside every subagent, including the ones that skip CLAUDE.md entirely. The harness's own interface surfaces are a bundled script's CLI, a hook script's configuration input, a workflow's `args`, a skill's `description`, an agent's `tools:`. The design lever is the parameter space: an argument that can only take three named values teaches the three cases by existing. This is also the strongest compression available: prose moved into a signature is not shortened, it is relocated to a surface that is re-read for free. The boundary runs both ways, and it splits on ownership: the tool owns what is *valid*, what it does, and what it prints; the project owns when to reach for it, what it costs, and why it was chosen. Neither side restates the other. **If editing the tool would make the sentence false, the sentence belongs in the tool.** `--help` cannot drift from the code that emits it; a summary of `--help` can, and is the copy nothing checks. This applies to what the harness contains; this skill designs harnesses, not the project's application code.

A check's failure message is an interface too — read at exactly the moment it matters, free otherwise. Where a rule is mechanically detectable, state the decision in prose and let the check's own output carry the consequence, instead of paying for both on every load. A pointer inherits its target's reader, so it moves who pays rather than whether.

**No mid-sentence hard-wrapping.** Line breaks in every file you write fall only at sentence, list-item, or paragraph boundaries, never in the middle of a sentence to fit a column width. Hard wraps break a future Edit tool's exact-string matching and pollute diffs; renderers soft-wrap on their own, so there's no display benefit to doing it manually.

Two interview rules shape every stage, so they live here rather than in the file that branches: use AskUserQuestion for **convergence** among options you already know, and ordinary conversation for **divergence** (goals, pain points) where the option space isn't known yet. And never ask a question the codebase already answers — state the finding instead.

## Scripts

All five live in `scripts/` and are plain-argument Python 3.10+ CLIs (stdlib only). Always invoke them as `${CLAUDE_SKILL_DIR}/scripts/<name>.py`: the working directory is the target project, and a plugin install runs them from the plugin cache, so a relative path breaks in both cases. `${CLAUDE_SKILL_DIR}` is substituted in this skill's own markdown and in `allowed-tools` rules — **not** inside a workflow's prompt strings or a subagent's shell environment, where it expands to nothing. Resolve it to an absolute path before passing it anywhere else.

Their flags are not listed here. Read a script's `--help` the first time you reach for it in a session — every argument carries a `help=`.

| Script | Run it when |
|---|---|
| `audit_harness.py` | Always, first, before any interview |
| `validate_harness.py` | Immediately after generating or editing any component |
| `hook_event.py` | Once you know which event you're targeting, instead of reading all thirty |
| `test_hook.py` | Right after generating any hook, before calling it delivered |
| `run_e2e.py` | Only with explicit user consent, during the validation stage |

`validate_harness.py` checks structural integrity and prints the always-loaded budget, but it cannot grade a skill's `description` for trigger quality or near-miss overlap with sibling skills. Re-read every description you generate against references/skills.md before calling it done — including a lone new skill, not just a batch.

`run_e2e.py`'s docstring records when its headless permission handling was last confirmed and on what; auth is per-machine, so read references/e2e-testing.md before the first run in a new environment.

## Hard lines

1. **Never advertise a component you haven't actually generated.** Every pointer this skill or its output writes — a reference to a script, a skill, a file — must resolve to a real file. `validate_harness.py` catches the ones written with a `references/` or `scripts/` prefix; a bare filename, or a name in any other shape, is invisible to it. The check is a floor, not a substitute for looking.
2. **A generated harness is not finished until `validate_harness.py` exits 0 (errors), and a generated hook is not finished until `test_hook.py` passes against it.** A checklist that isn't mechanically enforced doesn't get enforced. Nothing can mechanically confirm you ran `test_hook.py`, so that one rests on you.
3. **`.claude/harness-spec.md` and the actual files must never drift apart silently.** Every generation or edit updates the spec in the same pass; `audit_harness.py`'s drift check exists to catch the times this slips, not to be the only thing keeping them in sync.
