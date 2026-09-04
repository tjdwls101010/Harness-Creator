#!/usr/bin/env python3
"""Shape checks V06-V14 in validate_harness.py (agents, workflows, rules,
CLAUDE.local.md), plus the workflow name collision -- which audit_harness.py
reports without a code, because it is a fact about two directories rather
than a shape inside a file. The plan called it V16; no such finding exists.

    python3 -m unittest discover -s tests -p "test_component_shapes.py" -q

Positive fixture: tests/fixtures/component-shapes, one occurrence per code.
Near misses: near-miss-harness, good-harness, this repo. A finding reports a
shape the docs say cannot mean what it looks like; it predicts no verdict.

Sources re-read live on 2026-09-02 (https://code.claude.com/docs/en/sub-agents,
https://code.claude.com/docs/en/hooks, https://code.claude.com/docs/en/workflows,
https://code.claude.com/docs/en/memory, Agent SDK TypeScript reference);
excerpts sit on each test. stdlib unittest only.
"""

import json
import os
import shutil
import subprocess
import inspect
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import audit_harness as ah  # noqa: E402
import validate_harness as vh  # noqa: E402

POSITIVE = REPO_ROOT / "tests" / "fixtures" / "component-shapes"
NEAR_MISSES = [
    REPO_ROOT / "tests" / "fixtures" / "near-miss-harness",
    REPO_ROOT / "tests" / "fixtures" / "good-harness",
    REPO_ROOT,
]
CODES = ("V06", "V07", "V08", "V09", "V10", "V11", "V12", "V13")


def by_code(findings):
    out = {}
    for f in findings:
        code = getattr(f, "code", None)
        if code:
            out.setdefault(code, []).append(f)
    return out


class PositiveFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings, cls.exit_code = vh.run(POSITIVE, strict=False)
        cls.coded = by_code(cls.findings)

    def _one(self, code, level):
        hits = self.coded.get(code, [])
        self.assertEqual(len(hits), 1, f"{code}: {hits or self.findings}")
        self.assertEqual(hits[0][0], level, code)
        return hits[0][2]

    def test_v06_ui_bound_tool_in_agent_tools(self):
        """sub-agents, Available tools: "The following tools depend on the main
        conversation's UI or session state and aren't available to subagents,
        even when listed in the `tools` field: `AskUserQuestion`,
        `EnterPlanMode`, `ExitPlanMode`, unless the subagent's `permissionMode`
        is `plan`, `ScheduleWakeup`, `WaitForMcpServers`." """
        m = self._one("V06", "E")
        self.assertIn("AskUserQuestion", m)

    def test_v07_once_true_outside_skill_frontmatter(self):
        """hooks, handler fields: "`once` -- If `true`, runs once per session
        then is removed. Only honored for hooks declared in skill frontmatter;
        ignored in settings files and agent frontmatter." """
        m = self._one("V07", "E")
        self.assertIn("once", m)
        self.assertIn("skill", m.lower())

    def test_v08_memory_re_enables_writes_on_a_read_only_allowlist(self):
        """sub-agents, memory: "When memory is enabled: ... Read, Write, and
        Edit tools are automatically enabled so the subagent can manage its
        memory files." """
        m = self._one("V08", "W")
        self.assertIn("memory", m)
        self.assertIn("Write", m)

    def test_v09_meta_without_description_or_not_a_literal(self):
        """Agent SDK TypeScript reference, Workflow tool: "Must begin with
        `export const meta = { name, description }` as a literal". The
        workflows guide's saved example carries both fields."""
        m = self._one("V09", "E")
        self.assertIn("description", m)

    def test_v10_direct_fs_or_shell_from_the_script(self):
        """workflows, Behavior and limits: "No direct filesystem or shell
        access from the workflow itself -- Agents read, write, and run
        commands. The script coordinates the agents." """
        m = self._one("V10", "E")
        self.assertIn("child_process", m)

    def test_v11_skill_dir_placeholder_in_workflow_source(self):
        """skills, string substitutions: `${CLAUDE_SKILL_DIR}` is substituted
        in skill content and `allowed-tools`. The workflows guide documents
        `args` as the way values reach a script and no substitution there, so
        the literal arrives as text. A warning: absence of documentation is
        not documentation of failure."""
        m = self._one("V11", "W")
        self.assertIn("CLAUDE_SKILL_DIR", m)

    def test_v12_rule_frontmatter_that_does_not_parse(self):
        """memory, rules: a rule's `paths` frontmatter is what scopes it, and a
        block the parser cannot read was previously reported as merely
        "no paths" -- the file's real state (scoped or not) is unknown."""
        m = self._one("V12", "E")
        self.assertIn("frontmatter", m)

    def test_v13_paths_that_is_neither_list_nor_string(self):
        """memory, Path-specific rules: the documented shape is a YAML list
        under `paths:`; the docs show only that form, so anything else is a
        warning, not an error."""
        m = self._one("V13", "W")
        self.assertIn("paths", m)

    def test_no_other_shape_code_fires(self):
        self.assertEqual(set(self.coded), set(CODES))


