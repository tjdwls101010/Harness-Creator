# Interview protocol

This is how you run the conversation that turns a vague request ("set up Claude Code for this repo," "하네스 만들어줘") into an approved `.claude/harness-spec.md` you can generate from. Read this when you enter Phase 1 of the operating loop, after Phase 0's audit has told you which mode you're in (new / extend / improve / sync).

The interview exists because the spec is the product's real deliverable, not the generated files. Files can be regenerated from a spec; a spec cannot be reconstructed from files, because files don't record *why* a rule was routed to a hook instead of CLAUDE.md, or which of the user's own words a goal came from. Every stage below produces spec content and ends with the user confirming that content is right. If you skip a stage, you are guessing at spec content instead of recording it — which is exactly the failure mode this protocol prevents.

## Stages are a map, not rails

The five stages (I1-I5) describe the territory of everything a fresh-build spec needs filled in. They are not a script you read top to bottom regardless of context. Concretely:

- **Skip what's already answered.** If the user's opening request already states the goal ("I want risky shell commands blocked before they run"), you have I1's core content — don't re-ask it as a separate stage, fold it into the spec and move to confirming it.
- **Compress for simple asks.** "Just give me a CLAUDE.md and two hooks" does not need five gated stages. Collapse I2-I4 into a single round: propose the behavior inventory, the routing, and the component details together, and get one approval instead of three. The gate discipline (below) still applies — you still write it to the spec and still get a yes — but the *number of round trips* shrinks to match the size of the ask.
- **"Just build it" still gets a minimal check.** Even when a user explicitly wants zero ceremony, proceeding with literally no confirmation means you're generating a harness against assumptions nobody agreed to — and the first time it's wrong, you've burned a generation cycle. The floor is: confirm the goal in one sentence and surface any hard constraints (a monorepo layout, a language you should already know from the codebase, a "never touch `legacy/`" rule) before writing anything. That's a compressed I1, not a skipped one.
- **The spec-approval gate is never skipped, at any compression level.** You can collapse five stages into one question, but you cannot generate without an explicit yes on the resulting spec content. The gate is not bureaucracy layered on top of the interview — it *is* the interview's output. A spec nobody approved is just your guess wearing a formal-looking template.

The judgment call every time is: how many distinct decisions does this request actually contain, and how many of those are already resolved? Ask about what's unresolved, state what's already known, and gate on the result.

## The five stages (fresh build)

### I1 — Goals and pain points

**Purpose:** establish what the harness should change about how Claude behaves on this project, in the user's own words, plus a read on how much Claude Code vocabulary you can use with this person for the rest of the interview.

This stage is divergent — you don't yet know the shape of the answer space, so it's ordinary conversation, not AskUserQuestion (see the divergent-vs-convergent rule below). Ask open questions and let the answer run long:

- "What does Claude keep getting wrong on this project, or what do you find yourself repeating in every session?"
- "Is there anything Claude should never be allowed to do here — a path it shouldn't touch, a command it shouldn't run without asking?"
- "Have you set up a CLAUDE.md or any hooks/skills before, on this project or another one?" — this last question is also your proficiency probe. The point isn't the literal answer, it's *how* they answer: someone who says "yeah, I've got a few PreToolUse hooks already" can be talked to in tool vocabulary for the rest of the interview; someone who says "no, what's a hook?" needs plain-language framing throughout I2-I5, translated on the fly (see the calibration example below).

**Gate:** write a Goals section (quoting the user's own phrasing where it's sharper than a paraphrase would be) and get explicit approval before moving on. This is the cheapest gate to get right and the most expensive to get wrong — every later stage's routing decisions trace back to what you record here.

### I2 — Behavior inventory

**Purpose:** turn I1's prose into a discrete, numbered list of behaviors/knowledge/constraints — the raw material that I3 will route to layers. This is the first stage where the codebase itself becomes a source of candidates, not just the conversation.

Decompose I1's answer into items, then reconnoiter the codebase for things the user didn't think to mention: a test runner visible in `package.json` or a `Makefile`, an existing lint config, a directory that looks dangerous to touch (migrations, generated code, a `legacy/` folder), a monorepo boundary. Propose these as candidate inventory items rather than asking about them abstractly — "I see `npm test` runs the full suite in ~6 minutes; want a rule about running single test files instead?" is a fact-plus-proposal, not an open question.

