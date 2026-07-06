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


if __name__ == "__main__":
    unittest.main(verbosity=2)
