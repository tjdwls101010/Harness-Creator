# E2E Testing

This is the second, deeper tier of harness validation. Read this once the user has consented to an e2e run, right before you compose and launch it.

## Why this tier exists at all

- `validate_harness.py` is free, structural, and runs on every generation with no consent needed: it catches a hook pointing at a script that doesn't exist, a skill with a dead link, a CLAUDE.md past 200 lines — and you already fix every error it finds before declaring the generation done.
- It does not tell you whether the harness changes Claude's behavior: a skill with perfect frontmatter can still never trigger because its description's boundary language is fuzzy; a hook can be syntactically flawless and still fire on the wrong tool, or never fire, because the matcher assumed a tool-call shape that turned out wrong.
- Lint proves the harness is well-formed; only a real run against a real prompt proves it does what the spec's Behavior inventory says it should do. That gap is what e2e closes — by spawning an actual headless Claude session against the generated harness and watching what happens.

This costs real tokens and wall-clock time — a handful of full agentic sessions per scenario — so it runs only with the user's explicit consent, gathered alongside the scenario list when the spec's Validation section is filled. Never launch it silently as part of "finishing" a generation: offer it, name the rough cost (scenario count × roughly one full session each), and proceed only on yes.

## Shape: a workflow composed on the spot, not a file you ship

There is no `e2e-runner.js` sitting in this skill's workflows directory, and you should not create one. The scenarios that need checking are different for every project — a fixed workflow file would either be too narrow for the next project or so generic it checks nothing real. This is the same principle that governs every other variable-shaped task in this skill: pre-defined structure is for orchestrations whose *shape* stays fixed between runs, and e2e's shape — the scenario list — is different every time. Compose the workflow at the moment you need it, from the spec's Validation section, and throw the composition away afterward; only the results get recorded, in the spec.

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

Run and Grade are two separate phases, not one — grading needs the *whole* transcript and summary already written to disk, and the next scenario's run shouldn't wait on the previous one's grading. Keep them as sequential stages within the composed workflow (all Runs, then all Grades), with independence *within* each stage, not across them.

### Annotated skeleton

This is illustrative, not a file to ship — adapt the scenario count, prompts, and grading dimensions to what the spec's Validation section actually lists.

