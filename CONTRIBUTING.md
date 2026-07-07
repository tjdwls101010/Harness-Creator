# Contributing to harness-creator

Thanks for your interest. This project is small and has a strong point of view, so this guide is mostly about *how the repo is wired* — once you understand that, contributing is straightforward.

## The one thing to understand first

`.claude/skills/harness-creator/` is simultaneously two things:

1. A **project skill** for this repo (so the repo dogfoods its own output shape), and
2. The **plugin's skill component** (`.claude-plugin/plugin.json`'s `skills` field points at it).

Don't duplicate the skill anywhere else. Edit it in place.

## Development loop: use the symlink, not the plugin install

Day-to-day development is the symlink, not the plugin. Link the skill into your user skills directory once:

```bash
ln -s "$(pwd)/.claude/skills/harness-creator" ~/.claude/skills/harness-creator
```

Now edits to `SKILL.md` and `references/` are reflected immediately in a fresh Claude Code session — no plugin cache to refresh. Only install the plugin (via the local marketplace) when you're specifically smoke-testing the *distribution* path, and uninstall it afterward — running both at once double-registers the skill under two different names (`harness-creator` vs. `harness-creator:harness-creator`).

## Before you open a PR

- **Run the linter against the repo:** `python3 .claude/skills/harness-creator/scripts/validate_harness.py --path .` — it must report zero errors.
- **Run the tests:** `for f in tests/test_*.py; do python3 "$f"; done` — all should pass. The scripts are Python 3.10+ and use only the standard library; keep it that way (no third-party dependencies).
- **If you touched a script,** add or update a case in the matching `tests/test_*.py` and, if needed, the fixtures under `tests/fixtures/`. Fixtures live at the repo root, *not* inside the skill directory — anything under the skill ships to plugin users, so dev-only files stay outside it.

## House rules for writing (they are load-bearing, not style preferences)

These rules exist because this skill's entire value is dense, correct, decision-changing content — and because a future Claude has to read and edit these files.

- **No mid-sentence hard line wraps** in any markdown (SKILL.md, references, wiki, this file, generated output). Break lines only at sentence, list-item, or paragraph boundaries. Hard wraps break the Edit tool's string matching and pollute diffs; renderers soft-wrap anyway.
- **Verify every Claude Code mechanic against a primary source** before writing it into a reference file (the local docs snapshot, or the official Claude Code docs). A wrong gotcha is worse than no gotcha — the skill's credibility is its accuracy.
- **Write for the Claude that *uses* the skill, not for the developer building it.** Design rationale, project history, and "why the code is this way" belong in `docs/plan/` and in code comments — not in the markdown the skill loads into context. See the design-rationale record in [`docs/plan/`](docs/plan/).
- **Principle over rule.** Prefer explaining *why* a choice is good so the model can re-derive it, over a bare list of do/don'ts. Every threshold gets its justification and its exception in the same breath.

## Where design decisions live

`docs/plan/` is the binding record of the twelve design decisions (D1–D12) and the research behind each gotcha. If you want to change something structural — the layer-routing framework, the two-tier validation model, a decision in the log — update the relevant plan doc and explain why in your PR. The plan is a specification, not dogma, but changing it should be deliberate and documented.

## Reporting issues

Open a GitHub issue. For a bug in a generated harness, include the target project's language/build system and the relevant slice of the generated `.claude/` output. For a wrong or missing gotcha in a reference file, cite the Claude Code behavior you observed — that's the most valuable kind of report this project can get.
