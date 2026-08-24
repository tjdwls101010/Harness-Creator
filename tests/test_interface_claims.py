#!/usr/bin/env python3
"""Claims the package makes about its own code, checked against the code.

    python3 -m unittest discover -s tests -q

v5 fixed four prose statements the code contradicted. An independent audit
run afterwards, from a blank slate, found more -- and these differ in kind
from the first four: each one is a claim the package *acts on*. A delivery
gate that never fails, a guide that teaches a shape its own validator
rejects, a `--help` line describing behaviour nothing implements.

The pattern that produces all of them is the same one v5's doctrine names:
a sentence about how a tool currently behaves, with nothing contrasting it
against the tool.

stdlib unittest only, no pytest.
"""

import ast
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator"
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import harness_common as hc  # noqa: E402
import validate_harness as vh  # noqa: E402

TEST_HOOK = SCRIPTS_DIR / "test_hook.py"


def run_test_hook(*args):
    proc = subprocess.run(
        [sys.executable, str(TEST_HOOK), *args], capture_output=True, text=True, timeout=60
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestHookIsADeliveryGateTests(unittest.TestCase):
    """SKILL.md's Hard line 2 says a generated hook is not finished until
    `test_hook.py` passes against it. "Passes" had no mechanical meaning:
    the script returned 0 whatever the hook did, so a hook that exits 1 --
    which references/hooks.md documents as the silent-no-op failure, the
    single most common hook mistake -- cleared the gate.

    Exit 2 is deliberately NOT a failure here. A blocking hook exits 2 on
    the path it is meant to block, and that is the hook working."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def _hook(self, name, body):
        path = self.tmp / name
        path.write_text("#!/bin/bash\ncat >/dev/null\n" + body, encoding="utf-8")
        path.chmod(0o755)
        return str(path)

    def test_a_hook_that_exits_1_fails_the_gate(self):
        code, out = run_test_hook("--command", self._hook("one.sh", "exit 1"), "--event", "PreToolUse")
        self.assertNotEqual(code, 0, out)

    def test_a_hook_that_blocks_with_exit_2_passes(self):
        code, out = run_test_hook(
            "--command", self._hook("two.sh", 'echo "nope" >&2\nexit 2'), "--event", "PreToolUse"
        )
        self.assertEqual(code, 0, out)

    def test_a_hook_that_exits_0_passes(self):
        code, out = run_test_hook("--command", self._hook("zero.sh", "exit 0"), "--event", "PreToolUse")
        self.assertEqual(code, 0, out)

    def test_a_hook_that_cannot_run_fails_the_gate(self):
        path = self.tmp / "nonexec.sh"
        path.write_text("#!/bin/bash\nexit 0\n", encoding="utf-8")
        path.chmod(0o644)
        code, out = run_test_hook("--command", str(path), "--event", "PreToolUse")
        self.assertNotEqual(code, 0, out)

    def test_executing_nothing_fails_the_gate(self):
        """The worst case: reporting a pass having verified nothing. A
        matcher that silently matches no tool is a documented failure mode,
        not a clean run."""
        settings = self.tmp / "settings.json"
        settings.write_text(
            '{"hooks": {"PreToolUse": [{"matcher": "mcp__server", "hooks": '
            '[{"type": "command", "command": "/bin/true", "args": []}]}]}}',
            encoding="utf-8",
        )
        code, out = run_test_hook("--settings", str(settings), "--event", "PreToolUse", "--tool", "Bash")
        self.assertNotEqual(code, 0, out)

    def test_matrix_is_inspection_and_always_succeeds(self):
        settings = self.tmp / "settings.json"
        settings.write_text('{"hooks": {"PreToolUse": []}}', encoding="utf-8")
        code, out = run_test_hook("--settings", str(settings), "--matrix")
        self.assertEqual(code, 0, out)


class NestedFrontmatterTests(unittest.TestCase):
    """references/hooks.md, skills.md and agents.md all teach a `hooks:`
    block in a skill's or agent's own frontmatter -- and the parser gave up
    on the whole file when it saw one, so validate_harness.py reported
    "frontmatter did not parse ... auto-triggering is silently dead" on a
    component built exactly as the guide describes. Following the guide
    could not clear the delivery gate.

    The parser's rule stands: never guess a structure it does not
    understand. Recording the key as present-but-unparsed keeps that
    promise without discarding the fields around it."""

    NESTED = textwrap.dedent("""\
        ---
        name: deploy
        description: Deploys the thing. Use when the user asks to deploy.
        hooks:
          PreToolUse:
            - matcher: Bash
              hooks:
                - type: command
                  command: ./guard.sh
        ---
        Body here.
        """)

    def test_the_surrounding_fields_still_parse(self):
        fm = hc.parse_frontmatter(self.NESTED)
        self.assertTrue(fm.ok, fm.warnings)
        self.assertEqual(fm.data["name"], "deploy")
        self.assertIn("Use when", fm.data["description"])

    def test_the_nested_key_is_marked_unparsed_rather_than_guessed(self):
        fm = hc.parse_frontmatter(self.NESTED)
        self.assertIs(fm.data["hooks"], hc.UNPARSED_BLOCK)
        self.assertTrue(any("hooks" in w for w in fm.warnings), fm.warnings)

    def test_the_unparsed_block_keeps_its_raw_lines(self):
        """v6. Refusing to guess at a nested shape and throwing the text away
        are different things, and this parser now only does the first. The
        assertion above is the half that must not change: `data` still says
        nothing about what is in there, so no caller can mistake raw lines for
        a parsed value."""
        fm = hc.parse_frontmatter(self.NESTED)
        raw = fm.raw_blocks["hooks"]
        self.assertTrue(raw)
        self.assertTrue(all(line.startswith((" ", "\t")) for line in raw if line.strip()))

    def test_a_skill_following_the_guide_clears_the_lint(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        skill = tmp / ".claude" / "skills" / "deploy"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(self.NESTED, encoding="utf-8")
        findings, _ = vh.run(tmp, strict=False)
        self.assertEqual(
            [f for f in findings if "frontmatter did not parse" in f[2]], []
        )

    def test_a_genuinely_unparseable_file_still_fails(self):
        self.assertFalse(hc.parse_frontmatter("---\nname: x\n").ok)
        self.assertFalse(hc.parse_frontmatter("---\ntools: [Read]\n---\n").ok)


class RunE2eModelHelpTests(unittest.TestCase):
    """`--model`'s help said "default: whatever the invoking session uses".
    Nothing reads or forwards the parent session's model; omitting the flag
    lets the spawned `claude` apply its own default. e2e's entire premise is
    behavioural fidelity, so a caller who believed the help would have been
    measuring a different model than the user runs."""

    def _model_help(self):
        tree = ast.parse((SCRIPTS_DIR / "run_e2e.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument":
                if node.args and getattr(node.args[0], "value", None) == "--model":
                    for kw in node.keywords:
                        if kw.arg == "help":
                            return kw.value.value
        self.fail("run_e2e.py declares no --model help")

    def test_nothing_forwards_the_parent_session_model(self):
        source = (SCRIPTS_DIR / "run_e2e.py").read_text(encoding="utf-8")
        self.assertNotIn("CLAUDE_MODEL", source)
        self.assertNotIn("ANTHROPIC_MODEL", source)

    def test_the_help_does_not_promise_the_session_model(self):
        self.assertNotIn("invoking session", self._model_help())

    def test_the_help_says_who_supplies_the_default(self):
        self.assertIn("claude", self._model_help())


class PluginSkillDiscoveryTests(unittest.TestCase):
    """A plugin's skills live at `./skills` unless plugin.json says
    otherwise, and discovery only ever looked at `.claude/skills/`. A plugin
    laid out the default way had every one of its skills skipped -- silently,
    reported as a clean run."""

    def _plugin(self, skills_field, skills_rel):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / ".claude-plugin").mkdir(parents=True)
        manifest = '{"name": "p", "version": "1.0.0"'
        if skills_field is not None:
            manifest += f', "skills": "{skills_field}"'
        (tmp / ".claude-plugin" / "plugin.json").write_text(manifest + "}", encoding="utf-8")
        skill = tmp / skills_rel / "leaky"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: leaky\ndescription: A skill. Use when testing discovery.\n---\n"
            "See references/missing.md for detail.\n",
            encoding="utf-8",
        )
        return tmp

    def test_the_default_skills_root_is_discovered(self):
        findings, _ = vh.run(self._plugin(None, "skills"), strict=False)
        self.assertTrue(
            any("references/missing.md" in f[2] for f in findings),
            f"a plugin's default ./skills root went unlinted: {findings}",
        )

    def test_a_custom_skills_root_is_discovered(self):
        findings, _ = vh.run(self._plugin("./bundles/skills", "bundles/skills"), strict=False)
        self.assertTrue(
            any("references/missing.md" in f[2] for f in findings), findings
        )

    def test_a_repo_with_no_manifest_is_unaffected(self):
        """`skills/` is an ordinary directory name. Without a plugin
        manifest it means nothing, and treating it as a skills root would
        fire on any project that happens to have one."""
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        skill = tmp / "skills" / "not-a-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: x\ndescription: y\n---\n", encoding="utf-8")
        self.assertEqual(list(hc.iter_skill_dirs(tmp)), [])


class ReferenceTraversalTests(unittest.TestCase):
    """Reference-to-reference pointers were scanned only in `*.md`, while a
    reference file is whatever the skill bundles. A dead pointer inside
    `references/guide.txt` was invisible."""

    def test_a_dead_pointer_in_a_txt_reference_is_caught(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        refs = tmp / ".claude" / "skills" / "s" / "references"
        refs.mkdir(parents=True)
        (refs.parent / "SKILL.md").write_text(
            "---\nname: s\ndescription: A skill. Use when testing traversal.\n---\nSee references/guide.txt.\n",
            encoding="utf-8",
        )
        (refs / "guide.txt").write_text("Next, read references/missing.md.\n", encoding="utf-8")
        findings, _ = vh.run(tmp, strict=False)
        self.assertTrue(
            any("references/missing.md" in f[2] for f in findings), findings
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
