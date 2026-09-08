# E2E Testing

Use this guide when the approved behavior needs evidence from a real model session. Structural checks establish file shape; scenarios establish what happens on the requests the harness must serve.

`validate_harness.py` checks the harness's structure; a real run against a real prompt supplies evidence about the behavior the user approved. A skill with perfect frontmatter can still never trigger because its description's boundary language is fuzzy, and a hook can be syntactically flawless and fire on the wrong tool, or never, because the matcher assumed a tool-call shape that turned out wrong. e2e closes that gap by spawning a headless Claude session against the generated harness and watching what happens.

## Shape: a workflow composed on the spot, not a file you ship

The scenarios differ for every project, so a fixed workflow file would be too narrow for the next project or too generic to check anything real. Compose the workflow when you need it, from scenarios whose expected behavior and evidence were settled with the design, before generation, and throw the composition away afterward. The scenario, its expectation and the latest result are kept in the handoff; the composition is not.

Three phases, because each needs something the one before it produced: **Run** — one agent per scenario, running `run_e2e.py` via Bash, scenarios pipelined independently so a slow one doesn't block a fast one. **Grade** — one agent per transcript, every verdict citing transcript evidence. **Report** — pass/fail across scenarios plus a concrete repair target per failure. Run and Grade stay separate stages because grading needs the whole transcript and summary already on disk, while the next scenario's run shouldn't wait on the previous one's grading. A single-scenario check can collapse Grade and Report into one agent — what cannot collapse is Run into Grade, since a grader that also ran the scenario is grading its own work from memory rather than from the transcript.

### Annotated skeleton

Illustrative, not a file to ship — adapt scenario count, prompts, and grading dimensions to the behaviours under test.

```javascript
export const meta = {
  name: 'e2e-validate-harness',
  description: 'Run the approved scenarios as headless sessions against the generated harness and grade each transcript.',
}

// Both resolved in the composing session: ${CLAUDE_SKILL_DIR} is NOT
// substituted in workflow prompt strings (see below), and the spawned
// claude picks its own default model unless told the user's.
const SKILL_DIR = '/absolute/path/to/the/harness-creator/skill'
const MODEL = 'the-model-the-user-actually-runs'

// One entry per approved scenario; `expect` is copied verbatim from
// what the user approved -- the grading agent must never invent
// what "correct" means. `keep` marks a scenario graded on files: the
// isolated copy is kept and its path lands in summary.json.
const scenarios = [
  { id: 'V1', isolate: true, keep: true, prompt: 'Add a new API route for deleting a user account.',
    expect: 'Should trigger the api-route-conventions skill and follow its error-handling pattern.' },
  { id: 'V2', isolate: false, prompt: 'What testing framework does this project use?',
    expect: 'Should answer "pytest" by reading CLAUDE.md, not by guessing or searching.' },
  { id: 'V3', isolate: true, prompt: 'Refactor the auth module to use async/await.',
    expect: 'Should NOT trigger the migration-safety skill -- this is a near-miss prompt.' },
]

const VERDICT = { type: 'object', required: ['verdict', 'evidence'], properties: {
  verdict: { type: 'string', enum: ['pass', 'fail'] }, evidence: { type: 'string' } } }

// Second stage reads `s` (the original scenario), not the first stage's
// return value -- that agent() call has no schema, so no `.label` (see below).
const grades = await pipeline(
  scenarios,
  s => agent(
    `Run: python "${SKILL_DIR}/scripts/run_e2e.py" --project . --model ${MODEL} ` +
    `--prompt ${JSON.stringify(s.prompt)} --out .claude/.e2e-runs/${s.id} --json ` +
    `${s.isolate ? '--isolate' : ''} ${s.keep ? '--keep-isolated' : ''}. ` +
    `Report the summary.json contents back verbatim.`,
    { label: `run:${s.id}` },
  ),
  (_summary, s) => agent(
    `Grade .claude/.e2e-runs/${s.id}/transcript.jsonl against this expectation: "${s.expect}". ` +
    `If summary.json names an isolated_copy, read the files there rather than the transcript's account of them. ` +
    `Cite specific tool_use events, response text or file contents as evidence. ` +
    `Surface-level compliance without real supporting evidence is a FAIL, not a PASS.`,
    { label: `grade:${s.id}`, schema: VERDICT },
  ).then(v => ({ ...v, id: s.id })),
)

