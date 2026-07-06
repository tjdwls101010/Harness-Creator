#!/usr/bin/env python3
"""Self-test for run_e2e.py's parsing/isolation/command-building logic.

Does NOT invoke a real `claude` process -- that part is documented as
unverified in this sandbox (see references/e2e-testing.md). This tests
everything that doesn't require a live authenticated session: stream-json
parsing against synthetic fixtures, --isolate's copy behavior, and CLI
argument construction.

    python3 tests/test_run_e2e.py
"""

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import run_e2e as re2  # noqa: E402


def event_lines(*events):
    return [json.dumps(e) for e in events]


class ParseStreamTests(unittest.TestCase):
    def test_extracts_skill_invocation(self):
        lines = event_lines(
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": "harness-creator"}},
            ]}},
            {"type": "result", "subtype": "success", "is_error": False, "num_turns": 1, "result": "done", "total_cost_usd": 0.01},
        )
        summary = re2.parse_stream(lines)
        self.assertEqual(summary["skill_invocations"], ["harness-creator"])
        self.assertEqual(len(summary["tool_calls"]), 1)
        self.assertIsNotNone(summary["final_result"])
        self.assertEqual(summary["final_result"]["result"], "done")

    def test_extracts_multiple_tool_calls(self):
        lines = event_lines(
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Read", "input": {"file_path": "a.py"}},
                {"type": "text", "text": "looking at the file"},
            ]}},
            {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Edit", "input": {"file_path": "a.py"}},
            ]}},
        )
        summary = re2.parse_stream(lines)
        self.assertEqual([c["name"] for c in summary["tool_calls"]], ["Read", "Edit"])

    def test_hook_evidence_heuristic(self):
        lines = event_lines(
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "content": "Error: blocked by hook -- protected path"},
            ]}},
        )
        summary = re2.parse_stream(lines)
        self.assertEqual(len(summary["hook_evidence"]), 1)

    def test_no_false_hook_evidence_on_ordinary_result(self):
        lines = event_lines(
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "content": "file contents here, nothing special"},
            ]}},
        )
        summary = re2.parse_stream(lines)
        self.assertEqual(summary["hook_evidence"], [])

    def test_malformed_json_lines_are_skipped_not_fatal(self):
        lines = ["not json at all", '{"type": "result", "result": "ok"}']
        summary = re2.parse_stream(lines)
        self.assertIsNotNone(summary["final_result"])

    def test_empty_input(self):
        summary = re2.parse_stream([])
        self.assertEqual(summary["tool_calls"], [])
        self.assertIsNone(summary["final_result"])


class BuildCommandTests(unittest.TestCase):
    def test_basic_command_shape(self):
        cmd = re2.build_command("hello", None, None, False)
        self.assertEqual(cmd[:3], ["claude", "-p", "hello"])
        self.assertIn("--output-format", cmd)
        self.assertIn("stream-json", cmd)

    def test_model_flag(self):
        cmd = re2.build_command("hello", "claude-sonnet-5", None, False)
        self.assertIn("--model", cmd)
        self.assertIn("claude-sonnet-5", cmd)

    def test_skip_permissions_flag(self):
        cmd = re2.build_command("hello", None, None, True)
        self.assertIn("--dangerously-skip-permissions", cmd)
        self.assertNotIn("--permission-mode", cmd)

    def test_permission_mode_flag(self):
        cmd = re2.build_command("hello", None, "acceptEdits", False)
        self.assertIn("--permission-mode", cmd)
        self.assertIn("acceptEdits", cmd)

    def test_skip_permissions_takes_priority_over_permission_mode(self):
        cmd = re2.build_command("hello", None, "acceptEdits", True)
        self.assertIn("--dangerously-skip-permissions", cmd)
        self.assertNotIn("--permission-mode", cmd)


class IsolateProjectTests(unittest.TestCase):
    def test_copies_tracked_files_and_excludes_junk(self):
        import shutil
        import tempfile
        src = Path(tempfile.mkdtemp())
        try:
            (src / "keep.py").write_text("print(1)")
            (src / "node_modules").mkdir()
            (src / "node_modules" / "junk.js").write_text("junk")
            (src / ".git").mkdir()
            (src / ".git" / "HEAD").write_text("ref: refs/heads/main")

            dest = re2.isolate_project(src)
            self.assertTrue((dest / "keep.py").is_file())
            self.assertFalse((dest / "node_modules").exists())
            self.assertFalse((dest / ".git").exists())
            self.assertNotEqual(dest, src)
        finally:
            shutil.rmtree(src, ignore_errors=True)


class OutputWritingTests(unittest.TestCase):
    def test_write_outputs_creates_both_files(self):
        import shutil
        import tempfile
        out_dir = Path(tempfile.mkdtemp())
        try:
            lines = ['{"type": "result", "result": "ok"}']
            summary = {"tool_calls": [], "final_result": {"result": "ok"}}
            re2.write_outputs(out_dir, lines, summary)
            self.assertTrue((out_dir / "transcript.jsonl").is_file())
            self.assertTrue((out_dir / "summary.json").is_file())
            written_summary = json.loads((out_dir / "summary.json").read_text())
            self.assertEqual(written_summary["final_result"]["result"], "ok")
        finally:
            shutil.rmtree(out_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
