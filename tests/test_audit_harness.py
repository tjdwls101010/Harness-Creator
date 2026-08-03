#!/usr/bin/env python3
"""Self-test for audit_harness.py against tests/fixtures/{good,bad}-harness.

    python3 tests/test_audit_harness.py
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import audit_harness as ah  # noqa: E402


class GoodHarnessAuditTests(unittest.TestCase):
    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "good-harness"
        self.result = ah.run(self.root)

    def test_finds_all_component_types(self):
        inv = self.result["inventory"]
        self.assertIsNotNone(inv["claude_md"])
        self.assertEqual(len(inv["rules"]), 1)
        self.assertEqual(len(inv["skills"]), 1)
        self.assertEqual(len(inv["agents"]), 1)
        self.assertEqual(len(inv["workflows"]), 1)
        self.assertIn(".claude/settings.json", inv["settings"])

    def test_skill_path_is_directory_not_skill_md(self):
        skill = self.result["inventory"]["skills"][0]
        self.assertEqual(skill["path"], ".claude/skills/example-skill")
        self.assertEqual(skill["skill_md_path"], ".claude/skills/example-skill/SKILL.md")

    def test_no_spec_drift(self):
        self.assertTrue(self.result["spec_drift"]["spec_exists"])
        self.assertEqual(self.result["spec_drift"]["on_disk_not_in_spec"], [])

    def test_no_hygiene_problems(self):
        h = self.result["hygiene"]
        self.assertEqual(h["dead_link_count"], 0)
        self.assertEqual(h["duplicate_agent_name_count"], 0)
        self.assertEqual(h["non_executable_hook_count"], 0)
        self.assertEqual(h["total_lint_errors"], 0)

    def test_suggested_mode_is_not_new(self):
        self.assertNotIn("new --", self.result["suggested_mode"])


class BadHarnessAuditTests(unittest.TestCase):
    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "bad-harness"
        self.result = ah.run(self.root)

    def test_hygiene_reflects_real_problems(self):
        h = self.result["hygiene"]
        self.assertGreater(h["duplicate_agent_name_count"], 0)
        self.assertGreater(h["non_executable_hook_count"], 0)
        self.assertGreater(h["dead_link_count"], 0)
        self.assertGreater(h["total_lint_errors"], 0)

    def test_suggested_mode_is_improve_when_spec_missing(self):
        self.assertIn("improve", self.result["suggested_mode"])


class EmptyProjectAuditTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmpdir = tempfile.mkdtemp()
        self.root = Path(self.tmpdir)
        self.result = ah.run(self.root)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_suggests_new_mode(self):
        self.assertTrue(self.result["suggested_mode"].startswith("new"))

    def test_empty_inventory(self):
        inv = self.result["inventory"]
        self.assertIsNone(inv["claude_md"])
        self.assertEqual(inv["rules"], [])
        self.assertEqual(inv["skills"], [])


class SpecNotOnDiskDriftTests(unittest.TestCase):
    """B6. The audit only ever checked one direction of drift and its own
    comment declined the other, delegating it to 'a human (or the interviewing
    Claude)' -- but no instruction anywhere told the model to do that, so half
    of sync mode was performed by nobody."""

    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "spec-claims-missing-skill"
        self.drift = ah.check_spec_drift(self.root, ah.run(self.root)["inventory"])
        self.missing = {r["component"] for r in self.drift["in_spec_not_on_disk"]}

    def test_reports_generated_row_with_no_file(self):
        self.assertIn(".claude/skills/ghost-skill", self.missing)

    def test_reports_validated_row_with_no_file(self):
        self.assertIn(".claude/agents/ghost-agent.md", self.missing)

    def test_does_not_report_a_component_that_exists(self):
        self.assertNotIn(".claude/skills/real-skill", self.missing)

    def test_intent_statuses_are_not_drift(self):
        # `proposed` and `approved` assert intent, not an artifact. Reporting
        # them would make every mid-interview harness look broken.
        self.assertNotIn(".claude/skills/not-yet", self.missing)
        self.assertNotIn(".claude/hooks/maybe.sh", self.missing)

    def test_row_carries_its_id_and_status(self):
        by_component = {r["component"]: r for r in self.drift["in_spec_not_on_disk"]}
        self.assertEqual(by_component[".claude/skills/ghost-skill"]["id"], "B2")
        self.assertEqual(by_component[".claude/agents/ghost-agent.md"]["status"], "validated")

    def test_suggests_sync_mode(self):
        self.assertTrue(ah.run(self.root)["suggested_mode"].startswith("sync"))


class SpecDriftJsonContractTests(unittest.TestCase):
    """B11. `in_spec_not_on_disk` was returned in the no-spec branch but
    omitted when a spec existed, so a --json consumer keying on it broke in
    exactly the case the key was meant for."""

    def _drift(self, fixture):
        root = REPO_ROOT / "tests" / "fixtures" / fixture
        return ah.check_spec_drift(root, ah.run(root)["inventory"])

    def test_key_present_whether_or_not_a_spec_exists(self):
        for fixture in ("good-harness", "bad-harness", "spec-claims-missing-skill"):
            drift = self._drift(fixture)
            self.assertIn("in_spec_not_on_disk", drift, fixture)
            self.assertIn("on_disk_not_in_spec", drift, fixture)

    def test_both_directions_are_lists(self):
        drift = self._drift("good-harness")
        self.assertIsInstance(drift["in_spec_not_on_disk"], list)
        self.assertIsInstance(drift["on_disk_not_in_spec"], list)


class InventoryTableParsingTests(unittest.TestCase):
    def test_skips_header_and_separator_rows(self):
        spec = (
            "## Behavior inventory\n"
            "| id | behavior | layer | component | status |\n"
            "|----|----------|-------|-----------|--------|\n"
            "| B1 | thing | skill | `a/b/` | generated |\n"
        )
        rows = list(ah._iter_inventory_rows(spec))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "B1")

    def test_stops_at_the_next_heading(self):
        spec = (
            "## Behavior inventory\n"
            "| B1 | thing | skill | `a/` | generated |\n"
            "## Component specs\n"
            "| B2 | other | skill | `b/` | generated |\n"
        )
        rows = list(ah._iter_inventory_rows(spec))
        self.assertEqual([r[0] for r in rows], ["B1"])

    def test_no_inventory_section_yields_nothing(self):
        self.assertEqual(list(ah._iter_inventory_rows("# Spec\nno table here\n")), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
