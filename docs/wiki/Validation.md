# Validation & Testing

How harness-creator proves a harness is actually good, not just present. Validation runs in two tiers — a free deterministic lint that runs on every generation, and a paid end-to-end tier that spawns real sessions and grades their transcripts — with a free hook unit-tester sitting between them.

## Why two tiers

A harness can be perfectly well-formed and still do nothing. A skill with flawless frontmatter never triggers if its description's boundary language is fuzzy; a hook with valid JSON fires on the wrong tool if its matcher was written against a wrong assumption about tool-call shape. Structure and behavior are different properties, and they need different checks:

- **Tier 1 — [`validate_harness.py`](Scripts.md):** deterministic, free, structural. Proves the harness is well-formed. Runs on every generation, no consent needed.
- **Tier 2 — end-to-end:** spawns real headless sessions and grades what actually happens. Proves the harness changes Claude's behavior. Costs tokens, so it is always consent-gated.

Lint tells you the harness *is well-formed*. Only a real run against a real prompt tells you it *does what the spec's behavior inventory says it should*.

## Tier 1: the deterministic lint

`validate_harness.py` is the always-on floor. The generate step runs it immediately after writing or editing any component, and **does not declare the work done until it exits 0.** This is a hard rule, not a suggestion — it is the fix for the classic failure mode where a project ships a validation checklist that nobody ever actually runs.

```
python "${CLAUDE_SKILL_DIR}/scripts/validate_harness.py" --path <target-repo> [--json] [--strict]
```

Findings are split into errors (`E`) that must be fixed and warnings (`W`) that are advisory. What it checks, by component:

