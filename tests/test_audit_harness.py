#!/usr/bin/env python3
"""Self-test for audit_harness.py against tests/fixtures/{good,bad}-harness.

    python3 tests/test_audit_harness.py
"""

import contextlib
import io
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
        self.assertIn("Does not detect:", text)
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

    def test_no_hygiene_problems(self):
        h = self.result["hygiene"]
        self.assertEqual(h["dead_link_count"], 0)
        self.assertEqual(h["duplicate_agent_name_count"], 0)
        self.assertEqual(h["non_executable_hook_count"], 0)
        self.assertEqual(h["total_lint_errors"], 0)

    def test_reports_facts_not_a_mode(self):
        """The audit says what is on disk and what the history holds; which
        kind of pass to run is the interviewer's call, made with the user."""
        self.assertNotIn("suggested_mode", self.result)
        self.assertIn("harness_history", self.result)
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


class EmptyProjectAuditTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmpdir = tempfile.mkdtemp()
        self.root = Path(self.tmpdir)
        self.result = ah.run(self.root)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_an_empty_project_has_no_components(self):
        inv = self.result["inventory"]
        self.assertFalse(any(inv[k] for k in ("claude_md", "rules", "skills", "agents", "workflows", "settings")))
        self.assertNotIn("suggested_mode", self.result)

    def test_empty_inventory(self):
        inv = self.result["inventory"]
        self.assertEqual(inv["claude_md"], [])
        self.assertEqual(inv["rules"], [])
        self.assertEqual(inv["skills"], [])


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

    def test_the_text_report_distinguishes_every_empty_outcome(self):
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
        self.assertIn("not a git repository", texts["not_repo"].lower())
        self.assertIn("no commits yet", texts["empty"].lower())
        self.assertIn("touched a harness component", texts["no_match"].lower())
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
        discovery, not this list.

        Its reach stops at the discovery functions named below, so a source
        reached another way -- a plugin manifest's roots, a file CLAUDE.md
        imports -- is held by its own behavioural test instead."""
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

    def test_a_git_call_that_cannot_run_is_reported_not_raised(self):
        """`_git` returns None when git cannot run at all -- a missing
        binary, or a log that outran its timeout, which a large history
        really can. An audit that raises there takes the inventory down
        with it, and the inventory is the part that still worked."""
        repo = self._repo()
        self._commit(repo, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        real = ah._git

        def every_log_fails(cwd, *args):
            # Keyed on the call, not on where its arguments sit: git-level
            # options come before the subcommand, so a positional check
            # stops standing for "this is the log call" the moment one is added.
            return None if "log" in args else real(cwd, *args)

        ah._git = every_log_fails
        self.addCleanup(setattr, ah, "_git", real)
        history = ah.run(repo)["harness_history"]
        self.assertEqual(history["status"], "unavailable")
        self.assertEqual(history["commits"], [])
        rendered = io.StringIO()
        with contextlib.redirect_stdout(rendered):
            ah.print_markdown(ah.run(repo))
        self.assertIn("could not be read", rendered.getvalue())

    def test_a_file_claude_md_imports_is_searched_too(self):
        """`@file` pulls another file into every session, so editing it
        changes what the harness says without touching a path on the fixed
        list. The reference recommends exactly this arrangement for a repo
        that keeps one source of truth for several agents."""
        repo = self._repo()
        self._commit(repo, "point CLAUDE.md at the shared instructions", {
            "CLAUDE.md": "@AGENTS.md\n",
            "AGENTS.md": "build with make\n",
        })
        self._commit(repo, "change how the project is built", {"AGENTS.md": "build with bazel\n"})
        subjects = [c["subject"] for c in ah.run(repo)["harness_history"]["commits"]]
        self.assertIn("change how the project is built", subjects)

    def test_a_harness_spec_left_by_an_earlier_version_is_searched(self):
        """A project set up before this tool kept its record in git has one
        file holding every decision it ever made. Dropping that path from
        the search does not retire the file -- it retires the history."""
        repo = self._repo()
        self._commit(repo, "record why the hook was declined",
                     {".claude/harness-spec.md": "# Harness Spec\n"})
        subjects = [c["subject"] for c in ah.run(repo)["harness_history"]["commits"]]
        self.assertEqual(subjects, ["record why the hook was declined"])

    def test_a_shallow_clone_says_its_history_is_incomplete(self):
        """At a shallow boundary git treats the cut-off commit as a root, so
        every file in it reads as an addition -- the report would credit a
        commit with creating a harness it merely inherited, and would say
        "no commit touched" for anything below the cut. Truncation is about
        this report; incompleteness is about the clone, and they are not the
        same disclosure."""
        origin = self._repo()
        self._commit(origin, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        self._commit(origin, "tune the review skill", {".claude/skills/review/SKILL.md": "y\n"})
        clone = Path(tempfile.mkdtemp()) / "shallow"
        self.addCleanup(shutil.rmtree, clone.parent, True)
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{origin}", str(clone)],
                       capture_output=True, text=True, check=True)
        history = ah.run(clone)["harness_history"]
        self.assertTrue(history["shallow"])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            ah.print_markdown(ah.run(clone))
        self.assertIn("shallow", out.getvalue().lower())

    def test_a_full_repository_is_not_marked_shallow(self):
        repo = self._repo()
        self._commit(repo, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        self.assertFalse(ah.run(repo)["harness_history"]["shallow"])

    def test_a_merge_that_brought_in_a_harness_change_names_its_paths(self):
        """Measured on this repository: five merges match the pathspec and
        all five list no files, because a merge is not diffed by default.
        They still consume the cap, so a busy project spends its report on
        entries that say a change happened and not what changed."""
        repo = self._repo()
        self._commit(repo, "base", {"README.md": "x\n"})
        self._git(repo, "checkout", "-q", "-b", "side")
        self._commit(repo, "add the review skill on a branch", {".claude/skills/review/SKILL.md": "x\n"})
        self._git(repo, "checkout", "-q", "main")
        self._commit(repo, "unrelated main work", {"src/app.py": "pass\n"})
        self._git(repo, "merge", "-q", "--no-ff", "-m", "merge the review skill", "side")
        merge = ah.run(repo)["harness_history"]["commits"][0]
        self.assertEqual(merge["subject"], "merge the review skill")
        self.assertEqual(merge["matched"], [".claude/skills/review/SKILL.md"])

    def test_a_declared_skills_root_is_searched_after_its_last_skill_is_deleted(self):
        """Deleting the last skill under a declared root removes the
        directory, and a path list built from what exists now loses exactly
        the commit that removed it -- the decision a later pass most needs
        not to re-litigate."""
        repo = self._repo()
        (repo / ".claude-plugin").mkdir(parents=True)
        (repo / ".claude-plugin" / "plugin.json").write_text('{"skills": "./packaged"}\n')
        self._commit(repo, "ship the packaged skill", {"packaged/only/SKILL.md": "x\n"})
        shutil.rmtree(repo / "packaged")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", "retire the packaged skill")
        subjects = [c["subject"] for c in ah.run(repo)["harness_history"]["commits"]]
        self.assertEqual(subjects, ["retire the packaged skill", "ship the packaged skill"])

    def test_git_being_unavailable_is_not_reported_as_having_no_repository(self):
        """"There is no repository here" is a fact about the project; "git
        did not run" is a fact about this machine. Reported as the first, a
        broken install tells every project it has nowhere to keep a record."""
        repo = self._repo()
        self._commit(repo, "add the review skill", {".claude/skills/review/SKILL.md": "x\n"})
        self.addCleanup(setattr, ah, "_git", ah._git)
        ah._git = lambda cwd, *args: None
        self.assertEqual(ah.run(repo)["harness_history"]["status"], "unavailable")

    def test_the_absence_messages_report_the_search_not_a_conclusion(self):
        """A project can keep its reasons somewhere this search cannot
        reach. Saying the decisions do not exist, rather than that no commit
        matched, is how a pass talks a user into deciding it all again."""
        rendered = []
        for status in ("not_a_repository", "no_history", "no_match"):
            out = io.StringIO()
            result = ah.run(REPO_ROOT / "tests" / "fixtures" / "good-harness")
            result["harness_history"] = {"status": status, "commits": [], "truncated": False,
                                         "shallow": False, "paths": []}
            with contextlib.redirect_stdout(out):
                ah.print_markdown(result)
            section = out.getvalue().split("## Harness change history")[1].split("##")[0]
            rendered.append(section)
            for invented in ("survive only as long", "nowhere a past decision",
                            "was not recorded", "no durable record"):
                self.assertNotIn(invented, section, status)
        self.assertEqual(len(set(rendered)), 3)

    def test_subjects_and_paths_survive_bytes_that_would_frame_a_record(self):
        """The framing bytes have to be ones the data cannot contain. A
        subject may hold any byte but NUL, and a path may hold any byte but
        NUL and `/` -- so NUL is the only safe frame, and `%x00` supplies it
        from inside git rather than through argv, which is where the null
        byte is actually forbidden. Without `-z`, git also hands back its
        display form: a Korean path arrives octal-escaped and a quoted one
        keeps its quotes, so `matched` would name files that do not exist."""
        repo = self._repo()
        subject = "keep \x1f and \x1e literal"
        self._commit(repo, subject, {
            ".claude/skills/\ud55c\uae00/SKILL.md": "x\n",
            '.claude/rules/we"ird.md': "y\n",
        })
        commit = ah.run(repo)["harness_history"]["commits"][0]
        self.assertEqual(commit["subject"], subject)
        self.assertEqual(sorted(commit["matched"]), [
            '.claude/rules/we"ird.md',
            ".claude/skills/\ud55c\uae00/SKILL.md",
        ])

    def test_a_skills_root_whose_name_looks_like_pathspec_magic_is_matched_literally(self):
        """A plugin manifest names a directory; git reads a pathspec. A name
        starting with `:` is magic to git, and the failure is silent -- the
        search returns nothing and the report says no commit touched a
        component, which is the one answer a reader will act on."""
        repo = self._repo()
        (repo / ".claude-plugin").mkdir(parents=True)
        (repo / ".claude-plugin" / "plugin.json").write_text('{"skills": "./:(top)odd"}\n')
        self._commit(repo, "ship the packaged skill", {":(top)odd/packaged/SKILL.md": "x\n"})
        subjects = [c["subject"] for c in ah.run(repo)["harness_history"]["commits"]]
        self.assertEqual(subjects, ["ship the packaged skill"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
