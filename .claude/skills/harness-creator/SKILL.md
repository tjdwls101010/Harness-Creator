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

`ai-agent = ai-model + ai-harness`. A harness — CLAUDE.md, rules, skills, hooks, permissions, agents, workflows — adds capability to a model without touching its judgment. A bad one either says nothing (Claude re-derives the same context every session) or hard-codes every case (Claude fights it the moment reality differs from what its author anticipated).

This skill turns a request into an approved `.claude/harness-spec.md` and generates from it. The spec is the deliverable: files can be regenerated from a spec, but not the reverse, because files never record why a rule went to a hook instead of CLAUDE.md. A spec nobody approved is your guess wearing a template.

## How a pass runs

Each step consumes what the one before it produced; that is why the order is fixed. Audit first: `audit_harness.py`, the existing spec, a scout of the codebase (build system, test runner, team-size signals, directories that look dangerous to touch) and, if it exists, this project's auto-memory `MEMORY.md` answer questions you would otherwise ask and show which work must be preserved. Run `audit_harness.py --template` once, even on an existing spec, for its section guidance, then fill the spec in section order, nothing depending on a section the user has not approved — sections whose inputs are already settled can be approved together; the last approval marks the spec `approved`, generation's only input. The moment a component type becomes a candidate in routing, load its `references/<component>.md` (the eligibility tests that decide the route live there) and keep it through generation — one reference per component type, never one stretched over another — and read it again after a compaction, which re-attaches this file but summarizes a reference read away. Warn once before the first `.claude/` write: a protected path prompts in most modes, is refused under `dontAsk`, and no allow rule pre-approves it (references/hooks.md). Generate; `validate_harness.py` exit 0 is what finished means, and a hook is finished when `test_hook.py` passes against it — nothing can confirm you ran that one, so it rests on you. Offer e2e only as K14 says, loading references/e2e-testing.md then. Wrap up: record the pass in the spec's Change history and move the inventory rows whose reality changed — the spec and the files move in the same pass, and `audit_harness.py`'s drift check exists to catch the times that slips, not to be the only thing keeping them together — update CLAUDE.md's pointers if needed (never an inventory — references/claude-md-and-rules.md), run `validate_harness.py` once more because those edits touch files it lints, and leave a reviewable handoff in the form the target project's git conventions expect.

## What a harness engineer asks

Running a conversation is yours already. These are the questions only someone who has built harnesses brings, each with the reason that lets you re-derive it.

- **K1.** State as fact-plus-proposal what the audit, the spec, the codebase scout and `MEMORY.md` already answer; ask only what is left open and fills a spec cell — a question the repo answers spends the user's attention twice, one that fills no cell is decorative, and `MEMORY.md` is the most honest record of what Claude has repeatedly needed here.
- **K2.** On an empty repo ask for goals and pain points; on an existing harness ask whether the request adds a capability or repairs a behaviour — a repair arrives as a symptom, not a diagnosis; route it through the fix column — and in the same breath **what is now unnecessary** — a harness only grows and nothing on disk records what was used, so nobody asks unless you do; "nothing comes to mind" is a real answer.
- **K3.** The audit sees existence, not content. Read a file before overwriting it, and scope a return visit to the delta the user asked for — a teammate's edit to a skill body reads as zero drift.
- **K4.** On a return visit, keep every approved section the delta does not invalidate and re-approve only the sections whose inputs changed — reopening a settled decision adds no evidence and risks erasing a hand edit.
- **K5.** When the spec and the disk disagree, the spec is usually the one behind. Ask which side is right before regenerating a file — silently reverting a colleague's work is far worse than an unnecessary question — and record the outcome as what it was.
- **K6.** Record a declined candidate as a `declined` row with its one-line reason, and fold near-duplicate candidates at that moment — without the row the next pass re-proposes it and the user decides the same thing twice.
- **K7.** Fill the spec in dependency order and approve each section before the next depends on it. Keep "is this worth having" (inventory) apart from "where does it live" (routing) — different questions, and mixing them makes both harder to judge.
- **K8.** Propose the routing rather than deriving it silently, and surface every enforced-versus-advisory call to the user — that is the one judgment with a real cost when it is wrong.
- **K9.** Before routing anything to a hook, look for an interface that makes the wrong move unavailable — a signature is re-read on every call, in every subagent; a hook fires after Claude has already decided.
- **K10.** New `permissions.allow` entries get their own question, each rule named with what it grants — an allow rule removes a checkpoint the user has today and ships to every clone. Deny and ask rules only add friction and need no such question.
- **K11.** Ask once whether any of this must work beyond this repo, and record the answer in the spec — skills, agents, hooks and workflows can be packaged in a plugin; CLAUDE.md, rules and permissions have no portable form, so a harness leaning on them travels as a repo `.claude/` tree or not at all.
- **K12.** Ask what language the generated harness should be written in — it may differ from the language of the interview.
- **K13.** Diverge in conversation while the option space is unknown, converge with AskUserQuestion once it is, and make each option's description the reason to pick it rather than its label restated — that is what lets the user judge. Read the user's vocabulary from their first answer and keep speaking it — jargon they didn't bring, or mechanics they already know, tax the pace.
- **K14.** Offer e2e only after stating its cost and getting consent — roughly one full headless session per scenario, two to four scenarios by default, on the user's own model — it spends real tokens and time.
- **K15.** Ablate one rule at a time, as a proposal, starting with rules written to fight a model default — one fighting an old default reads exactly like one still needed; a clean run is evidence for retiring it, not proof, and a break re-earns the rule, which goes in Design rationale so the next pass doesn't repeat the experiment; never ablate a hook or a permission rule — removing several hides which one mattered, and an enforcement layer's failure is too expensive to observe even once.

