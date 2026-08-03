#!/usr/bin/env python3
"""Regression tests for the shipped skill surface itself (SKILL.md + references/).

    python3 tests/test_skill_surface.py

These cover the WS1 "truth repair" bugs. Most were classified as prose-only
in the plan, but each one has a mechanical shadow -- an ordering, a count, a
grep that must stay at zero -- and a check that runs on every commit is worth
more than a review note that runs once. stdlib unittest only, no pytest.
"""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator"
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_harness as vh  # noqa: E402

SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES = sorted((SKILL_DIR / "references").glob("*.md"))


def read(path):
    return path.read_text(encoding="utf-8")


class WrapUpOrderTests(unittest.TestCase):
    """B2. The Wrap-up ran validate_harness.py first, then edited the spec and
    CLAUDE.md -- so the state that actually got committed was never validated,
    and a line claimed the earlier run would 'independently catch' drift that
    did not exist yet when it ran."""

    def setUp(self):
        self.lines = read(SKILL_MD).splitlines()
        start = next(i for i, l in enumerate(self.lines) if "Wrap-up" in l)
        self.block = self.lines[start:start + 12]

    def _index_of(self, needle):
        for i, line in enumerate(self.block):
            if needle in line:
                return i
        self.fail(f"{needle!r} not found in the Wrap-up block")

    def test_validation_runs_after_the_edits_it_checks(self):
        change_history = self._index_of("Change history")
        pointers = self._index_of("update CLAUDE.md's pointers")
        validate = self._index_of("validate_harness.py")
        self.assertLess(change_history, validate)
        self.assertLess(pointers, validate)

    def test_commit_is_proposed_last(self):
        self.assertLess(self._index_of("validate_harness.py"), self._index_of("propose a commit"))

    def test_false_independence_claim_is_gone(self):
        self.assertNotIn("will independently catch", read(SKILL_MD))


class TimeoutFactsTests(unittest.TestCase):
    """B5. hooks-events.md called both MessageDisplay (10s) and SessionEnd
    (1.5s) 'the shortest of any event', hooks.md said 'two events' and listed
    two of three, and SessionEnd's 1.5s was labelled a per-hook default when
    the live docs call it a budget shared across all SessionEnd hooks."""

    def setUp(self):
        self.hooks = read(SKILL_DIR / "references" / "hooks.md")
        self.events = read(SKILL_DIR / "references" / "hooks-events.md")

    def test_only_one_shortest_of_any_event_claim_at_most(self):
        hits = sum(read(p).count("shortest of any event") for p in REFERENCES)
        self.assertLessEqual(hits, 1, "two events cannot both be the shortest")

    def test_session_end_is_described_as_a_shared_budget(self):
        for text, name in ((self.hooks, "hooks.md"), (self.events, "hooks-events.md")):
            self.assertRegex(text, r"budget shared across all|shared across all `SessionEnd`", name)

    def test_no_stale_two_events_count(self):
        self.assertNotIn("Two events break that pattern", self.hooks)

    def test_all_three_departing_events_are_named_together(self):
        section = self.hooks.split("Default timeouts are wildly uneven")[1][:1500]
        for event in ("UserPromptSubmit", "MessageDisplay", "SessionEnd"):
            self.assertIn(event, section, event)


class DanglingPointerTests(unittest.TestCase):
    """B8. Three pointers named a destination that did not exist: a 'see Hard
    lines' that said nothing about protected paths, a 'SKILL.md §3' when
    SKILL.md has no numbered sections, and a 'timeout column' in a table with
    no timeout column."""

    def test_no_dangling_pointers(self):
        pattern = re.compile(r"see Hard lines|SKILL\.md §|timeout column")
        for path in [SKILL_MD] + REFERENCES:
            self.assertIsNone(pattern.search(read(path)), path.name)

    def test_skill_md_still_has_no_numbered_sections(self):
        # The reason `SKILL.md §3` could never resolve. If numbered sections
        # are ever introduced, this test should be deleted, not worked around.
        self.assertNotIn("§", read(SKILL_MD))


class FenceBalanceTests(unittest.TestCase):
    """B10. agents.md opened a ```markdown fence and never closed it, so
    renderers and parsers swallowed the rest of the file as a code block."""

    def test_every_file_has_balanced_fences(self):
        for path in [SKILL_MD] + REFERENCES:
            count = len(re.findall(r"^```", read(path), re.MULTILINE))
            self.assertEqual(count % 2, 0, f"{path.name} has {count} fences")


class DeadLinkCoverageTests(unittest.TestCase):
    """B7. Hard line 1 claimed validate_harness.py checked pointers
    mechanically, but the check matched only backtick-wrapped forms and ran
    only against SKILL.md -- one pointer out of dozens."""

    def _scan(self, text):
        found = []
        for m in vh._SKILL_POINTER_RE.finditer(text):
            if m.group("prefix") in ("./", "/"):
                continue
            name = m.group("name")
            if "*" in name or not name.strip("."):
                continue
            found.append(f"{m.group('subdir')}/{name}")
        return found

    def test_pointers_in_both_skill_md_and_references_are_scanned(self):
        self.assertGreater(len(self._scan(read(SKILL_MD))), 10)
        ref_hits = sum(len(self._scan(read(p))) for p in REFERENCES)
        self.assertGreater(ref_hits, 0, "reference-to-reference pointers must be scanned")

    def test_bare_prose_and_markdown_link_forms_are_caught(self):
        for form in (
            "see references/hooks.md for detail",
            "[hooks](references/hooks.md)",
            "`references/hooks.md`",
            'python "${CLAUDE_SKILL_DIR}/scripts/run_e2e.py"',
        ):
            self.assertTrue(self._scan(form), form)

    def test_target_project_paths_and_globs_are_not_pointers(self):
        for form in (
            'command: "./scripts/security-check.sh"',
            "each `references/template-*.md` holds",
            "use `${CLAUDE_SKILL_DIR}/scripts/...` never a bare path",
        ):
            self.assertEqual(self._scan(form), [], form)

    def test_every_pointer_in_the_shipped_skill_resolves(self):
        findings = []
        for path in [SKILL_MD] + REFERENCES:
            vh._check_dead_links(SKILL_DIR, path.name, read(path), findings)
        self.assertEqual([f for f in findings if f[0] == "E"], [])


class NoExternalToolNamesTests(unittest.TestCase):
    """D14. The shipped skill is a self-contained plugin and must not name
    Claude Code UI commands."""

    def test_no_ui_command_names(self):
        pattern = re.compile(r"doctor|checkup", re.IGNORECASE)
        for path in [SKILL_MD] + REFERENCES:
            self.assertIsNone(pattern.search(read(path)), path.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
