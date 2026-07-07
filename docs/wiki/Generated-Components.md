# Generated Components

A tour of the seven layers harness-creator can put in a target project — CLAUDE.md, rules, skills, hooks, permissions, agents, workflows — plus the `harness-spec.md` record that ties them together. For each layer: what it is, when harness-creator reaches for it, and one concrete gotcha it handles so you don't have to. How the choice between layers actually gets made lives in [Layer-Routing.md](Layer-Routing.md); this page is the catalogue of what comes out the other side.

The one thing to hold onto while reading: harness-creator generates only the layers your project actually needs. There is no fixed default set — no "every harness gets five agents," no "always ship a workflow." A project whose whole need is a CLAUDE.md and two hooks gets exactly that. Each layer below is generated only when the interview surfaces a concrete need for it.

## CLAUDE.md

The first and most-loaded layer: project facts and constraints delivered to Claude as a user message injected after the system prompt, read once at the start of every session. It carries what Claude cannot infer from reading the code — non-default build and test commands, style rules that diverge from the language's own defaults, architecture decisions invisible from the file structure, environment quirks. It is advisory, not enforced: Claude tries to comply the way it complies with anything else in the conversation, so anything that must hold with zero exceptions routes to hooks and permissions instead.

harness-creator chooses CLAUDE.md for a fact or constraint that nearly every request needs, and keeps it under ~200 lines because adherence measurably drops as the file grows.

**Gotcha it handles for you:** it never lists your skills, agents, or hooks by name. A hand-maintained inventory in CLAUDE.md starts drifting the moment anyone adds or renames a component, and nobody remembers to update the prose. Instead the generated CLAUDE.md points at `.claude/harness-spec.md` for the full picture and lets the filesystem be the source of truth for what exists.

## Rules

`.claude/rules/*.md` — conventions scoped to one part of the tree, loaded only when Claude touches a matching file. A migration convention that only applies under `src/db/**` belongs here, not in CLAUDE.md, so that most sessions never pay for context they don't need.

harness-creator chooses a rule when a convention matters in one region of the codebase rather than everywhere, or when the same pattern (`*.test.ts` across many packages) needs to be targeted centrally.

**Gotcha it handles for you:** every generated rule file gets a `paths:` glob in its frontmatter. A file dropped in `.claude/rules/` *without* `paths:` loads at launch with the exact same priority as CLAUDE.md itself — so splitting content into `rules/` buys nothing if the frontmatter is missing. The `paths:` key is what actually makes a rule lazy-load.

## Skills

`.claude/skills/<name>/` — a procedure, domain playbook, or reference asset that loads only when a specific job comes up. The metadata (name + description) sits in context every session; the SKILL.md body loads only once the skill triggers, and bundled `references/` and `scripts/` load only when a step reaches them. A skill is a repeated prompt turned into an on-demand asset — and it earns generation only when there's a real gotcha worth capturing, not just a restatement of what a capable model already knows.

harness-creator chooses a skill for on-demand know-how, and actively looks to consolidate related behaviors during the interview rather than minting one skill per requested behavior.

**Gotcha it handles for you:** skill count is a real cost. Every skill's `description` sits in a shared listing budget of roughly 1% of the context window, spent every session whether or not any skill triggers. Add skills one at a time and each new description silently taxes the others; once the listing overflows, the least-recently-used descriptions collapse to bare names, quietly disabling their ability to auto-trigger with no error. So harness-creator weighs consolidation into the behavior inventory itself.

## Hooks

`.claude/hooks/*.sh|*.py` scripts wired through `.claude/settings.json` — the enforcement layer, the only one that is deterministic rather than advisory. A hook fires on a lifecycle event regardless of what the model decides, which is why it's the home for "must happen every time" (a formatter always runs) and "must never happen" (a protected path is never edited).

harness-creator chooses a hook when the interview surfaces something that must never be violated — and pairs it with a permission rule, because a hook's own `if` filter is best-effort and fails open on input it can't parse.

**Gotcha it handles for you:** exit 1 does not block anything. This inverts ordinary Unix convention, where nonzero means failure — in Claude Code's hook contract only **exit 2** blocks, and exit 1 is a *non-blocking* error that lets the action proceed anyway while showing an easy-to-miss stderr notice. A hook written to enforce a policy that exits 1 on the violation path silently does nothing. harness-creator generates the correct exit-code shape and verifies every hook with `test_hook.py` before calling it delivered — see [Scripts.md](Scripts.md).

## Permissions

The `permissions.allow` / `permissions.deny` block in `.claude/settings.json` — rules enforced by the client itself, independent of model behavior. Deny and ask rules apply immediately; allow rules grant. This is where a specific tool, command, or path gets force-approved or blocked outright.

harness-creator chooses a permission rule for a concrete allow/deny, and always pairs a `permissions.deny` rule with the hook for anything that must be truly unbypassable — the deny rule holds even under `bypassPermissions` mode, where a hook is the wall and the deny rule is the guarantee behind it.