## The layer-routing framework

Which layer holds each thing the user wants, and where is the repair when it misbehaves?

| What it is | Layer | Why | When it fails, fix |
|---|---|---|---|
| A fact or constraint nearly every request needs (build commands, an architecture decision, why a hook exists) | CLAUDE.md | Loaded every session; adherence drops past ~200 lines, so the bar is "does every session need this" (references/claude-md-and-rules.md) | Ignored: sharpen the phrasing. If the violation's cost says never, the routing was wrong — promote to hook plus deny |
| A rule for one part of the tree | `.claude/rules/*.md` + `paths:` | Loads only when a matching file is touched; without `paths:` it loads at launch like CLAUDE.md | Never loads: the glob doesn't match what Claude actually reads |
| A procedure or playbook needed only when a job comes up | skill | Triggers on `description`; the body loads only then. Skill count is a cost (references/skills.md), so consolidate in the inventory, not after | Doesn't trigger or steals triggers: frontmatter parse → listing budget → `disable-model-invocation` → compaction → wording — cheapest and most decisive first; any of the first four kills triggering outright. Wrong behaviour after triggering: the body's *why* |
| Something that must (or must never) happen every time | hook; a must-never `PreToolUse` gets a `permissions.deny` pair | Advisory layers can be deviated from; a hook blocks the calls it reaches, in every mode. The pair, because reaching them is the best-effort half — an `if` over-fires rather than filters precisely, and an `@file` never becomes a call at all; a guarantee about an event rather than a call has no rule saying the same thing and stands alone (references/hooks.md) | Doesn't fire: reproduce with `test_hook.py` first. Over-fires: narrow the matcher, or downgrade to a warning if the cost never justified blocking |
| A tool, command or path to block or force-approve | `permissions.allow` / `permissions.deny` | Enforced by the client, independent of the model | An allow rule never fires: a deny, or an ask, matched first — they are evaluated before allow; carve the exception out of that rule |
| A read-heavy role where only the conclusion matters (research, review, QA) | `.claude/agents/*.md` | Isolates context and restricts tools per role; agent count is a cost (references/agents.md) | Ignores a CLAUDE.md rule: Explore and Plan never load it — restate in the delegation, shadow with a custom agent, or inject via `SubagentStart` |
| An orchestration whose shape is fixed and repeats | `.claude/workflows/*.js` | Determinism is the point; skeleton in the script, judgment in the prompts (references/workflows.md) | Stalls: an agent needed a permission not in `allow`. Keeps needing edits: the shape varies, move to guidance |
| Parallel work whose shape differs every time | Guidance in CLAUDE.md or a skill ("fan out: find → verify → synthesize") | A fixed file for a variable task is a flexibility tax | — |

Four questions decide a row. **Enforced or advisory** — fine if Claude usually gets it right, or must it never fail? Prose for the first, code for the second. **When does it load** — every session, on a path, on demand, on an event; the answer names the layer. **Who needs it, and who writes it** — every clone or this machine, you or Claude at runtime; a fact only this developer needs goes in `CLAUDE.local.md`, not the CLAUDE.md the team pays for. **What does it cost** — the always-loaded bill is CLAUDE.md plus every rule without `paths:` plus every `@import` plus the first 200 lines of `MEMORY.md`; a description sits in a listing budget of about 1% of context; a hook costs a process spawn on every matching event and context only when it outputs; an agent costs a routing decision whenever it exists.

