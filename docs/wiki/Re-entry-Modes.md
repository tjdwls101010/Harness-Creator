# Re-entry Modes

harness-creator is re-entrant: running it again on a project that already has a harness does not regenerate everything from scratch. This page explains the four modes it can enter — `new`, `extend`, `improve`, `sync` — how Phase 0's audit picks a starting suggestion, and how each mode reshapes the interview.

## Why re-entry is a first-class path

A harness is not a one-shot artifact. You add a behavior a month after the first build, a rule turns out to be too advisory and gets ignored, or someone hand-edits `.claude/` and the persisted `.claude/harness-spec.md` no longer matches what's on disk. Re-invoking the skill in any of these situations should pick up where the last pass left off, not blow away and re-ask everything. That is what the four modes are for — each one is a different answer to "the harness already exists; what does this pass actually need to do?"

Every invocation begins the same way: Phase 0 runs `audit_harness.py` before any interview question, inventories what already exists, and returns a suggested mode. See [The-Interview.md](The-Interview.md) for the full operating loop the modes plug into.

## The four modes

| Mode | When it applies | What it does to the interview |
|------|-----------------|-------------------------------|
| `new` | Nothing exists yet — no CLAUDE.md, no `.claude/` components. | The full five-stage fresh build (I1 goals → I2 inventory → I3 routing → I4 detail → I5 validation). |
| `extend` | The harness works; the user wants to add something new to it. | I1 shrinks to one question — "what's newly wanted, beyond what's already here?" — and the resulting Goals are *merged into* the existing spec, not replacing it. I2–I5 run as normal against just the delta. |
| `improve` | Something the harness already does is uncomfortable, wrong, or annoying. | I1 is *replaced* by "what went wrong?" instead of "what's the goal?" Each complaint is routed to the layer that can actually fix it. |
| `sync` | The spec and the files on disk disagree (drift). | No I1–I5 traversal at all. The interview collapses to walking the audit's drift list and resolving each item. |

Whichever mode runs, the pass still ends by updating `.claude/harness-spec.md`, and the spec's Change history records the date, the mode, and a summary of what changed — so the *next* re-entry has an accurate starting point.

## How the audit suggests a mode

`audit_harness.py` inventories CLAUDE.md, rules, skills, agents, workflows, and settings, checks the spec against what's on disk, runs hygiene lint, and prints a suggested mode. Run it directly to see the same signal the skill sees:

```
python "${CLAUDE_SKILL_DIR}/scripts/audit_harness.py" --path .
```

Its suggestion follows a fixed decision ladder, checked top to bottom:

| Audit finding | Suggested mode |
|---------------|----------------|
| No harness components found at all | `new` |
| Components exist, but there is no `harness-spec.md` | `improve` or `sync` — treat the first pass as recovering a spec from what's on disk |
| Components on disk that the spec never mentions, **or** a spec row at `generated`/`validated` with nothing on disk | `sync` — confirm whether to update the spec or the files |
| `validate_harness.py` finds real errors in the existing harness | `improve` — likely a pass to fix them |
| A spec exists, matches disk, and lints clean | `extend` or `improve` — ask the user directly |

That third row covers both drift directions — a file the spec never mentions, and a spec row claiming a file that isn't there. Earlier builds of `audit_harness.py` only caught the first direction; the second (a validated component that quietly vanished, or a generation that was interrupted partway) went unreported because nothing parsed the Behavior inventory table's `status` column against the filesystem. Both directions are now first-class audit findings — see the status table below.

The audit is a report, not a verdict — it always exits 0 unless `--path` itself is invalid. It never *decides* the mode; it hands you the most likely one and the evidence behind it.

## Why extend vs. improve is confirmed with the user

Notice the bottom two rows above both resolve to a pair, not a single mode. That is deliberate. An audit can read the filesystem, but it cannot read intent. A clean, spec-matching, lint-passing harness is exactly the state you're in whether the user shows up wanting to *add* something (`extend`) or to *fix* something that annoyed them (`improve`) — the two are indistinguishable from disk alone. So the skill asks plainly: "what's new that you want" versus "what's been uncomfortable about how it behaves." The audit narrows the field; the user's answer settles it.

