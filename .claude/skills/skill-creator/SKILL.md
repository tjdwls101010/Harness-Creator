---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and improving them through evaluation.

## 1. What this skill does

Creating a skill is a loop, not a writing exercise:

- Decide what the skill should do, and roughly how.
- Write a draft.
- Run Claude with the skill on realistic prompts, alongside a baseline without it.
- Evaluate with the user — qualitatively (read the outputs) and quantitatively (assertions, timing, tokens).
- Rewrite based on what you learned. Repeat until the skill earns its keep.
- Optionally, tune the description so the skill triggers when it should.

Your job is to find where the user is in this loop and move them forward. "I want a skill for X" starts at the top: narrow down what they mean, draft, test, evaluate, iterate. A user who already has a draft jumps straight to evaluation. A user who says "skip the evals, just vibe with me" gets exactly that — the loop serves the skill, never the reverse.

## 2. How to write a skill

Everything below rests on one idea, and this document is written to obey it: **where you find a *why*, it is there to convince you — not to decorate a rule after the fact.** Read it that way, and notice where it persuades you and where it merely asserts. That noticing is the craft you're here to build.

### Conviction over compliance

A rule tells the model what to do. A principle convinces it *why* — and a convinced model does the right thing in situations the rule never named.

The difference is mechanical, not stylistic. A rule sits outside the model's judgment, a rail bolted on. When a new case bends away from what the rule's author anticipated, the rail and the model's own reasoning collide: obey the rail and the intelligence is overridden, or break the rail and the rule is lost. Either way something good is destroyed. A principle the model is genuinely *persuaded* of has no such collision. In the new case it applies the reasoning directly and lands somewhere sensible. Its intelligence isn't overridden — it's recruited.

So "principle-based" is not a gentler way to give orders. It is the only way to instruct a model without clipping the very capability you're instructing. Persuade, and the principle becomes part of how the model thinks rather than a fence around it.

This is the test for every line you write: *given only the why I supplied, could the model re-derive this instruction — and handle the case I forgot to mention?* If yes, you wrote a principle. If the line only works for the cases you happened to list, you wrote a rail.

### The mechanism: what + a why that convinces + a picture

A bare rule is brittle. The same rule carrying its reason and a concrete instance becomes something the model can generalize from. So every instruction should answer three things: *what* to do, *why* it matters, and *what it looks like*.

The weight sits on the *why* — and not every why carries it. A why can be present and still fail to convince. Watch the difference:

> **Flat:** "Use ISO 8601 dates — they're unambiguous."
> **Convincing:** "Use ISO 8601 dates (`2025-03-15`). When input mixes US and European conventions, `03/04/2025` is March 4th to the author and April 3rd to a parser in another locale — and nothing errors. The data just silently corrupts. An unambiguous format kills the failure at its source."

Both state a reason. Only the second makes you *see* the corruption — and a model that has seen it reaches for unambiguous formats in places this instruction never listed: log lines, filenames, API payloads. That reach is the entire point. Convince once; generalize everywhere.

You'll see this applied to this document's own content below. Where §4 and §7 give a number — how many test prompts, how many trigger queries — they give the number *and* its reason *and* when to leave it behind, because a number stripped of its reason is just a rail wearing a digit.

### The target: persuade only what isn't already believed

Persuasion has an aim, and aiming well matters as much as arguing well. The model already believes most of what a competent practitioner believes — general coding sense, standard formatting, the ordinary judgment calls. Spend a paragraph convincing it of something it already owns and you've done worse than waste space: you've signaled "I don't trust you to know this," and a model told it isn't trusted works smaller. Over-explaining the obvious clips intelligence exactly the way a rail does — from the other side.

