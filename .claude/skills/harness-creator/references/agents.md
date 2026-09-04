# Agents and the other three ways to run work in parallel

This is the authoring guide for `.claude/agents/*.md` — custom subagents. It opens one level up, on the choice between four surfaces, because three of the four produce no agent file at all and an interview answer rarely names which one it means; then the eligibility test, the frontmatter fields that take a judgment call, and the gotchas to re-check a generated definition against.

## Four surfaces, one question: who decides what runs next

"We want several of these running at once" can land on any of four surfaces. The discriminant is **who decides what runs next**:

| Who decides | Surface | What the harness has to contain |
|---|---|---|
| Claude, turn by turn, inside one conversation | subagents | `.claude/agents/*.md` for a role that recurs; an ad hoc delegation needs no file |
| The user, handing tasks off and checking back later | agent view (`claude agents`) | **Nothing.** A way of working, not a component — at most one CLAUDE.md line if the project has a habit worth naming |
| A lead agent, assigning and supervising | agent teams | **Usually nothing** — a team forms at runtime. Pre-writing a teammate role as an ordinary subagent file is worth it only for a role that recurs, and buys less than it looks like (below) |
| A script, fixed ahead of time | dynamic workflows | `.claude/workflows/*.js` (see references/workflows.md) |

Two follow-ups settle what's left. **Do the workers need to talk to each other?** Subagents report only to whoever spawned them, and agent-view sessions report only to the user; teammates share a task list and message each other directly. **Do the tasks touch the same files?** Subagents and agent-view sessions can each take a worktree — teammates cannot, which is the next section.

### When a team is actually right, and what it costs

The antipattern above rules teams out as a *default* shape. This is the other half, and without it that warning has no honest opposite. Teams fit work that is genuinely independent and gets better from workers challenging each other: multi-angle research or review, competing-hypothesis debugging, cross-layer feature work where each layer has one owner. They fit badly in the mirror image — sequential steps, same-file edits, many dependencies — where a single session or plain subagents do better for less.

Four costs, none of which an interview volunteers:

