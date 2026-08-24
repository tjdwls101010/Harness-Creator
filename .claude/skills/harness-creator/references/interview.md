# The interview

This is how you run the conversation that turns a vague request ("set up Claude Code for this repo," "하네스 만들어줘") into an approved `.claude/harness-spec.md` you can generate from — on a fresh project and on one that already has a harness. Read it when you enter Phase 1, after Phase 0's audit has told you what's on disk.

The interview exists because the spec is the product's real deliverable, not the generated files. Files can be regenerated from a spec; a spec cannot be reconstructed from files, because files don't record *why* a rule was routed to a hook instead of CLAUDE.md, or which of the user's own words a goal came from. So every stage below produces spec content and ends with the user confirming that content is right, and **the spec-approval gate is never skipped, at any compression level** — it isn't bureaucracy layered on top of the interview, it *is* the interview's output. A spec nobody approved is your guess wearing a formal-looking template.

## Which mode you're in, and what it changes

Four modes, and they differ almost entirely in the opening question. **The audit's suggested mode is a hint, not a verdict**: it tells `new` from `not-new` reliably and it detects drift, but **extend and improve look identical on disk** — the difference lives entirely in what the user wants. Ask them rather than inferring.

| Mode | Opening | What follows |
|---|---|---|
| `new` | Goals and pain points, from scratch | All five stages |
| `extend` | "What's newly wanted, beyond what's here?" | All five stages, against the delta only |
| `improve` | "What was uncomfortable, wrong, or annoying?" | Re-enter at the stage the symptom points to |
| `sync` | None — the audit already produced the list | No stages at all; see [Sync](#sync--no-stages-just-the-drift-list) |

Extend and improve still traverse the stages because a new or repaired behavior still needs inventory, routing, and component detail even when the surrounding harness already exists.

## Stages are a map, not rails

The five stages describe the territory of everything a spec needs filled in. They are not a script you read top to bottom regardless of context.

- **Skip what's already answered.** If the opening request already states the goal ("I want risky shell commands blocked before they run"), you have I1's content — fold it into the spec and move to confirming it, don't re-ask it as a stage.
- **Compress for simple asks.** "Just give me a CLAUDE.md and two hooks" does not need five gated stages. Collapse I2-I4 into a single round — propose the inventory, the routing, and the component details together, and take one approval instead of three. The number of round trips shrinks to match the size of the ask; the gate discipline does not.
- **"Just build it" still gets a floor.** Even when a user explicitly wants zero ceremony, generating against assumptions nobody agreed to burns a whole cycle the first time one is wrong. The floor is: confirm the goal in one sentence and surface any hard constraints (a monorepo layout, a "never touch `legacy/`" rule) before writing anything. That's a compressed I1, not a skipped one.

The judgment call every time: how many distinct decisions does this request actually contain, and how many are already resolved? Ask about what's unresolved, state what's already known, and gate on the result.

## I1 — the opening question

**Purpose:** establish what the harness should change about how Claude behaves here, in the user's own words, plus a read on how much Claude Code vocabulary you can use with this person for the rest of the interview.

Whichever variant you're in, this stage is plain conversation rather than a tool call — the answer space isn't enumerable yet, and 2-4 options would bias it toward your guesses.

**Gate:** write a Goals section (quoting the user's own phrasing where it's sharper than a paraphrase would be) and get explicit approval before moving on. This is the cheapest gate to get right and the most expensive to get wrong — every later stage's routing decisions trace back to what you record here.

### New — goals and pain points

Ask open questions and let the answer run long:

- "What does Claude keep getting wrong on this project, or what do you find yourself repeating in every session?"
- "Is there anything Claude should never be allowed to do here — a path it shouldn't touch, a command it shouldn't run without asking?"
- "Have you set up a CLAUDE.md or any hooks/skills before, on this project or another one?"

That last one is also your proficiency probe. The point isn't the literal answer, it's *how* they answer: someone who says "yeah, I've got a few PreToolUse hooks already" can be talked to in tool vocabulary for the rest of the interview; someone who says "no, what's a hook?" needs plain-language framing throughout, translated on the fly.

### Extend — what is newly wanted

Shrink I1 to a single question: what's newly wanted, beyond what's already here? Merge the resulting Goals content into the existing spec's Goals section rather than replacing it — the old goals didn't stop being true.

### Improve — what stopped working

Replace I1 entirely. The question is not "what's the goal" but **"what was uncomfortable, wrong, or annoying about how this behaves?"** The framing shifts from greenfield intent to observed failure, and the answers are usually symptoms rather than diagnoses.

Route each symptom through the feedback-routing table in `references/e2e-testing.md` (wrong trigger → the description; triggered but did the wrong thing → the skill body; the rule was ignored → CLAUDE.md, then escalate to a hook). That table also tells you which stage to re-enter at, so you rarely need all five.

**Ask the second question in the same breath: what is now unnecessary?** Every arrow in that routing table ends in a repair or a promotion, so a harness that is only ever improved only ever grows. Nothing on disk tells you what stopped earning its keep — there is no invocation telemetry — so if you don't ask, nobody does. Ask both, and take "nothing comes to mind" as a real answer rather than pressing for one.

### Ablation — the only way an improve pass subtracts

A component that stopped being used is at least visible as a file. A *line* that stopped being needed is invisible: a rule written to fight a model's old default reads exactly like one still fighting the current default, and the model changes under a harness that doesn't. That is the dead weight that accumulates fastest, because every pass adds rules and no pass re-examines the ones already there.

**Ablation is how you find out, and it is a proposal, not an action.** Take one rule you suspect — start with the ones written to fight a default, since those are the ones a better model may have stopped needing — remove it, and run the work it was written for. Nothing goes wrong: it was carrying nothing. Something does: you have just re-earned it, and that belongs in the spec's Design rationale, because the next pass will suspect it again and should not have to re-run the experiment.

One rule at a time. Removing several at once turns a clean result into a guess about which one mattered. And **never ablate a hook or a permission rule** — those layers exist precisely because their failure mode is the one you cannot afford to observe once.

## I2 — Behavior inventory

**Purpose:** turn I1's prose into a discrete, numbered list of behaviors/knowledge/constraints — the raw material that I3 will route to layers. This is the first stage where the codebase itself becomes a source of candidates, not just the conversation.

Decompose I1's answer into items, then reconnoiter the codebase for things the user didn't think to mention: a test runner visible in `package.json` or a `Makefile`, an existing lint config, a CI config, a directory that looks dangerous to touch (migrations, generated code, a `legacy/` folder), a monorepo boundary. Propose these as candidate inventory items rather than asking about them abstractly — "I see `npm test` runs the full suite in ~6 minutes; want a rule about running single test files instead?" is a fact-plus-proposal, not an open question.

**Say out loud what you are choosing not to build, and record it.** Every layer in this framework costs something on every session — a CLAUDE.md line, a skill's description sitting in the listing budget, an agent adding a routing decision — so a harness is defined as much by what it leaves out as by what it contains. When you decline a candidate, name it and give the reason in one line ("skipping a skill for changelog entries: it's two commands, and a CLAUDE.md line covers it"), then write it into the inventory table with `status: declined`. Without that row the next pass re-proposes the same idea, the user re-decides something they already decided, and there is no record of *why* the harness looks the way it does. This is also the moment to fold near-duplicate candidates together, rather than discovering the overlap after three skills already exist.

**Gate:** approve the inventory as a list (this becomes the spec's Behavior inventory rows, `status: proposed`). Don't route to layers yet — that's I3's job, and mixing the two makes it harder for the user to evaluate either one cleanly ("is this item worth having" vs "where should it live" are different questions).

## I3 — Layer routing

**Purpose:** for each inventory item, decide which layer it belongs to using the layer-routing framework in SKILL.md, then get the user to confirm the routing — especially the enforce-vs-advise calls, which are the ones with real consequences if you get them wrong.

Propose routing, don't derive it silently. For most items the routing is unambiguous enough to just state ("test-runner convention → CLAUDE.md, it's a fact every session needs"), but flag the ones where you're making a judgment call the user might disagree with — typically anything that could plausibly be either a strong CLAUDE.md instruction or a hook. Example: the user said in I1 "Claude should never commit without running tests." A CLAUDE.md line can be ignored under context pressure; a hook cannot. Surface that tradeoff plainly rather than picking silently: "should this be a hard block before commit, or a reminder Claude usually follows?"

Before routing anything to a hook, probe for an **interface** that would make the wrong move unavailable instead. A hook fires after Claude has already decided to do the thing; a signature is re-read every time the tool is used, in every session and every subagent. If the item is "Claude keeps calling the deploy script against prod," a script that requires an explicit `--env` argument settles it more durably than a hook that inspects the command string. This won't apply to most items, but when it does apply it's strictly better, and it's easy to miss because the interview's vocabulary is all layers and the answer isn't one.

**Widening permissions gets its own question.** If the routing produces new `permissions.allow` entries, don't fold them into a general "approve the routing?" gate — ask separately, and name every rule and what it grants: "this adds `Bash(npm test)` and `Bash(git push)` to the always-approved list, meaning Claude runs those without asking, in this repo, for everyone who clones it." Allow rules are the one output of this interview that removes a checkpoint the user currently has, and they ship to the whole team in version control. Deny and ask rules don't need this treatment — they only ever add friction.

**Gate:** approve the routing column of the inventory table. This is the stage most likely to produce a real back-and-forth, since it's where "advisory" vs "enforced" gets decided — don't rush it just because I2 already felt like the substantive stage.

## I4 — Component detail

**Purpose:** collect the information each routed component actually needs to be generated, which varies by target layer:

- **Hooks:** does a failure block the action or just warn? What's the matcher (which tools/paths trigger it)? What should the message to the user or to Claude look like on failure?
- **Skills:** where does its reference material live or come from (existing docs to point at, or knowledge you need to author fresh)? Does it need bundled scripts?
- **Workflows:** is this orchestration shape fixed and reusable enough to pre-define as a `.claude/workflows/*.js` file, or does it vary too much run to run to be worth pre-defining (see references/workflows.md)?
- **Cross-cutting:** what language should the generated harness's own documentation be written in? This is independent of the interview conversation's language — the interview happens in the user's language, but the *generated* CLAUDE.md and skills' language is itself an I4 answer you collect, not an assumption.
- **Deployment:** does any of this need to work in more than this one repo? Ask once, because the answer changes what a component may be. Skills, agents, hooks, and workflows can be packaged and distributed; **CLAUDE.md, rules, and permissions cannot** — those are per-project files with no shareable form, so "make our whole team's setup portable" has to be answered as "the skill and the hook travel; the CLAUDE.md gets copied or re-derived per repo." Packaging also strips fields and changes what can ship at all (see references/agents.md). If the answer is yes, name the path in the spec so the next pass knows the target shape; producing the packaging itself is out of scope here.

**Gate:** approve the component specs section. This is where "hook blocks vs warns" and similar binary calls get locked in — don't leave them implicit, because generation needs a concrete answer, not a vibe.

## I5 — Validation plan

**Purpose:** decide what "this harness works" will mean, concretely, before you generate anything — which scenarios count as proof, and whether the user wants to spend tokens on live e2e validation or stop at the free deterministic lint.

- "What's a concrete situation where you'd want to see this behave correctly before you trust it? For example, a prompt that should trigger the new skill, and a similar-sounding one that shouldn't."
- "Live end-to-end validation spins up real headless Claude Code sessions to test this, which costs tokens and time. Want to run that after generation, or just the free structural checks?"

**Gate:** this is the final spec approval — once the user signs off here, the spec's overall status moves to `approved` and generation begins. Everything upstream was staged; this gate is the one that actually unblocks Phase 2.

## Asking well

**The number of questions you ask matters far less than whether each one maps to a specific, identifiable cell in the eventual harness-spec.md.** Before you fire off a question, know which row of the Behavior inventory table, which Component spec field, or which line of Context it will fill. A question that doesn't correspond to a spec cell is a question you don't need to ask — either it's genuinely open-ended (route it to plain conversation) or it's decorative.

This has a direct corollary: **if the codebase already answers the question, don't ask it — state the finding.** If `package.json` has a `"test": "jest"` script, don't ask "what's your test runner?" Say "I see this project uses Jest via `npm test`" and move straight to the follow-up that's actually still open, like "should Claude always run a single file instead of the full suite?" Asking a question you could have answered yourself wastes a round trip and signals you didn't actually look.

**Once the option space is small and known, switch to AskUserQuestion.** "Hook or CLAUDE.md rule?" and "block or warn?" are exactly that shape — a handful of options you can name in advance — and that is where the tool earns its keep, in contrast to I1's open questions.

**An option's description carries the reason, not a restatement of the label.** A weak description says again what the header already said; a strong one gives the reason a reasonable person would pick it. For routing "block commits with raw SQL":

- Header `Hook` — "Enforced automatically, can't be bypassed by context pressure — appropriate since you said this must never happen."
- Header `CLAUDE.md rule` — "Advisory only; Claude usually follows it but nothing stops a slip under a long session."

**Calibrate vocabulary to the proficiency you read in I1.** The same routing decision gets asked in different words depending on who's answering. For a self-described non-developer:

> "Should risky commands be blocked automatically before they run, or just flagged to you after the fact?"

For someone who mentioned existing hooks unprompted in I1:

> "PreToolUse hook with a deny matcher on `Bash`, or leave it advisory in CLAUDE.md?"

Same decision, same spec cell, different surface language. Don't force tool jargon on someone who didn't bring it up first, and don't over-explain hook mechanics to someone who clearly already knows them — both are a tax on the interview's pace.

## Sync — no stages, just the drift list

Sync has no I1-I5 traversal. Phase 0's audit already produced the drift list, in both directions:

- **A spec row whose `status` claims a file that isn't there** — a row at `generated` or `validated` with nothing on disk.
- **A file on disk the spec never mentions.**

The whole mode is: present that list, and ask per item whether the spec should be corrected to match reality or the files regenerated to match the spec.

**Default to correcting the spec, and ask before anything else.** Divergence is not automatically corruption. A component the spec doesn't mention is usually a teammate's work, another tool's, or a deliberate hand-edit; behavior that migrated from CLAUDE.md into a skill is someone's routing decision, possibly a better one than yours. "The spec is behind" is the common case, "the files are wrong" is the rare one, and quietly reverting a colleague's work is far worse than asking an unnecessary question. Establish which you're in first, and record the outcome in Change history as what it was — an external edit the spec now reflects, not a file restoration.

**Say what sync cannot see when you present the list**, or a clean report reads as "nothing changed." The check is about existence, not correctness. So edits to CLAUDE.md never appear (the audit inventories instruction files without diffing them), and neither do edits to a component's *contents* — a rewritten skill body is still a file at the path the spec names, and reads as perfectly in sync. Compare those by hand.

## The harness-spec.md template

This is the exact section skeleton to generate and keep updated across every stage. Don't improvise a different structure — `audit_harness.py` locates the `## Behavior inventory` heading and reads that table's `component` and `status` columns, so drift detection in the spec-claims-a-missing-file direction depends on that heading and those columns staying stable. The rest of the spec is matched as plain text.

**Write the `component` cell as a backticked repo-relative path** (`` `.claude/skills/pr-opener/` ``), not a bare name. Both scripts accept a bare name today, but `validate_harness.py`'s spec-coverage check wants the full path, so a bare name is the shape that eventually produces a false report on a correct harness.

```markdown
# Harness Spec — <project>

## Context
<!-- Project summary: language(s), build system, test runner, team size, user proficiency notes from I1 -->

## Goals
<!-- What this harness should achieve, in the user's own words where possible -->

## Behavior inventory
| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | Must pass tests before commit | hook  | `.claude/hooks/pre-commit-test.sh` | generated |

## Component specs
<!-- Per-component detail: hooks need event/matcher/action/failure-policy, skills need trigger description/body contents/bundled scripts, etc. -->

## Design rationale
<!-- Why each routing decision was made, and which alternatives were rejected and why -->

## Validation
<!-- e2e scenario list and the result of the most recent run -->

## Change history
<!-- Date, mode (new/extend/improve/sync), summary of what changed -->
```

### Reading the status column

`proposed` (surfaced in I2, not yet approved) → `approved` (survived its stage gate, locked as intent) → `generated` (a file now exists on disk) → `validated` (it passed lint, and e2e too if e2e was run) is a progression; `declined` and `retired` are terminal rather than sequential. Keep the terminal rows — a spec that only records what was built loses the record of what was decided against, and the next pass re-proposes it.

Only two values assert that a file exists, and that is exactly what the sync drift check reads:

| Status | Claims a file exists? | A missing file means |
|---|---|---|
| `proposed` | No | Nothing — surfaced in I2, not yet approved |
| `approved` | No | Nothing — locked as intent, generation not started |
| `generated` | Yes | Generation was interrupted or failed partway |
| `validated` | Yes | It existed and passed, then something removed it |
| `declined` | No | Nothing — deliberately not built |
| `retired` | No | Nothing — deliberately removed |

So `proposed` and `approved` are never drift: a harness paused mid-interview is full of them, and reporting those would make every pass on an existing harness look broken. The two that do assert a file want different questions — an interrupted generation usually just needs finishing, while a component that was validated and then vanished is a question about who removed it and why.

Keep a row's status current in the same pass that changes its reality.

### Two sections grow every pass, so give them an eviction rule now

This is the one file this skill writes on every pass, and the only one nothing else prunes. A spec that has recorded six passes in full is a spec the seventh pass reads past.

**Change history** keeps in full what a re-entering pass can still act on — the current generation of work, and any pass that recorded someone *else's* edit, because that entry is the only place the next pass learns this harness has more than one author. Everything older folds to one line: date, mode, and what changed in a clause. Whoever needs the detail is reconstructing a decision and has git for it; the spec's reader wants the shape the harness is in now.

**Design rationale** holds the decision and the alternatives that were rejected, and stops there. A rejected alternative is the expensive thing to lose — it is what stops the next pass re-proposing it — so it survives compression while the sentences defending the choice do not. When a later pass supersedes a decision, rewrite the entry to its outcome instead of stacking the new one beneath the old; two live answers to one question is worse than either.

**Don't copy a skill's `description` into Component specs.** It is already in the frontmatter, which is where it gets read from, so the copy is the half that drifts — and this file's own fixture drifted exactly that way. Record what the spec uniquely knows: why this behavior went to a skill rather than a rule or a hook.

## Ending a pass

Every mode ends the same way: spec updated, `validate_harness.py` clean, Change history written.
