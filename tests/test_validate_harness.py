#!/usr/bin/env python3
"""Self-test for validate_harness.py against tests/fixtures/{good,bad}-harness.

    python3 tests/test_validate_harness.py

stdlib unittest only, no pytest (per docs/plan/04-scripts-and-validation.md).
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_harness as vh  # noqa: E402


class GoodHarnessTests(unittest.TestCase):
    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "good-harness"
        self.findings, self.exit_code = vh.run(self.root, strict=False)

    def test_no_errors_or_warnings(self):
        self.assertEqual(self.findings, [])

    def test_exit_code_is_ok(self):
        self.assertEqual(self.exit_code, vh.hc.EXIT_OK)

    def test_strict_mode_still_passes(self):
        _, exit_code = vh.run(self.root, strict=True)
        self.assertEqual(exit_code, vh.hc.EXIT_OK)


class BadHarnessTests(unittest.TestCase):
    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "bad-harness"
        self.findings, self.exit_code = vh.run(self.root, strict=False)
        self.by_location = {}
        for level, location, message in self.findings:
            self.by_location.setdefault(location, []).append((level, message))

    def _assert_error_contains(self, location_substr, message_substr):
        for location, entries in self.by_location.items():
            if location_substr in location:
                for level, message in entries:
                    if level == "E" and message_substr in message:
                        return
        self.fail(f"expected an error containing {message_substr!r} at a location containing {location_substr!r}")

    def _assert_warning_contains(self, location_substr, message_substr):
        for location, entries in self.by_location.items():
            if location_substr in location:
                for level, message in entries:
                    if level == "W" and message_substr in message:
                        return
        self.fail(f"expected a warning containing {message_substr!r} at a location containing {location_substr!r}")

    def test_exit_code_is_lint_failed(self):
        self.assertEqual(self.exit_code, vh.hc.EXIT_LINT_FAILED)

    def test_missing_hook_script_is_error(self):
        self._assert_error_contains("PreToolUse", "does not exist")

    def test_non_matcher_event_with_matcher_is_error(self):
        self._assert_error_contains("UserPromptSubmit", "does not support a 'matcher'")

    def test_unknown_hook_event_is_error(self):
        self._assert_error_contains("NotARealEvent", "unknown hook event")

    def test_non_executable_hook_script_is_error(self):
        self._assert_error_contains("PostToolUse", "not executable")

    def test_unknown_permission_tool_is_error(self):
        self._assert_error_contains("permissions.allow", "NotARealTool")

    def test_broken_skill_frontmatter_is_error(self):
        self._assert_error_contains("broken-skill", "frontmatter did not parse")

    def test_dead_reference_link_is_error(self):
        self._assert_error_contains("dead-link-skill", "references/nonexistent.md")

    def test_dead_script_link_is_error(self):
        self._assert_error_contains("dead-link-skill", "scripts/nonexistent.py")

    def test_missing_skill_md_is_error(self):
        self._assert_error_contains("empty-skill-dir", "no SKILL.md")

    def test_agent_unknown_tool_is_error(self):
        self._assert_error_contains("reviewer-a.md", "unknown tool")

    def test_duplicate_agent_name_is_error(self):
        self._assert_error_contains("reviewer-b.md", "duplicate agent name")

    def test_agent_missing_description_is_error(self):
        self._assert_error_contains("reviewer-b.md", "missing required 'description'")

    def test_workflow_missing_meta_is_error(self):
        self._assert_error_contains("broken-workflow.js", "export const meta")

    def test_workflow_date_now_is_error(self):
        self._assert_error_contains("broken-workflow.js", "Date.now()")

    def test_bad_glob_syntax_is_error(self):
        self._assert_error_contains("bad-glob.md", "unmatched")

    def test_bad_at_import_is_error(self):
        self._assert_error_contains("CLAUDE.md", "nonexistent-doc.md")

    def test_unanchored_matcher_is_warning(self):
        self._assert_warning_contains("PreToolUse", "UNANCHORED regex")

    def test_if_on_non_tool_event_is_warning(self):
        self._assert_warning_contains("UserPromptSubmit", "no tool_input")

    def test_broad_allow_is_warning(self):
        self._assert_warning_contains("permissions.allow", "broad allow rule")

    def test_no_description_is_warning(self):
        self._assert_warning_contains("no-desc-skill", "no 'description'")

    def test_unknown_model_is_warning(self):
        self._assert_warning_contains("reviewer-a.md", "unrecognized 'model'")

    def test_rule_without_paths_is_warning(self):
        self._assert_warning_contains("no-paths.md", "no 'paths:'")

    def test_claude_md_too_long_is_warning(self):
        self._assert_warning_contains("CLAUDE.md", "over the 200-line guideline")

    def test_component_inventory_listing_is_warning(self):
        self._assert_warning_contains("CLAUDE.md", "component inventory")

    def test_missing_harness_spec_is_warning(self):
        self._assert_warning_contains("harness-spec.md", "missing")


class FrontmatterParserTests(unittest.TestCase):
    def test_simple_fields(self):
        fm = vh.hc.parse_frontmatter("---\nname: x\ndescription: y\n---\nbody\n")
        self.assertTrue(fm.ok)
        self.assertEqual(fm.data["name"], "x")
        self.assertEqual(fm.body.strip(), "body")

    def test_folded_scalar(self):
        fm = vh.hc.parse_frontmatter("---\ndescription: >\n  line one\n  line two\n---\n")
        self.assertTrue(fm.ok)
        self.assertEqual(fm.data["description"], "line one line two")

    def test_list_field(self):
        fm = vh.hc.parse_frontmatter("---\ntools:\n  - Read\n  - Bash\n---\n")
        self.assertTrue(fm.ok)
        self.assertEqual(fm.data["tools"], ["Read", "Bash"])

    def test_unclosed_fence_fails_conservatively(self):
        fm = vh.hc.parse_frontmatter("---\nname: x\n")
        self.assertFalse(fm.ok)

    def test_flow_style_rejected_conservatively(self):
        fm = vh.hc.parse_frontmatter("---\ntools: [Read, Bash]\n---\n")
        self.assertFalse(fm.ok)

    def test_no_fence_at_all(self):
        fm = vh.hc.parse_frontmatter("# just a heading\nno frontmatter here\n")
        self.assertFalse(fm.ok)


class MatcherHelperTests(unittest.TestCase):
    def test_exact_matchers(self):
        for m in ("Bash", "Edit|Write", "code-reviewer", "a,b,c"):
            self.assertTrue(vh.hc.is_exact_matcher(m), m)

    def test_regex_matchers(self):
        for m in ("Edit.*", "^Edit$", "mcp__server__.*"):
            self.assertFalse(vh.hc.is_exact_matcher(m), m)


if __name__ == "__main__":
    unittest.main(verbosity=2)
