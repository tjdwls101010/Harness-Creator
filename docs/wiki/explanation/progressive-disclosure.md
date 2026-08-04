# Progressive disclosure

This explanation shows why Harness Creator loads context at the branch where it becomes useful instead of placing every instruction up front.

## 1. Context has recurring cost

Root `CLAUDE.md`, unscoped rules, and a skill's always-loaded body compete with the user's task, repository evidence, tool results, and conversation history. An instruction that is valuable during hook authoring can be noise during a documentation-only task.

Progressive disclosure reduces that conflict by keeping discoverable pointers present and loading details only when needed.

## 2. Split by invocation pattern

A useful split answers a real runtime branch:

- every invocation needs the operating loop;
- only a fresh or delta build needs the interview reference;
- only re-entry needs the re-entry reference;
- only hook generation needs hook authoring guidance;
- only one selected hook event needs its event schema.

File length alone is not a reason to split. A short file behind an unreliable pointer can cost more than it saves.

## 3. Progressive disclosure is not omission

Deferred content still needs a discoverable, accurate route. A skill description must expose when the procedure applies. A parent reference must name the child resource and the condition for reading it. A script interface should make the parameter space visible.

When a task cannot find the deferred detail reliably, the design has hidden required context rather than disclosed it progressively.

## 4. The repository's pattern

| Surface | Load point |
|---|---|
| `SKILL.md` | Every Harness Creator invocation |
| Interview or re-entry reference | After Phase 0 chooses a mode |
| Component reference | When routing reaches that component |
| Hook event row | When an event is selected |
| Python implementation | Executed as a subprocess, not loaded as prose |

This pattern keeps the main skill focused while preserving reviewable primary guidance beside it.

## 5. Empirical deletion

Progressive disclosure should be measured, not treated as aesthetic doctrine. When duplicated or overlapping instructions are removed, evaluate whether behavior or structural compliance changes. Keep product context, useful references, test rubrics, and deterministic controls that still carry evidence.

Deletion is successful when the removed instruction was redundant, not when a file merely becomes shorter.

## 6. Failure modes

- Over-splitting: too many pointers must be followed for one procedure.
- Duplicate authority: the same rule appears in several layers and later conflicts.
- Hidden prerequisite: a deferred file contains information needed before its load condition.
- Stale pointer: a path or event name changes without updating the router.
- Always-loaded index bloat: the navigation surface becomes the documentation it was meant to defer.

## 7. Next

Read [Architecture](architecture.md) for the concrete load path or [Principles and verified boundaries](principles-and-verified-boundaries.md) for the relationship between context and enforcement. Return to the [documentation index](../README.md).
