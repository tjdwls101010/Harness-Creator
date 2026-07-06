#!/usr/bin/env python3
"""Self-test for test_hook.py against tests/fixtures/good-harness.

    python3 tests/test_test_hook.py
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import test_hook as th  # noqa: E402


class MatcherMatchingTests(unittest.TestCase):
    def test_exact_match(self):
        self.assertTrue(th.matches_matcher("Bash", "Bash"))
        self.assertFalse(th.matches_matcher("Bash", "Edit"))

    def test_pipe_list(self):
        self.assertTrue(th.matches_matcher("Edit|Write", "Write"))
        self.assertFalse(th.matches_matcher("Edit|Write", "Read"))

    def test_unanchored_regex_gotcha_reproduced(self):
        # This is the exact trap documented in references/hooks.md: an
        # unanchored "Edit.*" also matches "NotebookEdit".
        self.assertTrue(th.matches_matcher("Edit.*", "NotebookEdit"))

    def test_anchored_regex_does_not_overmatch(self):
        self.assertFalse(th.matches_matcher("^Edit$", "NotebookEdit"))
        self.assertTrue(th.matches_matcher("^Edit$", "Edit"))

    def test_no_matcher_matches_everything(self):
        self.assertTrue(th.matches_matcher(None, "AnyTool"))
        self.assertTrue(th.matches_matcher("", "AnyTool"))


class SampleInputTests(unittest.TestCase):
    def test_pretooluse_has_tool_name_and_input(self):
        data = th.build_sample_input("PreToolUse", "Bash", {})
        self.assertEqual(data["tool_name"], "Bash")
        self.assertIn("command", data["tool_input"])

    def test_stop_has_stop_hook_active(self):
        data = th.build_sample_input("Stop", None, {})
        self.assertIn("stop_hook_active", data)
        self.assertFalse(data["stop_hook_active"])

    def test_unknown_event_still_gets_hook_event_name(self):
        data = th.build_sample_input("SomeFutureEvent", None, {})
        self.assertEqual(data["hook_event_name"], "SomeFutureEvent")

    def test_overrides_apply(self):
        data = th.build_sample_input("PreToolUse", "Bash", {"command": "custom"})
        self.assertEqual(data["command"], "custom")


class InterpretTests(unittest.TestCase):
    def test_exit_2_blocks(self):
        lines = th.interpret("PreToolUse", 2, "", "denied: protected path")
        self.assertTrue(any("BLOCKS" in l for l in lines))
        self.assertTrue(any("protected path" in l for l in lines))

    def test_exit_1_does_not_block(self):
        lines = th.interpret("PreToolUse", 1, "", "some error")
        self.assertTrue(any("does NOT block" in l for l in lines))

    def test_exit_0_no_output_is_noop(self):
        lines = th.interpret("PostToolUse", 0, "", "")
        self.assertTrue(any("no side effect" in l for l in lines))

    def test_exit_0_json_decision_block(self):
        lines = th.interpret("UserPromptSubmit", 0, '{"decision": "block", "reason": "nope"}', "")
        self.assertTrue(any("decision:block" in l for l in lines))

    def test_exit_2_with_json_notes_discard(self):
        lines = th.interpret("PreToolUse", 2, '{"permissionDecision": "deny"}', "blocked")
        self.assertTrue(any("DISCARDED" in l for l in lines))

    def test_worktree_create_any_nonzero_fails(self):
        lines = th.interpret("WorktreeCreate", 1, "", "could not create")
        self.assertTrue(any("ANY nonzero exit" in l for l in lines))

    def test_worktree_create_success_path(self):
        lines = th.interpret("WorktreeCreate", 0, "/tmp/worktree-x", "")
        self.assertTrue(any("worktree creation proceeds" in l for l in lines))


class EndToEndGoodHarnessTests(unittest.TestCase):
    def setUp(self):
        self.settings_path = REPO_ROOT / "tests" / "fixtures" / "good-harness" / ".claude" / "settings.json"
        self.data, err = th.hc.load_json_lenient(self.settings_path)
        self.assertIsNone(err)

    def test_protect_files_blocks_env_edit(self):
        matched = th.find_matching_groups(self.data, "PreToolUse", "Edit")
        self.assertEqual(len(matched), 1)
        gi, group = matched[0]
        hook_entry = group["hooks"][0]
        input_data = th.build_sample_input("PreToolUse", "Edit", {"tool_input": {"file_path": "/repo/.env"}})
        exit_code, stdout, stderr, err = th.run_hook_command(hook_entry, input_data, self.settings_path.resolve().parent.parent)
        self.assertIsNone(err)
        self.assertEqual(exit_code, 2)

    def test_protect_files_allows_normal_edit(self):
        matched = th.find_matching_groups(self.data, "PreToolUse", "Edit")
        gi, group = matched[0]
        hook_entry = group["hooks"][0]
        input_data = th.build_sample_input("PreToolUse", "Edit", {"tool_input": {"file_path": "/repo/src/app.ts"}})
        exit_code, stdout, stderr, err = th.run_hook_command(hook_entry, input_data, self.settings_path.resolve().parent.parent)
        self.assertIsNone(err)
        self.assertEqual(exit_code, 0)

    def test_matrix_shows_no_matcher_gotcha_for_good_harness(self):
        rows = th.cmd_matrix(self.data)
        # good-harness's PreToolUse matcher is "Edit|Write" (exact), so it
        # must NOT also match NotebookEdit the way bad-harness's "Edit.*" does.
        notebook_rows = [r for r in rows if r[0] == "PreToolUse" and r[1] == "NotebookEdit"]
        self.assertEqual(notebook_rows, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
