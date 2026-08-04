# Positioning and messaging

## 1. Identity

- Display name: `Harness Creator`
- Code identifier: `harness-creator`
- Headline: `The interview-driven harness creator for Claude Code.`
- Supporting line: `Preserve Claude’s judgment. Enforce only what must not fail.`
- Audience: Claude Code users, including people who do not yet know harness terminology
- Voice: precise, quietly opinionated, evidence-first

## 2. Core model

`ai-agent = ai-model + ai-harness` is a design heuristic, not a literal or exhaustive definition. It directs attention to the project-specific context, procedures, permissions, hooks, and validation surrounding the model.

The completeness definition is fixed:

> Complete does not mean every layer. It means every identified need has a deliberate home, and no layer is generated without a reason.

## 3. Value proposition

Harness Creator audits the project, interviews the user, routes each identified need to an appropriate Claude Code surface, generates only the justified components, and validates their structure. Optional behavioral end-to-end testing is a separate, consent-gated step.

## 4. Vocabulary rules

- Do not use `architect` as the product category.
- Use `meta-skill` only when explaining the technical implementation.
- Prefer `interview-driven`, `project-specific`, `route`, `generate`, and `validate`.
- Say `structural validation` for deterministic linting.
- Say `optional behavioral end-to-end validation` for real Claude sessions.
- Never imply that structural checks prove behavior.

## 5. Claim boundaries

Public copy must not claim:

- consciousness, emotions, or moral status for Claude;
- that respectful treatment improves model performance;
- an 80% improvement from Harness Creator;
- official Anthropic verification or endorsement;
- cross-agent reliability that the project has not measured;
- behavioral correctness from structural validation alone.

Anthropic, Amanda Askell, and Boris Cherny appear only in explanatory rationale with claims limited to what their sources support.

## 6. Comparison frame

The public comparison uses four categories:

1. Manual configuration: maximum direct control, high expertise and maintenance burden.
2. Static template: fast start, limited project discovery and routing.
3. Component collection: reusable parts, assembly decisions remain with the user.
4. Harness Creator: structured audit and interview, deliberate layer routing, generation, and structural validation.

No named competitor appears outside this dossier.