```javascript
export const meta = {
  name: 'e2e-validate-harness',
  description: 'Run the spec Validation scenarios as headless sessions against the generated harness and grade each transcript.',
}

// Absolute path, resolved here -- ${CLAUDE_SKILL_DIR} is NOT substituted in
// workflow prompt strings (see gotcha below).
const SKILL_DIR = '/absolute/path/to/the/harness-creator/skill'

// One entry per scenario in the spec's Validation section; `expect` is
// copied verbatim from the spec -- the grading agent must never invent
// what "correct" means.
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

// Second stage reads `s` (the original scenario), not the first stage's
// return value -- that agent() call has no schema, so no `.label` (see below).
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

Notice what the script never does: it never decides whether a transcript shows real trigger evidence, or what "correct behavior" means — both live in the prompt strings and the spec, not in code. Route each failure to a repair target yourself using the feedback-routing table below; don't hand that table to another agent inside the workflow, since you're the one who then has to act on it.

**Two failure modes in this shape are worth naming, because both are silent.** First, `${CLAUDE_SKILL_DIR}` is substituted in a skill's own markdown body and in `allowed-tools` Bash rules — **not** in a workflow's prompt strings, and not in a subagent's shell environment. Written there, it arrives as literal text and becomes either a permission stall or a `python "/scripts/run_e2e.py"` file-not-found, which reads like a permissions problem and isn't one. Resolve the absolute path in the composing session. Second, an `agent()` call **without** a `schema` returns its final text as a plain string, so reading a property off it (`run.label`, `run.id`) silently yields `undefined` and you get a path like `.e2e-runs/undefined/`. Either attach a schema, or carry the identity from the original item the way the second stage above does.

### Fallback when dynamic workflows are unavailable

Workflows require Claude Code v2.1.154+, a paid plan (and on Pro specifically, opt-in via `/config`), and can be turned off outright with `disableWorkflows` or `CLAUDE_CODE_DISABLE_WORKFLOWS`. Don't assume any of that is true. When it isn't, run the same three-phase sequence as ordinary subagent calls in plain conversation turns: spawn one subagent per scenario to run `run_e2e.py` (sequentially, or concurrently via multiple Agent calls in one message), then spawn one grading subagent per transcript with the same evidence-citation instructions, then synthesize the report yourself in the main thread. The scenarios, expected-behavior text, and grading doctrine are identical either way — only the launch mechanism changes. Never let the absence of workflows become an excuse to skip e2e or to grade more loosely; state the fallback path is what's happening and proceed.

## Scenario count and model choice

Default to 2-4 scenarios: start small and look deeply at each result rather than spreading thin across a dozen shallow checks. A grading agent that has to produce evidence-cited verdicts for 12 transcripts either takes forever or starts skimming, and skimming is how surface compliance slips past as a false PASS. Expand past 4 only when the user asks for broader coverage or the spec's Behavior inventory genuinely has more independent things worth checking than 4 scenarios can cover — don't pad the count for its own sake.

Default the model to the user's actual currently-configured model, not a cheaper stand-in — the point of e2e is behavioral fidelity: does the *real* model, under *real* session conditions, trigger this skill and follow this rule, and a cheap model's trigger behavior isn't the same distribution as what the user experiences day to day. `--model` is available on `run_e2e.py` as an explicit cost/fidelity tradeoff; offer it by name ("this will be cheaper but may not represent how your actual sessions behave") rather than defaulting to it silently, and let a cost-sensitive user choose it with eyes open.

With/without-harness A/B comparison is optional in v1, not a default. It earns its cost in two situations:

- Fresh build — the user is curious what baseline behavior looks like without any harness at all (motivating evidence for why the harness is worth having).
- A repair pass on an existing harness — comparing old-harness-behavior against new-harness-behavior on the same scenario is the most direct evidence a fix actually worked.

Outside those two cases, skip it — doubling every scenario to get a baseline nobody asked to see is exactly the kind of scope creep this skill is designed to resist.

## The assertion types

Every scenario's expected behavior should map to one of these five checkable assertion types. Pick the type (or types) the scenario is actually testing before you write its expected-behavior text — an assertion that doesn't fit one of these rows is probably not concretely checkable, and needs rewording before it goes in the spec.

| Assertion type | Evidence to look for |
|---|---|
| Skill trigger hit / near-miss | Does a `Skill` or `Read` tool_use event reference the skill by name? For near-miss prompts (similar to a real trigger phrase but not meant to fire it), the correct evidence is the *absence* of that event — a near-miss scenario passes when the skill does NOT appear. |
| Hook fired / blocked | Two independent signals: the hook's own side effects (a log file it writes, a file it prevented from being edited) and the transcript's hook-related events (a blocked-tool-call entry, Claude's visible reaction — did it stop, explain the block, retry differently, or plow through). Either signal alone is weaker than both together. |
| Behavior compliance | A grading agent directly comparing the spec's expected behavior against what the transcript actually shows the model doing, with cited evidence — the least mechanically checkable type and the one most prone to a lazy PASS, so hold it to the same evidence-citation bar as the others. |
| CLAUDE.md knowledge reflected | Ask a project-fact question the CLAUDE.md is supposed to answer (test runner, build command, an architecture decision) and check the final response for correctness — not for the presence of the right words, for the actual right fact. |
| Artifact quality | Inspect files the session actually created or modified, ideally in an isolated copy so a bad run never touches the real project. Read the file, don't trust the transcript's description of the file — a transcript can claim it wrote correct code while the file itself is empty or wrong. |

**Two of these five want a rubric; the other three don't.** *Skill trigger*, *hook fired*, and *CLAUDE.md knowledge* are binary — an event is in the transcript or it isn't, a fact is right or wrong — so a rubric adds ceremony without adding resolution. *Behavior compliance* and *artifact quality* are the two where a grader can reasonably return "mostly," and they're also the two most prone to a lazy PASS, so for those add a `rubric:` to the spec's scenario listing the dimensions that matter and have the grader score each one:

```markdown
| V4 | Artifact quality | Generated migration has a rollback path | rubric: has-rollback; idempotent; names the table |
```

If you widen the grader's schema to return per-dimension scores rather than one verdict, **update whatever filters the results in the same edit** — the skeleton above filters on `g.verdict`, and a schema that no longer returns `verdict` makes that filter silently match nothing, so the workflow reports a clean pass over zero scenarios.

## Grading doctrine: evidence-citation required, surface compliance is a FAIL



The rule: every verdict a grading agent produces must name the specific transcript line, tool_use event, or file content it's based on. "The skill triggered correctly" is not a verdict; "the transcript's third tool_use event calls `Skill` with `skill: 'api-route-conventions'`" is a verdict. If a grading agent can't point at something concrete, the honest verdict is FAIL — the burden of proof to pass sits on the assertion, not on the transcript to disprove it.

Surface-level compliance is not success. A scenario asking "does the harness prevent editing the protected `db/migrations/` directory" is satisfied on the surface if the transcript shows a blocked tool call — but if Claude's next move was to edit the same file through a Bash heredoc instead, the harness failed even though the specific hook "worked." A scenario asking whether an artifact was created correctly is satisfied on the surface if the right filename exists — but if the file is empty or the content is wrong, the task failed even though the assertion as literally worded passed. Grade the underlying outcome the assertion was trying to protect, not the letter of the assertion. When you notice an assertion that would pass even for an obviously wrong output, say so in the report — a passing grade on a weak assertion manufactures false confidence in a harness that hasn't actually been checked.

## Feedback routing

Every failure resolves to one layer to edit, never to "make it work better" in the abstract. The map is SKILL.md's layer-routing table, whose repair column runs the same routing backwards, and its rules for repairing the smallest causally supported set, re-running only the changed surface, and retiring a component as a question with its cost stated. Route each failure yourself; don't hand that judgment to another agent inside the workflow, since you are the one who then has to act on it.

## Re-run discipline

After a repair, re-run only the scenarios that failed — not the whole suite. This is cost-containment, not a suggestion: re-running scenarios that already passed to "make sure nothing broke" burns budget without new information, since a change scoped to fix one skill's description has no plausible mechanism to break an unrelated hook test that already passed. Record the outcome in the spec's Validation section regardless of which way it went — a fix that still fails after a re-run is exactly as important to have on record as one that now passes, because the next person (or the next you, next month) needs to see the history, not just the current state.

## Headless permission handling: the mechanism is settled, the machine never is

Headless `-p` permission handling — which combination of `--permission-mode`, `--dangerously-skip-permissions`, and pre-registered `permissions.allow` entries lets a scenario run to completion without stalling — went four generations without a confirmed run and now has one: `--isolate` plus skip-permissions completed three scenarios on 2026-08-22 (`claude` 2.1.239), no auth failure, no permission stall.

That settles the flag combination and it does not settle the box you are on, because **auth is per-machine**: the credentials a spawned `claude` needs are the ones where it spawns, not the ones the calling session holds. A `claude` child spawned via Bash can fail with "Not logged in" even on a simple headless call, because the host session's OAuth/keychain credentials don't always propagate to a Bash-spawned child — and that link is what `run_e2e.py`'s `claude -p` invocation depends on.

The likely-correct approach is an isolated project copy combined with skip-permissions — a scenario that can't damage the real project because it isn't touching the real project, running without permission prompts because there's no interactive terminal to answer them in a headless call anyway. **`--isolate` is opt-in**, so choosing it is a decision you make per run: without it the headless session runs in the user's actual working tree, and a scenario that writes will write there. Attach it for anything that isn't purely read-only, use `--permission-mode` when a scenario needs to run under a specific mode rather than with permissions skipped, and say which you picked when you propose the run. Add `--keep-isolated` when the scenario grades *files* rather than the transcript — the copy is where the generated files are, and it is deleted otherwise. Delete it yourself once you have graded: a project copy per run is not collected by anything else, and eight gigabytes of them accumulated here before this was noticed.

So on a machine you have not run this on before, say to the user that the first run *is* the confirmation, and read its outcome that way: scenarios that complete with a sensible transcript settle it for this machine and you can stop flagging it; a scenario that stalls on a permission prompt nobody answers, or an auth-shaped failure, is a signal to adjust the flag combination rather than evidence that something else is broken. Note which happened in the spec's Validation section, so the next e2e run in this project doesn't re-litigate it.

## What e2e cannot cover

The interview itself can never be e2e-tested. `AskUserQuestion` is unavailable in headless (`-p`) and subagent contexts, so there is no way to spawn a scripted session that exercises the interview flow the way a real user would. The only validation path for the interview — question phrasing, proficiency calibration, the approval sequence — is dogfooding: running it manually, interactively, yourself, against a real or sample project, and noticing where it feels wrong. Don't let a clean e2e report create the impression that the whole skill has been validated end to end; it validates the *generated harness*, never the *interview that produced it*.
