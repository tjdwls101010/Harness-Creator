#!/usr/bin/env python3
"""Tests for scripts/hook_event.py.

    python3 tests/test_hook_event.py

stdlib unittest only, no pytest.
"""

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
EVENTS_MD = SCRIPTS_DIR.parent / "references" / "hooks-events.md"
sys.path.insert(0, str(SCRIPTS_DIR))

import harness_common as hc  # noqa: E402
import hook_event as he  # noqa: E402


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPTS_DIR / "hook_event.py"), *args],
                          capture_output=True, text=True)


class CoverageTests(unittest.TestCase):
    """Every event the file documents must be reachable. A lookup tool that
    silently omits an event is worse than no tool: the model asks, gets
    nothing, and concludes the event does not exist -- which is the exact
    failure the file's own 'treat this list as authoritative' warning
    exists to prevent."""

    def test_all_thirty_events_resolve(self):
        names = he.event_names()
        self.assertEqual(len(names), 30, names)
        text, expanded, tabled = he.load()
        for n in names:
            self.assertIsNotNone(he.render(n, text, expanded, tabled), n)

    def test_names_match_the_files_own_enumeration(self):
        """The preamble list is the authority. If a section is added without
        being listed there, or listed without being defined, this fails."""
        text, expanded, tabled = he.load()
        self.assertEqual(set(he.event_names()), set(expanded) | set(tabled))

    def test_the_two_shipped_event_lists_agree(self):
        """test_hook.py takes --event from harness_common.HOOK_EVENTS;
        hook_event.py derives its choices from hooks-events.md. Two
        interfaces that can disagree is the drift this pins shut."""
        self.assertEqual(set(he.event_names()), set(hc.HOOK_EVENTS))

    def test_order_is_lifecycle_not_alphabetical(self):
        names = he.event_names()
        self.assertEqual(names[0], "SessionStart")
        self.assertEqual(names[-1], "SessionEnd")
        self.assertNotEqual(names, sorted(names))


class EscapedPipeTests(unittest.TestCase):
    """Regression. This file writes alternatives inside a cell as `a`\\|`b`.
    Splitting rows on a bare pipe tears those apart, makes well-formed rows
    look malformed, and drops the trailing columns of the three rows that
    use it. A session-long detour was spent 'fixing' a table that was never
    broken."""

    def test_escaped_pipe_rows_keep_every_column(self):
        _, _, tabled = he.load()
        for name in ("UserPromptExpansion", "FileChanged", "Elicitation"):
            row = tabled.get(name)
            self.assertIsNotNone(row, f"{name} row was dropped by the parser")
            self.assertIn("Version caveats", row)
            self.assertTrue(row["Decision channel"], f"{name} lost its decision channel")

    def test_a_cell_containing_an_escaped_pipe_is_not_split(self):
        _, _, tabled = he.load()
        self.assertIn("|", tabled["FileChanged"]["Key input fields"] +
                           tabled["FileChanged"]["Matcher"])


class OutputTests(unittest.TestCase):
    def test_lookup_is_far_smaller_than_the_file(self):
        """The whole point. If this ratio ever approaches 1, the script has
        stopped earning its place."""
        whole = len(EVENTS_MD.read_text(encoding="utf-8").split())
        one = len(run("--event", "PreToolUse").stdout.split())
        self.assertLess(one, whole / 4, f"{one} words of {whole}")

    def test_expanded_and_tabled_events_both_render(self):
        self.assertIn("Trigger timing", run("--event", "PreToolUse").stdout)   # a section
        self.assertIn("Trigger timing", run("--event", "Setup").stdout)        # a table row

    def test_common_input_fields_travel_with_a_single_event(self):
        """The per-event rows deliberately omit the fields every event
        carries, so a reader who takes one row without them is missing
        session_id and friends."""
        self.assertIn("session_id", run("--event", "Setup").stdout)

    def test_setup_keeps_the_qualifier_that_makes_it_correct(self):
        """`--init` and `--maintenance` fire Setup only in -p mode. The
        router in hooks.md stated these as three equivalent flags and was
        wrong for months; this file is where the qualified version lives."""
        out = run("--event", "Setup").stdout
        self.assertIn("-p", out)
        self.assertIn("Never fires on normal startup", out)

    def test_invalid_event_is_rejected_and_lists_the_valid_ones(self):
        """argparse choices double as the authoritative event list: several
        of these postdate common training data, and a model that cannot see
        them enumerated refuses to author one as nonexistent."""
        r = run("--event", "NotARealEvent")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("TaskCompleted", r.stderr)
        self.assertIn("PostToolBatch", r.stderr)

    def test_list_prints_one_per_line(self):
        r = run("--list")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(len(r.stdout.strip().split("\n")), 30)

    def test_requires_an_argument(self):
        self.assertNotEqual(run().returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