So a skill should hold only what the model *can't* supply itself: domain knowledge it hasn't seen (your org's conventions, a proprietary workflow, a hard-won heuristic), preferences it can't guess (this user wants X, not the sensible default Y), and decisions already made (the exact command, the schema a tool depends on). Everything else, leave out — not for brevity, but because every line that doesn't earn trust spends it.

The highest-signal line of all is a **gotcha** — a trap the model walks into precisely because it *can't* know your domain: *"the `subscriptions` table is append-only; the row you want has the highest version, not the latest `created_at`."* The model can't derive that; it learns it by failing. One such note prevents more wasted runs than a page of general advice — which is why the strongest skills accumulate gotchas over time rather than front-loading cleverness (how, in §6).

Turned into a per-line verdict — keep or cut:

| The line is… | Example | Verdict |
|---|---|---|
| Direction — what/where the system has decided | "Outputs go to `evals/evals.json`" | **Keep** |
| A principle — claim + reason + instance | the ISO example above | **Keep** |
| Knowledge counter to the model's default | "here, prefer breadth-first; the tree is wide and shallow" | **Keep** |
| A bare rule — steps with no reason | "always do X, then Y, then Z" | **Cut** — supply the reason, or trust the model |
| A denial of something never raised | "this skill has no quick mode" | **Cut** — see below |

That last row is the tempting one. Stating what a skill *doesn't* do feels like responsible boundary-setting. But to deny a "quick mode" you first have to plant the idea of one, and now the reader is turning over a mode that was never on the table. You added a concept and a negation where silence would have left nothing to misread. Describe what *is*, and let absence stay absent.

### What follows from this

Two things fall out of writing this way, and naming them lets you trust the approach instead of second-guessing it.

You stop needing to foresee every case. A model convinced of the principle handles the edge you didn't predict — that *is* what conviction buys. So resist enumerating fifteen scenarios with a rule apiece; that's the brittle path and it snaps on the sixteenth. Make two or three cases vivid enough to carry the principle, state the principle, and stop. When in doubt, delete the edge case and strengthen the principle.

And leanness stops being a discipline you impose and becomes one that follows. You're not trimming words to be terse; you're cutting lines that don't pull weight, because each dead line dilutes the live ones around it. A 200-line skill of filler is worse than a 700-line skill where every line earns its place — length isn't the enemy, *non-contributing* length is. The audit: read each paragraph and ask what would change if it vanished. If the answer is "nothing," or "the model would do the same anyway," it's already gone.

## 3. Anatomy of a skill

```
skill-name/
├── SKILL.md            required — frontmatter (name, description) + instructions
└── (optional bundles)
    ├── scripts/        executable code for deterministic, repeated work
    ├── references/     docs loaded into context only when a task needs them
    └── assets/         files used in output (templates, icons, fonts)
```

A skill loads in three stages, and the staging is the point:

1. **Metadata** (name + description) — always in context, every session, ~100 words.
2. **SKILL.md body** — loaded when the skill triggers.
3. **Bundled resources** — loaded only when reached. A script can *run* without its source ever entering context.

This is progressive disclosure, and it earns its keep against a specific cost: irrelevant text degrades the model even when the tokens are free. A long SKILL.md doesn't only cost load time — it buries its own key instructions in the middle, where attention thins. So the question for each piece of content isn't "is this useful?" but "is this needed on *every* path through the skill?"

- **Needed on every invocation → SKILL.md.** The backbone: triggers, the decision tree, the top-level procedure, the philosophy that governs judgment calls. The model must orient on this each time.
- **Needed only sometimes → references/.** Conditional depth: a schema used at one step, a framework-specific variant, a deep example for a sub-task. Most invocations never read it, so most shouldn't pay for it.

But splitting carries a cost of its own, and it's easy to miss because it points the other way. Every reference file is a routing decision you hand to the model: *which* file do I load now? Split along natural seams and the answer is obvious. Shatter the same material into a dozen fragments and the model now spends judgment deciding what to read — loads the wrong one, misses the right one, or reads three to find the paragraph it needed. Worse, knowledge that belongs together loses its connective tissue: the model loads fragment A, needs context that lived in B, and doesn't know B exists. A skill that can't reliably find its own knowledge fails silently — the worst way to fail, because nothing signals it.

So progressive disclosure has an optimum, not a direction. Under-split, and the key lines drown; over-split, and the skill can't route to itself. Split when the expected saving — this material is skipped on most runs — beats the expected routing cost. When a fragment is small, or its load-trigger is ambiguous, or it's needed on most paths anyway, the split loses that bet; keep it inline.

The classic mistake is splitting by *volume* — "SKILL.md feels long, move something out." Length is the wrong axis; invocation pattern is the right one. Pushing the core decision tree into `references/workflow.md` because the file "felt long" means the model can't orient without an extra read on every call. Pushing the exact JSON schemas into `references/schemas.md` is right: only the eval step needs those fields, and most sessions never reach it.

When a skill spans several frameworks or domains, organize references by variant — `references/{aws,gcp,azure}.md` — so the model reads only the one in play. Let the same optimum govern: one file per variant the model genuinely chooses between, not one per topic you could name.

**Bundled scripts give the model leverage — but only when they compose.** Code lets the model spend its turn deciding *what to do* instead of rebuilding boilerplate. That only pays off when the script is *parameterized*: a CLI that takes arguments (`search.py --query "..." --after 2025-01 --author jane`), or importable helpers it assembles for the task at hand (`fetch(day)`, `by_referrer(df)`). The trap is the frozen script — no arguments, one hardcoded purpose. It can't be composed and it can't be reused, so the moment the task shifts by an inch the model rewrites it from scratch and the bundle bought nothing. Write the parameterized version; this skill's own `scripts/` — argparse'd CLIs — are the model to copy.

**A skill can also carry state in its own folder**, which keeps it portable without making it amnesiac. Two idioms cover most needs. For *setup* the skill shouldn't hardcode (which Slack channel? which dashboard?), keep a `config.json` and have SKILL.md run a shell check that prints it or `NOT_CONFIGURED`; on `NOT_CONFIGURED`, ask once and save, so the user configures it a single time instead of on every run. For *memory* across runs, append to a log or a small SQLite under `${CLAUDE_PLUGIN_DATA}` (a stable data dir) — a standup skill that logs each post opens the next run by reading what changed since yesterday. Reach for this only when the skill genuinely needs to remember; most don't.

One hard line, regardless of the above: a skill must not surprise the user against its stated intent. No malware, no exploit code, nothing that quietly enables unauthorized access or data exfiltration. Behavior should match the description the user agreed to. (Whimsy like "roleplay as X" is fine — the bar is deception and harm, not playfulness.)

## 4. Creating a skill

### Start from intent

Begin by understanding what the user actually wants — and mine the conversation you're already in, because it often holds the answer. "Turn this into a skill" has just shown you the workflow: the tools used, the order of steps, the corrections the user made, the input and output formats. Extract that, then confirm the gaps instead of re-asking what's already on the table.

The questions worth resolving early:

1. What should the skill let Claude do?
2. When should it trigger — which phrasings, which contexts?
3. What's the expected output?
4. Should there be test cases? Skills with objectively checkable outputs (file transforms, data extraction, fixed workflows) gain a lot from tests; subjective ones (writing style, visual taste) often don't, and forcing assertions onto them just measures noise. Suggest a default from the skill's type, then let the user decide.

### Ask far more than feels natural

This is the one place to deliberately override a trained instinct. Claude's default is to avoid bothering the user — to guess and press on. Inside skill creation, flip it on purpose. The economics are lopsided: a clarifying question costs the user seconds; a wrong guess costs hours — you build the wrong thing, the user spends their expensive review attention discovering it's wrong, and then you rebuild. "Guessing well" doesn't save that time. It just moves the cost from your cheap question onto their costly review.

So whenever you're unsure about scope, naming, output format, audience, edge-case handling — any judgment call where the user's answer changes the result — ask. Not once at the start, but throughout. Thinking hard about what the user *probably* wants is not a substitute for asking; asking is the substitute for guessing. Reach for `AskUserQuestion` freely.

### Calibrate to the human in front of you

Skill-creator's users run from non-coders to staff engineers, and the same word lands differently across that range. "Assertion" and "JSON" assume a technical reader; drop them unqualified on someone without the background and you lose them. Define them *for* an expert, though, and you've done the human version of over-explaining — the faint signal that you've misread who they are. Read the cues in how the user writes and match them; a one-line definition when you're genuinely unsure costs nothing. The dual-edge from §2 applies to people too.

### Write the SKILL.md

- **name** — kebab-case identifier.
- **description** — when to trigger and what the skill does. This is the primary trigger mechanism, so it carries *all* the "when to use" information; that information is useless in the body, which loads too late to inform the decision to load it. (Tuning it is §7.)
- the skill itself, written the way §2 asks.

A note on the description, because it cuts against instinct: Claude currently *under*-triggers skills — it skips them when they'd help. So lean the wording slightly toward triggering. "How to build a dashboard for internal data" becomes "How to build a dashboard for internal data. Use whenever the user mentions dashboards, metrics, or displaying company data — even if they never say 'dashboard.'" A skill loading when marginally unneeded costs little; a skill staying dark when needed costs the whole skill.

### Draft the test cases

After the draft, write a small handful of realistic test prompts — start around two or three. The reason to keep it small: you and the user are about to study each output closely, and a few cases you both understand in depth beat a large set neither of you can hold in mind. Scale up later, once the skill is stable and you're probing for breadth rather than learning its behavior. Make them the kind of thing a real user would actually type, not sanitized stand-ins. Share them first — "here are a few cases I'd try; right shape?" — then run them.

Save them to `evals/evals.json` as prompts only for now; assertions come in the next section, drafted while the runs are in flight. See `references/schemas.md` for the full structure.

```json
{
  "skill_name": "example-skill",
  "evals": [
    { "id": 1, "prompt": "User's task prompt", "expected_output": "What success looks like", "files": [] }
  ]
}
```

## 5. Running and evaluating

This section is one continuous stretch — once the runs start, carry through to the viewer without stopping. And don't reach for `/skill-test` or any other testing skill mid-flow: each runs its own loop with its own state, and interleaving them leaves results that won't line up across iterations.

Put results in `<skill-name>-workspace/`, a sibling of the skill directory. Inside, organize by iteration (`iteration-1/`, `iteration-2/`, …), and within each, one directory per test case named for what it tests — `eval-ocean/`, not `eval-0/`, so the name tells you what broke at a glance. Create directories as you go.

### Spawn every run — with-skill and baseline — in the same turn

For each test case, launch two subagents together: one with the skill, one without. Launch them in the same turn so they finish around the same time. Stagger them — with-skill now, baselines later — and you fold in timing skew from shifting machine load, which is indistinguishable from a real performance difference once you're reading the numbers. Same turn removes that confound.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<name>/with_skill/outputs/
- Outputs to save: <what the user cares about — "the .docx", "the final CSV">
```

**Baseline run** — same prompt, but what "baseline" means depends on the task:

- **New skill:** no skill at all. Save to `without_skill/outputs/`.
- **Improving a skill:** the *old* version. Snapshot before you edit (`cp -r <skill-path> <workspace>/skill-snapshot/`), point the baseline at the snapshot, and save to `old_skill/outputs/`. Skip the snapshot and you've overwritten the very thing you're measuring against.

Write an `eval_metadata.json` per test case (assertions can come later). Name each eval descriptively and reuse the name for its directory. If this iteration changed the prompts, write fresh metadata — it doesn't carry over.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### While the runs are in flight, draft assertions

Don't idle — this is free time. Write the quantitative assertions now and explain them to the user. Good assertions are objectively checkable and named so they read clearly in the viewer: anyone glancing at the results should see what each one tests. For anything a script can verify, write the script rather than eyeballing it — faster, repeatable across iterations, and it won't drift. Leave the subjective qualities (does the prose sound right, is the design tasteful) to human judgment; an assertion bolted onto those just measures noise. Update `eval_metadata.json` and `evals/evals.json` as you go.

### As each run finishes, capture its timing

Each completed subagent task hands you `total_tokens` and `duration_ms` in its notification. Save them immediately to `timing.json` in the run directory — this is the only moment they exist. Nothing else persists them, and they can't be recovered after the fact.

```json
{ "total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3 }
```

### Grade, aggregate, and open the viewer

Once the runs are done:

1. **Grade each run.** Spawn a grader (or grade inline) following `agents/grader.md`; save to `grading.json` in each run directory. The `expectations` array must use exactly `text`, `passed`, and `evidence` — the viewer reads those field names, and any variant renders as blank cells. Check programmatically-verifiable assertions with a script, not your eye.

2. **Aggregate into a benchmark:**

   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

   This writes `benchmark.json` and `benchmark.md` — pass rate, time, tokens per configuration, mean ± stddev, and the delta. Put each `with_skill` config before its baseline. If you ever hand-write `benchmark.json`, match `references/schemas.md` exactly; the viewer depends on the field names.

3. **Read the benchmark before you show it.** Aggregates hide things. Following `agents/analyzer.md`, look for assertions that pass regardless of the skill (they discriminate nothing), evals with high variance (possibly flaky), and time or token cost traded for pass rate.

4. **Launch the viewer:**

   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```

   For iteration 2+, add `--previous-workspace <workspace>/iteration-<N-1>` so the user sees the diff. In a headless environment with no browser, use `--static <output_path>` to write a standalone HTML file instead of serving; the user's feedback downloads as `feedback.json`, which you copy back into the workspace. Use `generate_review.py` rather than hand-rolling HTML — it encodes the layout and submission behavior the rest of this loop depends on.

5. **Hand it off:** *"Opened the results in your browser — two tabs. 'Outputs' walks each test case for feedback; 'Benchmark' is the quantitative comparison. Tell me when you're done."*

### What the user sees

The **Outputs** tab shows one test case at a time: the prompt, the files produced (rendered inline where possible), last iteration's output collapsed (from iteration 2 on), the assertion pass/fail if grading ran, and a feedback box that auto-saves. The **Benchmark** tab is the stats — pass rates, timing, tokens per configuration, with per-eval breakdowns and the analyst's notes. The user navigates with arrows or buttons and clicks "Submit All Reviews" when done, which writes `feedback.json`.

### Read the feedback

When they say they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-ocean-with_skill", "feedback": "chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-harbor-with_skill", "feedback": "", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means it looked fine — spend your changes where the user actually had something to say. Then stop the viewer:

```bash
kill $VIEWER_PID 2>/dev/null
```

## 6. Improving the skill

This is the center of the loop: runs done, user reviewed, now make the skill better. How to think about the changes:

**Generalize from the feedback.** You're tuning on a few examples because they're cheap to study together — but the skill will run on prompts neither of you has seen. So a fix that only satisfies these three cases is a loss disguised as progress. When an issue is stubborn, don't reach for a tighter rule; reach *wider* — a different metaphor, a different framing of the work. It's cheap to try and sometimes lands somewhere much better.

**Read the transcripts, not just the outputs.** The outputs tell you *what* happened; the transcripts tell you *why*. If the skill sent the model chasing something unproductive, find the line that caused it and cut it. If all three runs independently wrote near-identical helper scripts — `create_docx.py`, `build_chart.py` — that's the skill failing to bundle something it should: write it once, drop it in `scripts/`, and every future run skips reinventing it.

**Explain the why — hardest exactly when the feedback is terse.** Frustrated feedback ("no, not like that") still encodes a real preference. Your job is to recover *why* they wrote it and fold that understanding into the skill, not to bolt on one more imperative. Every time a hard rule or rigid structure tempts you, that's the signal to step back and explain the reasoning instead — for all the reasons in §2.

**Accumulate gotchas — the other half of improving.** Cutting a bad instruction removes friction; adding a gotcha adds knowledge. When a run fails not because the skill said something wrong but because the model hit a domain trap it couldn't have known — an append-only table, a field that goes by two names, a staging endpoint that returns 200 while quietly doing nothing — write that trap down as one line. Skills grow this way: a billing skill that began with a single note had four hard-won gotchas three months later, and each one is a failure that never recurs.

Take the time. Your thinking isn't the bottleneck here; getting into the user's head is the work. Draft a revision, look at it fresh, improve it.

### The loop

1. Apply the changes.
2. Rerun every test case into `iteration-<N+1>/`, baselines included. For a new skill, the baseline stays `without_skill` throughout. For an existing one, use judgment about which baseline answers your question: the original version, or the previous iteration.
3. Launch the viewer with `--previous-workspace` pointing at the prior iteration.
4. Let the user review.
5. Read the feedback and go again.

Stop when the user is happy, when the feedback comes back empty, or when you've stopped making real progress — whichever comes first.

## 7. Optimizing the description

The description decides whether Claude ever loads the skill, so it's worth tuning on its own once the skill works. Offer this as a separate pass.

### Build a trigger eval set

Create queries — some that should trigger the skill, some that shouldn't — split fairly evenly between the two. Aim for around 20 to start: enough that the trigger boundary shows up clearly without the eval dragging, with room to scale up if the skill competes with many neighbors and the boundary is subtle. The even split matters more than the exact count.

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Make them *real* — what an actual user types, not abstract stand-ins. Concrete detail, file paths, a little backstory, lowercase, abbreviations, the occasional typo, varied length:

> *Bad:* "Format this data"
> *Good:* "ok so my boss just sent me this xlsx (its in downloads, 'Q4 sales final FINAL v2.xlsx') and wants a column for profit margin as a %. revenue's in column C, costs in D i think"

Put the real effort into the **near-misses**, on both sides — that's where the boundary actually lives, so that's where the learning is. The should-trigger queries that earn their keep are the ones where the user never names the skill or file type but clearly needs it, and the ones where this skill competes with another and should win. The should-not-trigger queries that earn their keep share keywords or surface features with the skill but actually need something else — adjacent domains, phrasings a naive keyword match would grab. A negative like "write a fibonacci function" for a PDF skill tests nothing. Weight your time toward the hard cases; the user signs off on the set, so the obvious ones need little of your attention.

### Review with the user

Bad queries make bad descriptions, so confirm the set first, using the HTML template:

1. Read `assets/eval_review.html`.
2. Replace the placeholders: `__EVAL_DATA_PLACEHOLDER__` → the JSON array (no quotes; it's a JS assignment), `__SKILL_NAME_PLACEHOLDER__` → the name, `__SKILL_DESCRIPTION_PLACEHOLDER__` → the current description.
3. Write it to a temp file and `open` it.
4. The user edits, toggles, adds, then clicks "Export Eval Set"; it downloads to `~/Downloads/eval_set.json` (grab the most recent if there are duplicates like `eval_set (1).json`).

### Run the optimization loop

Tell the user it runs in the background and you'll check in periodically. Then:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt, so the triggering test matches what the user actually experiences. The loop splits the set into train and held-out test, evaluates the current description (running each query a few times for a stable trigger rate), asks Claude to propose improvements from what failed, and re-evaluates — up to five iterations. It returns `best_description`, chosen by *test* score rather than train score so it doesn't overfit the queries it was tuned on. Tail the output now and then to keep the user posted.

### Why triggering works the way it does

This shapes good eval queries, so hold it in mind. Claude sees each skill's name and description in an `available_skills` list and decides whether to consult it — but it only bothers for tasks it *can't* easily handle alone. "Read this PDF" may not trigger a PDF skill no matter how well the description matches, because Claude just does it directly. Complex, multi-step, specialized tasks trigger reliably when the description fits. So write substantive queries; trivial ones fail to trigger regardless of description quality, and teach you nothing.

### Apply it

Take `best_description`, update the frontmatter, and show the user before/after with the scores.

If the `present_files` tool is available, package and present the installable skill (skip this step if it isn't):

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

Then point the user to the resulting `.skill` file.

## 8. Advanced, and reference files

**Blind comparison.** When the question is sharper than "is this good?" — specifically "is the new version *actually* better than the old?" — there's a more rigorous option: hand both outputs to an independent agent without telling it which is which, let it judge, then analyze why the winner won. Stripping the labels strips the bias toward the version you hope wins. It needs subagents, and most iterations won't call for it — the human review loop usually settles the question. Details in `agents/comparator.md` and `agents/analyzer.md`.

**Session-scoped hooks.** A skill can register hooks that switch on only while it's active — a guardrail that blocks `rm -rf` or `DROP TABLE` during a risky operation, or freezes edits outside one directory during a delicate pass. Opinionated safety you'd never want on globally, available exactly when the skill that needs it runs; see Claude Code's hook documentation for the mechanics.

**The bundled files**, each loaded when its step arrives:

- `agents/grader.md` — grade assertions against a run's transcript and outputs.
- `agents/comparator.md` — blind A/B judgment between two outputs.
- `agents/analyzer.md` — why one version beat another.
- `references/schemas.md` — exact JSON for `evals.json`, `grading.json`, `benchmark.json`, and the rest. Needed only at the eval and grading steps, which is why it lives here rather than in the body.
