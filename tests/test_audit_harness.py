#!/usr/bin/env python3
"""Self-test for audit_harness.py against tests/fixtures/{good,bad}-harness.

    python3 tests/test_audit_harness.py
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import audit_harness as ah  # noqa: E402
import harness_common as hc  # noqa: E402

AUDIT = SCRIPTS_DIR / "audit_harness.py"


def run_cli(*args):
    return subprocess.run([sys.executable, str(AUDIT), *args], capture_output=True, text=True, timeout=120)


class ScopeAndJsonContractTests(unittest.TestCase):
    """The audit checks existence, not content. Saying so on every run is
    what keeps a clean report from reading as "nothing changed"."""

    def setUp(self):
        self.result = ah.run(REPO_ROOT / "tests" / "fixtures" / "good-harness")

    def test_scope_is_stated_in_both_directions(self):
        scope = self.result["scope"]
        self.assertTrue(scope["detects"])
        self.assertTrue(scope["does_not_detect"])
        blind = " ".join(scope["does_not_detect"]).lower()
        self.assertIn("claude.md", blind)
        self.assertIn("body", blind)

    def test_text_output_states_the_scope_even_when_clean(self):
        text = run_cli("--path", str(REPO_ROOT / "tests" / "fixtures" / "good-harness")).stdout
        self.assertIn("No drift detected", text)
        self.assertIn("existence", text.lower())
        self.assertNotIn("Suggested mode", text)
        self.assertNotIn("ask before proposing", text)

    def test_user_config_root_and_how_it_was_chosen_are_exposed(self):
        self.assertIn("user_config_root", self.result)
        self.assertIn(self.result["user_config_root_source"], ("CLAUDE_CONFIG_DIR", "default"))

    def test_config_dir_env_var_moves_the_user_root(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        root, source = ah.user_config_root({"CLAUDE_CONFIG_DIR": str(tmp)})
        self.assertEqual(root, tmp)
        self.assertEqual(source, "CLAUDE_CONFIG_DIR")
        root, source = ah.user_config_root({})
        self.assertEqual(root, Path.home() / ".claude")
        self.assertEqual(source, "default")


class TemplateTests(unittest.TestCase):
    """`--template` prints the spec skeleton the parser reads, from the same
    constants, so heading and column names cannot drift apart."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        proc = run_cli("--template")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.template = proc.stdout

    def test_sections_come_in_dependency_order(self):
        headings = [l for l in self.template.splitlines() if l.startswith("## ")]
        self.assertEqual(headings, [f"## {name}" for name in hc.SPEC_SECTIONS])
        self.assertEqual(hc.SPEC_SECTIONS, (
            "Context", "Goals", "Behavior inventory", "Component specs",
            "Design rationale", "Validation", "Change history",
        ))

    def test_inventory_header_and_status_vocabulary_come_from_the_shared_constants(self):
        self.assertIn("| " + " | ".join(hc.INVENTORY_COLUMNS) + " |", self.template)
        for status in hc.SPEC_STATUSES:
            self.assertIn(f"`{status}`", self.template)
        self.assertEqual(set(hc.STATUSES_CLAIMING_A_FILE), {"generated", "validated"})
        self.assertLessEqual(set(hc.STATUSES_CLAIMING_A_FILE), set(hc.SPEC_STATUSES))

    def test_example_rows_are_comments_the_parser_ignores(self):
        self.assertEqual(list(hc.iter_inventory_rows(self.template)), [])
        self.assertIn("<!--", self.template)

    def test_change_history_has_no_mode_column(self):
        section = self.template.split("## Change history")[1]
        self.assertNotIn("mode", section.lower())
        self.assertIn("date", section.lower())

    def test_maintenance_rules_travel_as_comments(self):
        for phrase in ("fold", "rejected alternative", "description"):
            self.assertIn(phrase, self.template.lower())
        # But not the approval policy, which belongs to the skill's prose
        # (`approved` the status is vocabulary, not policy).
        lowered = self.template.lower()
        for policy in ("approval", "sign off", "signs off", "approve before", "gate"):
            self.assertNotIn(policy, lowered)

    def test_round_trip_reports_no_drift(self):
        (self.tmp / ".claude").mkdir()
        (self.tmp / ".claude" / "harness-spec.md").write_text(self.template, encoding="utf-8")
        proc = run_cli("--path", str(self.tmp), "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        drift = json.loads(proc.stdout)["spec_drift"]
        self.assertTrue(drift["spec_exists"])
        self.assertEqual(drift["in_spec_not_on_disk"], [])
        self.assertEqual(drift["on_disk_not_in_spec"], [])

    def test_template_and_path_are_mutually_exclusive_and_one_is_required(self):
        self.assertEqual(run_cli().returncode, 2)
        self.assertEqual(run_cli("--template", "--path", ".").returncode, 2)
        self.assertEqual(run_cli("--template", "--json").returncode, 2)


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

    def test_reports_facts_not_a_mode(self):
        """The audit says what is on disk and what the spec claims; which
        kind of pass to run is the interviewer's call, made with the user."""
        self.assertNotIn("suggested_mode", self.result)
        self.assertTrue(self.result["spec_drift"]["spec_exists"])
        self.assertTrue(self.result["inventory"]["skills"])


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

    def test_a_missing_spec_is_reported_with_the_way_to_start_one(self):
        self.assertFalse(self.result["spec_drift"]["spec_exists"])
        text = run_cli("--path", str(self.root)).stdout
        self.assertIn("No harness-spec.md", text)
        self.assertIn("--template", text)
        self.assertNotIn("Suggested mode", text)


class EmptyProjectAuditTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmpdir = tempfile.mkdtemp()
        self.root = Path(self.tmpdir)
        self.result = ah.run(self.root)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_an_empty_project_has_no_components_and_no_spec(self):
        inv = self.result["inventory"]
        self.assertFalse(any(inv[k] for k in ("claude_md", "rules", "skills", "agents", "workflows", "settings")))
        self.assertFalse(self.result["spec_drift"]["spec_exists"])
        self.assertNotIn("suggested_mode", self.result)

    def test_empty_inventory(self):
        inv = self.result["inventory"]
        self.assertEqual(inv["claude_md"], [])
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

    def test_missing_files_are_reported_as_facts(self):
        result = ah.run(self.root)
        self.assertTrue(result["spec_drift"]["in_spec_not_on_disk"])
        self.assertNotIn("suggested_mode", result)


class SpecDriftGranularityTests(unittest.TestCase):
    """B13. Found by dogfooding: writing this repo's own harness-spec.md
    reported all sixteen components as missing. The check compared spec rows
    only against component-level inventory paths, so a spec naming a file
    *inside* a component -- a skill's SKILL.md, one of its references -- drew
    a false 'not on disk' for a path that plainly exists. A check that fires
    on a correct harness is worse than no check."""

    def test_this_repo_reports_no_drift(self):
        drift = ah.check_spec_drift(REPO_ROOT, ah.run(REPO_ROOT)["inventory"])
        self.assertEqual(drift["in_spec_not_on_disk"], [])

    def test_a_path_that_exists_is_never_reported(self):
        spec = (
            "## Behavior inventory\n"
            "| id | b | layer | component | status |\n"
            "| B1 | x | skill | `.claude/skills/harness-creator/SKILL.md` | validated |\n"
            "| B2 | y | skill | `.claude/skills/harness-creator/references/hooks.md` | validated |\n"
        )
        self.assertEqual(ah._spec_rows_without_files(REPO_ROOT, spec, set()), [])

    def test_a_path_that_does_not_exist_is_still_reported(self):
        spec = (
            "## Behavior inventory\n"
            "| id | b | layer | component | status |\n"
            "| B1 | x | skill | `.claude/skills/harness-creator/nope.md` | validated |\n"
        )
        rows = ah._spec_rows_without_files(REPO_ROOT, spec, set())
        self.assertEqual([r["id"] for r in rows], ["B1"])


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
    def test_an_escaped_pipe_inside_a_cell_does_not_shift_columns(self):
        spec = (
            "## Behavior inventory\n"
            "| id | b | layer | component | status |\n"
            "| B1 | allow `a`\\|`b` | hook | `.claude/hooks/x.sh` | generated |\n"
        )
        rows = list(ah._iter_inventory_rows(spec))
        self.assertEqual(rows[0][3], "`.claude/hooks/x.sh`")
        self.assertEqual(rows[0][4], "generated")

    def test_a_comment_opened_after_prose_still_hides_its_rows(self):
        spec = (
            "## Behavior inventory\n"
            "| id | b | layer | component | status |\n"
            "Some prose <!-- a comment that runs on\n"
            "| B9 | hidden | skill | `.claude/skills/ghost/` | generated |\n"
            "--> and closes here\n"
            "| B1 | real | skill | `.claude/skills/real/` | proposed |\n"
        )
        self.assertEqual([r[0] for r in ah._iter_inventory_rows(spec)], ["B1"])

    def test_status_comparison_is_case_sensitive_like_the_template(self):
        """`Validated` is not `validated`: V01 reports it, and the drift
        check must not quietly read it as a file claim either."""
        spec = (
            "## Behavior inventory\n"
            "| id | b | layer | component | status |\n"
            "| B1 | x | skill | `.claude/skills/nope/` | Validated |\n"
            "| B2 | y | skill | `.claude/skills/nope2/` | validated |\n"
        )
        rows = ah._spec_rows_without_files(REPO_ROOT, spec, set())
        self.assertEqual([r["id"] for r in rows], ["B2"])

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
