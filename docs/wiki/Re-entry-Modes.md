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
| Components on disk that the spec never mentions | `sync` — confirm whether to update the spec or the files |
| `validate_harness.py` finds real errors in the existing harness | `improve` — likely a pass to fix them |
| A spec exists, matches disk, and lints clean | `extend` or `improve` — ask the user directly |

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

`sync` is the smallest mode. Phase 0's audit already produced the drift list — components on disk that the spec doesn't mention (for example, a hand-added skill or a rule someone dropped in outside the harness-creator flow). There is no goals-to-validation traversal. The interview is just that list, walked one item at a time, asking per item: correct the spec to match reality, or regenerate the files to match the spec? Whichever direction you pick, the pass finishes with the spec and the disk back in agreement.

One direction of drift the audit reports conservatively: it flags files on disk that the spec omits, but it does not try to flag spec entries whose files have gone missing, because the spec's behavior-inventory table is free-form prose the script won't parse for that. Reading the spec's inventory against the audit's on-disk list — a job for the interviewing Claude, or you — is the reliable way to catch that other direction.

## See also

- [The-Interview.md](The-Interview.md) — the five staged questions and approval gates that `new` runs in full and the other modes reshape.
- [Validation.md](Validation.md) — where improve-mode feedback usually originates, and the feedback-routing table it flows through.
- [Scripts.md](Scripts.md) — `audit_harness.py` and the other three CLIs the loop calls.
