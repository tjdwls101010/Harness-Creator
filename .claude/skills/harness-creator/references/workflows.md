# Workflows

This is the authoring guide for `.claude/workflows/*.js` — the layer that turns an orchestration into a checked-in, rerunnable artifact instead of something Claude re-improvises turn by turn.

## The decision: is the orchestration itself the deliverable?

Every other layer routes a behavior, a fact, or a constraint; a workflow routes a *plan*, and the plan itself is the repeatable thing. The test: is this orchestration fixed in shape, with only the arguments varying between runs, launched with one command and held to the same bar every time? A recurring release-readiness sweep is — same phases, same checks, only the branch name changes. If so, pre-define a thin `.claude/workflows/<name>.js` so it becomes `/name` and never needs re-explaining.

Before that, check you are on the right surface at all: a workflow is one of four ways Claude Code parallelizes work, and the four-way choice — plus what each one does and does not let a harness ship — is in `references/agents.md`.

If the shape varies each time — "audit these three files for this bug pattern", "compare these two approaches" — do not pre-define anything; next month's version fans out differently, verifies differently, or skips a stage. Put natural-language guidance in CLAUDE.md or a skill saying when and how to compose a fan-out/verify/synthesize on the fly ("use a workflow to ..." in a prompt is the same opt-in as the `ultracode` keyword). A rigid file for a variable task is a flexibility tax.

The ambiguous cases resolve on one question to the user, asked while collecting the component's detail: "will you run this the same way every time, or does it change based on what's being investigated?"

## Keep the script thin — judgment lives in the agent prompts, not the control flow

A workflow script should hold only the fan-out / collect / gate skeleton: which agents to spawn, over what list, gathered into what shape, checked against what condition. Every actual judgment call — what counts as a bug, how to phrase the audit question, what "looks suspicious" means, how to weigh conflicting findings — belongs inside the string you pass to `agent()`, never inside the JS control flow around it.

A thick workflow (if/else chains encoding decision logic, hardcoded severity thresholds, string-matching on agent output to decide what happens next) is where "Conviction over compliance" fails in the one layer that is code: glue stops being glue the moment it decides *what* to look for instead of *how many agents to run and in what order*. A conditional that encodes a judgment call rather than a control-flow gate — `if (finding.severity === 'high')` where "high" was invented by the script author — belongs in a prompt, with the agent asked to return a structured field for the gate to read.

## The default composable pattern: fan-out → verify → synthesize

When a workflow is warranted, start from this shape and adapt it rather than reinventing structure each time — it's the pattern the docs recommend precisely because a single pass of independent findings is less trustworthy than findings that survived a second, adversarial look:

1. **Fan-out** — one agent per independent unit of work (one file, one route, one source), each asked to find or produce something, ideally returning a structured result (`schema` option) rather than free text so the next stage can consume it programmatically.
2. **Verify** — a second wave of agents, each given one finding from stage 1 (not the whole batch) and asked to adversarially check it: is this actually true, does the evidence support the claim, would a skeptical reviewer accept it? This is the stage that catches a fan-out agent's overclaim or hallucinated finding before it reaches the user.
3. **Synthesize** — one final agent that receives all verified findings and produces the single artifact the user actually wanted (a ranked list, a report, a go/no-go verdict) — this is also the only stage whose output should reach Claude's context; everything upstream stays in script variables.

A starting silhouette, not a template: a "keep fixing until a check passes" workflow needs no verify stage because the check is the verifier, and a research workflow might verify against several independent sources instead of one adversarial pass.

## Hard gotchas — not general JS knowledge