- **Experimental, off by default.** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` must be set in `settings.json` or the environment; without it Claude does not spawn or propose teammates at all. A harness whose plan assumes a team therefore does nothing at all for a user who hasn't set it — design the fallback in the same breath, the way a workflow-dependent harness has to.
- **Token cost scales linearly with teammate count** — each has its own context window.
- **No file isolation.** Teams do not put teammates in worktrees, so two teammates editing one file overwrite each other. The mitigation is partitioned ownership, and partitioning is a *design* act: a harness that recommends a team owes the user a rule for who owns which files, or it has recommended the overwrite.
- **Permissions start from the lead's and cannot be set per-teammate at spawn** — individual modes can be changed afterward. A teammate can never approve a prompt on anyone's behalf, and teammate prompts surface to the lead.

One trap on the pre-written-role idea: **a subagent definition's `skills:` and `mcpServers:` fields are not applied when that definition runs as a teammate.** A teammate loads skills and MCP servers from project and user settings like an ordinary session. So the file buys the body and the tool list, and not the preloads.

### Distribution decides part of this before the interview does

- **A plugin's subagents lose `hooks`, `mcpServers`, and `permissionMode`.** Those three fields are ignored when an agent loads from a plugin, for security reasons. An agent whose safety story rests on its own frontmatter hook has no safety story the moment it ships that way.
- **A workflow can be packaged.** A plugin ships one from a `workflows/` directory at its root, or wherever its manifest's `workflows` field points, and it runs namespaced as `/<plugin>:<name>`. Outside a plugin the load paths are `.claude/workflows/` (project, walked up to the repo root) and `~/.claude/workflows/`, and the project copy wins a name collision.

Only the first of those forces a distribution choice: a harness depending on the ignored fields travels as a repo `.claude/` tree rather than as a plugin. A workflow does not — it packages. Ask whether the harness must travel (SKILL.md's K11) before routing a role, so this is a design input rather than a discovery.

## The eligibility test: don't generate an agent by default

What justifies an agent is a concrete advantage the work cannot get inline. Name the advantage before the role, because the ones that pay recur — and the list is not closed, so an advantage nobody wrote down still counts if you can state it. The two that come up constantly:

- **Context isolation is actually valuable**: the work is read-heavy (research, code review, QA sweeps, log triage) and only the conclusion needs to survive back in the main thread, not the search trail that produced it.
- **The task genuinely needs a distinct tool restriction or a distinct system prompt** that the main conversation shouldn't carry by default (a read-only database analyst, a reviewer that must never Edit).

Two more show up less often and are just as real: a role that has to remember across sessions, which is what a subagent's own `memory` field buys, and work that has to run while the conversation does something else. What does *not* justify one is an advantage you could get with a sentence — if the work would go the same way inline, the right answer is no agent at all: do it in the main conversation, or write it as a skill that runs there.

Agent count is itself a cost: each addition is one more role the orchestrating Claude weighs when routing, one more `description` competing for the same attention, one more definition that can rot out of sync with the codebase. The known antipattern is a meta-harness that makes "Agent Teams, 4-5 agents" the default architecture for every project, a travel-planning harness getting the same five-agent shape as an incident postmortem. Generate a role only for a concrete, demonstrated need — an advantage of the kind above, shown in something the interview actually described: a recurring task whose output the main thread throws away, a tool restriction that is part of the point, a system prompt the main conversation shouldn't carry, a role that has to remember.

The question that separates isolation from inline work: would this task's exploration output (file contents, search results, log lines, diff context) be useless to the main conversation once a verdict is reached? Then isolate. Would the main conversation benefit from seeing the intermediate steps, because the user might redirect mid-task or the next step depends on the details? Then keep it inline; an agent adds a round-trip and a lossy summary. A security reviewer that reads a diff and fifty lines of context per finding and returns five sentences is the first; "rename this function and update its ten call sites" is the second.

## The body is a full replacement, not an addition

An agent's markdown body becomes its entire system prompt. Claude Code's default system prompt — the one that knows to be concise, to prefer editing over rewriting, to run tests before declaring done, all the baseline behavior you get in an ordinary session — is gone entirely when a custom agent runs. The subagent receives only what you write in the body, plus bare environment details (working directory and similar), plus whatever CLAUDE.md and skills content loads through the normal mechanisms. Nothing else carries over.

Write generated agent bodies as if briefing someone who has never used Claude Code and has no idea what "the default way Claude behaves" even means. If the agent's job requires being concise, say so. If it needs to run a verification step before finishing, spell that out — don't assume "run tests before declaring done" survives from some ambient default, because for this agent there is no ambient default.

## Gotcha: Explore and Plan don't load CLAUDE.md or git status at all

The two most commonly auto-invoked built-in subagents — Explore (fast read-only search) and Plan (research during plan mode) — skip the CLAUDE.md hierarchy and the parent session's git status entirely, by design, to keep exploration fast and cheap. This is not configurable per-agent; there's no frontmatter field that changes it. Every other built-in and every custom subagent you generate *does* load both. So if a harness rule genuinely needs to reach a delegated task — "ignore everything under `vendor/`," "never touch files in `legacy/`" — and that delegation happens to go through Explore or Plan, the rule in your generated CLAUDE.md simply never arrives. The main conversation sees Explore's or Plan's results with full CLAUDE.md context of its own, so most rules don't need to reach the subagent itself; the gap only matters for a rule the *subagent's own behavior* must obey while it's running, not a rule about how to interpret what it finds.

The principle that decides the fix: the rule has to be in the subagent's startup context before its first action, and the surface you put it on determines how durably and how widely it holds. Anything that reaches that context qualifies; these three are the ones a harness can ship, weakest and most local first:

1. **Restate the rule directly in the delegation prompt text** — an instruction in the main harness surface telling Claude "when delegating searches to Explore, always tell it to skip `vendor/`" bakes the restatement into the ask itself. Cheapest fix, no new files, but only as durable as the phrasing of each delegation — easy to forget on an ad hoc request.
2. **Replace the built-in with a custom agent of the same name.** A project or user-scoped agent file named `Explore` overrides the built-in of the same name, and a custom agent — unlike the true built-in — does load CLAUDE.md and git status like any other custom subagent, and its body can additionally restate the critical rule outright. Use this when the rule needs to hold on *every* Explore-shaped delegation in the project, not just ones the main conversation remembers to caveat.
3. **Inject it via a `SubagentStart` hook's `additionalContext`.** A project-level hook matched on the agent type name fires when the subagent begins and can add context to its startup state programmatically, which reaches even the true built-ins (since the hook operates at the session level, not inside the agent definition). Use this when the rule is closer to "operational fact the subagent should know" than "constraint on the main conversation's phrasing," or when you want it enforced by configuration rather than by remembering to phrase things right in the moment.

So the choice follows from how wide and how durable the rule has to be: per-ask phrasing for a one-off, an agent file when every delegation of that shape must obey it, a hook when the rule should also reach agent types you didn't enumerate — including the true built-ins, which no agent file can reach.

## Gotcha: agent-scoped hooks and the `Stop`→`SubagentStop` conversion

Hooks declared inside an agent's own frontmatter (as opposed to `settings.json`) are scoped to that agent's lifetime — they run only while the agent is active and are cleaned up the moment it finishes, which makes them the right place for validation that's specific to one agent's job (a `PreToolUse` hook on `Bash` that blocks anything but `SELECT` for a read-only database agent, for instance) rather than a project-wide concern. A naming gotcha inside this mechanism: a `Stop` hook declared in an agent's frontmatter is automatically treated as `SubagentStop` at runtime. Write `Stop` in the agent file; Claude Code fires it when *that agent* stops, not when the main session stops — don't confuse this with a project-level `SubagentStop` hook in `settings.json`, which is the same semantic reached a different way (matched by agent-type name from the session level instead of declared inline). One field is skill-only and silently does nothing here: `once: true` (run once per session, then remove itself) is honored on a hook declared in a *skill's* frontmatter, but has no effect on an agent-frontmatter hook — don't generate an agent hook expecting `once` semantics, since nothing will tell you it was ignored.

**Frontmatter hooks on a project agent are gated on workspace trust** (v2.1.218+). Until the user accepts the trust dialog for the folder the agent file came from, the agent still runs but its hooks are skipped, and the only trace is an entry in the debug log. So an agent whose safety story rests on its own `PreToolUse` hook — the read-only-database example above is exactly this shape — has no safety story at all on an untrusted fresh clone, and nothing in the session says so. Agents in `~/.claude/agents/` are exempt because the user wrote them; a directory added with `--add-dir` from outside the trusted repo must be trusted separately rather than inheriting the workspace's grant. When you generate an agent carrying frontmatter hooks, record the trust dependency in the spec's Design rationale, and don't let the hook be the only thing standing between the agent and something irreversible — pair it with a `permissions.deny` rule, which needs no trust to bite.

## Gotcha: identity is `name`, not the filename, and duplicates fail silently

An agent's identifier — what Claude matches on for delegation, `@`-mention, and `Agent(name)` permission rules — is its frontmatter `name`, never the filename; `reviewer.md` with `name: code-reviewer` resolves by the frontmatter value alone. So keep `name` unique across the whole tree, not just per directory: two files in one `.claude/agents/` tree with the same `name` leave only one loaded, and which one is filesystem read order rather than a documented precedence — there is no rule you can reason from, and a human skimming filenames sees two agents. (Across *nested* project directories it is documented: the definition closest to the working directory wins.)

## Gotcha: AskUserQuestion does not exist inside a subagent

`AskUserQuestion` is stripped from every subagent before `tools:` is even consulted — it renders in the main conversation's UI, which an isolated agent has no access to. What an agent loses is *interactive* input mid-task, not the ability to raise a question: it can end its turn returning the question, and the main conversation answers and delegates again. So design the boundary rather than the agent's manners — resolve the ambiguity before delegating, or make "here is what I could not decide and why" a legitimate result of the role. A role written as "asks clarifying questions before proceeding" is the one shape that cannot work: it plans to block mid-task on an answer that can only arrive by starting the task over.

## Frontmatter fields in practice

Only `name` and `description` are required. The rest is the full schema; this table covers only the fields that require a judgment call when you're generating an agent, not an exhaustive dump of every field that exists.

| Field | Judgment call |
|---|---|
| `tools` | Omit to inherit everything (simplest, right default for a general-capability agent). List explicitly as an allowlist when the whole point of the agent is a restriction — e.g. `Read, Grep, Glob, Bash` with no `Edit`/`Write` for a review-only role. Prefer this over `disallowedTools` when the safe set is small and enumerable; prefer `disallowedTools` when you want "everything except X" (e.g. inherit everything but deny `Write, Edit`) and the exception list is shorter than the inclusion list. An allowlist does not imply `Skill`: omitting it from the list is the documented way to stop a subagent invoking skills entirely, and nothing announces the loss at runtime. So a restricted agent that still needs to reach a project skill has to name `Skill` explicitly alongside its file tools. |
| `model` | Default to unset or `inherit` — the agent then runs on whatever model the parent conversation is using. Pin only with a stated reason, written next to the pin: high-volume+low-complexity toward a cheaper tier (`haiku` for a per-file sweep that is pattern-matching, not judgment), rare+high-stakes toward a stronger one (final security sign-off). A blanket `opus` is paid on every invocation and buys nothing on the tasks that didn't need it. |
| `skills:` | Injects each listed skill's **complete body** at startup — not its description, the way normal discovery works — so a 300-line skill listed here is 300 lines carried into every invocation whether the task needs it or not. Only list one the agent needs in full on essentially every run; otherwise leave it out and let it discover the skill on demand through the Skill tool, which pays only when used. |
| `permissionMode` | Leave unset (inherits the parent's mode) unless the agent's whole purpose is a stricter posture — e.g. a read-only analyst that should never even be asked to accept an edit prompt. The parent's `bypassPermissions`/`acceptEdits` always wins over whatever you set here; this field can tighten a `default`-mode parent, not loosen a locked-down one. Under `auto` mode it is **ignored entirely** — every subagent action goes through the classifier with the parent's rules — so an agent whose safety story rests on this field has no safety story in a session that entered auto mode. |
| `hooks` | Only for validation specific to this one agent's job (see the `PreToolUse` read-only-database example above). Scoped to the agent's lifetime; remember `Stop` becomes `SubagentStop`. Don't use this for project-wide policy — that belongs in `settings.json`. |
| `isolation: worktree` | Set when the agent's file edits should land in a separate git worktree rather than the parent checkout — useful for an agent you want to experiment freely without risking the main working tree, at the cost of needing to merge or discard the worktree afterward. |
| `memory` | **Read the trap before setting this.** `memory: user\|project\|local` gives the agent its own persistent notes across invocations. Enabling it **automatically enables `Read`, `Write`, and `Edit`** — so on a read-only agent whose entire point is a restricted `tools:` allowlist, turning on memory can hand back the write access the allowlist was there to remove. The docs don't state which wins when the two conflict, so don't rely on either outcome: if an agent must not write, leave `memory` unset. `project` scope (the documented default recommendation) also creates a **version-controlled** `.claude/agent-memory/<name>/`, which means the agent's notes land in the team's diffs. And because auto memory can be switched off globally, an agent prompt that assumes its memory exists degrades silently — never generate one that depends on it. |

## A well-scoped example

This role passes the eligibility test cleanly: its job is entirely read-heavy (scanning a diff and the surrounding code for security issues), the main conversation has no use for the search trail that produces a finding, only the finding itself, and the tool restriction (no `Edit`, no `Write`) is itself part of the point — a reviewer that can quietly patch the very code it's supposed to be critiquing is a reviewer you can no longer trust. Read what the restriction actually buys, though, before you sell it as read-only: this role keeps `Bash` because it needs `git diff`, and `Bash` writes files (`sed -i`, `echo >> file`). Withholding `Edit` and `Write` narrows the write path; it does not close it.

```markdown
---
name: security-reviewer
description: Reviews a diff or file set for security issues — injection, auth bypass, secret exposure, unsafe deserialization. Use after implementing a change that touches authentication, database queries, or user input handling. Not for general code style or performance review — use a general review pass for those.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a security-focused code reviewer. You read code; you never modify it. If asked to fix something, hand the fix back as a recommendation, not an edit.

Start from `git diff`, or the named files if no diff is in scope. Check for the traps this project has actually been bitten by: unsanitized input reaching a query or a shell command, an auth check that was weakened rather than removed, and secrets reaching a log line. Style, naming, and performance belong to a different pass — ignore them.

State the exploit path for each finding, not just that something looks unsafe. If you find nothing, say so in one line.

Keep the final report short — it exists to hand a verdict back to a conversation that doesn't need to see the files you read to reach it.
```

Three things in that body are the transferable part, and none of them are about security:

- It opens by **restating the read-only boundary in prose**, which is doing real work and not ceremony: `tools:` withholds the tools named for writing, and the prose is what closes the `Bash` path this role has to keep. It also tells an agent that doesn't know why it lacks `Edit` not to waste a turn trying — the body replaces the system prompt entirely, so nothing else will.
- It names **what this project has actually been burned by** rather than a generic checklist, which is the same gotcha-over-general-competence test every other layer gets.
- It ends by **constraining the output**, because the entire reason to spend an agent here is that the main thread wants the verdict and not the search trail.

Swap the domain to performance or accessibility and those three still hold; the checklist in the middle is the only part you rewrite.