**Gate:** approve the inventory as a list (this becomes the spec's Behavior inventory table rows, `status: proposed`). Don't route to layers yet — that's I3's job, and mixing the two makes it harder for the user to evaluate either one cleanly ("is this item worth having" vs "where should it live" are different questions).

### I3 — Layer routing

**Purpose:** for each inventory item, decide which layer it belongs to (CLAUDE.md / rules / skill / hook+permission / agent / workflow) using the layer-routing framework from SKILL.md §3, then get the user to confirm the routing — especially the enforce-vs-advise calls, which are the ones with real consequences if you get them wrong.

Propose routing, don't derive it silently. For most items the routing is unambiguous enough to just state ("test-runner convention → CLAUDE.md, it's a fact every session needs"), but flag the ones where you're making a judgment call the user might disagree with — typically anything that could plausibly be either a strong CLAUDE.md instruction or a hook. Example: the user said in I1 "Claude should never commit without running tests." That's a candidate for a hook (enforced) or a CLAUDE.md line (advised), and the difference matters — a CLAUDE.md line can be ignored under context pressure, a hook cannot. Surface the tradeoff plainly rather than picking silently: "should this be a hard block before commit, or a reminder Claude usually follows?"

**Gate:** approve the routing column of the inventory table. This is the stage most likely to produce a real back-and-forth, since it's where "advisory" vs "enforced" gets decided — don't rush it just because I2 already felt like the substantive stage.

### I4 — Component detail

**Purpose:** collect the information each routed component actually needs to be generated, which varies by target layer:

- **Hooks:** does a failure block the action or just warn? What's the matcher (which tools/paths trigger it)? What should the message to the user or to Claude look like on failure?
- **Skills:** where does its reference material live or come from (existing docs to point at, or knowledge you need to author fresh)? Does it need bundled scripts?
- **Workflows:** is this orchestration shape fixed and reusable enough to pre-define as a `.claude/workflows/*.js` file, or does it vary too much run to run to be worth pre-defining (D12 — see `workflows.md`)?
- **Cross-cutting:** what language should the generated harness's own documentation be written in? (This is independent of the interview conversation's language — D7: the interview happens in the user's language, but the *generated* CLAUDE.md/skills' language is itself an I4 answer you need to collect, not an assumption.)

**Gate:** approve the component specs section. This is where "hook blocks vs warns" and similar binary calls get locked in — don't leave them implicit, because `03-component-generators.md`'s generation step will need a concrete answer, not a vibe.

### I5 — Validation plan

**Purpose:** decide what "this harness works" will mean, concretely, before you generate anything — which scenarios count as proof, and whether the user wants to spend tokens on live e2e validation or stop at the free deterministic lint.

- "What's a concrete situation where you'd want to see this behave correctly before you trust it? For example, a prompt that should trigger the new skill, and a similar-sounding one that shouldn't."
- "Live end-to-end validation spins up real headless Claude Code sessions to test this, which costs tokens and time. Want to run that after generation, or just the free structural checks?"

**Gate:** this is the final spec approval — once the user signs off here, the spec's overall status moves to `approved` and generation begins. Everything upstream was staged; this gate is the one that actually unblocks Phase 2.

## AskUserQuestion operating rules

The tool has fixed mechanical limits: **max 4 questions per call, 2-4 options per question, option headers capped at 12 characters, and an "Other" option is always auto-appended by the tool** — never author your own "Other"/"Something else" option, you'll end up with two.

Beyond the mechanics, the rule that actually determines interview quality is this: **the number of questions you ask matters far less than whether each one maps to a specific, identifiable cell in the eventual harness-spec.md.** Before you fire off a question, know which row of the Behavior inventory table, which Component spec field, or which line of Context it will fill. A question that doesn't correspond to a spec cell is a question you don't need to ask — either it's genuinely open-ended (route it to plain conversation instead, see below) or it's decorative.

This has a direct corollary: **if the codebase already answers the question, don't ask it — state the finding.** If `package.json` has a `"test": "jest"` script, don't ask "what's your test runner?" Say "I see this project uses Jest via `npm test`" and move straight to the follow-up that's actually still open, like "should Claude always run a single file instead of the full suite?" Asking a question you could have answered yourself wastes a round trip and signals you didn't actually look.

**When you have a clear recommendation, lead with it.** Put the recommended option first, suffix its header with "(Recommended)", and use the option's description field to say *why* — not just what it is. A weak description restates the label; a strong one gives the reason a reasonable person would pick it. For example, routing "block commits with raw SQL":