## How improve mode routes feedback

`improve` is the one mode built entirely around observed failure rather than fresh intent. It opens with "what was uncomfortable, wrong, or annoying about how the current harness behaves?" and then routes each piece of feedback to the component that can actually repair it — a symptom-to-target mapping, for example:

- A skill that fires when it shouldn't (or doesn't fire when it should) → its `description`, not its body.
- A skill that triggers correctly but then does the wrong thing → its body.
- A rule Claude keeps ignoring → strengthen the CLAUDE.md line first, and if it still slips, escalate it from advisory prose to an enforced hook.

That escalation from prose to a hook is the [Layer-Routing.md](Layer-Routing.md) framework applied in reverse: the first build routed the behavior to a layer, and the complaint is evidence the first routing was too weak. The full feedback-routing table lives with the end-to-end testing guidance, since a failed validation run is the most common source of improve-mode feedback — see [Validation.md](Validation.md).

## How sync mode resolves drift

`sync` is the smallest mode, and the one place the "tool" framing in this handbook deliberately drops out: the drift `sync` reconciles isn't only harness-creator's own doing. Phase 0's audit already produced the drift list, in **both** directions:

- **A file on disk the spec never mentions** — a hand-added skill, a rule someone dropped in outside the harness-creator flow, or any other edit the harness picked up between passes.
- **A spec row whose `status` claims a file that isn't there** — a row at `generated` or `validated` with nothing on disk.

There is no goals-to-validation traversal in `sync`. The interview is just that list, walked one item at a time, asking per item: correct the spec to match reality, or regenerate the files to match the spec? The status column carries the meaning the filesystem alone can't:

| Status | Claims a file exists? | A missing file means |
|---|---|---|
| `proposed` | No | Nothing — surfaced during I2, not yet approved |
| `approved` | No | Nothing — locked as intent, generation not started |
| `generated` | Yes | Generation was interrupted or failed partway |
| `validated` | Yes | It existed and passed, then something removed it |
| `declined` | No | Nothing — deliberately not built; keep the row, it's the record of that decision |
| `retired` | No | Nothing — deliberately removed |

`proposed`, `approved`, `declined`, and `retired` are never drift — a harness paused mid-interview is full of `proposed`/`approved` rows, and reporting those on every re-entry would make a perfectly normal pause look broken. Only `generated`/`validated` rows without a matching file, or a file without a matching row, get flagged.

**Default to correcting the spec, not the files, and ask before doing anything else.** Divergence is not automatically corruption — a component on disk the spec doesn't mention is usually a teammate's ordinary work, another tool's, or a deliberate hand-edit, not damage to revert. "The spec is behind" is the common case; "the files are wrong" is the rare one. Record whichever resolution you land on in the spec's Change history as what it was — an external edit the spec now reflects — not as a file restoration, so the next reader can see the harness has more than one author.

Two things sync still cannot see, worth saying out loud when you present the list so a clean report doesn't read as "nothing changed": edits to the *contents* of `CLAUDE.md` (root or nested) never appear, because the audit inventories instruction files without diffing their prose against the spec; and edits to the *contents* of an existing component don't appear either — a skill whose body was quietly rewritten is still a file at the path the spec names, so it reads as perfectly in sync. The drift check is about existence, not correctness; `validate_harness.py` covers structural correctness; neither one confirms a component still does what its spec row says it does.

Whichever mode ran, the pass still ends the way a fresh build does: spec updated, `validate_harness.py` clean, and a Change-history entry recording what happened and in which mode — the Change history matters more after a re-entry than after a fresh build, since it's the only place the next pass learns this harness has been touched by more than one process.

## See also

- [The-Interview.md](The-Interview.md) — the five staged questions and approval gates that `new` runs in full and the other modes reshape.
- [Validation.md](Validation.md) — where improve-mode feedback usually originates, and the feedback-routing table it flows through.
- [Scripts.md](Scripts.md) — `audit_harness.py` and the other three CLIs the loop calls.
