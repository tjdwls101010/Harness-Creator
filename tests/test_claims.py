#!/usr/bin/env python3
"""Tests for tools/claims.py at its CLI seam, against a hand-read golden source.

    python3 -m unittest discover -s tests -p "test_claims.py" -q

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


# Read from the fixture by hand, not derived from the extractor: every
# heading, bold span, table row, and sentence with a negation, a number or a
# backticked identifier, in document order, and nothing from inside a code
# fence or an HTML comment. (anchor, source line) pairs.
EXPECTED = [
    ("Golden source", 1),
    ("Loading", 3),
    ("A rule with `paths:` loads only on a matching read.", 5),
    ("Never ablate a hook.", 7),
    ("Hooks exist for the failure you cannot observe.", 7),
    ("| Status | Claims a file exists? |", 9),
    ("| `generated` | Yes |", 11),
    ("| `proposed` | No |", 12),
    ("The ceiling is 5,000 tokens.", 22),
    ("It is not a target.", 22),
    ("A bullet that names `validate_harness.py` is a claim.", 24),
]
EXPECTED_ANCHORS = [a for a, _ in EXPECTED]

# The affirmative sentences the default heuristic deliberately skips. The
# affirmative claim among them is what --all-sentences exists to catch.
AFFIRMATIVE = [
    "Every rule loads at launch.",
    "Plain sentence about the weather.",
    "Another plain sentence, still background.",
    "A bullet that describes background.",
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

    def test_every_claim_points_at_its_own_source_line(self):
        self.assertEqual([(c["anchor"], c["line"]) for c in self.claims], EXPECTED)

    def test_all_sentences_catches_the_affirmative_claim_the_heuristic_skips(self):
        """The heuristic misses "Every rule loads at launch." -- a claim with
        no marker. A full rewrite uses --all-sentences and prunes by hand."""
        _, out, _ = run("extract", "--all-sentences", str(SOURCE))
        anchors = [c["anchor"] for c in json.loads(out)]
        for sentence in AFFIRMATIVE:
            self.assertIn(sentence, anchors)
        self.assertEqual([a for a in anchors if a not in AFFIRMATIVE], EXPECTED_ANCHORS)

    def test_a_second_sentence_on_a_wrapped_line_gets_the_line_it_starts_on(self):
        wrapped = self.tmp_source("First, 5 apples.\nThen, 6 pears.\n")
        _, out, _ = run("extract", wrapped)
        self.assertEqual([(c["anchor"], c["line"]) for c in json.loads(out)],
                         [("First, 5 apples.", 1), ("Then, 6 pears.", 2)])

    def test_a_longer_fence_is_not_closed_by_a_shorter_one(self):
        source = self.tmp_source("````md\n```\nnot a claim, 42\n```\n````\nA real claim, 7.\n")
        _, out, _ = run("extract", source)
        self.assertEqual([c["anchor"] for c in json.loads(out)], ["A real claim, 7."])

    def test_a_heading_ending_in_a_hash_keeps_it(self):
        source = self.tmp_source("# C#\n\n## Closing hashes go ##\n")
        _, out, _ = run("extract", source)
        self.assertEqual([c["anchor"] for c in json.loads(out)], ["C#", "Closing hashes go"])

    def tmp_source(self, text):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        path = tmp / "s.md"
        path.write_text(text, encoding="utf-8")
        return str(path)

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
        self.assertTrue(report["ok"])
        self.assertEqual(report["failures"], [])
        self.assertEqual(set(report["claims"].values()), {"SURVIVED"})
        self.assertEqual(sorted(report["claims"]), sorted(c["id"] for c in json.loads(self.claims_path.read_text())))
        self._drop_anchor(EXPECTED_ANCHORS[2])
        _, out, _ = self._check("--json")
        report = json.loads(out)
        self.assertFalse(report["ok"])
        self.assertEqual(report["claims"]["C3"], "MISSING")

    def test_an_anchor_surviving_only_inside_a_code_fence_is_a_loss(self):
        self._drop_anchor(EXPECTED_ANCHORS[2])
        with open(self.target, "a", encoding="utf-8") as f:
            f.write("\n```\nA rule with `paths:` loads only on a matching read.\n```\n")
        code, out, err = self._check()
        self.assertEqual(code, 1, out + err)
        self.assertIn("C3", out + err)

    def test_two_frozen_copies_need_two_surviving_copies(self):
        claims = json.loads(self.claims_path.read_text(encoding="utf-8"))
        claims.append({"id": "C12", "kind": "sentence", "anchor": EXPECTED_ANCHORS[9], "line": 99})
        self.claims_path.write_text(json.dumps(claims), encoding="utf-8")
        code, out, err = self._check()
        self.assertEqual(code, 1, out + err)
        self.assertIn("fewer copies", out + err)
        with open(self.target, "a", encoding="utf-8") as f:
            f.write("\nIt is not a target.\n")
        code, out, err = self._check()
        self.assertEqual(code, 0, out + err)

    def test_malformed_input_is_a_usage_error_not_a_traceback(self):
        self.claims_path.write_text("{not json", encoding="utf-8")
        code, out, err = self._check()
        self.assertEqual(code, 2, out + err)
        self.assertNotIn("Traceback", err)
        self.claims_path.write_text('[{"id": "C1", "anchor": "x"}, {"id": "C1", "anchor": "y"}]', encoding="utf-8")
        code, out, err = self._check()
        self.assertEqual(code, 2, out + err)
        self.assertIn("duplicate", err)


class HelpTests(unittest.TestCase):
    def test_help_says_what_the_tool_cannot_see(self):
        code, out, _ = run("--help")
        self.assertEqual(code, 0)
        self.assertIn("paraphrase", out.lower())

    def test_each_subcommand_help_defines_its_own_contract(self):
        code, out, _ = run("extract", "--help")
        self.assertEqual(code, 0)
        for token in ("id", "kind", "anchor", "line", "--all-sentences"):
            self.assertIn(token, out)
        code, out, _ = run("check", "--help")
        self.assertEqual(code, 0)
        for verb in ("DROP", "REWORDED", "MOVED", "TOOL", "KEEP"):
            self.assertIn(verb, out)
        self.assertIn("Exit 0", out)

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
