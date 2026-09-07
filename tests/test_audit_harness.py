#!/usr/bin/env python3
"""Self-test for audit_harness.py against tests/fixtures/{good,bad}-harness.

    python3 tests/test_audit_harness.py
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


class HarnessHistoryTests(unittest.TestCase):
    """The record of why a harness looks the way it does now lives in the
    commits that changed it. A pass that cannot find those commits is in the
    same position as one with no record at all, so the audit reports them
    rather than instructing the reader to run git."""

    def test_a_directory_that_is_not_a_repo_says_so(self):
        """Three outcomes have to stay apart: no repository, a repository
        with no matching commit, and a repository never searched. Collapsing
        them turns "nothing was recorded" into "nothing was decided"."""
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        history = ah.run(tmp)["harness_history"]
        self.assertEqual(history["status"], "not_a_repository")
        self.assertEqual(history["commits"], [])

    def _repo(self):
        """A throwaway repository. Real git, because the three things that
        actually broke here -- pathspecs resolved against the wrong root,
        history simplification dropping branch commits, and a target whose
        repository lives further up -- are all git's behaviour, and a fake
        runner reproduces whatever the author already believed."""
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        self._git(tmp, "init", "-q", "-b", "main")
        self._git(tmp, "config", "user.email", "t@example.com")
        self._git(tmp, "config", "user.name", "t")
        # Hermetic against the developer's own global excludes. This machine's
        # ~/.config/git/ignore drops `**/.claude/plans/`, which would make the
        # exclusion test below pass for a reason the shipped code has nothing
        # to do with -- and fail on a machine without that line.
        self._git(tmp, "config", "core.excludesFile", os.devnull)
        return tmp

    @staticmethod
    def _git(cwd, *args):
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True)

    def _commit(self, repo, subject, files):
        for rel, body in files.items():
            path = repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", subject)

    def test_a_commit_that_changed_a_component_is_found(self):
        repo = self._repo()
        self._commit(repo, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        history = ah.run(repo)["harness_history"]
        self.assertEqual(history["status"], "searched")
        self.assertEqual([c["subject"] for c in history["commits"]], ["add the review skill"])

    def test_a_commit_that_only_used_the_harness_is_not_found(self):
        """The distinction the whole report rests on. Work done *with* a
        harness edits the project; work done *on* one edits the harness. A
        path filter does not rank the two -- it never meets the first."""
        repo = self._repo()
        self._commit(repo, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        self._commit(repo, "implement checkout", {"src/checkout.py": "pass\n"})
        self._commit(repo, "write a plan", {".claude/plans/some-plan.md": "plan\n"})
        subjects = [c["subject"] for c in ah.run(repo)["harness_history"]["commits"]]
        self.assertEqual(subjects, ["add the review skill"])

    def test_an_empty_repository_and_a_repository_with_no_match_read_differently(self):
        """"No harness commit exists" and "this project has no history at
        all" lead a pass to different next moves: one says the decision was
        never recorded, the other that there is nowhere to record it."""
        empty = self._repo()
        self.assertEqual(ah.run(empty)["harness_history"]["status"], "no_history")

        unrelated = self._repo()
        self._commit(unrelated, "implement checkout", {"src/checkout.py": "pass\n"})
        history = ah.run(unrelated)["harness_history"]
        self.assertEqual(history["status"], "no_match")
        self.assertEqual(history["commits"], [])

    def test_a_target_inside_a_monorepo_searches_its_own_subtree_only(self):
        """Measured: a pathspec that matches from one directory matches
        nothing from another, because git resolves it against its own working
        directory. The failure is silent -- an empty report reads exactly
        like a project whose harness nobody has touched."""
        repo = self._repo()
        self._commit(repo, "app harness", {"packages/app/.claude/skills/a/SKILL.md": "x\n"})
        self._commit(repo, "api harness", {"packages/api/.claude/skills/b/SKILL.md": "x\n"})
        history = ah.run(repo / "packages" / "app")["harness_history"]
        self.assertEqual([c["subject"] for c in history["commits"]], ["app harness"])

    def test_a_deleted_component_keeps_its_history(self):
        """Why the pathspec is directory patterns and not the files
        discovery finds today: the decision to remove a component is exactly
        the one a later pass must not re-litigate, and nothing on disk
        records it."""
        repo = self._repo()
        self._commit(repo, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        shutil.rmtree(repo / ".claude" / "skills" / "review")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", "retire the review skill")
        subjects = [c["subject"] for c in ah.run(repo)["harness_history"]["commits"]]
        self.assertEqual(subjects, ["retire the review skill", "add the review skill"])

    def test_a_hook_body_change_counts(self):
        """A hook whose settings entry never moves still changes what the
        harness enforces. Discovery reaches hooks through settings.json, so
        a path list derived from it alone would miss this commit."""
        repo = self._repo()
        self._commit(repo, "tighten the pre-commit hook", {".claude/hooks/pre-commit.sh": "#!/bin/sh\n"})
        subjects = [c["subject"] for c in ah.run(repo)["harness_history"]["commits"]]
        self.assertEqual(subjects, ["tighten the pre-commit hook"])

    def test_a_mixed_commit_is_kept_and_says_which_paths_matched(self):
        """Feature work that adds a build command to CLAUDE.md really did
        change the harness, so it belongs in the list -- but its subject
        describes the feature. Naming the matched paths is what stops a
        reader from having to open every commit to find the harness half."""
        repo = self._repo()
        self._commit(repo, "add checkout, document its build step", {
            "src/checkout.py": "pass\n",
            "CLAUDE.md": "run `make build`\n",
        })
        commit = ah.run(repo)["harness_history"]["commits"][0]
        self.assertEqual(commit["subject"], "add checkout, document its build step")
        self.assertEqual(commit["matched"], ["CLAUDE.md"])

    def test_a_long_history_is_capped_and_says_it_was(self):
        """A report that silently stops at N reads as a project with N
        harness commits. The cap is a budget on this report, not a claim
        about the repository."""
        repo = self._repo()
        for i in range(ah.HISTORY_LIMIT + 1):
            self._commit(repo, f"pass {i}", {".claude/skills/review/SKILL.md": f"{i}\n"})
        history = ah.run(repo)["harness_history"]
        self.assertEqual(len(history["commits"]), ah.HISTORY_LIMIT)
        self.assertTrue(history["truncated"])
        self.assertEqual(history["commits"][0]["subject"], f"pass {ah.HISTORY_LIMIT}")

    def test_a_short_history_is_not_marked_truncated(self):
        repo = self._repo()
        self._commit(repo, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        self.assertFalse(ah.run(repo)["harness_history"]["truncated"])

    def test_the_text_report_distinguishes_the_three_states(self):
        """The structured result is not what a pass reads. If the rendered
        report collapses these, the distinction exists only in the JSON
        nobody opened."""
        empty = self._repo()
        no_match = self._repo()
        self._commit(no_match, "implement checkout", {"src/checkout.py": "pass\n"})
        found = self._repo()
        self._commit(found, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        not_repo = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, not_repo, True)

        texts = {name: run_cli("--path", str(path)).stdout
                 for name, path in (("empty", empty), ("no_match", no_match),
                                    ("found", found), ("not_repo", not_repo))}
        for text in texts.values():
            self.assertIn("Harness change history", text)
        self.assertIn("not a git repository", texts["not_repo"])
        self.assertIn("no commits", texts["empty"])
        self.assertIn("no commit has touched", texts["no_match"])
        self.assertIn("add the review skill", texts["found"])
        self.assertEqual(len(set(texts.values())), 4)

    def test_the_text_report_names_the_paths_it_searched(self):
        """The report is bounded by a path list, and a reader who does not
        know the bounds reads "nothing found" as "nothing happened"."""
        repo = self._repo()
        self._commit(repo, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        text = run_cli("--path", str(repo)).stdout
        self.assertIn(".claude/hooks", text)
        self.assertIn("CLAUDE.md", text)

    def test_every_component_discovery_finds_is_a_path_history_searches(self):
        """Two definitions of "harness component" -- one that inventories the
        disk, one that searches history -- drift apart silently, and the
        symptom is a whole component type quietly missing from the record.
        The fixture is the independent source here: it was built to exercise
        discovery, not this list."""
        fixture = REPO_ROOT / "tests" / "fixtures" / "good-harness"
        discovered = [
            *hc.claude_md_paths(fixture),
            *hc.iter_rule_files(fixture),
            *hc.iter_agent_files(fixture),
            *hc.iter_workflow_files(fixture),
            *hc.settings_paths(fixture),
            *(d / "SKILL.md" for d in hc.iter_skill_dirs(fixture)),
        ]
        self.assertTrue(discovered, "the fixture stopped exercising discovery")
        searched = ah.harness_history_paths(fixture)
        for path in discovered:
            rel = Path(path).relative_to(fixture).as_posix()
            self.assertTrue(
                any(rel == s or rel.startswith(s + "/") for s in searched),
                f"{rel} is inventoried but its history is never searched",
            )

    def test_the_scope_states_what_the_history_cannot_see(self):
        """The history is about to become the record, and a record whose
        limits are unstated is read as complete. Each of these is a way a
        real decision leaves no trace the search can reach."""
        blind = " ".join(ah.SCOPE["does_not_detect"]).lower()
        self.assertIn("did not change any file", blind)
        self.assertIn("pull request", blind)
        self.assertIn("revert", blind)
        detects = " ".join(ah.SCOPE["detects"]).lower()
        self.assertIn("commits that changed a harness component", detects)


if __name__ == "__main__":
    unittest.main(verbosity=2)