class WorkflowShapeBoundaryTests(unittest.TestCase):
    """One invalid shape per case, plus valid shapes that look invalid."""

    def _wf(self, source):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        wf = tmp / ".claude" / "workflows"
        wf.mkdir(parents=True)
        (wf / "w.js").write_text(source, encoding="utf-8")
        findings, _ = vh.run(tmp, strict=False)
        return {code: [f[2] for f in fs] for code, fs in by_code(findings).items()}

    GOOD = "export const meta = { name: 'w', description: 'Maps input: value, then more', phases: [{ title: 'A' }] }\n"

    def test_a_literal_meta_with_colons_in_strings_and_a_phases_array_is_fine(self):
        self.assertNotIn("V09", self._wf(self.GOOD + "const r = await agent('go')\nreturn { r }\n"))

    def test_missing_description_alone(self):
        codes = self._wf("export const meta = { name: 'w' }\nreturn {}\n")
        self.assertEqual(len(codes.get("V09", [])), 1)
        self.assertIn("description", codes["V09"][0])

    def test_computed_value_alone(self):
        codes = self._wf("export const meta = { name: config.name, description: 'x' }\nreturn {}\n")
        self.assertEqual(len(codes.get("V09", [])), 1)
        self.assertIn("literal", codes["V09"][0])

    def test_meta_after_another_statement(self):
        codes = self._wf("const NAME = 'w'\nexport const meta = { name: 'w', description: 'x' }\nreturn {}\n")
        self.assertEqual(len(codes.get("V09", [])), 1)
        self.assertIn("first statement", codes["V09"][0])

    def test_a_prompt_that_mentions_fs_is_not_io(self):
        codes = self._wf(self.GOOD + "const r = await agent(\"Use `import fs from 'node:fs'` in the script you write.\")\n// import fs from 'fs'\nreturn { r }\n")
        self.assertNotIn("V10", codes)

    def test_dynamic_import_and_require_are_io(self):
        for line in ("const fs = await import('node:fs')", "const cp = require('child_process')", "execSync('ls')"):
            codes = self._wf(self.GOOD + line + "\nreturn {}\n")
            self.assertEqual(len(codes.get("V10", [])), 1, line)


class ClaudeLocalGitignoreTests(unittest.TestCase):
    """memory, CLAUDE.md locations: "Local instructions -- `./CLAUDE.local.md`
    -- Personal project-specific preferences; add to `.gitignore`". An error
    inside a git repository, where the file will otherwise be committed; a
    warning outside one, where nothing can be inferred."""

    def _project(self, git, ignored, gitignore="CLAUDE.local.md\n", tracked=False):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "CLAUDE.local.md").write_text("# mine\n", encoding="utf-8")
        if git:
            subprocess.run(["git", "init", "-q", str(tmp)], check=True, capture_output=True)
        if ignored:
            (tmp / ".gitignore").write_text(gitignore, encoding="utf-8")
        if tracked:
            subprocess.run(["git", "-C", str(tmp), "add", "-f", "CLAUDE.local.md"], check=True, capture_output=True)
        return tmp

    def test_negation_after_a_broad_pattern_is_read_the_way_git_reads_it(self):
        findings, _ = vh.run(self._project(git=True, ignored=True, gitignore="*.md\n!CLAUDE.local.md\n"), strict=False)
        self.assertEqual(len(by_code(findings).get("V14", [])), 1)

    def test_a_tracked_file_is_an_error_even_when_a_pattern_matches(self):
        findings, _ = vh.run(self._project(git=True, ignored=True, tracked=True), strict=False)
        hits = by_code(findings).get("V14", [])
        self.assertEqual(len(hits), 1)
        self.assertIn("tracked", hits[0][2])

    def test_error_in_a_repo_that_does_not_ignore_it(self):
        findings, _ = vh.run(self._project(git=True, ignored=False), strict=False)
        hits = by_code(findings).get("V14", [])
        self.assertEqual(len(hits), 1, findings)
        self.assertEqual(hits[0][0], "E")

    def test_warning_outside_a_repo(self):
        findings, _ = vh.run(self._project(git=False, ignored=False), strict=False)
        hits = by_code(findings).get("V14", [])
        self.assertEqual(len(hits), 1, findings)
        self.assertEqual(hits[0][0], "W")

    def test_silent_when_ignored(self):
        findings, _ = vh.run(self._project(git=True, ignored=True), strict=False)
        self.assertEqual(by_code(findings).get("V14", []), [])


