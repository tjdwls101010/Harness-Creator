# Re-entry: extend, improve, and sync

Read this when Phase 0's audit found an existing harness. It covers the three re-entry modes and, in full, the sync procedure — which is the one mode that runs without an interview at all. For a fresh build, or for the stage-by-stage protocol that extend and improve reuse, read `references/interview.md` instead.

The audit's suggested mode is a hint, not a verdict. It can tell `new` from `not-new` reliably, and it can detect drift, but **extend and improve look identical on disk** — the difference lives entirely in what the user wants, so ask them directly rather than inferring: "what's newly wanted?" versus "what's been uncomfortable?"

## Extend — the harness is fine, there's more to add

Shrink I1 to a single question: what's newly wanted, beyond what's already here? Everything else follows the normal stage flow against the delta, since a new behavior still needs inventory, routing, and component detail even when the surrounding harness already exists. Merge the resulting Goals content into the existing spec's Goals section rather than replacing it — the old goals didn't stop being true.

## Improve — the harness exists and something about it is wrong

Replace I1 entirely. The question is not "what's the goal" but **"what was uncomfortable, wrong, or annoying about how this behaves?"** — the framing shifts from greenfield intent to observed failure, and the answers are usually symptoms rather than diagnoses.

Route each symptom through the feedback-routing table in `references/e2e-testing.md` (wrong trigger → the description; triggered but did the wrong thing → the skill body; the rule was ignored → CLAUDE.md, then escalate to a hook). That table also tells you which stage of the interview protocol to re-enter at, so you rarely need to re-run all five.

**Ask the second question in the same breath: what is now unnecessary?** Every arrow in that routing table ends in a repair or a promotion, so a harness that is improved often only ever grows. Nothing on disk tells you what stopped earning its keep — there is no invocation telemetry — so if you don't ask, nobody does. Ask both, and take "nothing comes to mind" as a real answer rather than pressing for one.

### Instructions go stale in a way components do not

A component that stopped being used is at least visible as a file. A *line* that stopped being needed is invisible: a rule written to fight a model's old default reads exactly like one still fighting the current default, and the model changes under a harness that doesn't. That is the dead weight that accumulates fastest, because every pass adds rules and no pass re-examines the ones already there.

**Ablation is how you find out, and it is a proposal, not an action.** Take one rule you suspect — start with the ones written to fight a default, since those are the ones a better model may have stopped needing — remove it, and run the work it was written for. Nothing goes wrong: it was carrying nothing. Something does: you have just re-earned it, and that belongs in the spec's Design rationale, because the next pass will suspect it again and should not have to re-run the experiment.

One rule at a time. Removing several at once turns a clean result into a guess about which one mattered. And **never ablate a hook or a permission rule** — those layers exist precisely because their failure mode is the one you cannot afford to observe once.

## Sync — the spec and the disk disagree

Sync has no I1-I5 traversal. Phase 0's audit already produced the drift list, in both directions:

- **A spec row whose `status` claims a file that isn't there** — a row at `generated` or `validated` with nothing on disk.
- **A file on disk the spec never mentions.**

The whole mode is: present that list, and ask per item whether the spec should be corrected to match reality or the files regenerated to match the spec.

### Default to correcting the spec, and ask before anything else

**Divergence is not automatically corruption.** A component the spec doesn't mention is usually a teammate's work, another tool's, or a deliberate hand-edit; behavior that migrated from CLAUDE.md into a skill is someone's routing decision, possibly a better one than yours. "The spec is behind" is the common case, "the files are wrong" is the rare one, and quietly reverting a colleague's work is far worse than asking an unnecessary question. Establish which you're in first.

Record it in Change history as what it was — an external edit the spec now reflects, not a file restoration — so the next pass sees that this harness has other authors.

### Reading the status column

The `status` values carry meaning the filesystem cannot, which is why the audit reports the row rather than just the missing path:

| Status | Claims a file exists? | A missing file means |
|---|---|---|
| `proposed` | No | Nothing — surfaced in I2, not yet approved |
| `approved` | No | Nothing — locked as intent, generation not started |
| `generated` | Yes | Generation was interrupted or failed partway |
| `validated` | Yes | It existed and passed, then something removed it |
| `declined` | No | Nothing — deliberately not built (keep the row; it's the record of a decision) |
| `retired` | No | Nothing — deliberately removed |

`proposed` and `approved` are never drift. A harness paused mid-interview is full of them, and reporting those would make every re-entry look broken. The two that assert a file are the two the audit acts on, and they want different questions: an interrupted generation usually just needs finishing, while a component that was validated and then vanished is a question about who removed it and why.

### What sync cannot see

Say this when you present the list, or a clean report reads as "nothing changed." **The check is about existence, not correctness.** So edits to CLAUDE.md never appear (the audit inventories instruction files without diffing them), and neither do edits to a component's *contents* — a rewritten skill body is still a file at the path the spec names, and reads as perfectly in sync. Compare those by hand.

Re-entry then ends like a fresh build: spec updated, `validate_harness.py` clean, Change history written. That last entry carries more weight here — it's the only place the next pass learns this harness has more than one author.
