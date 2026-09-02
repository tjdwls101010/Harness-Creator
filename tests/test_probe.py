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
# One observation file per invocation: cwd, its listing, stdin byte count,
# argv (one per line). Then answers like `claude -p --output-format json`.
if [ "$1" = "--version" ]; then echo "9.9.9 (fake)"; exit 0; fi
obs=$(mktemp "$FAKE_CLAUDE_LOG/obs.XXXXXX")
{
  printf 'cwd=%s\\n' "$PWD"
  printf 'listing=%s\\n' "$(ls -A "$PWD" | tr '\\n' ',')"
  printf 'stdin_bytes=%s\\n' "$(cat | wc -c | tr -d ' ')"
  printf 'argv_start\\n'
  for a in "$@"; do printf '%s\\n' "$a"; done
} > "$obs"
if [ -n "$FAKE_CLAUDE_ERROR" ]; then
  printf '{"type":"result","is_error":true,"result":"Not logged in","modelUsage":{}}'; exit 1
fi
printf '{"type":"result","is_error":false,"result":"fake answer","total_cost_usd":0.01,"modelUsage":{"claude-fake-1":{"inputTokens":1}}}'
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
        self.log.mkdir()
        self.env = dict(os.environ)
        self.env["PATH"] = f"{bin_dir}{os.pathsep}{self.env.get('PATH', '')}"
        self.env["FAKE_CLAUDE_LOG"] = str(self.log)
        self.env["CLAUDECODE"] = "1"  # the probe must strip this so nesting works
        self.out = self.tmp / "out"

    def run_probe(self, *args, stdin_text="SENTINEL-FROM-CALLER-STDIN\n"):
        proc = subprocess.run(
            [sys.executable, str(PROBE), *args],
            capture_output=True, text=True, timeout=120, env=self.env, cwd=str(REPO_ROOT),
            input=stdin_text,
        )
        return proc.returncode, proc.stdout, proc.stderr

    def observations(self):
        """What the fake claude saw, one dict per invocation."""
        out = []
        for path in sorted(self.log.glob("obs.*")):
            lines = path.read_text(encoding="utf-8").splitlines()
            argv = lines[lines.index("argv_start") + 1:]
            head = dict(l.split("=", 1) for l in lines[:lines.index("argv_start")])
            head["argv"] = argv
            out.append(head)
        return out

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

    def test_every_launched_process_was_bare_toolless_and_stdin_closed(self):
        """Checked against what the fake saw, not only against the record
        the probe wrote about itself: one observation per launched process."""
        code, out, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "2")
        self.assertEqual(code, 0, err)
        observed = self.observations()
        self.assertEqual(len(observed), 4)
        for obs in observed:
            self.assertIn("--bare", obs["argv"])
            self.assertIn("-p", obs["argv"])
            self.assertEqual(obs["argv"][obs["argv"].index("--tools") + 1], "")
            self.assertEqual(obs["stdin_bytes"], "0", "caller stdin leaked into the model's context")
            self.assertEqual(obs["listing"], "")
        for qid in ("hooks-01", "skills-01"):
            for i in (1, 2):
                rec = json.loads((self.out / qid / f"run-{i}.json").read_text(encoding="utf-8"))
                self.assertTrue(rec["argv"][0].endswith("claude"))
                self.assertIn("--bare", rec["argv"])
                self.assertEqual(rec["stdin"], "devnull")
                self.assertIn(Path(rec["cwd"]).resolve(), {Path(o["cwd"]).resolve() for o in observed})

    def test_the_cwd_is_an_empty_directory_outside_the_repo(self):
        code, _, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "1")
        self.assertEqual(code, 0, err)
        rec = json.loads((self.out / "hooks-01" / "run-1.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["cwd_listing_at_launch"], [])
        self.assertNotEqual(Path(rec["cwd"]).resolve(), REPO_ROOT.resolve())
        self.assertNotIn(str(REPO_ROOT), rec["cwd"])
        matching = [o for o in self.observations() if Path(o["cwd"]).resolve() == Path(rec["cwd"]).resolve()]
        self.assertEqual(len(matching), 1, "exactly one launched process used the recorded cwd")
        self.assertEqual(matching[0]["listing"], "")

    def test_the_answer_key_never_reaches_the_model(self):
        self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "1")
        for obs in self.observations():
            self.assertNotIn("directory name, not frontmatter", " ".join(obs["argv"]))
            self.assertNotIn("Only exit 2 blocks", " ".join(obs["argv"]))

    def test_summary_pairs_every_answer_with_its_key(self):
        code, out, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "3")
        self.assertEqual(code, 0, err)
        summary = json.loads((self.out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["runs"], 3)
        self.assertEqual([q["id"] for q in summary["questions"]], ["hooks-01", "skills-01"])
        for q in summary["questions"]:
            self.assertEqual(len(q["answers"]), 3)
            self.assertTrue(q["answer_key"])
            for i, a in enumerate(q["answers"], 1):
                self.assertEqual(a["answer"], "fake answer")
                self.assertEqual(a["model"], ["claude-fake-1"])
                self.assertEqual(a["claude_version"], "9.9.9 (fake)")
                self.assertEqual(a["exit_code"], 0)
                self.assertIsNone(a["error"])
                self.assertTrue(Path(a["file"]).is_file())
        self.assertFalse(summary["provenance"]["drift_detected"])
        self.assertEqual(summary["provenance"]["distinct_model_version_pairs"], 1)

    def test_version_model_and_cost_are_recorded(self):
        self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "1")
        rec = json.loads((self.out / "hooks-01" / "run-1.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["claude_version"], "9.9.9 (fake)")
        self.assertEqual(rec["model"], ["claude-fake-1"])
        self.assertEqual(rec["total_cost_usd"], 0.01)
        self.assertEqual(rec["isolation"], "bare")

    def test_safe_mode_isolation_swaps_the_flag_and_is_recorded(self):
        """--bare skips OAuth, so a machine without ANTHROPIC_API_KEY needs the
        documented alternative that disables the same customizations."""
        code, _, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out),
                                      "--runs", "1", "--isolation", "safe-mode")
        self.assertEqual(code, 0, err)
        rec = json.loads((self.out / "hooks-01" / "run-1.json").read_text(encoding="utf-8"))
        self.assertIn("--safe-mode", rec["argv"])
        self.assertNotIn("--bare", rec["argv"])
        self.assertEqual(rec["argv"][rec["argv"].index("--tools") + 1], "")
        self.assertEqual(rec["isolation"], "safe-mode")
        summary = json.loads((self.out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["isolation"], "safe-mode")

    def test_an_error_envelope_is_recorded_as_an_error_and_fails(self):
        """The first real smoke run recorded `Not logged in` as a normal
        answer with error None. An auth failure is not an answer."""
        self.env["FAKE_CLAUDE_ERROR"] = "1"
        code, _, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "1")
        self.assertEqual(code, 1, err)
        rec = json.loads((self.out / "hooks-01" / "run-1.json").read_text(encoding="utf-8"))
        self.assertIsNotNone(rec["error"])
        self.assertIn("Not logged in", rec["error"])

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

    def test_ids_must_be_unique_slugs(self):
        for rows, needle in (
            ([{"id": "../escape", "question": "q", "answer_key": "a"}], "slug"),
            ([{"id": "a", "question": "q", "answer_key": "a"}, {"id": "a", "question": "q2", "answer_key": "a2"}], "duplicate"),
        ):
            code, _, err = self.run_probe("quiz", "--questions", str(self.write_questions(*rows)), "--out", str(self.out))
            self.assertEqual(code, 2, err)
            self.assertIn(needle, err)
            self.assertFalse(list(self.observations()), "nothing may be launched on bad input")

    def test_an_out_dir_with_files_is_refused(self):
        self.out.mkdir()
        (self.out / "stale.json").write_text("{}", encoding="utf-8")
        code, _, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out))
        self.assertEqual(code, 2, err)
        self.assertIn("already has files", err)

    def test_bad_counts_and_unknown_only_ids_are_usage_errors(self):
        for extra in (("--runs", "0"), ("--timeout", "0"), ("--only", "nope")):
            code, _, err = self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), *extra)
            self.assertEqual(code, 2, (extra, err))
        self.assertEqual(self.observations(), [])

    def test_model_affecting_env_is_recorded_without_secrets(self):
        self.env["ANTHROPIC_MODEL"] = "claude-fake-2"
        self.env["ANTHROPIC_API_KEY"] = "sk-should-not-appear"
        self.run_probe("quiz", "--questions", str(self.questions), "--out", str(self.out), "--runs", "1")
        rec = json.loads((self.out / "hooks-01" / "run-1.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["env_recorded"]["ANTHROPIC_MODEL"], "claude-fake-2")
        self.assertEqual(rec["env_recorded"]["ANTHROPIC_API_KEY"], "<set, not recorded>")
        self.assertNotIn("sk-should-not-appear", json.dumps(rec))


class ContrastTests(ProbeTestCase):
    def setUp(self):
        super().setUp()
        self.task = self.tmp / "task.md"
        self.task.write_text("Write a PreToolUse hook that blocks edits to .env.\n", encoding="utf-8")
        self.reference = self.tmp / "ref.md"
        self.reference.write_text("REFERENCE-MARKER: only exit 2 blocks.\n", encoding="utf-8")

    def test_two_arms_differ_only_by_the_reference_slot(self):
        """Same wrapper both times, so an observed difference is attributable
        to the reference text and not to the wrapper that carries it."""
        code, _, err = self.run_probe("contrast", "--task", str(self.task), "--reference", str(self.reference),
                                      "--out", str(self.out), "--runs", "2")
        self.assertEqual(code, 0, err)
        without = json.loads((self.out / "without" / "run-1.json").read_text(encoding="utf-8"))
        with_ref = json.loads((self.out / "with" / "run-1.json").read_text(encoding="utf-8"))
        ref_text = self.reference.read_text(encoding="utf-8").strip()
        self.assertEqual(with_ref["prompt"].replace(ref_text, ""), without["prompt"])
        self.assertIn("<reference>\n\n</reference>", without["prompt"])
        self.assertIn(f"<reference>\n{ref_text}\n</reference>", with_ref["prompt"])
        for rec in (without, with_ref):
            self.assertIn("--bare", rec["argv"])
            self.assertEqual(rec["argv"][rec["argv"].index("--tools") + 1], "")
            self.assertEqual(rec["cwd_listing_at_launch"], [])
        # Arms alternate run by run rather than all-without then all-with.
        starts = [(json.loads(p.read_text())["started_at"], p) for p in self.out.glob("*/run-*.json")]
        self.assertEqual(len(starts), 4)
        summary = json.loads((self.out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(set(summary["arms"]), {"without", "with"})
        self.assertEqual(len(summary["arms"]["with"]), 2)
        self.assertEqual(summary["arms"]["with"][0]["answer"], "fake answer")
        self.assertIn("provenance", summary)


class HelpTests(unittest.TestCase):
    def test_help_states_the_isolation_flags_and_their_auth_requirement(self):
        proc = subprocess.run([sys.executable, str(PROBE), "--help"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        for token in ("--bare", "--safe-mode", "ANTHROPIC_API_KEY", "summary.json"):
            self.assertIn(token, proc.stdout)
        # Policy (when to probe, what a result licenses) is the project's, not the tool's.
        for owned_elsewhere in ("candidate for deletion", "spends real tokens"):
            self.assertNotIn(owned_elsewhere, proc.stdout)

    def test_every_argument_has_help(self):
        sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"))
        import validate_harness as vh
        findings = []
        vh._check_cli_self_description(PROBE, "tools/probe.py", findings)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
