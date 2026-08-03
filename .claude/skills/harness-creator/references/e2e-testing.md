# E2E Testing

This is the second, deeper tier of harness validation. Read this when the interview reaches the Validation stage (I5) and again right before you actually compose and launch the e2e run. It tells you what e2e proves that the linter cannot, how to build the run on the spot from that session's scenarios, how to grade a transcript without fooling yourself, and what to say to the user about the one mechanism in this whole pipeline that has not been watched to work in a real authenticated session.

## Why this tier exists at all

`validate_harness.py` is free and structural: it catches a hook that points at a script which doesn't exist, a skill with a dead link, a CLAUDE.md that ballooned past 200 lines. It runs on every generation, no consent needed, and you already fix every error it finds before declaring the generation done. None of that tells you whether the harness actually changes Claude's behavior. A skill can have perfect frontmatter and a beautifully structured body and still never trigger, because the description's boundary language is fuzzy. A hook can be syntactically flawless and still fire on the wrong tool, or never fire, because the matcher was written against an assumption about tool-call shape that turned out wrong. Lint proves the harness is well-formed; only a real run against a real prompt proves it does what the spec's Behavior inventory says it should do. That gap is what e2e closes, and it can only be closed by spawning an actual headless Claude session against the generated harness and watching what happens.

This costs real tokens and real wall-clock time — a handful of full agentic sessions per scenario, not a lint pass — so it only runs with the user's explicit consent, gathered as part of interview item I5 alongside the scenario list itself. Never launch it silently as part of "finishing" a generation. Offer it, name the rough cost (scenario count × roughly one full session each), and proceed only on yes.

## Shape: a workflow composed on the spot, not a file you ship

There is no `e2e-runner.js` sitting in this skill's workflows directory, and you should not create one. The scenarios that need checking are different for every project — a Python API's harness needs a scenario about a migration-safety hook, a frontend monorepo's harness needs one about a component-generation skill — so freezing a fixed workflow file would either be too narrow to fit the next project or so generic it checks nothing real. This is the same D12 principle that governs every other variable-shaped task in this skill: pre-defined structure is for orchestrations whose *shape* stays fixed between runs; e2e validation's shape is the scenario list itself, and that list is different every single time. So you compose the workflow at the moment you need it, using the spec's Validation section as the input, and you throw the composition away afterward — only the results get recorded, in the spec.

The shape to compose, every time, is three phases:

```
Phase Run:    one agent per scenario, running run_e2e.py via Bash, scenarios pipelined
              independently of each other (a slow scenario shouldn't block a fast one)
Phase Grade:  one grading agent per transcript — trigger hit? hook fired? behavior
              followed? artifact quality good? every verdict cites transcript evidence;
              surface-level compliance without real evidence is a FAIL
Phase Report: synthesize pass/fail across all scenarios, plus a concrete per-failure
              repair suggestion pointing at the specific layer to fix
```

Run and Grade are two separate phases, not one — grading needs the *whole* transcript and summary already written to disk, and running the next scenario shouldn't wait on grading the previous one's output. Keep them as sequential stages within the composed workflow (all Runs, then all Grades), with independence *within* each stage, not across them.

### Annotated skeleton

This is illustrative, not a file to ship — adapt the scenario count, prompts, and grading dimensions to what the spec's Validation section actually lists.

```javascript
export const meta = {
  name: 'e2e-validate-harness',
  description: 'Run the spec Validation scenarios as headless sessions against the generated harness and grade each transcript.',
}

// Resolve this in the composing session and paste the absolute path in.
// `${CLAUDE_SKILL_DIR}` is NOT substituted inside a workflow's prompt strings
// (see the gotcha below) -- it would reach the subagent as literal text.
const SKILL_DIR = '/absolute/path/to/the/harness-creator/skill'

// One entry per scenario in the spec's Validation section. Each `expect` is
// copied from the spec -- the grading agent must never invent what "correct"
// means, and at least one scenario should be a near-miss whose expectation is
// that nothing triggers.
const scenarios = [
  { id: 'V1', isolate: true,  prompt: 'Add a new API route for deleting a user account.',
    expect: 'Should trigger the api-route-conventions skill and follow its error-handling pattern.' },
  { id: 'V2', isolate: false, prompt: 'What testing framework does this project use?',
    expect: 'Should answer "pytest" by reading CLAUDE.md, not by guessing or searching.' },
  { id: 'V3', isolate: false, prompt: 'Refactor the auth module to use async/await.',
    expect: 'Should NOT trigger the migration-safety skill -- this is a near-miss prompt.' },
]

const VERDICT = { type: 'object', required: ['verdict', 'evidence'], properties: {
  verdict: { type: 'string', enum: ['pass', 'fail'] }, evidence: { type: 'string' } } }

// Two stages over the same item. The second stage reads `s`, the original
// scenario -- not the first stage's return value, which is a plain string
// because that agent() call has no schema and so has no `.label` to read.
const grades = await pipeline(
  scenarios,
  s => agent(
    `Run: python "${SKILL_DIR}/scripts/run_e2e.py" --project . --prompt ${JSON.stringify(s.prompt)} ` +
    `--out .claude/.e2e-runs/${s.id} --json ${s.isolate ? '--isolate' : ''}. ` +
    `Report the summary.json contents back verbatim.`,
    { label: `run:${s.id}` },
  ),
  (_summary, s) => agent(
    `Grade .claude/.e2e-runs/${s.id}/transcript.jsonl against this expectation: "${s.expect}". ` +
    `Cite specific tool_use events or response text as evidence. ` +
    `Surface-level compliance without real supporting evidence is a FAIL, not a PASS.`,
    { label: `grade:${s.id}`, schema: VERDICT },
  ).then(v => ({ ...v, id: s.id })),
)

return { passed: grades.filter(g => g.verdict === 'pass').length, total: grades.length, grades }
```