class WorkflowNameCollisionTests(unittest.TestCase):
    """workflows, save locations: "If a project workflow and a personal
    workflow share a name, the project one runs." The audit reports it under
    user-scope conflicts, keyed on the user config root it already resolves."""

    def setUp(self):
        self.user_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.user_root, True)
        (self.user_root / "workflows").mkdir()
        (self.user_root / "workflows" / "example-workflow.js").write_text(
            "export const meta = { name: 'example-workflow', description: 'personal' }\n", encoding="utf-8"
        )

    def test_a_personal_workflow_with_a_project_name_is_reported(self):
        root = REPO_ROOT / "tests" / "fixtures" / "good-harness"
        inventory = ah.run(root)["inventory"]
        conflicts = ah.check_user_scope_conflicts(root, inventory, self.user_root)
        hits = [c for c in conflicts if "example-workflow" in c]
        self.assertEqual(len(hits), 1, conflicts)
        self.assertIn("project one runs", hits[0])

    def test_no_report_without_a_collision(self):
        root = REPO_ROOT / "tests" / "fixtures" / "good-harness"
        (self.user_root / "workflows" / "example-workflow.js").rename(self.user_root / "workflows" / "other.js")
        inventory = ah.run(root)["inventory"]
        conflicts = ah.check_user_scope_conflicts(root, inventory, self.user_root)
        self.assertEqual([c for c in conflicts if "workflow" in c.lower()], [])


class NearMissTests(unittest.TestCase):
    def test_no_shape_code_fires_on_correct_harnesses(self):
        for root in NEAR_MISSES:
            findings, _ = vh.run(root, strict=False)
            self.assertEqual(set(by_code(findings)) & (set(CODES) | {"V14"}), set(), root.name)

    def test_near_miss_fixture_stays_clean_under_strict(self):
        findings, code = vh.run(NEAR_MISSES[0], strict=True)
        self.assertEqual(findings, [])
        self.assertEqual(code, vh.hc.EXIT_OK)


class LiveDocAgreementTests(unittest.TestCase):
    """Gate B, 2026-09-04. Three checks and one message had drifted from the
    documentation they were derived from. Each assertion below names the
    section it was read against, because the failure mode is not a bug in
    the code -- the code does what it was written to do -- but a product
    that moved underneath a check nobody re-read."""

    def test_v06_covers_every_unconditionally_removed_tool(self):
        """code.claude.com/docs/en/sub-agents#available-tools (2026-09-04)
        lists nine tools stripped from every subagent even when `tools`
        names them. V06 knew four. The two conditional ones (`Agent` at the
        depth limit, `ExitPlanMode` outside plan mode) are deliberately not
        here: a check that cannot see the condition would fire on a correct
        file."""
        for tool in ("AskUserQuestion", "EndConversation", "EnterPlanMode",
                     "ScheduleWakeup", "TaskOutput", "WaitForMcpServers", "Workflow"):
            self.assertIn(tool, vh._UI_BOUND_TOOLS, tool)
        for conditional in ("Agent", "ExitPlanMode"):
            self.assertNotIn(conditional, vh._UI_BOUND_TOOLS, conditional)

    def test_the_if_on_a_non_tool_event_is_reported_as_definite(self):
        """docs/en/hooks#hook-handler-fields: "On other events, a hook with
        `if` set never runs." The old message hedged both ways in one
        sentence -- "can never match" and then "always fires (or never
        does)" -- which is the shape of a check whose author was unsure."""
        root = REPO_ROOT / "tests" / "fixtures" / "bad-harness"
        findings, _ = vh.run(root, strict=False)
        msgs = [m for _, _, m in findings if "'if' is evaluated" in m]
        self.assertTrue(msgs, "no 'if'-on-non-tool-event finding in the fixture")
        for m in msgs:
            self.assertIn("never runs", m)
            self.assertNotIn("always fires", m)

    def test_a_skill_without_a_description_is_not_called_untriggerable(self):
        """docs/en/skills#frontmatter-reference: "If omitted, uses the first
        paragraph of markdown content." So the skill still triggers -- on
        prose written for a human reader, which is worse than a bad
        description and invisible, but not never."""
        src = inspect.getsource(vh)
        self.assertNotIn("can never auto-trigger", src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
