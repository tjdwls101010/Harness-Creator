---
name: harness-creator
description: >
  Design, generate, validate, and maintain a complete Claude Code harness
  (CLAUDE.md, rules, skills, hooks, permissions, agents, workflows) for a project
  through a structured interview. Use when the user wants to create or set up a
  harness / CLAUDE.md / skills / hooks for a project, improve or extend an
  existing .claude/ setup, or asks how Claude should be configured to work on
  their codebase. Also triggers on Korean requests like "하네스 만들어줘",
  "하네스 구성해줘", "클로드 세팅해줘".
---

# harness-creator

## What a harness is, and what this skill does

`ai-agent = ai-model + ai-harness`. A harness — CLAUDE.md, rules, skills, hooks, permissions, agents, workflows — supplies the context, capabilities and boundaries a model needs for a project. A good one lets the model reason through cases its author never enumerated while enforcing the boundaries that cannot depend on judgment.

This skill turns a request into an approved design, generates it, and checks the resulting behavior. A complete harness gives every established need an appropriate home; it does not need every available component. The user owns the goals and authority boundaries, and you propose the design and the evidence that would establish it before generation. Preserve an existing approval wherever its inputs still hold.

Use `scripts/audit_harness.py` to locate the existing harness and the commits that shaped it before proposing changes. The target project's files and prior decisions are the design inputs; history supplies reasons, not permission to overwrite a conflicting current file. A repair starts from the reported behavior and follows the routing table back to its cause. Consider what is no longer needed alongside additions, since a harness can accumulate components without recording whether they are still used.

Run bundled scripts with Python 3 using `${CLAUDE_SKILL_DIR}/scripts/<name>.py`. The target project's working directory and a plugin's cache directory are different places, so a project-relative path does not locate the bundle. Read a CLI's `--help` on first use. `${CLAUDE_SKILL_DIR}` is substituted in this skill's markdown, not in a workflow prompt or a subagent's shell; resolve the absolute path in this session before delegating a call.

## The layer-routing framework

Choose the surface by what must hold, when it must arrive, and who needs it. Before encoding a requirement in prose or a hook, inspect the interface the model would operate: an explicit argument, schema or restricted tool surface may make the invalid action unavailable. Use prose for judgment; use an enforceable boundary for a prohibition that must hold regardless of judgment.

| What the requirement needs | Layer | Why it belongs there | When it fails, investigate |
|---|---|---|---|
| Project context needed across requests | CLAUDE.md | Supplies facts and intent at session start | Whether the instruction reaches the session and gives a usable reason; a must-never requirement belongs in enforcement |
| Guidance for a particular part of the tree | `.claude/rules/*.md` with `paths:` | Reaches the model when that scope is read | The glob against the paths the model actually reads |
| Knowledge or a procedure needed for a particular job | Skill | The description selects when the body is needed | Discovery before wording: frontmatter, listing visibility, invocation policy and compaction can prevent the body arriving at all; then examine trigger boundaries and the body's reasoning |
| A required response to an event, or a content-dependent block | Hook | Runs at the event rather than relying on a remembered instruction | The event, matcher and actual input, reproduced with `scripts/test_hook.py`; an over-broad block may need a narrower condition or an advisory response |
| A tool, command or path access boundary | Permissions | The client applies the rule independently of the model | The effective deny and ask rules before any allow; a separate allow does not carve an exception out of a deny |
| A distinct role whose result matters more than its search trail | Agent | Separates context and can restrict the role's tools | The startup context and tools the role actually receives, especially built-in Explore and Plan |
| An orchestration that repeats with a stable shape | Workflow | Makes the repeatable coordination executable | Required permissions, availability and whether the shape is still stable; variable coordination belongs in guidance |
| Parallel work whose shape depends on the request | Guidance in a skill or CLAUDE.md | Lets the model compose the coordination for this case | Whether the delegation supplies the context and result contract each role needs |

The table chooses a candidate, not its full contract. Read the relevant authoring guide while deciding whether it qualifies: `references/claude-md-and-rules.md`, `references/skills.md`, `references/hooks.md` for hooks and permissions, `references/agents.md` or `references/workflows.md`. Keep that guide through generation; after compaction, reload the selected references because their earlier reads may have been summarized away. For an individual hook event, use `scripts/hook_event.py` to retrieve its contract rather than loading the whole event catalog.

One requirement can need more than one surface. A hook protecting a must-never tool action needs the corresponding permission deny where the rule can express the same prohibition: the hook only covers calls it receives, and an `@file` expansion is not a Read call. An event obligation without an equivalent permission rule stands alone. The explanation of why a block exists belongs in guidance where the model needs it; the enforcement belongs in the mechanism. `references/hooks.md` describes the remaining coverage limits, including writes through subprocesses.

Establish the intended distribution before choosing components: skills, agents, hooks and workflows can be packaged, while CLAUDE.md, rules and permissions travel as a repository tree rather than plugin components. A reference into the source repository is unusable to an installed skill unless that target ships with it.

Distinguish shared facts from machine-local ones. Personal URLs and local test data belong in `CLAUDE.local.md`, not in a file every clone inherits. Distinguish relevant context from indiscriminate loading: unscoped rules and imports join the always-loaded context, descriptions compete for discovery, and unnecessary roles complicate routing. Consolidate components that serve the same job; keep separate ones whose triggers or authority differ.