Notice what the script never does: it never decides whether a transcript shows real trigger evidence, and it never decides what "correct behavior" means — both judgments live in the prompt strings and the spec, keeping judgment out of control flow. Route each failure to a repair target yourself using the feedback-routing table below; don't hand that table to another agent inside the workflow, since you're the one who then has to act on it.

**Two failure modes in this shape are worth naming, because both are silent.** First, `${CLAUDE_SKILL_DIR}` is substituted in a skill's own markdown body and in `allowed-tools` Bash rules — **not** in a workflow's prompt strings, and not in a subagent's shell environment. Written there, it arrives as literal text and becomes either a permission stall or a `python "/scripts/run_e2e.py"` file-not-found, which reads like a permissions problem and isn't one. Resolve the absolute path in the composing session. Second, an `agent()` call **without** a `schema` returns its final text as a plain string, so reading a property off it (`run.label`, `run.id`) silently yields `undefined` and you get a path like `.e2e-runs/undefined/`. Either attach a schema, or carry the identity from the original item the way the second stage above does.

### Fallback when dynamic workflows are unavailable

Workflows require Claude Code v2.1.154+, a paid plan (and on Pro specifically, opt-in via `/config`), and can be turned off outright with `disableWorkflows` or `CLAUDE_CODE_DISABLE_WORKFLOWS`. Don't assume any of that is true. When it isn't, run the exact same three-phase sequence as ordinary subagent calls in plain conversation turns instead: spawn one subagent per scenario to run `run_e2e.py` (sequentially, or in a single message with multiple Agent calls if you want them concurrent), then spawn one grading subagent per transcript with the same evidence-citation instructions, then synthesize the report yourself in the main thread. The scenarios, the expected-behavior text, and the grading doctrine below are identical either way — only the launch mechanism changes. Never let the absence of workflows become an excuse to skip e2e or to grade more loosely; state the fallback path is what's happening and proceed.

## Scenario count and model choice

Default to 2-4 scenarios: start small and look deeply at each result rather than spreading thin across a dozen shallow checks. A grading agent that has to produce evidence-cited verdicts for 12 transcripts either takes forever or starts skimming, and skimming is exactly how surface compliance slips past as a false PASS. Expand past 4 only when the user asks for broader coverage or the spec's Behavior inventory genuinely has more independent things worth checking than 4 scenarios can cover — don't pad the count for its own sake.

Default the model to the user's actual currently-configured model, not a cheaper stand-in. The entire point of e2e is behavioral fidelity — does the *real* model, under *real* session conditions, actually trigger this skill and follow this rule — and a cheap model's trigger behavior and instruction-following are not the same distribution as what the user will experience day to day. `--model` is available on `run_e2e.py` as an explicit cost/fidelity tradeoff, but offer it as a named tradeoff ("this will be cheaper but may not represent how your actual sessions behave") rather than defaulting to it silently. If the user is cost-sensitive, let them choose that tradeoff with eyes open.

With/without-harness A/B comparison is optional in v1, not a default. It earns its cost in two situations specifically: a fresh build, where the user is curious what baseline behavior looks like without any harness at all (motivating evidence for why the harness is worth having); and an improve-mode pass, where comparing old-harness-behavior against new-harness-behavior on the same scenario is the most direct evidence a fix actually worked. Outside those two cases, skip it — doubling every scenario to get a baseline nobody asked to see is exactly the kind of scope creep this skill is designed to resist.

## The assertion types

Every scenario's expected behavior should map to one of these five checkable assertion types. Pick the type (or types) the scenario is actually testing before you write its expected-behavior text — an assertion that doesn't fit one of these rows is probably not concretely checkable, and needs rewording before it goes in the spec.

