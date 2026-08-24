# Workflows

This is the authoring guide for `.claude/workflows/*.js` — the layer that turns an orchestration into a checked-in, rerunnable artifact instead of something Claude re-improvises turn by turn. Read this before deciding whether an interview item deserves a workflow file, and before drafting one.

## The decision: is the orchestration itself the deliverable?

Every other layer in this skill routes a behavior, a fact, or a constraint. Workflows are different — what you're routing here is a *plan*, and the plan itself becomes the repeatable thing, not the outcome it produces. That's the test to apply during the interview: is this orchestration fixed in shape, with only the arguments varying between runs, meant to be launched with one command and held to the same quality bar every single time? A recurring release-readiness sweep is exactly this — same phases, same checks, only the branch name changes. If the answer is yes, pre-define a thin `.claude/workflows/<name>.js` file so it becomes `/name` and never needs to be re-explained.

If the answer is no — the task's shape genuinely varies each time it comes up — do not pre-define anything. A one-off "audit these three files for this specific bug pattern" or "compare these two approaches" doesn't have a stable shape worth freezing into a script; next month's version of the same request will fan out differently, verify differently, or skip a stage entirely. For this case, put natural-language guidance in CLAUDE.md or a skill telling Claude when and how to compose a fan-out/verify/synthesize pattern on the fly (the docs explicitly endorse this: "use a workflow to ..." in a prompt is treated as the same opt-in as the `ultracode` keyword). Pre-defining rigid orchestration for a variable-shaped task is not a convenience, it's a flexibility tax.

Concretely: "run our full pre-release check (lint, type-check, changelog audit, dependency scan) and produce a go/no-go report" is a workflow candidate — ship `.claude/workflows/pre-release-check.js`. "Investigate why this one flaky test fails intermittently" is not — the investigation path depends entirely on what today's failure looks like, so it belongs in CLAUDE.md as a pointer to composing an ad hoc fan-out, not as a frozen script. When in doubt, ask the user directly during interview stage I4: "will you run this the same way every time, or does it change based on what's being investigated?" — that single question resolves the ambiguous cases.

## Keep the script thin — judgment lives in the agent prompts, not the control flow

A workflow script should hold only the fan-out / collect / gate skeleton: which agents to spawn, over what list, gathered into what shape, checked against what condition. Every actual judgment call — what counts as a bug, how to phrase the audit question, what "looks suspicious" means, how to weigh conflicting findings — belongs inside the string you pass to `agent()`, never inside the JS control flow around it.

A thick workflow (if/else chains encoding decision logic, hardcoded severity thresholds, string-matching on agent output to branch the next step) is where "Conviction over compliance" fails in the one layer that is code rather than prose: a script invites the method back in under the excuse that "it's just glue." It isn't just glue the moment it starts deciding *what* to look for instead of *how many agents to run and in what order*. If you notice yourself writing a conditional that encodes a judgment call rather than a control-flow gate (e.g., `if (finding.severity === 'high')` where "high" was invented by the script author rather than assigned by an agent), that judgment call belongs in a prompt, with the agent asked to return a structured field for the gate to read.

## The default composable pattern: fan-out → verify → synthesize

When a workflow is warranted, start from this shape and adapt it rather than reinventing structure each time — it's the pattern the docs recommend precisely because a single pass of independent findings is less trustworthy than findings that survived a second, adversarial look:

1. **Fan-out** — one agent per independent unit of work (one file, one route, one source), each asked to find or produce something, ideally returning a structured result (`schema` option) rather than free text so the next stage can consume it programmatically.
2. **Verify** — a second wave of agents, each given one finding from stage 1 (not the whole batch) and asked to adversarially check it: is this actually true, does the evidence support the claim, would a skeptical reviewer accept it? This is the stage that catches a fan-out agent's overclaim or hallucinated finding before it reaches the user.
3. **Synthesize** — one final agent that receives all verified findings and produces the single artifact the user actually wanted (a ranked list, a report, a go/no-go verdict) — this is also the only stage whose output should reach Claude's context; everything upstream stays in script variables.

Treat this as a starting silhouette, not a rigid template — a "keep fixing until a check passes" workflow doesn't need a verify stage because the check itself is the verifier, and a pure research workflow might verify claims against multiple independent sources instead of a single adversarial pass. The shape is a default to adapt, the same way the layer-routing table in SKILL.md is a default to adapt — not a checklist to satisfy mechanically.

## Hard gotchas — not general JS knowledge

