# Contributing to Harness Creator

Thank you for helping make Harness Creator clearer, safer, and more useful to Claude Code users.

## What contributions are useful

Focused fixes, tests, documentation corrections, compatibility updates grounded in current Claude Code behavior, and small improvements with a clear user need are welcome. Open an issue before a large redesign, new dependency, or new generated component type.

Use the dedicated [bug](https://github.com/tjdwls101010/Harness-Creator/issues/new?template=bug.yml), [feature](https://github.com/tjdwls101010/Harness-Creator/issues/new?template=feature.yml), and [documentation](https://github.com/tjdwls101010/Harness-Creator/issues/new?template=documentation.yml) forms.

Security vulnerabilities must follow [SECURITY.md](SECURITY.md), not the public issue tracker.

## Repository shape

`.claude/skills/harness-creator/` is both this repository's project skill and the skill shipped by `.claude-plugin/plugin.json`. Edit it in place; do not create a second copy under a root-level `skills/` directory.

Everything beneath that directory ships to plugin users. Tests, contributor utilities, and project documentation belong outside it unless they are required at runtime by the skill.

## Development setup

Requirements:

- Git;
- Python 3.10 or later;
- Claude Code when changing plugin packaging or interactive behavior.

Clone the repository and create a topic branch:

```bash
git clone https://github.com/tjdwls101010/Harness-Creator.git
cd Harness-Creator
git switch -c your-change
```

The Python scripts use only the standard library; there is no dependency installation step.

For interactive skill development, uninstall other Harness Creator copies and create one symlink:

```bash
ln -s "$(pwd)/.claude/skills/harness-creator" ~/.claude/skills/harness-creator
```

Do not keep the symlink active while the plugin or skills CLI installation is active.

## Required checks

Run the unit suite:

```bash
python3 -m unittest discover -s tests -q
```

Validate this repository's harness:

```bash
python3 .claude/skills/harness-creator/scripts/validate_harness.py --path .
```

Validate plugin packaging when the Claude CLI is available:

```bash
claude plugin validate .
```

Check whitespace errors:

```bash
git diff --check
```

CI runs the unit suite and harness validator on Python 3.10 and 3.14. Pull requests also run internal-link validation. External links are checked weekly and manually so a third-party outage does not block an unrelated pull request.

If you change a Python script, add or update a matching test under `tests/` and the smallest fixture needed under `tests/fixtures/`.

## Documentation conventions

Canonical user documentation lives in `docs/wiki/` and follows the [Diátaxis](https://diataxis.fr/) categories: tutorials, how-to guides, reference, and explanation.

- Add every canonical page to `docs/wiki/README.md` and `_Sidebar.md`.
- Use relative links for repository files and images.
- Keep the README as the front door; put depth in the wiki.
- Write English public documentation in plain language for Claude Code users, not only harness experts.
- Distinguish structural validation from optional behavioral E2E evidence.
- Cite current primary sources for Claude Code mechanics.
- Do not copy local research transcripts or `.tmp/` material into tracked files.
- Avoid hard line wraps inside paragraphs; let Markdown renderers wrap prose.

The flat wiki compatibility files remain pointers through v1.0. Update their canonical target when moving a page, but do not create a second source of truth in them.

## Code and content style

- Keep Python 3.10 compatible and standard-library only.
- Prefer parameterized command-line tools over one-off scripts.
- Preserve existing user changes and keep the diff scoped.
- Explain consequences in validation errors when the source mechanics support them.
- Never invent a Claude Code behavior. Verify current mechanics against official documentation.
- Put deterministic guarantees in executable controls, not unsupported prose claims.

## Pull requests

Keep commits focused and write a pull-request description that explains the user impact, why the change belongs in this layer, and which checks passed. Include screenshots only when a rendered visual changed.

Review the generated diff before submitting. Do not include caches, local transcripts, credentials, `.DS_Store`, or temporary E2E artifacts.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Support expectations

Review and maintenance are best effort. The project does not promise a review, merge, response, or release SLA. See [SUPPORT.md](SUPPORT.md) for routing.