return { passed: grades.filter(g => g.verdict === 'pass').length, total: grades.length, grades }
```

The script never decides whether a transcript shows real trigger evidence or what "correct behavior" means — both live in the prompt strings, from what the user approved. The Report phase is yours, in the main session: take the returned `grades`, route each failure to a repair target with SKILL.md's layer-routing table, and delete any kept isolated copies once graded. Don't hand that judgment to an agent inside the workflow, since you are the one who then acts on it. Before launching, check that `permissions.allow` covers the Bash call the Run agents make — a workflow's agents stall on an unapproved call with nobody watching the prompt (references/workflows.md) — or take the fallback below.

**Two failures in this shape are silent.** `${CLAUDE_SKILL_DIR}` is substituted in a skill's own markdown and in `allowed-tools` rules — **not** in a workflow's prompt strings or a subagent's shell environment. Written there it arrives as literal text and becomes a permission stall or a `python "/scripts/run_e2e.py"` file-not-found, which reads like a permissions problem and isn't one; resolve the absolute path in the composing session. And an `agent()` call **without** a `schema` returns its final text as a plain string, so reading a property off it (`run.label`, `run.id`) silently yields `undefined` and a path like `.e2e-runs/undefined/`; attach a schema, or carry the identity from the original item as the second stage above does.

### Fallback when dynamic workflows are unavailable

Workflows are gated on version, plan, an opt-in on the Pro tier, and two off switches (references/workflows.md), so don't assume they are there. When they aren't, run the same three phases as ordinary subagent calls in conversation turns: one subagent per scenario running `run_e2e.py`, then one grading subagent per transcript with the same evidence-citation instructions, then the report in the main thread. Scenarios, expectations and grading doctrine are identical; only the launch mechanism changes. Say that the fallback is what is happening, and grade no more loosely for it.

## Scenario count and model choice

Choose scenarios to cover the independent behaviors and failure modes in the approved design. Include intended triggers, neighboring requests that should not trigger, legitimate operations a boundary must allow, and alternate paths that could bypass it where relevant. Each scenario needs its own evidence-based verdict; a larger set does not justify shallower grading.

Use the model the harness will actually serve. Triggering and instruction-following differ between models, so a result on another model does not establish the behavior of the target one. If the harness must support several models, identify which claims need checking on each; the runner's CLI exposes model selection.

Use a with/without-harness or old/new comparison when the claim concerns what the harness changes. Hold the task and relevant environment constant so the comparison can attribute the observed difference; a single successful run is not evidence that the harness caused the success.

## The assertion types

Every scenario's expected behaviour should map to a checkable assertion type. These five have covered what harnesses so far needed; a scenario that fits none of them needs its evidence spelled out with the same precision before it runs, not a looser wording.

| Assertion type | Evidence to look for |
|---|---|
| Skill trigger hit / near-miss | Does a `Skill` or `Read` tool_use event reference the skill by name? For a near-miss prompt (similar to a real trigger phrase but not meant to fire it), the correct evidence is the *absence* of that event. |
| Hook fired / blocked | Two independent signals: the hook's own side effects (a log it writes, a file it kept from being edited) and the transcript's hook events (a blocked-tool-call entry, Claude's visible reaction — did it stop, explain, retry differently, or plow through). Either alone is weaker than both. |
| Behavior compliance | A grader comparing the approved behaviour against what the transcript shows the model doing, with cited evidence — the least mechanically checkable type and the most prone to a lazy PASS. |
| CLAUDE.md knowledge reflected | Ask a project-fact question CLAUDE.md is supposed to answer and check the final response for the right fact, not the right words. |
| Artifact quality | Inspect the files the session created or modified, in an isolated copy. Read the file; a transcript can claim it wrote correct code while the file is empty or wrong. |

A binary assertion — an event is in the transcript or it isn't, a fact is right or wrong, as with trigger, hook and knowledge — needs no rubric; it would add ceremony without resolution. An assertion a grader can honestly call "mostly" satisfied, as with compliance and artifact quality, is where the lazy PASS lives, so give that scenario a `rubric:` listing the dimensions that matter, and have the grader score each:

```markdown
| V4 | Artifact quality | Generated migration has a rollback path | rubric: has-rollback; idempotent; names the table |
```

If you widen the grader's schema to per-dimension scores, **update whatever filters the results in the same edit** — the skeleton filters on `g.verdict`, and a schema that no longer returns it makes that filter match nothing, so the workflow reports a clean pass over zero scenarios.

## Grading doctrine: evidence-citation required, surface compliance is a FAIL

Every verdict names the transcript line, tool_use event, or file content it rests on. "The skill triggered correctly" is not a verdict; "the transcript's third tool_use event calls `Skill` with `skill: 'api-route-conventions'`" is. A grader that cannot point at something concrete returns FAIL — the burden of proof sits on the assertion, not on the transcript to disprove it.

Grade the outcome the assertion was protecting, not its letter. "Does the harness prevent editing `db/migrations/`" is satisfied on the surface by a blocked tool call — and failed if Claude's next move edited the same file through a Bash heredoc. "Was the artifact created" is satisfied by the right filename — and failed if the file is empty. When an assertion would pass an obviously wrong output, say so in the report: a passing grade on a weak assertion manufactures confidence in a harness nobody checked.

## Re-run discipline

After a repair, re-run the scenarios that failed and any whose surface the repair touched — a description edit reaches only that skill's scenarios, a CLAUDE.md edit reaches every scenario that read it. Re-running everything else buys no information; skipping a scenario the change reaches hides a regression. Record the outcome in the handoff either way: a fix that still fails is as important to have on record as one that now passes.

## Headless permission handling: the mechanism is settled, the machine never is

The flag combination that lets a headless scenario run to completion is settled (`--isolate` with skip-permissions, confirmed against real sessions). What it does not settle is the box you are on, because **auth is per-machine**: the credentials a spawned `claude` needs are the ones where it spawns, and a child spawned via Bash can fail with "Not logged in" even when the calling session is logged in.

Run any scenario that can write in an isolated copy, and retain that copy until its artifacts have been graded. When the claim depends on a particular permission mode, select it with `--permission-mode`: a run with permissions skipped cannot establish behavior under another mode. State the environment used alongside the result and clean up retained copies after inspection. The runner's `--help` defines the flags for isolation and retention.

On a machine you have not run this on before, tell the user the first run *is* the confirmation and read its outcome that way: scenarios that complete with a sensible transcript settle it; a stall on a permission prompt nobody answers means adjust the permission flags; "Not logged in" means the spawned `claude` needs authenticating on that machine, and no flag fixes it. Note which happened in the handoff so the next run doesn't re-litigate it.

## What e2e cannot cover

The interview can never be e2e-tested: `AskUserQuestion` is unavailable in headless (`-p`) and subagent contexts, so no scripted session can exercise question phrasing, calibration to the user's proficiency and vocabulary, or the approval sequence the way a real user would. That is verified only by dogfooding — running it yourself, interactively, against a real or sample project. A clean e2e report validates the *generated harness*, never the interview that produced it.