- **The file must open with a pure-literal `meta` export.** `export const meta = { name: '...', description: '...' }` has to be a literal object — no variables, no function calls, no template-string interpolation inside it. This is a hard parser requirement: the runtime reads the file to extract `meta` before it ever executes anything, so `meta` can't depend on execution. Everything after that line is plain JavaScript with top-level `await` — you write `agent()`/`pipeline()` calls directly at the top level, no wrapping `async function main()` needed.
- **A workflow script cannot observe wall-clock time or randomness at all.** `Date.now()`, `Math.random()` and argless `new Date()` are rejected outright; `validate_harness.py` errors on each and its message carries the reason and the fix, so a slip gets caught at generation time. What matters while you're still *designing* the workflow is the consequence: anything that varies per run has to arrive through `args`, or be stamped onto the result after the workflow returns.
- **A file at `.claude/workflows/<name>.js` auto-registers as `/<name>`.** No separate registration step — dropping the file in is the registration. Project-scope (`.claude/workflows/`, checked into the repo, shared with every clone) shadows personal-scope (`~/.claude/workflows/`, local to one user) on a name collision, so if you're generating a project workflow and the user already has a personal one with the same name, the generated one is what actually runs for them in this repo — worth flagging during generation rather than letting them discover it by surprise.
- **Every agent a workflow spawns runs in `acceptEdits` mode, unconditionally.** This holds regardless of what permission mode the invoking session itself is in — even a `default`-mode session's workflow agents get auto-approved file edits. The agents also inherit the session's tool allowlist as-is. The direct consequence: any Bash command, WebFetch call, or MCP tool a workflow's agents will need has to already be sitting in `permissions.allow` by the time the workflow launches, because there's no interactive prompt waiting for you mid-run to grant it on the fly — the run just stalls on the permission prompt until someone goes and approves it out-of-band. Concretely, if you generate a workflow whose fan-out agents run `npm test` or fetch a URL, generate the matching `permissions.allow` entries in the same pass, in the same commit — treat them as one deliverable, not a follow-up. Record why those entries exist in the spec's Design rationale: on disk they look like ordinary convenience allowances, and the next person to tighten permissions will delete them and leave a workflow that stalls mid-run against a prompt nobody is watching.
- **Workflows are gated behind version, plan, and explicit opt-in — and can be turned off entirely.** They require Claude Code v2.1.154+ and a paid plan; on the Pro tier specifically, the user must also opt in via the "Dynamic workflows" row in `/config`. Beyond that, a user or org can disable the feature outright with `disableWorkflows` (settings.json) or the `CLAUDE_CODE_DISABLE_WORKFLOWS` env var. Because of this stack of gates, any generated harness that leans on a workflow for something functionally important MUST also document a subagent-sequential fallback — the same fan-out/verify/synthesize job done by spawning ordinary subagents one phase at a time through normal conversation turns — directly in the CLAUDE.md or skill text that references the workflow, not as an afterthought bolted on later. A user on a disabled or gated setup should be able to read that same paragraph and get the job done without ever touching `/name`.
- **Launching a workflow still prompts for approval by default.** Under `default` and `acceptEdits` session permission modes, every launch shows an approval prompt (planned phases, with Yes / "Yes, and don't ask again for `<name>` in `<path>`" / view raw script / No) unless the user has already picked the "don't ask again" option for that specific workflow in that specific project. Worth one line in a generated README or CLAUDE.md so a user isn't confused the first time `/name` stops for confirmation instead of just running — and worth mentioning that "don't ask again" exists, since it's the difference between a workflow that feels like friction and one that feels like a real one-button command.
- **The script itself cannot touch the filesystem or shell.** No `fs.readFile`, no `exec`, nothing — only the `agent()` calls it spawns can read files, write files, or run commands. The script's job is purely to hold variables and control flow between agent calls; treat any temptation to do direct I/O from the script as a sign the work belongs in an agent prompt instead.
- **Concurrency has hard caps: 16 simultaneous agents, 1,000 total per run.** These exist as backstops against runaway resource use and infinite-loop scripts, not as a budget to design toward — don't write a workflow that assumes it can fan out unboundedly and rely on the cap to save it; size the fan-out to the actual unit count (one agent per file, per route, per source) and let the cap be a safety net you never expect to hit, not a throttle you're designing around.

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

That is what "thin" means operationally: the script decides only how many agents run, over what list, and which boolean gates the next stage. Every judgment call lives inside a prompt string.