| Assertion type | Evidence to look for |
|---|---|
| Skill trigger hit / near-miss | Does a `Skill` or `Read` tool_use event in the transcript reference the skill by name? For near-miss prompts (deliberately similar to a real trigger phrase but not meant to fire it), the correct evidence is the *absence* of that event — a near-miss scenario passes when the skill does NOT appear. |
| Hook fired / blocked | Two independent signals, both worth checking: the hook's own side effects (a log file it writes, a file it prevented from being edited) and the transcript's hook-related events (a blocked-tool-call entry, Claude's visible reaction — did it stop, explain the block, retry differently, or plow through). Either signal alone is weaker than both together. |
| Behavior compliance | A grading agent directly comparing the spec's expected behavior against what the transcript actually shows the model doing, with cited evidence — this is the least mechanically checkable type and the one most prone to a lazy PASS, so hold it to the same evidence-citation bar as the others. |
| CLAUDE.md knowledge reflected | Ask a project-fact question the CLAUDE.md is supposed to answer (test runner, build command, an architecture decision) and check the final response for correctness — not for the presence of the right words, for the actual right fact. |
| Artifact quality | Inspect files the session actually created or modified, ideally in an isolated copy so a bad run never touches the real project. Read the file, don't trust the transcript's description of the file — a transcript can claim it wrote correct code while the file itself is empty or wrong. |

**Two of these five want a rubric; the other three don't.** *Skill trigger*, *hook fired*, and *CLAUDE.md knowledge* are binary — an event is in the transcript or it isn't, a fact is right or wrong — so a rubric adds ceremony without adding resolution. *Behavior compliance* and *artifact quality* are the two where a grader can reasonably return "mostly," and they're also the two most prone to a lazy PASS, so for those add a `rubric:` to the spec's scenario listing the dimensions that matter and have the grader score each one:

```markdown
| V4 | Artifact quality | Generated migration has a rollback path | rubric: has-rollback; idempotent; names the table |
```

If you widen the grader's schema to return per-dimension scores rather than one verdict, **update whatever filters the results in the same edit** — the skeleton above filters on `g.verdict`, and a schema that no longer returns `verdict` makes that filter silently match nothing, so the workflow reports a clean pass over zero scenarios.

## Grading doctrine: evidence-citation required, surface compliance is a FAIL

This is the single most important grading habit, because it's the difference between an e2e tier that catches real problems and one that produces reassuring-looking JSON that means nothing.

The rule: every verdict a grading agent produces must name the specific transcript line, tool_use event, or file content it's based on. "The skill triggered correctly" is not a verdict; "the transcript's third tool_use event calls `Skill` with `skill: 'api-route-conventions'`" is a verdict. If a grading agent can't point at something concrete, the honest verdict is FAIL, not a vague pass — the burden of proof to pass sits on the assertion, not on the transcript to disprove it.

The second habit worth carrying over just as deliberately: surface-level compliance is not success. A scenario asking "does the harness prevent editing the protected `db/migrations/` directory" is satisfied on the surface if the transcript shows a blocked tool call — but if Claude's next move was to edit the same file through a Bash heredoc instead, the harness failed even though the specific hook "worked." A scenario asking whether an artifact was created correctly is satisfied on the surface if the right filename exists — but if the file is empty or the content is wrong, the task failed even though the assertion as literally worded passed. Grade the underlying outcome the assertion was trying to protect, not the letter of the assertion. When you notice an assertion that would pass even for an obviously wrong output, say so in the report rather than letting it pass quietly — a passing grade on a weak assertion is worse than no assertion at all, because it manufactures false confidence in a harness that hasn't actually been checked.

## Feedback routing: from failure symptom to repair target

Every failure should resolve to one specific layer to edit — never "make it work better" in the abstract. This table is the same layer-routing logic from SKILL.md's framework, run in reverse: instead of asking "which layer does this new requirement belong in," you're asking "which layer's placement decision was wrong, given how it actually behaved."

| Symptom | Repair target |
|---|---|
| Skill doesn't trigger, or triggers on prompts it shouldn't | Fix the description — strengthen boundary language. This is almost always a wording problem, not a body-content problem. |
| Skill triggers but the behavior it produces is wrong | Fix the skill body — and specifically, strengthen the *why* before reaching for more rules. A skill that states a principle convincingly gets followed more reliably than one with a longer checklist; adding a fifth bullet to a body that already isn't landing rarely helps. |
| An always-required rule gets ignored | First, strengthen the CLAUDE.md phrasing. If that's still not enough after a re-run, escalate it to a hook — this is a real re-decision about which layer the requirement belongs in (advisory vs. enforced), not just a wording tweak, so treat it with the same weight as the original layer-routing choice. |
| Hook doesn't fire | Recheck the matcher and event choice, and reproduce the exact input with `test_hook.py` before touching anything else — this isolates whether the problem is the hook's logic or its trigger condition. |
| Hook over-fires (blocks legitimate work) | Narrow the matcher, or downgrade the hook from a hard block to a warning if the underlying concern doesn't actually justify blocking. |
| An agent ignores a rule that CLAUDE.md clearly states | Check first whether the agent is a built-in Explore or Plan agent — both never load CLAUDE.md at all, by design, regardless of how the rule is worded. If so, the fix is a restated delegation prompt that repeats the relevant constraint directly, or a custom agent with the rule baked into its own system prompt. |
| The session feels slow or expensive | Check hook count and their timeouts, CLAUDE.md length, and the total skill-description budget across all installed skills — any of the three can silently inflate every single turn's cost, not just the turns that use them. |
| A component seems to earn nothing | Raise retirement as a question, never as an action — see below. |

### Retiring a component

A harness only grows unless something makes it shrink, and every layer keeps charging rent whether or not it earns it: a skill's description sits in the listing budget on every session even when the skill never fires, a rule without `paths:` loads at launch forever, an agent adds a routing decision every time it exists as an option. So an improve pass should look for what to remove, not only what to add.

**Every retirement candidate is a question with its cost stated, and never an action.** You cannot measure this from disk — there is no invocation telemetry, so "unused" is not something you can observe, only something the user can tell you. Deleting something a user deliberately added is far worse than leaving it: they had a reason, it may have been working exactly as intended, and silence looks like it was never there. Ask like this: "`changelog-helper`'s description costs part of the skill listing budget every session — is it still earning that, or should we retire it?"

Offer the middle setting before deletion. `disable-model-invocation: true` keeps a skill available under its explicit `/name` while removing it from auto-triggering, which fits the common case of "I still want it, I just don't want it firing on its own."

When something is retired, mark the spec row `status: retired` rather than deleting it. Same reason as `declined`: the next pass otherwise re-proposes it, and the harness loses the record of a decision that was made deliberately.

## Re-run discipline

After a repair, re-run only the scenarios that failed — not the whole suite. This is a direct cost-containment rule, not a suggestion: e2e already costs real tokens per scenario, and re-running scenarios that already passed to "make sure nothing broke" burns budget without new information, since a change scoped to fix one skill's description has no plausible mechanism to break an unrelated hook test that already passed. Record the outcome in the spec's Validation section regardless of which way it went — a fix that still fails after a re-run is exactly as important to have on record as one that now passes, because the next person (or the next you, next month) needs to see the history, not just the current state.

## Headless permission handling: unverified in this build, verify once yourself

State this plainly to the user the first time you propose running e2e for real, in these words or close to them: headless `-p` mode's permission handling — which combination of `--permission-mode`, `--dangerously-skip-permissions`, and pre-registered `permissions.allow` entries actually lets a scenario run to completion without stalling — is this file's best documented guess, not a confirmed fact. A `claude` child process spawned via Bash can itself fail with "Not logged in" even on a simple headless call, because the host session's OAuth/keychain credentials don't propagate to a Bash-spawned child — which is exactly the link `run_e2e.py`'s `claude -p` invocation depends on. That invocation was built from documented behavior and has never been watched to succeed end to end, so the first real e2e run is the actual confirmation, not this file.

The likely-correct approach, and the one `run_e2e.py` implements as its default, is an isolated project copy (`--isolate`) combined with skip-permissions — a scenario that can't damage the real project because it's not touching the real project, running without permission prompts because there's no interactive terminal to answer them in a headless call anyway. That is a reasoned default, not a verified one. Do not present it to the user as already confirmed, and do not let this document's confidence in the reasoning substitute for an actual run. The first time you run e2e for real against a user's project, in an environment where `claude` is actually authenticated, treat *that run's outcome* as the confirmation — if scenarios complete and produce a sensible transcript, the mechanism works and you can stop flagging this; if a scenario stalls waiting on a permission prompt that never gets answered, or fails with an auth-shaped error, that's the signal to adjust the flag combination, not a sign something else is broken. Either way, note the outcome in the spec's Validation section so it doesn't need re-litigating on the next e2e run in the same project.

## What e2e cannot cover

The interview itself can never be e2e-tested. `AskUserQuestion` is unavailable in headless (`-p`) and subagent contexts, so there is no way to spawn a scripted session that exercises the interview flow the way a real user would. The only validation path for the interview protocol — question phrasing, proficiency calibration, the gate sequence — is dogfooding: running it manually, interactively, yourself, against a real or sample project, and noticing where it feels wrong. Don't let a clean e2e report create the impression that the whole skill has been validated end to end; it validates the *generated harness*, never the *interview that produced it*.
