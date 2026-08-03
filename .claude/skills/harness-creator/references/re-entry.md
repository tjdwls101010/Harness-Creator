# Re-entry: extend, improve, and sync

Read this when Phase 0's audit found an existing harness. It covers the three re-entry modes and, in full, the sync procedure — which is the one mode that runs without an interview at all. For a fresh build, or for the stage-by-stage protocol that extend and improve reuse, read `references/interview.md` instead.

The audit's suggested mode is a hint, not a verdict. It can tell `new` from `not-new` reliably, and it can detect drift, but **extend and improve look identical on disk** — the difference lives entirely in what the user wants, so ask them directly rather than inferring: "what's newly wanted?" versus "what's been uncomfortable?"

## Extend — the harness is fine, there's more to add

Shrink I1 to a single question: what's newly wanted, beyond what's already here? Everything else follows the normal stage flow against the delta, since a new behavior still needs inventory, routing, and component detail even when the surrounding harness already exists. Merge the resulting Goals content into the existing spec's Goals section rather than replacing it — the old goals didn't stop being true.

## Improve — the harness exists and something about it is wrong

Replace I1 entirely. The question is not "what's the goal" but **"what was uncomfortable, wrong, or annoying about how this behaves?"** — the framing shifts from greenfield intent to observed failure, and the answers are usually symptoms rather than diagnoses.

Route each symptom through the feedback-routing table in `references/e2e-testing.md` (wrong trigger → the description; triggered but did the wrong thing → the skill body; the rule was ignored → CLAUDE.md, then escalate to a hook). That table also tells you which stage of the interview protocol to re-enter at, so you rarely need to re-run all five.

## Sync — the spec and the disk disagree

Sync has no I1-I5 traversal. Phase 0's audit already produced the drift list, in both directions:

- **A spec row whose `status` claims a file that isn't there** — a row at `generated` or `validated` with nothing on disk.
- **A file on disk the spec never mentions.**

The whole mode is: present that list, and ask per item whether the spec should be corrected to match reality or the files regenerated to match the spec.

### Default to correcting the spec, and ask before anything else

**Divergence is not automatically corruption.** A component on disk the spec doesn't mention is usually a teammate's ordinary work, or another tool's, or a deliberate hand-edit — not damage to be reverted. The same goes for behavior that migrated out of CLAUDE.md into a skill: someone made a routing decision, and it may well have been the right one. Establish which case you're in before offering to regenerate anything. "The spec is behind" is the common case; "the files are wrong" is the rare one. A sync pass that quietly reverts a colleague's work is far worse than one that asks an unnecessary question.

Record the resolution in the spec's Change history as what it was — an external edit that the spec now reflects — rather than as a file restoration. The next person reading the history needs to see that the harness has other authors.

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

State this when you present the list, because otherwise a clean drift report reads as "nothing changed":

- **Edits to CLAUDE.md itself never appear** — root or nested. The audit inventories instruction files but does not diff their contents against the spec. If the drift you're chasing is "someone rewrote a section of CLAUDE.md," you have to read it and compare by hand.
- **Edits to the *contents* of a component don't appear either.** A skill whose body was rewritten is still a file at the path the spec names, so it reads as perfectly in sync.
- The drift check is about existence, not about correctness. `validate_harness.py` covers structural correctness; neither covers whether a component still does what its spec row says it does.

## After any re-entry mode

Re-entry ends the same way a fresh build does — spec updated, `validate_harness.py` clean, Change history recording what happened and in which mode. The Change history entry matters more here than on a fresh build: it is the only place the next pass learns that this harness has been edited by more than one process.
