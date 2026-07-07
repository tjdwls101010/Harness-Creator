# Architecture & Internals

How this repo is put together, for contributors and the curious. This page covers the repo layout, the one skill directory that plays two roles at once, how the plugin and marketplace manifests make that work, the two install paths and why you don't run both, where the design rationale lives, and the progressive-disclosure and test structure.

## Repo layout

| Path | What it is |
| --- | --- |
| `.claude-plugin/plugin.json` | The plugin manifest (name, version, description, author, `skills` path). |
| `.claude-plugin/marketplace.json` | Makes this repo its own single-plugin marketplace. |
| `.claude/skills/harness-creator/` | The skill itself — `SKILL.md`, `references/`, `scripts/`. Dual-purpose (see below). |
| `CLAUDE.md` | This repo's own development harness, not a generated artifact. |
| `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE` | Standard open-source top matter. |
| `docs/plan/` | The design-rationale record — kept after implementation as the source of truth for design decisions and per-gotcha research. |
| `docs/wiki/` | This handbook (the page you're reading). |
| `tests/` | Standard-library `unittest` cases plus `fixtures/` harnesses. |
| `.tmp/` | Gitignored local reference snapshots the plan was researched against; not part of this repo's history. |

## The dual-purpose skill directory

`.claude/skills/harness-creator/` is simultaneously two things:

1. A **project skill** for this repo, so the repo dogfoods its own output shape — the skill lives in exactly the `.claude/skills/<name>/` location it teaches other projects to use.
2. The **plugin's skill component**, the thing that ships when someone installs the plugin.

There is no second copy. The skill is edited in place, and the same files serve both roles. This is deliberate: the tool that generates harnesses is itself packaged as a harness component, so any structural mistake in the shape it produces would show up in its own repo first.

## Packaging: how one directory serves both roles

Two small manifests make the dual role work.

`marketplace.json` declares this repo as a marketplace with a single plugin whose source is the repo root:

```json
{
  "name": "harness-creator",
  "owner": { "name": "seongjin" },
  "plugins": [ { "name": "harness-creator", "source": "./" } ]
}
```

`plugin.json` names the plugin, pins a semver `version` (`0.1.0`), and points the `skills` field at the in-repo skills directory:

```json
{
  "name": "harness-creator",
  "version": "0.1.0",
  "skills": "./.claude/skills"
}
```

The load-bearing mechanic is the `skills` field. A plugin's components are scanned by default from a `skills/` directory at the plugin root, and the `skills` path field **adds to** that scan rather than replacing it. Pointing it at `./.claude/skills` lets the very same directory be both the repo's project skill and the plugin's shipped component — no duplication, no root-level `skills/` folder. Pinning an explicit `version` matters too: without it, the plugin is versioned by git SHA and appears to update on every commit.

Note that the general plugin constraints (plugin-shipped agents ignore their hooks/mcpServers/permissionMode, workflows can't be distributed as plugin components) don't bite here. harness-creator ships one skill plus its internal scripts; the agents and workflows it deals with are artifacts it *generates into a target project*, not components this plugin carries.

## Two install paths, and why not both at once

There are two ways to get the skill into a Claude Code session, and they are for different jobs.

- **Symlink — the development loop.** `ln -s <repo>/.claude/skills/harness-creator ~/.claude/skills/harness-creator`. Edits to `SKILL.md` and `references/` are reflected immediately in a fresh session, with no cache to refresh. It triggers under the bare name `/harness-creator`. This is the day-to-day loop.
- **Plugin — the distribution path.** Install via the local (or GitHub) marketplace. The skill is copied into `~/.claude/plugins/cache/`, so changes require a `claude plugin update`. It triggers under the namespaced name `/harness-creator:harness-creator`.

Don't activate both at once. A symlink that resolves to an already-registered target is de-duplicated, but the plugin skill lives in its own namespace and is not a de-dup candidate — so running both registers the same skill twice under two different names (`harness-creator` and `harness-creator:harness-creator`). Keep the symlink for daily work, and only add the marketplace and install the plugin when you're specifically smoke-testing the distribution path; uninstall it afterward.

One contributor-facing caution when smoke-testing: installing from a **local path** marketplace copies the filesystem as-is (including gitignored directories like `.tmp/`) into the plugin cache, and `uninstall` + `marketplace remove` can leave the cache folder behind — clear it by hand. Installing from the GitHub source is clean, because a clone only carries tracked content.

## Where design rationale lives

Design rationale is pointed to, not reproduced into the loaded skill. The decision log and the primary-source research behind each Claude Code gotcha live in [`docs/plan/`](../plan/) and stay there as the binding record after implementation. The markdown the skill loads into context (`SKILL.md`, `references/`) is written for the Claude that *uses* the skill — it carries the principles and the mechanics, not the project history or the "why we chose this" narration. If you change something structural, change the plan doc and say why.

## Progressive disclosure: small orchestrator, references on demand

The skill body is split by *when each piece is needed*, so a session pays context only for what it actually does.

| Piece | Loaded | Role |
| --- | --- | --- |
| `SKILL.md` | Every invocation | The orchestrator — philosophy, the layer-routing framework, the operating loop, script usage summaries. Deliberately small (~110 lines). |
| `references/*.md` | On demand, per component | Eight authoring guides (CLAUDE.md & rules, skills, hooks, hook events, agents, workflows, interview, e2e testing) — together far larger than `SKILL.md` (~1,200 lines). A session that only writes a `CLAUDE.md` never loads the hook-events table. |
| `scripts/*.py` | Never loaded into context | Invoked as subprocesses (`${CLAUDE_SKILL_DIR}/scripts/<name>.py`), so their size costs nothing at read time. |

The split follows the branch "which component am I generating right now," which is exactly the point at which the matching reference becomes relevant. What is deliberately *not* split: the interview protocol stays in one `interview.md` because all its stages run in one flow, and per-component templates stay inline in each guide rather than in a separate `templates/` directory that would only add routing cost.

The four script CLIs share one non-CLI helper module, `scripts/harness_common.py` (a conservative frontmatter parser, the canonical tool list, the 30-event hook table, and a matcher-exactness helper). Keeping that shared logic in one place is why the scripts stay consistent about, say, what counts as an exact matcher. See [Scripts.md](Scripts.md) for the CLIs themselves.

## Test setup

Tests are plain `unittest` from the Python standard library — one `tests/test_*.py` per script CLI, run directly (`for f in tests/test_*.py; do python3 "$f"; done`). No third-party dependencies; the scripts target Python 3.10+ standard library only, and the tests keep it that way.

The fixtures live at the **repo root** (`tests/fixtures/`), not inside the skill directory. This is the same dogfooding principle in reverse: anything under `.claude/skills/harness-creator/` ships to plugin users, so dev-only files stay outside it. There are two fixture harnesses — `good-harness/` (a clean `.claude/` the linter should pass) and `bad-harness/` (a deliberately broken one exercising each check: bad globs, a non-executable hook, dead skill links, a missing skill description, a broken workflow, and more). Together they pin the linter's behavior on both the clean and the failing case.

If you touch a script, add or update a case in the matching `tests/test_*.py` and, when needed, the fixtures. See [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) for the full pre-PR checklist and the house rules for writing.

## See also

- [Scripts.md](Scripts.md) — the four CLIs and the shared helper, in detail.
- [Generated-Components.md](Generated-Components.md) — the standard output shape this repo dogfoods.
- [Concepts.md](Concepts.md) — the mental model behind the whole tool.
