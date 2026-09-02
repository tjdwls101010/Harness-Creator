#!/usr/bin/env python3
"""Tests for tools/claims.py, the rewrite claim-loss audit.

    python3 -m unittest tests.test_claims -q

The seam is the CLI: `extract <file>` freezes a claim list with stable IDs,
`check <claims> <file> --dispositions <file>` says whether every frozen ID
either survived verbatim or has a disposition with a reason. Anything the
tool cannot see -- a paraphrase, a claim losing part of itself -- is the
reviewer's job, and the tool's --help says so.

stdlib unittest only, no pytest.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAIMS = REPO_ROOT / "tools" / "claims.py"
SOURCE = REPO_ROOT / "tests" / "fixtures" / "claims" / "source.md"


def run(*args, cwd=None):
    proc = subprocess.run(
        [sys.executable, str(CLAIMS), *args],
        capture_output=True, text=True, timeout=60, cwd=cwd,
    )
    return proc.returncode, proc.stdout, proc.stderr


# Read from the fixture by hand, not derived from the extractor. Every
# sentence that carries a marker the tool looks for (bold, heading, table
# row, negation, digit, backtick identifier), in document order, and nothing
# from inside a code fence or an HTML comment.
EXPECTED_ANCHORS = [
    "Golden source",
    "Loading",
    "A rule with `paths:` loads only on a matching read.",
    "Never ablate a hook.",
    "Hooks exist for the failure you cannot observe.",
    "| Status | Claims a file exists? |",
    "| `generated` | Yes |",
    "| `proposed` | No |",
    "The ceiling is 5,000 tokens.",
    "It is not a target.",
    "A bullet that names `validate_harness.py` is a claim.",
]


class ExtractTests(unittest.TestCase):
    def setUp(self):
        code, out, err = run("extract", str(SOURCE))
        self.assertEqual(code, 0, err)
        self.claims = json.loads(out)

    def test_golden_source_yields_exactly_the_expected_ids(self):
        ids = [c["id"] for c in self.claims]
        self.assertEqual(ids, [f"C{i}" for i in range(1, len(EXPECTED_ANCHORS) + 1)])
        self.assertEqual([c["anchor"] for c in self.claims], EXPECTED_ANCHORS)

    def test_every_claim_carries_its_line_number(self):
        for claim in self.claims:
            self.assertIsInstance(claim["line"], int, claim)
            self.assertGreater(claim["line"], 0)

    def test_code_fences_and_html_comments_are_not_claims(self):
        joined = " ".join(c["anchor"] for c in self.claims)
        self.assertNotIn("999", joined)
        self.assertNotIn("42", joined)

    def test_extraction_is_deterministic(self):
        _, again, _ = run("extract", str(SOURCE))
        self.assertEqual(json.loads(again), self.claims)


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.claims_path = self.tmp / "claims.json"
        _, out, _ = run("extract", str(SOURCE))
        self.claims_path.write_text(out, encoding="utf-8")
        self.target = self.tmp / "rewritten.md"
        self.target.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
        self.dispositions = self.tmp / "dispositions.txt"
        self.dispositions.write_text("", encoding="utf-8")

    def _check(self, *extra):
        return run("check", str(self.claims_path), str(self.target),
                   "--dispositions", str(self.dispositions), *extra)

    def _drop_anchor(self, anchor):
        text = self.target.read_text(encoding="utf-8")
        self.assertIn(anchor, text)
        self.target.write_text(text.replace(anchor, ""), encoding="utf-8")

    def test_an_unchanged_file_passes(self):
        code, out, err = self._check()
        self.assertEqual(code, 0, out + err)

    def test_a_deleted_anchor_fails_and_names_its_id(self):
        self._drop_anchor(EXPECTED_ANCHORS[2])  # C3
        code, out, err = self._check()
        self.assertEqual(code, 1, out + err)
        self.assertIn("C3", out + err)

    def test_a_drop_without_a_reason_fails(self):
        self._drop_anchor(EXPECTED_ANCHORS[2])
        self.dispositions.write_text("C3 DROP\n", encoding="utf-8")
        code, out, err = self._check()
        self.assertEqual(code, 1, out + err)
        self.assertIn("C3", out + err)
        self.assertIn("reason", (out + err).lower())

    def test_a_drop_with_a_reason_passes(self):
        self._drop_anchor(EXPECTED_ANCHORS[2])
        self.dispositions.write_text(
            "C3 DROP the rule moved into validate_harness.py's message\n", encoding="utf-8"
        )
        code, out, err = self._check()
        self.assertEqual(code, 0, out + err)

    def test_a_reworded_claim_must_have_its_new_anchor_present(self):
        self._drop_anchor(EXPECTED_ANCHORS[9])  # C10 "It is not a target."
        self.dispositions.write_text("C10 REWORDED The ceiling is a ceiling\n", encoding="utf-8")
        code, out, err = self._check()
        self.assertEqual(code, 1, out + err)
        with open(self.target, "a", encoding="utf-8") as f:
            f.write("\nThe ceiling is a ceiling, not a goal.\n")
        code, out, err = self._check()
        self.assertEqual(code, 0, out + err)

    def test_a_claim_moved_to_another_file_is_checked_there(self):
        self._drop_anchor(EXPECTED_ANCHORS[4])  # C5
        other = self.tmp / "other.md"
        other.write_text("Hooks exist for the failure you cannot observe.\n", encoding="utf-8")
        self.dispositions.write_text(
            f"C5 MOVED {other} :: Hooks exist for the failure you cannot observe.\n",
            encoding="utf-8",
        )
        code, out, err = self._check()
        self.assertEqual(code, 0, out + err)
        other.write_text("something else\n", encoding="utf-8")
        code, out, err = self._check()
        self.assertEqual(code, 1, out + err)

    def test_a_disposition_for_an_unknown_id_fails(self):
        self.dispositions.write_text("C99 DROP no such claim\n", encoding="utf-8")
        code, out, err = self._check()
        self.assertEqual(code, 1, out + err)
        self.assertIn("C99", out + err)

    def test_whitespace_rewrapping_does_not_count_as_loss(self):
        text = self.target.read_text(encoding="utf-8")
        text = text.replace("A rule with `paths:` loads only on a matching read.",
                            "A rule with `paths:` loads\nonly on a matching read.")
        self.target.write_text(text, encoding="utf-8")
        code, out, err = self._check()
        self.assertEqual(code, 0, out + err)

    def test_json_output_maps_every_id_to_a_verdict(self):
        code, out, err = self._check("--json")
        self.assertEqual(code, 0, err)
        report = json.loads(out)
        self.assertEqual(sorted(report["claims"]), sorted(c["id"] for c in json.loads(self.claims_path.read_text())))


class HelpTests(unittest.TestCase):
    def test_help_says_what_the_tool_cannot_see(self):
        code, out, _ = run("--help")
        self.assertEqual(code, 0)
        self.assertIn("paraphrase", out.lower())
        for sub in ("extract", "check"):
            code, sub_out, _ = run(sub, "--help")
            self.assertEqual(code, 0, sub)
            self.assertTrue(sub_out.strip())

    def test_every_argument_has_help(self):
        """The same rule this repo's validate_harness.py applies to bundled
        scripts, applied to the dev tool that audits them."""
        sys.path.insert(0, str(REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"))
        import validate_harness as vh
        findings = []
        vh._check_cli_self_description(CLAIMS, "tools/claims.py", findings)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