One request often splits: "always run tests before committing" is a hook (the guarantee) plus a CLAUDE.md line saying why it exists. Repair runs the table backwards under three rules: fix the smallest set the failure causally supports, pair rules included; re-run only the surface you changed and what it reaches; a component that seems to earn nothing is a question with its cost stated, never a deletion — `disable-model-invocation: true` is the usual answer, recorded on the row, and only removal marks it `retired`. Nothing failed but the harness grew is K15's cue.

## Authoring philosophy

Conviction over compliance: every instruction you write is what + a convincing why + a concrete picture, and the test is whether the why alone would let the model re-derive the rule for a case you didn't enumerate. A rule with no reason is a rail — it holds the cases its author listed and snaps on the one that wasn't.

Don't write what a capable model already knows; what earns its tokens is the **gotcha** — a trap nobody derives from general competence, only from having been burned. The same filter runs on the why: keep the clause that makes the rule re-derivable, cut the sentences that argue for it. The shapes that go: restating the claim, arguing for it, spelling out a consequence the reader computes anyway, giving the negative case equal weight when the positive implies it, narrating what comes next. A reference gotcha is kept by what the builder does with it: a paragraph that changes nothing you write or do is background.

Progressive disclosure is an optimum, not a default: the seam that pays is one the model genuinely branches on, so each invocation reads one file. Volume is a weaker reason, not a non-reason — `validate_harness.py` carries the body-length guideline in its message. Splitting a file the model always reads in full buys a routing decision and sometimes a silently missed fragment.

A reference does not have to be prose. A failing test, a schema, a rubric, or a function pins a target more precisely than a paragraph, and the runnable ones fail loudly when the target moves; when the interview surfaces "here's what good looks like," ask whether that is a file that already exists.

Numbers need their justification and their exception in the same breath — a number alone is a rail wearing a digit, and nobody can tell when it stopped applying.

**Prefer an interface over an instruction where one exists.** The thing Claude operates can be shaped so the wrong move isn't available, and an interface is re-read from the tool's own signature on every use — every session, after every compaction, inside every subagent. The harness's interface surfaces are a bundled script's CLI, a hook's configuration input, a workflow's `args`, a skill's `description`, an agent's `tools:`; an argument that takes three named values teaches the three cases by existing. The boundary runs both ways and splits on ownership: the tool owns what is *valid*, what it does, and what it prints; the project owns when to reach for it, what it costs, and why it was chosen. Neither side restates the other. **If editing the tool would make the sentence false, the sentence belongs in the tool.** `--help` cannot drift from the code that emits it; a summary of it can, and is the copy nothing checks. A check's failure message is an interface too, read exactly when it matters: state the decision in prose and let the check carry the consequence. A pointer inherits its target's reader, so it moves who pays rather than whether. This governs what the harness contains, not the project's application code.

**No mid-sentence hard-wrapping.** Line breaks fall only at sentence, list-item or paragraph boundaries — hard wraps break a future Edit's exact-string match and pollute diffs, and renderers soft-wrap anyway.

## Scripts

Five Python 3.10+ CLIs, stdlib only, in `scripts/`. Invoke them as `${CLAUDE_SKILL_DIR}/scripts/<name>.py`: the working directory is the target project and a plugin install runs from the plugin cache, so a relative path breaks in both. `${CLAUDE_SKILL_DIR}` is substituted in this skill's own markdown and in `allowed-tools` rules — **not** inside a workflow's prompt strings or a subagent's shell, where it expands to nothing; resolve it to an absolute path before passing it on. Flags are not listed here: read a script's `--help` the first time you reach for it.

| Script | Run it when |
|---|---|
| `audit_harness.py` | First, always, before the interview: it answers questions and shows what to preserve. Its template flag once per pass, before filling the spec |
| `validate_harness.py` | After every generation or edit, and again after the wrap-up edits. Exit 0 is the definition of finished |
| `hook_event.py` | Once you know which event you target, instead of reading the whole event reference |
| `test_hook.py` | After generating or wiring any hook, before calling it delivered |
| `run_e2e.py` | Only with the user's consent, during validation: it spends real tokens. Isolate anything that writes; the first run on a new machine is itself the confirmation that its auth works |

Whether a `description` triggers on the requests it should, and whether it steals a sibling's, are judgments no check makes for you: re-read every one you generate against references/skills.md, a lone one included. Same for a pointer: what a check can confirm is never that the file is there for the reader who ends up with it, so look.
