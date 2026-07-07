# The Interview & Spec

Before harness-creator writes a single file, it interviews you. This page explains how that staged conversation works, why it comes first, and how it produces `.claude/harness-spec.md` — the one document everything else is generated from.

## Why the interview comes first

The real deliverable of harness-creator is not the generated files — it's the **spec**. Files can be regenerated from a spec at any time; a spec cannot be reconstructed from files, because files don't record *why* a requirement was routed to a hook instead of `CLAUDE.md`, or which of your own words a goal came from. So the interview is front-loaded on purpose: it exists to get every decision written down and agreed to *before* generation, so that generation is just transcription and there's a durable record to audit against on every later run.

The consequence for you is simple. You are never surprised by what gets built, because you approved the plan for it first.

## The five stages

A fresh build walks through five stages. They cover everything a spec needs filled in — think of them as a map of the territory, not a script read top to bottom.

| Stage | Name | What it establishes |
|-------|------|---------------------|
| **I1** | Goals & pain points | What the harness should change about how Claude behaves here, in your own words — plus a read on how much Claude Code vocabulary to use with you for the rest of the interview. |
| **I2** | Behavior inventory | I1's prose turned into a discrete, numbered list of behaviors, knowledge, and constraints. This is the first stage where your codebase becomes a source of candidates, not just the conversation. |
| **I3** | Layer routing | For each inventory item, which layer holds it — `CLAUDE.md`, a rule, a skill, a hook, a permission, an agent, or a workflow. The judgment call at the heart of the whole tool. |
| **I4** | Component detail | The specifics each routed component needs to be generated: does a hook block or just warn, what triggers it, where a skill's reference material comes from, what language the generated docs are written in. |
| **I5** | Validation plan | What "this harness works" will concretely mean — which scenarios count as proof, and whether you want to spend tokens on live end-to-end testing or stop at the free structural checks. |

The routing done in I3 is the core skill; it has its own page in **[The Layer-Routing Framework](Layer-Routing.md)**.

## Every stage ends in an approval gate

Each of the five stages finishes the same way: it writes its result into the spec, then stops and asks you to confirm that result is right before moving on. Nothing advances on assumption. This is what keeps you in control — the interview is a series of small, explicit yeses, not one big leap of faith at the end.

One gate matters more than the rest: **the spec-approval gate is never skipped, at any level of compression.** You can collapse five stages into a single question for a small ask, but harness-creator will not generate a harness without an explicit yes on the resulting spec. That gate isn't ceremony layered on top of the interview — it *is* the interview's output. A spec nobody approved is just a guess wearing a formal-looking template, and generating from it means there's nothing real to audit against next time.

## It scales to the size of your ask

The stages are a map, not rails. harness-creator sizes the conversation to how many decisions your request actually contains:

- **It skips what you've already answered.** If your opening request states the goal ("block risky shell commands before they run"), that's I1's content already — it folds it into the spec and confirms it rather than re-asking.
- **It compresses simple asks.** "Just give me a `CLAUDE.md` and two hooks" doesn't need five separate gated rounds. It proposes the inventory, routing, and component details together and asks for one approval.
- **"Just build it" still gets a minimal check.** Even when you want zero ceremony, it confirms the goal in one sentence and surfaces any hard constraints (a monorepo layout, a directory that should never be touched) before writing anything. That's a compressed first stage, not a skipped one — because generating against assumptions nobody agreed to burns a whole cycle the first time one is wrong.

## How it asks: open dialogue vs. structured choices

harness-creator uses two different question styles depending on the shape of the answer:

- **Divergent questions** — goals, pain points, "what does Claude keep getting wrong here" — have an answer space nobody can enumerate in advance. Forcing these into a fixed menu would bias the answer toward the tool's guesses or cut off something you needed to say in full. So these are asked as **ordinary conversation**, and you're encouraged to let the answer run long.
- **Convergent questions** — "should this be a hard block or an advisory reminder," "hook vs. `CLAUDE.md` rule" — have a small, known set of options. These are asked as **structured multiple-choice questions**: a short list of options to pick from, usually with the recommended one first and a one-line reason for each so you can see *why* you'd pick it, not just what it is.

The rule of thumb: divergence gets a conversation, convergence gets a menu.

## It won't ask what your codebase already tells it

A question you could have answered by reading the repo is a question harness-creator won't ask you. If your `package.json` has a `"test": "jest"` script, it won't ask "what's your test runner?" — it will state the finding and move straight to the follow-up that's actually still open:

> "I see this project uses Jest via `npm test` — should Claude always run a single file instead of the full suite?"

That's a fact plus a proposal, not an open question. It saves a round trip and means the interview spends your attention only on the things the codebase genuinely can't answer for it.

## It speaks at your level

Early in I1, harness-creator reads how much Claude Code vocabulary it can use with you — often just from how you answer "have you set up a `CLAUDE.md` or hooks before?" It then calibrates its wording for the rest of the interview. The *same* decision gets asked in different words depending on who's answering.

For someone who isn't a developer:

> "Should risky commands be blocked automatically before they run, or just flagged to you after the fact?"

For someone who mentioned existing hooks unprompted:

> "PreToolUse hook with a deny matcher on `Bash`, or leave it advisory in `CLAUDE.md`?"

Same decision, same slot in the spec, different surface language. It won't push jargon on you if you didn't bring it up, and it won't over-explain mechanics to someone who clearly already knows them.

## The spec: your single source of truth

Every stage feeds one file, `.claude/harness-spec.md`, built up with you across the interview and kept in a stable, predictable shape:

| Section | What it holds |
|---------|---------------|
| **Context** | Project summary — languages, build system, test runner, team size, and the proficiency read from I1. |
| **Goals** | What the harness should achieve, in your own words where your phrasing is sharper than a paraphrase. |
| **Behavior inventory** | The numbered table of behaviors/knowledge/constraints, each with its routed layer, its component, and a status. |
| **Component specs** | Per-component detail — a hook's event, matcher, action, and failure policy; a skill's trigger and body contents; and so on. |
| **Design rationale** | Why each routing decision was made, and which alternatives were rejected and why. |
| **Validation** | The end-to-end scenario list and the result of the most recent run. |
| **Change history** | Date, mode, and a summary of what changed, appended every time the harness is touched. |

Each inventory row carries a **status** that advances in one direction: `proposed` (surfaced during I2) → `approved` (survived its stage gate) → `generated` (a file now exists for it) → `validated` (it passed the checks). That status trail is what makes the spec auditable: on a later run, `audit_harness.py` reads this file and compares it against what's actually on disk, so a row stuck at `approved` with no file, or a file with no row, is caught rather than silently ignored.

This is why the spec is the persisted single source of truth. Because harness-creator keeps it in sync with the files on every pass, a future run — extending, improving, or reconciling the harness — starts from an accurate record instead of guessing at your setup. See **[Re-entry Modes](Re-entry-Modes.md)** for how those later runs use it.

## Next

- **[Layer-Routing](Layer-Routing.md)** — the routing decision I3 is built around
- **[Re-entry Modes](Re-entry-Modes.md)** — how new / extend / improve / sync reuse the spec
- **[Validation & Testing](Validation.md)** — what the I5 plan actually runs