- **The file must open with a pure-literal `meta` export.** `export const meta = { name: '...', description: '...' }` has to be a literal object — no variables, no function calls, no template-string interpolation inside it. This is a hard parser requirement: the runtime reads the file to extract `meta` before it ever executes anything, so `meta` can't depend on execution. Everything after that line is plain JavaScript with top-level `await` — you write `agent()`/`pipeline()` calls directly at the top level, no wrapping `async function main()` needed.
- **A workflow script cannot observe wall-clock time or randomness at all.** `Date.now()`, `Math.random()` and argless `new Date()` throw inside the script, so that relaunching a run repeats the same `agent()` calls. Design around it rather than discovering it: anything that varies per run arrives through `args`, or is stamped onto the result after the workflow returns.
- **A file at `.claude/workflows/<name>.js` auto-registers as `/<name>`.** No separate registration step — dropping the file in is the registration. Project-scope (`.claude/workflows/`, checked into the repo, shared with every clone) shadows personal-scope (`~/.claude/workflows/`, local to one user) on a name collision, so if you're generating a project workflow and the user already has a personal one with the same name, the generated one is what actually runs for them in this repo — worth flagging during generation rather than letting them discover it by surprise.
- **Pre-approve what a workflow's agents need, because an agent permission prompt can leave an unattended run paused.** They use your permission rules and resolve their mode the way any subagent does, so an agent can land on a permission prompt — the only thing that can pause a run. So if a fan-out runs `npm test` or fetches a URL, generate the matching `permissions.allow` entries in the same pass and the same commit, treat them as one deliverable, and record in the spec's Design rationale why they exist: on disk they read as ordinary convenience allowances, and the next person to tighten permissions deletes them and leaves a workflow that hangs. The launch itself is a tool call too, and in `claude -p` and the SDK there is no dialog to approve it — a `Workflow` allow rule (or `Workflow(<name>)` for one saved workflow) is the plainest way to let it start there, though auto mode's classifier, bypass mode, a `PreToolUse` hook returning allow, or the host's own approval callback each do it as well.
- **Workflows are gated behind version, plan, and explicit opt-in — and can be turned off entirely.** They require Claude Code v2.1.154+ and a paid plan; on the Pro tier the user must also opt in via the "Dynamic workflows" row in `/config`; `disableWorkflows` (settings.json) or `CLAUDE_CODE_DISABLE_WORKFLOWS` turns them off outright. Four gates, three of which live outside the repository, mean this is not a capability you can read off the project: assume nothing and check the ones you can see (version, the settings key) before generating a `/name` the user's tier or org may never expose. And since a gate can close after you generate — a plan change, an org setting — a harness that leans on a workflow for something functionally important owes the user a way to get the job done without `/name`, written where the workflow is referenced: usually the same phases run as ordinary subagents through conversation turns, which is the fallback the gates cannot switch off; a different fallback is fine when the work has one.
- **Launching a workflow prompts for approval, and how often depends on the mode.** Manual and accept-edits prompt on every run until the user picks "don't ask again" for that workflow in that project; auto mode prompts on the first launch only and records the consent; bypass mode and `claude -p` never prompt. Worth one line in a generated README or CLAUDE.md, so the first `/name` stopping for confirmation reads as designed — and worth naming the "don't ask again" option, which is the difference between friction and a one-button command.
- **The script itself cannot touch the filesystem or shell.** No `fs.readFile`, no `exec`, nothing — only the `agent()` calls it spawns can read files, write files, or run commands. The script's job is purely to hold variables and control flow between agent calls; treat any temptation to do direct I/O from the script as a sign the work belongs in an agent prompt instead.
- **Concurrency has hard caps: 16 simultaneous agents (fewer on machines with few cores), 1,000 total per run.** They are backstops against runaway loops, not a budget: size the fan-out to the real unit count (one agent per file, per route, per source) and let the cap be a net you never expect to hit.

## A properly-thin example: fan-out, adversarial verify, synthesize

```javascript
export const meta = {
  name: 'audit-auth-routes',
  description: 'Audit every route handler under src/routes/ for missing authentication checks, cross-verify each finding, and report only what survives verification.',
}

// --- Stage 1: fan-out.
const discovered = await agent(
  'List every file under src/routes/ that defines an HTTP route handler. Return only real route-handler files, not test files, mocks, or shared utilities.',
  { schema: { type: 'object', required: ['files'], properties: { files: { type: 'array', items: { type: 'string' } } } } },
)

// One independent agent per file. The script only knows "per file."
const findings = await pipeline(discovered.files, file =>
  agent(
    `Audit ${file} for a missing authentication check on any route it defines. ` +
    `Quote the offending code as evidence, or report no finding if the file is clean.`,
    {
      label: file,
      schema: {
        type: 'object',
        required: ['file', 'hasFinding'],
        properties: {
          file: { type: 'string' },
          hasFinding: { type: 'boolean' },
          evidence: { type: 'string' },
          explanation: { type: 'string' },
        },
      },
    },
  ),
)

// --- Stage 2: adversarial verify. `hasFinding` is pure control flow;
// whether a finding is *valid* is the verifier's judgment, not this script's.
const candidates = findings.filter(f => f.hasFinding)

const verified = await pipeline(candidates, finding =>
  agent(
    `A prior review flagged ${finding.file}, citing: "${finding.evidence}". ` +
    `Check that claim against the file yourself. Try to refute it — a gap that turns ` +
    `out to be covered elsewhere, or a misread, is a rejection. Return verdict and reasoning.`,
    {
      label: finding.file,
      schema: {
        type: 'object',
        required: ['file', 'confirmed'],
        properties: { file: { type: 'string' }, confirmed: { type: 'boolean' }, reasoning: { type: 'string' } },
      },
    },
  ),
)

const confirmed = verified.filter(v => v.confirmed)

// --- Stage 3: synthesize. Only this return value reaches Claude's context;
// the raw findings and rejected claims stay in script variables.
if (confirmed.length === 0) {
  return { summary: 'Nothing survived verification.', findings: [] }
}

const report = await agent(
  `Write a short report of these confirmed findings, most severe first: ${JSON.stringify(confirmed)}`,
)

return { summary: report, findings: confirmed }
```