| Component | Representative checks |
|---|---|
| `settings.json` (+ `.local`) hooks | E: bad JSON, unknown event name, `matcher` on an event that fires unconditionally, missing/unknown handler type, a `command` pointing at a script that doesn't exist or isn't executable. W: matcher with regex characters but no `^…$` anchor, an `if` field on an event that carries no tool input, two `updatedInput` hooks on the same tool |
| permissions | E: rule references an unknown tool name (checked against the canonical tool list). W: a broad `allow` like `Bash(*)` that auto mode silently drops |
| skills | E: directory with no `SKILL.md`, frontmatter that won't parse (auto-triggering is silently dead), a dead relative link, a referenced `scripts/`/`references/` file that's missing. W: no `description`, `description`+`when_to_use` over 1536 chars, body over 500 lines, combined description budget over ~1% of the context window |
| agents | E: missing `name`/`description`, duplicate `name` in one scope, unknown tool in `tools`. W: unrecognized `model` value |
| workflows | E: no `export const meta` with a `name`, or a `Date.now()`/`Math.random()`/arg-less `new Date()` call (breaks resume determinism). W (or E if node finds a real syntax error): ESM syntax checked with `node --input-type=module --check`, skipped if node is unavailable |
| rules | E: `paths:` glob with unbalanced braces. W: no `paths:` frontmatter (the rule loads at launch, same as if it weren't split out) |
| CLAUDE.md | E: an `@import` whose target is missing. W: over 200 lines, or a bare-name bullet list that looks like a component inventory (lines with trigger phrasing like "use X when Y" are exempt) |
| harness-spec.md | W: missing when components exist on disk, or a component on disk the spec never mentions (drift) |

Exit codes are consistent across all four [scripts](Scripts.md): `0` = no errors, `1` = at least one error (or, under `--strict`, at least one warning), `2` = the script itself couldn't run. `--strict` promotes warnings to failures for CI; `--json` emits machine-readable output for a grading agent or a pipeline.

## Free middle tier: hook unit-testing

Hooks are the hardest component to eyeball, because a matcher's behavior and an exit code's meaning both depend on the event. `test_hook.py` closes that gap without a live session, and **every hook the skill generates or wires up is expected to pass it before it counts as delivered.**

```
# Find the hooks a settings.json fires for an event/tool and run them with sample input:
python "${CLAUDE_SKILL_DIR}/scripts/test_hook.py" --settings .claude/settings.json \
    --event PreToolUse --tool Bash --input-field command="rm -rf /"

# Run one script directly against a specific input file:
python "${CLAUDE_SKILL_DIR}/scripts/test_hook.py" --command .claude/hooks/guard.sh \
    --event PreToolUse --input sample.json

# Show the matcher matrix without executing anything:
python "${CLAUDE_SKILL_DIR}/scripts/test_hook.py" --settings .claude/settings.json --matrix
```

It does four things: builds a realistic sample input for the event (overridable field-by-field with `--input-field k=v`), reproduces Claude Code's matcher evaluation exactly so you see which hook groups match, runs the hook with that input on stdin, and — the part that matters most — **interprets the result against the event's exit-code contract.** It turns a raw exit code into plain English: `exit 2` blocks and its stderr becomes the reason Claude sees; `exit 1` does *not* block (a common bug when a block was intended); `exit 0` with a JSON `decision`/`deny`/`additionalContext` field is read, while the same JSON on any nonzero exit is silently discarded. `--matrix` prints the full hook × tool match table without running anything.

## Tier 2: end-to-end

This is the paid tier, and it only runs with the user's explicit consent, gathered during the interview's validation stage (see [The Interview](The-Interview.md)) alongside the scenario list itself. It never launches silently as part of "finishing" a generation — the offer names the rough cost (roughly one full session per scenario) and proceeds only on yes.

There is **no fixed e2e workflow file shipped in the skill.** The scenarios worth checking differ for every project, so the run is composed on the spot from the spec's Validation section, executed once, and thrown away — only the results are recorded, back in the spec. The shape composed every time is three phases:

```
Phase Run:    one agent per scenario runs run_e2e.py via Bash, scenarios independent
Phase Grade:  one grading agent per transcript — every verdict cites transcript evidence
Phase Report: synthesize pass/fail, plus one concrete repair target per failure
```

When dynamic workflows aren't available (they need a recent Claude Code, a paid plan, and can be disabled), the exact same three phases run as ordinary sequential subagent calls instead. Only the launch mechanism changes; the scenarios, expectations, and grading doctrine are identical. The absence of workflows is never a reason to skip e2e or grade it more loosely.

Default to **2–4 scenarios** — start small and look deeply, because a grader forced to produce evidence-cited verdicts for a dozen transcripts starts skimming, and skimming is how a false PASS slips through. Default the **model** to the user's actual configured model, not a cheaper stand-in: the whole point is behavioral fidelity, and a cheap model's trigger and instruction-following behavior isn't the same distribution as day-to-day use. `--model` exists as a named cost/fidelity tradeoff, offered explicitly rather than taken silently.

### What e2e can assert

Every scenario maps to one of five checkable assertion types; an "assertion" that fits none of them probably isn't concretely checkable and needs rewording before it goes in the spec.

| Assertion type | Evidence to look for |
|---|---|
| Skill trigger hit / near-miss | A `Skill`/`Read` tool-use event that names the skill. For a near-miss prompt (deliberately close to a trigger phrase but not meant to fire), the passing evidence is the *absence* of that event |
| Hook fired / blocked | Both the hook's own side effects (a log file, a prevented edit) and the transcript's hook events, plus Claude's visible reaction — did it stop, or route around the block |
| Behavior compliance | A grader comparing the spec's expected behavior against what the transcript shows, with cited evidence — the least mechanical type, held to the same evidence bar |
| CLAUDE.md knowledge reflected | Ask a project-fact question (test runner, build command) and check the answer for the *right fact*, not merely the right words |
| Artifact quality | Read the file the session created or modified, ideally in an isolated copy — don't trust the transcript's description of a file it may have written wrong or empty |

### Grading doctrine: evidence required, surface compliance is a FAIL

This is the single most important habit in the whole tier. Every verdict must name the specific transcript line, tool-use event, or file content it rests on. "The skill triggered correctly" is not a verdict; "the third tool-use event calls `Skill` with `skill: 'api-route-conventions'`" is. If a grader can't point at something concrete, the honest verdict is FAIL — the burden of proof to pass sits on the assertion, not on the transcript to disprove it.

And surface-level compliance is not success. A scenario that checks whether a protected directory can't be edited is *not* satisfied just because one tool call was blocked — if Claude's next move edits the same file through a Bash heredoc, the harness failed even though the specific hook "worked." Grade the underlying outcome the assertion was protecting, not the letter of the assertion. A passing grade on a weak assertion is worse than no assertion, because it manufactures false confidence.

### From failure to fix

Each failure resolves to one specific layer to edit, running [layer routing](Layer-Routing.md) in reverse — instead of "which layer does this requirement belong in," you ask "which layer's placement was wrong, given how it behaved." A skill that doesn't trigger is a *description* fix; a skill that triggers but behaves wrong is a *body* fix (strengthen the "why" before adding rules); an always-required rule that gets ignored is a CLAUDE.md wording fix, escalated to a hook only if a re-run still fails. After a repair, re-run only the failed scenarios — not the whole suite — and record the outcome in the spec's Validation section either way.

## Two honest limits

Two things this pipeline cannot currently prove, stated plainly rather than papered over:

- **The interview itself can't be e2e-tested.** `AskUserQuestion` is unavailable in headless (`-p`) and subagent contexts, so there is no way to script a session that exercises the interview flow. The only validation path for question phrasing and the gate sequence is manual dogfooding. A clean e2e report validates the *generated harness*, never the *interview that produced it*.
- **`run_e2e.py`'s headless permission handling is unverified.** The combination of `--isolate`, skip-permissions, and pre-registered allow entries that lets a scenario run to completion is this build's best documented guess, not a confirmed fact — a `claude` child spawned via Bash can fail with "Not logged in" because the host session's credentials don't propagate to it. The subprocess pipeline, `CLAUDECODE` stripping, and stream-json parsing are confirmed end to end (through that very error path), but the permission mechanism under real tool calls has never been watched to succeed. **The first real e2e run, in an authenticated environment, is the actual confirmation** — if scenarios complete and produce sensible transcripts, the mechanism works and the flag stops mattering; if one stalls on a permission prompt, that's the signal to adjust the flags. Either way, note the outcome in the spec so it isn't re-litigated next time. See the [FAQ](FAQ.md) for more on this limitation.

## See also

- [Scripts](Scripts.md) — full CLI reference for `validate_harness.py`, `test_hook.py`, and `run_e2e.py`
- [FAQ](FAQ.md) — the unverified-permission caveat and other honest limits
- [Layer Routing](Layer-Routing.md) — the routing framework that failure-to-fix reverses
