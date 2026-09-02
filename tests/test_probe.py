#!/usr/bin/env python3
"""Tests for tools/probe.py, the gotcha knowledge probe.

    python3 -m unittest discover -s tests -p "test_probe.py" -q

No real `claude` is spawned: a fake executable on PATH records how it was
called and answers with a canned envelope. The seam is the CLI plus the
result files it writes -- the isolation evidence lives in those files (argv,
cwd, listing at launch), so that is what the tests read.

stdlib unittest only, no pytest.
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBE = REPO_ROOT / "tools" / "probe.py"

FAKE_CLAUDE = """#!/bin/sh
# Records argv and cwd, then answers like `claude -p --output-format json`.
printf '%s\\n' "$PWD" > "$FAKE_CLAUDE_LOG.cwd"
ls -A "$PWD" > "$FAKE_CLAUDE_LOG.listing"
: > "$FAKE_CLAUDE_LOG.argv"
for a in "$@"; do printf '%s\\n' "$a" >> "$FAKE_CLAUDE_LOG.argv"; done
if [ "$1" = "--version" ]; then echo "9.9.9 (fake)"; exit 0; fi
printf '{"type":"result","result":"fake answer","modelUsage":{"claude-fake-1":{"inputTokens":1}}}'
"""


class ProbeTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "claude"
        fake.write_text(FAKE_CLAUDE, encoding="utf-8")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        self.log = self.tmp / "fake-claude"
        self.env = dict(os.environ)
        self.env["PATH"] = f"{bin_dir}{os.pathsep}{self.env.get('PATH', '')}"
        self.env["FAKE_CLAUDE_LOG"] = str(self.log)
        self.env["CLAUDECODE"] = "1"  # the probe must strip this so nesting works
        self.out = self.tmp / "out"

    def run_probe(self, *args):
        proc = subprocess.run(
            [sys.executable, str(PROBE), *args],
            capture_output=True, text=True, timeout=120, env=self.env, cwd=str(REPO_ROOT),
        )
        return proc.returncode, proc.stdout, proc.stderr

    def write_questions(self, *rows):
        path = self.tmp / "q.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        return path


class QuizTests(ProbeTestCase):
    def setUp(self):
        super().setUp()
        self.questions = self.write_questions(
            {"id": "hooks-01", "source": "hooks.md:66", "question": "Which hook exit code blocks?",
             "answer_key": "Only exit 2 blocks; exit 1 is a non-blocking error."},
            {"id": "skills-01", "question": "What names a skill's slash command?",
             "answer_key": "The directory name, not frontmatter name."},
        )

    def test_every_run_is_bare_and_toolless(self):
        code, out, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "2")
        self.assertEqual(code, 0, err)
        for qid in ("hooks-01", "skills-01"):
            for i in (1, 2):
                rec = json.loads((self.out / qid / f"run-{i}.json").read_text(encoding="utf-8"))
                argv = rec["argv"]
                self.assertEqual(argv[0], "claude")
                self.assertIn("--bare", argv)
                self.assertIn("-p", argv)
                self.assertEqual(argv[argv.index("--tools") + 1], "")
                self.assertIn("-p", argv)
                self.assertNotIn("--output-format json", " ".join(argv[:argv.index("-p")]))

    def test_the_cwd_is_an_empty_directory_outside_the_repo(self):
        code, _, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "1")
        self.assertEqual(code, 0, err)
        rec = json.loads((self.out / "hooks-01" / "run-1.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["cwd_listing_at_launch"], [])
        self.assertNotEqual(Path(rec["cwd"]).resolve(), REPO_ROOT.resolve())
        self.assertNotIn(str(REPO_ROOT), rec["cwd"])
        # What the fake saw agrees with what the record claims.
        self.assertEqual((self.log.parent / "fake-claude.listing").read_text().strip(), "")
        seen_argv = (self.log.parent / "fake-claude.argv").read_text(encoding="utf-8").splitlines()
        self.assertIn("--bare", seen_argv)
        self.assertEqual(seen_argv[seen_argv.index("--tools") + 1], "")

    def test_the_answer_key_never_reaches_the_model(self):
        self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "1")
        seen_argv = (self.log.parent / "fake-claude.argv").read_text(encoding="utf-8")
        self.assertNotIn("directory name, not frontmatter", seen_argv)

    def test_summary_pairs_every_answer_with_its_key(self):
        code, out, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "3")
        self.assertEqual(code, 0, err)
        summary = json.loads((self.out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["runs"], 3)
        self.assertEqual([q["id"] for q in summary["questions"]], ["hooks-01", "skills-01"])
        for q in summary["questions"]:
            self.assertEqual(len(q["answers"]), 3)
            self.assertTrue(q["answer_key"])
            self.assertEqual(q["answers"], ["fake answer"] * 3)

    def test_version_and_model_are_recorded(self):
        self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "1")
        rec = json.loads((self.out / "hooks-01" / "run-1.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["claude_version"], "9.9.9 (fake)")
        self.assertEqual(rec["model"], ["claude-fake-1"])

    def test_only_restricts_to_the_named_ids(self):
        code, _, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out),
                                      "--runs", "1", "--only", "skills-01")
        self.assertEqual(code, 0, err)
        self.assertFalse((self.out / "hooks-01").exists())
        self.assertTrue((self.out / "skills-01" / "run-1.json").exists())

    def test_a_question_missing_its_key_is_a_usage_error(self):
        bad = self.write_questions({"id": "x", "question": "no key here"})
        code, _, err = self.run_probe("quiz", "--questions", str(bad), "--out", str(self.out))
        self.assertEqual(code, 2, err)
        self.assertIn("answer_key", err)


class ContrastTests(ProbeTestCase):
    def setUp(self):
        super().setUp()
        self.task = self.tmp / "task.md"
        self.task.write_text("Write a PreToolUse hook that blocks edits to .env.\n", encoding="utf-8")
        self.reference = self.tmp / "ref.md"
        self.reference.write_text("REFERENCE-MARKER: only exit 2 blocks.\n", encoding="utf-8")

    def test_two_arms_differ_only_by_the_inlined_reference(self):
        code, _, err = self.run_probe("contrast", "--task", str(self.task), "--reference", str(self.reference),
                                      "--out", str(self.out), "--runs", "1")
        self.assertEqual(code, 0, err)
        without = json.loads((self.out / "without" / "run-1.json").read_text(encoding="utf-8"))
        with_ref = json.loads((self.out / "with" / "run-1.json").read_text(encoding="utf-8"))
        self.assertNotIn("REFERENCE-MARKER", without["prompt"])
        self.assertIn("REFERENCE-MARKER", with_ref["prompt"])
        self.assertIn("blocks edits to .env", without["prompt"])
        self.assertIn("blocks edits to .env", with_ref["prompt"])
        for rec in (without, with_ref):
            self.assertIn("--bare", rec["argv"])
            self.assertEqual(rec["argv"][rec["argv"].index("--tools") + 1], "")
            self.assertEqual(rec["cwd_listing_at_launch"], [])
        summary = json.loads((self.out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(set(summary["arms"]), {"without", "with"})


class HelpTests(unittest.TestCase):
    def test_help_states_the_isolation_and_the_cost(self):
        proc = subprocess.run([sys.executable, str(PROBE), "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--bare", proc.stdout)
        self.assertIn("tokens", proc.stdout)

    def test_every_argument_has_help(self):
        sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"))
        import validate_harness as vh
        findings = []
        vh._check_cli_self_description(PROBE, "tools/probe.py", findings)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
