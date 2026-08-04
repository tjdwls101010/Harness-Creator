# Principles and verified boundaries

This explanation separates judgment for unenumerable cases from deterministic control for behavior that must not fail.

## 1. Two kinds of need

Some project decisions depend on context that cannot be exhaustively listed. “Write code that fits the surrounding module” requires judgment about naming, abstraction, and local style.

Other requirements have a crisp unacceptable state. “Never edit an applied migration” can be checked before the action and blocked.

Treating both as prose weakens the second. Treating both as rigid code makes the first brittle.

![Two-lane graphical abstract: Principles and context flow through Model judgment to Adapt to the case; Non-negotiable constraints flow through Hooks, permissions, and tests to Block or verify; both converge on Adaptable behavior within verified boundaries.](../../assets/figures/principles-and-verified-boundaries.png)

*Adaptable behavior comes from combining case-sensitive judgment with controls that verify or block the boundaries the project cannot leave to interpretation.*

## 2. Judgment for cases that cannot be enumerated

Principles, goals, examples, and project facts help the model infer the right action in a new case. They should explain what success means and why a constraint matters without prescribing a method that is wrong for plausible exceptions.

The test is not whether the instruction sounds strong. It is whether the model has enough context to make a sound decision in a case the author did not anticipate.

## 3. Deterministic controls for non-negotiable behavior

Hooks, permissions, scripts, schemas, and tests are appropriate when the project needs a repeatable decision independent of conversational context. They can reject a tool call, limit access, validate an artifact, or fail automation.

Deterministic does not mean automatically correct. The control still needs representative allowed, denied, boundary, and failure inputs. A bug in enforcement can be more disruptive than an advisory instruction.

## 4. Progressive disclosure reduces conflict

Always-loaded context should contain high-frequency facts and principles. Narrow procedures belong in skills. Path-specific conventions belong in scoped rules. Event-specific contracts can sit behind a query. This reduces the chance that several versions of a rule compete in the same context.

The objective is not the fewest tokens. It is the least conflicting context that still makes the needed guidance available at the right time.

## 5. Delete redundant rules empirically

Anthropic reported removing more than 80% of the Claude Code system prompt for newer models with no measurable loss on its coding evaluations. The supported lesson is to identify overlapping constraints, remove them, and evaluate the result while retaining useful product context, interfaces, references, and deterministic controls.

It does not support applying the same percentage to another harness, deleting constraints without evaluation, or claiming an 80% performance improvement.

## 6. Annotated primary sources

- [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) — Anthropic's account of overconstraint, empirical prompt reduction, progressive disclosure, and designing interfaces instead of repeating examples.
- [Steering Claude Code: when to use CLAUDE.md, skills, hooks, and subagents](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) — the product-level differences in load timing, compaction, context cost, and authority; it explicitly recommends hooks or permissions for real guardrails.
- [Claude's Constitution](https://www.anthropic.com/constitution) — primary context for principle-guided judgment, operator intent, and handling cases not explicitly covered by instructions.
- [Amanda Askell interview](https://podcast.newcomer.co/episode/amanda-askell-on-ai-consciousness-claude-amp-silicon-valleys-biggest-fear) — relevant here only for the engineering observation that novel situations require judgment and that judgment-heavy evaluation is difficult. It is not evidence for claims about model consciousness or performance gains from treatment.

## 7. Supports and does not support

| The sources support | The sources do not support |
|---|---|
| Give principles and context for cases that cannot be enumerated | Claude will always infer the intended action |
| Use deterministic controls for non-negotiable boundaries | Every important instruction must become a hook |
| Load narrow detail only when relevant | Shorter context is automatically better |
| Remove redundant constraints and evaluate the result | A universal 80% reduction or improvement claim |
| Preserve useful product context, references, evaluations, and controls | Claims about consciousness, emotions, or model welfare |

## 8. Practical synthesis

1. State the project purpose and success criteria.
2. Give the model the facts needed to adapt to the case.
3. Identify the states the project cannot accept.
4. Enforce or verify those states with the narrowest deterministic control.
5. Test the control and evaluate whether surrounding prose remains necessary.
6. Record both the principle and the boundary in the harness spec.

## 9. Next

Apply the model with [Layer routing](layer-routing.md), or see the exact control surfaces in [Generated components](../reference/generated-components.md). Return to the [documentation index](../README.md).