- Header: `Hook (Recommended)` — description: "Enforced automatically, can't be bypassed by context pressure — appropriate since you said this must never happen."
- Header: `CLAUDE.md rule` — description: "Advisory only; Claude usually follows it but nothing stops a slip under a long session."

**Calibrate vocabulary to the proficiency you read in I1.** The same routing decision gets asked in different words depending on who's answering. For a self-described non-developer:

> "Should risky commands be blocked automatically before they run, or just flagged to you after the fact?"

For someone who mentioned existing hooks unprompted in I1:

> "PreToolUse hook with a deny matcher on `Bash`, or leave it advisory in CLAUDE.md?"

Same decision, same spec cell, different surface language. Don't force tool jargon on someone who didn't bring it up first, and don't over-explain hook mechanics to someone who clearly already knows them — both are a tax on the interview's pace.

**Divergent questions are not AskUserQuestion's job.** AskUserQuestion is a convergence tool: it's for picking among a small set of options you can already enumerate. "What's your goal for this harness" and "what's been painful" have answer spaces you cannot enumerate in advance — forcing them into 2-4 options would either bias the answer toward your guesses or truncate something the user needed to say in full sentences. Those belong in ordinary dialogue (this is exactly why I1 above is written as plain questions, not a tool call). Once you're choosing between "hook vs CLAUDE.md rule" or "block vs warn," the option space is small and known — that's when the tool earns its keep.

## Re-entry mode variants

**Extend mode** shrinks I1 down to a single question — "what's newly wanted, beyond what's already in the harness?" — and everything else follows the same stage flow, except the resulting Goals content is merged into the existing spec's Goals section rather than replacing it. I2-I5 run as normal against the delta, since new behaviors still need inventory, routing, and component detail even if the overall harness already exists.

**Improve mode** replaces I1 entirely with "what was uncomfortable, wrong, or annoying about how the current harness behaves?" instead of "what's the goal" — the framing shifts from greenfield intent to observed failure. Each piece of feedback then gets routed through the feedback-routing table (symptom → repair target: wrong trigger → description, triggered-but-wrong-behavior → skill body, ignored rule → CLAUDE.md then escalate to hook, etc.) defined in `e2e-testing.md` — don't duplicate that table here, just route feedback through it and let it tell you which component and which stage of this protocol to re-enter at.

**Sync mode** minimizes the interview almost to nothing: Phase 0's audit already produced a drift list (spec claims component X exists, filesystem disagrees, or vice versa), so the entire interview collapses to presenting that list and asking, per drift item, whether the spec should be corrected to match reality or the files should be regenerated to match the spec. There is no I1-I5 traversal in sync mode — drift resolution is its own minimal loop.

## The harness-spec.md template

This is the exact section skeleton to generate and keep updated across every stage. Don't improvise a different structure — this shape is what `audit_harness.py` parses and diffs against on re-entry, so drift detection depends on the sections and the table columns staying stable.

```markdown
# Harness Spec — <project>

## Context
<!-- Project summary: language(s), build system, test runner, team size, user proficiency notes from I1 -->

## Goals
<!-- What this harness should achieve, in the user's own words where possible -->

## Behavior inventory
| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | Must pass tests before commit | hook  | pre-commit-test | generated |

## Component specs
<!-- Per-component detail: hooks need event/matcher/action/failure-policy, skills need trigger description/body contents/bundled scripts, etc. -->

## Design rationale
<!-- Why each routing decision was made, and which alternatives were rejected and why -->

## Validation
<!-- e2e scenario list and the result of the most recent run -->

## Change history
<!-- Date, mode (new/extend/improve/sync), summary of what changed -->
```

The `status` column progresses through four values, in order: `proposed` (surfaced during I2, not yet approved) → `approved` (survived its stage gate, locked as intent) → `generated` (a file now exists on disk for it) → `validated` (it passed lint and, if run, e2e). This progression exists because it's the exact mechanism `audit_harness.py` uses to detect drift on re-entry: a row stuck at `approved` with no matching file means generation was interrupted or failed; a row at `generated` whose file no longer exists on disk means something deleted it out from under the spec; a file on disk with no corresponding row means it was hand-added outside the harness-creator flow. Without a status column, drift detection degenerates into "diff the whole file tree and guess" — with it, the audit script can report precisely which behaviors are unresolved and why, which is what makes re-entrancy (D6) actually work instead of just being a promise in the docs.