**Gotcha it handles for you:** it generates narrow allow rules (`Bash(npm test)`), not broad ones (`Bash(*)`). When a session enters auto mode, Claude Code silently suspends broad allow rules that grant arbitrary code execution — a blanket `Bash(*)` or wildcarded interpreter simply stops covering anything the moment the mode switches, with no error. Narrow, specifically-named rules are the only kind that keep working across every permission mode.

## Agents

`.claude/agents/*.md` — custom subagents that isolate context and can restrict tools or carry a distinct system prompt per role. The right fit for a context-hungry, read-heavy job (research, code review, QA) where only the conclusion needs to survive back in the main thread, not the search trail that produced it.

harness-creator generates an agent only when the interview demonstrates a real need — context isolation that's actually valuable, or a genuine tool-restriction requirement — never as a default architecture. Making "four or five agents" the reflexive shape for every harness regardless of domain is exactly the antipattern it avoids; agent count is itself a routing cost.

**Gotcha it handles for you:** an agent's markdown body becomes its *entire* system prompt — Claude Code's default system prompt (be concise, prefer editing over rewriting, run tests before declaring done) is gone entirely for that agent's run. A one-line body like "you are a code reviewer, review the code" is not a thin version of the default; it's the whole thing, with everything else absent. harness-creator writes generated agent bodies as a full brief, spelling out behavior that would otherwise be ambient.

## Workflows

`.claude/workflows/*.js` — an orchestration whose shape is fixed and repeats (same phases, only the arguments change) frozen into a checked-in, one-button `/name` command. A recurring pre-release sweep is the archetype: same lint, type-check, changelog audit, dependency scan every time, only the branch name varying. The script stays thin — fan-out / collect / gate skeleton only — with every judgment call living inside the agent prompt strings, not the JS control flow.

harness-creator chooses a workflow only when the orchestration's shape is genuinely stable; a variable-shaped task gets natural-language guidance to compose a fan-out on the fly instead, because a rigid script for a variable task is a flexibility tax.

**Gotcha it handles for you:** every agent a workflow spawns runs in `acceptEdits` mode and inherits the session's tool allowlist as-is, with no interactive prompt waiting mid-run. So any `Bash`, `WebFetch`, or MCP tool the workflow's agents will need must already be in `permissions.allow` before launch, or the run stalls. harness-creator generates those allow entries in the same pass as the workflow, and — because workflows are version-, plan-, and opt-in-gated — documents a subagent-sequential fallback alongside any workflow it ships.

## The spec file: harness-spec.md

`.claude/harness-spec.md` is not one of the seven layers — it's the record that binds them. It's the single source of truth for what the harness contains and why: the interview updates it at the end of every stage, and every generation or edit updates it in the same pass, so it never drifts silently from the files on disk (`audit_harness.py`'s drift check exists to catch the times it slips). The generated CLAUDE.md points here rather than enumerating components itself. On the next invocation, the spec is what harness-creator audits against — which is why the spec-approval gate during the interview is the one step that never gets skipped.

## The standard generated output tree

When harness-creator generates a harness into a target project, the shape it produces is:

```
<target-project>/
├── CLAUDE.md                        # < 200 lines, pointer policy — no component enumeration
└── .claude/
    ├── harness-spec.md              # the spec record — single source of truth
    ├── settings.json                # hooks + permissions
    ├── rules/*.md                   # path-scoped rules (only if needed)
    ├── skills/<name>/SKILL.md       # domain skills (only if needed)
    ├── agents/*.md                  # custom subagents (only if needed)
    ├── workflows/*.js               # predefined workflows (only if needed)
    └── hooks/*.sh|*.py              # the hook scripts settings.json references
```

Read the "(only if needed)" comments literally. `rules/`, `skills/`, `agents/`, and `workflows/` appear only when the interview produced a concrete need for each — a real harness for a small project may be just CLAUDE.md, `settings.json`, and `harness-spec.md`. Two conventions hold throughout the tree: hook scripts live in `.claude/hooks/` and are referenced from `settings.json` by their `${CLAUDE_PROJECT_DIR}/.claude/hooks/<name>` absolute path (exec form), and every output uses only committable surfaces — `settings.local.json` is generated only when personal, non-shared configuration is genuinely required, and only after telling you first.

One more thing worth knowing before the first write: everything under `.claude/` is a protected path, so the first write in a session prompts for approval no matter what allow rules exist (the safety check runs before allow-rule evaluation). harness-creator warns you this prompt is coming, and choosing "allow Claude to edit its own settings for this session" clears the follow-up writes.

## See also

- [Layer-Routing.md](Layer-Routing.md) — the three-question framework that decides which of these layers each behavior lands in.
- [Scripts.md](Scripts.md) — `validate_harness.py`, `audit_harness.py`, and `test_hook.py`, which check and verify everything on this page.
- [The-Interview.md](The-Interview.md) — how the interview turns your goals into the concrete component specs generated here.
