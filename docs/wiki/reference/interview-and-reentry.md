# Interview and re-entry reference

This reference defines the interview stages, approval gates, re-entry modes, and behavior statuses.

## 1. Phase 0 audit

Every invocation begins with an audit before interview questions. It inventories `CLAUDE.md`, rules, skills, settings, hooks, agents, workflows, and the harness spec; reports structural findings and existence-level drift; then suggests a mode.

The audit cannot infer user intent when a clean harness could be either extended or improved. The user decides.

## 2. Interview stages

| Stage | Purpose | Output |
|---|---|---|
| I1 — Goals and pain points | Establish the desired change and calibrate terminology | Goals and context |
| I2 — Behavior inventory | Convert prose into discrete needs | Numbered inventory rows |
| I3 — Layer routing | Select a layer for every approved need | Layer, component, rationale |
| I4 — Component detail | Resolve trigger, scope, authority, inputs, outputs, and failure policy | Component specifications |
| I5 — Validation plan | Define observable evidence and whether E2E is approved | Validation scenarios |

Stages can be compressed for a small request. The spec approval gate remains mandatory before generation.

## 3. Question style

Divergent questions use open conversation because the answer space cannot be enumerated safely. Convergent decisions use a short structured choice with tradeoffs. Repository facts are stated from inspection rather than asked again.

## 4. Re-entry modes

| Mode | Entry condition | Interview shape |
|---|---|---|
| `new` | No existing harness | Full I1–I5 path |
| `extend` | Add a new need to a working harness | I1 asks only what is new; I2–I5 cover the delta |
| `improve` | Existing behavior is wrong or uncomfortable | I1 becomes failure evidence; later stages target the owning layer |
| `sync` | Spec and disk disagree | Walk the drift list; do not repeat I1–I5 |

## 5. Behavior statuses

| Status | Meaning | Claims a file exists? |
|---|---|---|
| `proposed` | Identified but not approved | No |
| `approved` | Approved intent awaiting generation | No |
| `generated` | A component was written | Yes |
| `validated` | The generated component passed its checks | Yes |
| `declined` | Considered and deliberately not built | No |
| `retired` | Previously present and deliberately removed | No |

Only a missing file for a `generated` or `validated` row is existence-level drift. Proposed, approved, declined, and retired rows are intentional no-file states.

## 6. Approval gates

Each stage writes its result into the spec and seeks confirmation before advancing. A compressed interview can combine gates, but generation still requires explicit approval of the complete proposed spec.

Optional behavioral E2E also requires explicit consent because it can consume model tokens and execute behavior in a real session.

## 7. Wrap-up

After generation, Harness Creator validates the final state, updates component statuses and validation evidence, appends change history, and proposes a commit. It does not treat a pre-generation check as evidence that the generated files are valid.

## 8. Next

Read [Harness spec](harness-spec.md) for the file schema or [Layer routing](../explanation/layer-routing.md) for I3's decision model. Return to the [documentation index](../README.md).
