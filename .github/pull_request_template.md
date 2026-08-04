## What changed

Describe the scoped change and the user or contributor impact.

## Why

Explain the need, the selected layer, and any relevant alternatives.

## Validation

- [ ] `python3 -m unittest discover -s tests -q`
- [ ] `python3 .claude/skills/harness-creator/scripts/validate_harness.py --path .`
- [ ] `claude plugin validate .` when plugin packaging changed
- [ ] `git diff --check`
- [ ] Documentation links and rendered assets reviewed when docs changed

## Risk and compatibility

Note behavior changes, migration needs, generated-file effects, or known boundaries. Write “None identified” when the change is documentation-only and no compatibility impact is expected.

## Checklist

- [ ] The diff contains no credentials, local transcripts, caches, or unrelated files.
- [ ] Tests or fixtures cover changed Python behavior.
- [ ] Canonical documentation and navigation are updated for user-facing changes.
- [ ] Structural validation is not described as behavioral proof.
- [ ] New Claude Code mechanics are supported by current primary sources.