Keep the decision to have a capability separate from its implementation, and approve the routing before generating it. Expose each advisory-versus-enforced choice: a misplaced block can prevent legitimate work. New `permissions.allow` entries need explicit approval naming what each grants, since they remove a checkpoint for every clone. Deny and ask rules belong in the design approval with their effect on legitimate operations; they do not require a separate permission-expansion approval. Existing authorization remains valid until the scope changes. Protected `.claude/` writes have their own client restrictions, which an allow rule cannot remove; explain an applicable restriction before the first write rather than promising that a rule pre-approves it (`references/hooks.md`).

## Authoring philosophy

Write instructions the model can re-derive: the desired behavior, the reason that determines it, and a concrete case where the distinction matters. The reason earns its place when it also guides an unlisted case. A fixed sequence or absolute prohibition needs a failure that explains why the model cannot choose another approach; an example illustrates the principle without silently becoming the only permitted shape.

Write for the model using the harness. Keep the **gotcha** that general competence cannot supply: a silent failure, an invisible project decision, a boundary the model would otherwise misread. The history of discovering it belongs in development records unless that history changes the next execution's judgment. A paragraph in a reference earns its place by changing what the builder writes or does.

Density means preserving the knowledge needed to decide while removing work the reader need not do. Keep the clause that makes the rule re-derivable; cut restatements, arguments that merely defend it, consequences the reader can compute, and narration of what comes next. Group related conditions with the judgment they qualify rather than compressing unrelated obligations into one paragraph. A useful example or necessary exception is not expendable to meet a word count. Numbers need a reason and the conditions under which another value is right.

Prefer an interface over a document for knowledge the tool owns. A bundled CLI, hook configuration, workflow argument, skill description or agent tool list can express the available choices where the model acts. The tool owns valid input, behavior and output; the harness owns when to use it and why it fits the task. If changing the tool would falsify a sentence, put that contract in its interface rather than maintaining a prose copy. Help text and failure messages must agree with the implementation; placing prose in `--help` alone does not make it true.

A reference can be a schema, a failing test, a rubric or a function instead of prose. When the user describes what good looks like, look for an existing artifact that establishes it. Progressive disclosure is useful at a real decision branch: a model choosing one variant should read that variant. Files always needed together gain no such separation. For a long body, remove unnecessary content first, then split where reading can genuinely be deferred; a guideline about size does not decide that boundary.

A pointer inherits its target's reader. A file that exists in the development repository can still be absent from the installed plugin, so verify the distribution boundary as well as local existence. Do not make the model read a maintainer document to recover runtime knowledge. Likewise, CLAUDE.md should name a component only when its condition, purpose or constraint changes the session; a registry of names duplicates discovery and drifts. `references/claude-md-and-rules.md` gives the boundary.

Write Markdown paragraphs without hard-wrapping them. Renderers wrap for the reader; inserted line breaks interrupt exact-string edits and obscure the change in a diff.

## Verify the intended behavior

Choose the evidence with the design, before generation. Structural validity, a hook responding correctly, a skill triggering on the intended request, and the quality of a generated artifact are different claims. An existing test, schema or worked example can establish the expectation; a verifier must not derive its expected answer from the output it is grading.

Use `scripts/validate_harness.py` on the final files, including any CLAUDE.md pointer edits. Its CLI describes the checks and exit statuses; a passing structural check does not show that the instructions were followed. Exercise generated or rewired hooks with `scripts/test_hook.py` on both intended matches and legitimate operations that must pass. Inspect the outcomes against the approved expectation, not merely whether the test command completed.

For behavior that a structural check cannot establish, run scenarios against the generated harness using `scripts/run_e2e.py` and `references/e2e-testing.md`. Choose coverage from the independent behaviors and failure modes in the design, including trigger near-misses and attempts that might bypass an enforcement surface. Use the model the harness will actually serve so the observed behavior answers the user's question. Compare with the previous or unharnessed behavior when that comparison establishes the effect under investigation.

Isolate scenarios that write and inspect their actual artifacts. A protected production path must not become an experiment: preserve active hook and permission protections, and test alternative enforcement in an isolated environment. For advisory rules fighting a model default, removing one rule at a time can reveal whether it still contributes; a clean run is evidence for retirement, not proof, and a regression identifies what the rule was protecting. Record the conditions of either result so a later pass can interpret it.

Check descriptions for intended triggers and neighboring requests using `references/skills.md`, even when only one skill was generated. When the claim concerns question selection or approval behavior, exercise it in an interactive session: a headless run cannot validate an interview it cannot conduct. When an environment prevents a required check, report the unverified claim and the blocker rather than treating another kind of check as its substitute.

Repair the smallest causal scope, including paired rules, and rerun the failed scenarios and the surfaces the change reaches. Completion means the approved expectations have supporting evidence and the final files pass their structural checks. Report what was checked, the evidence, and any remaining uncertainty; do not turn one clean run into a guarantee about every future request.

## Preserve what the next change depends on

A handoff explains the change on the project's delivery surface; it is not another harness component to generate. The diff shows what changed; the handoff supplies the decisions that explain it, the evidence behind them, and what would reopen them. If current files contradicted a past decision, record how that disagreement was resolved. A reversal names the decision it supersedes, since immutable history cannot be updated in place.

Fold equivalent candidates rather than recording two names for one capability. Preserve why a candidate was declined and what would make it relevant again. Never created, removed, and still present with `disable-model-invocation` limiting how it is reached are distinct outcomes: confusing the last with removal invites a later pass to delete working content.

Put these reasons where the merge convention retains them. A squash retains one commit rather than the branch's separate bodies, and a pull request alone is unavailable in an offline clone. A decision that changed no files has no commit to carry it. Use an established record when one exists; otherwise return the handoff with the result and settle a durable location with the user before adding a file. Keep development records out of the runtime harness unless their contents are needed to act.
