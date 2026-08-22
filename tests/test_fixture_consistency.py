#!/usr/bin/env python3
"""Consistency tests for tests/fixtures/good-harness.

    python3 -m unittest discover -s tests -q

good-harness is not just a lint input. It is the canonical example a
generated harness gets modelled on, so a false claim inside it propagates
into every harness this skill writes -- the same reasoning that made v4 fix
`scripts/run.py` rather than only the reference prose.

The specific false claim these tests exist to keep out: CLAUDE.md said "A
PreToolUse hook blocks commits containing raw SQL strings" while the only
PreToolUse hook checked `*.env|*package-lock.json` file paths and never
looked at a commit. Nothing contrasted the sentence against the hook,
because "does this prose describe this shell script" has no lexical signal
to key on -- until the fixture's CLAUDE.md is required to name the script
it is describing. Then the contrast is a path lookup.

stdlib unittest only, no pytest.
"""

import json
import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "good-harness"
CLAUDE_MD = FIXTURE / "CLAUDE.md"
SETTINGS = FIXTURE / ".claude" / "settings.json"

HOOK_PATH_RE = re.compile(r"\.claude/hooks/[A-Za-z0-9_.-]+\.sh")
HOOK_WORD_RE = re.compile(r"\bhooks?\b", re.IGNORECASE)


def sentences(text):
    for chunk in re.split(r"(?<=[.!?])\s+|\n", text):
        chunk = chunk.strip()
        if chunk:
            yield chunk


def wired_hook_commands():
    data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    for groups in data.get("hooks", {}).values():
        for group in groups:
            for entry in group.get("hooks", []):
                command = entry.get("command", "")
                if command:
                    yield command


class HookProseIsAnchoredToTheHookTests(unittest.TestCase):
    """A sentence describing a hook must name the script that implements it.

    Not a style rule. "A PreToolUse hook blocks X" is a claim about code
    with nothing to check it against, and that is exactly the shape that
    went false here. Naming the file turns the claim into a pointer, and a
    pointer either resolves or it doesn't."""

    def setUp(self):
        self.text = CLAUDE_MD.read_text(encoding="utf-8")

    def test_every_hook_sentence_names_the_script_it_describes(self):
        for sentence in sentences(self.text):
            if HOOK_WORD_RE.search(sentence):
                self.assertRegex(
                    sentence, HOOK_PATH_RE,
                    "a hook claim with no script path cannot be checked against "
                    f"the hook: {sentence!r}",
                )

    def test_every_named_script_exists(self):
        named = set(HOOK_PATH_RE.findall(self.text))
        self.assertTrue(named, "the fixture should describe at least one hook")
        for path in sorted(named):
            self.assertTrue((FIXTURE / path).is_file(), path)

    def test_every_named_script_is_wired_in_settings(self):
        commands = list(wired_hook_commands())
        for path in sorted(set(HOOK_PATH_RE.findall(self.text))):
            self.assertTrue(
                any(path in command for command in commands),
                f"{path} is described in CLAUDE.md but not wired in settings.json",
            )


class WiredHooksAreRunnableTests(unittest.TestCase):
    """test_hook.py executes these for real, and a non-executable hook fails
    at the moment it was supposed to enforce something."""

    def test_every_wired_script_exists_and_is_executable(self):
        for command in wired_hook_commands():
            rel = command.replace("${CLAUDE_PROJECT_DIR}/", "")
            path = FIXTURE / rel
            self.assertTrue(path.is_file(), command)
            self.assertTrue(os.access(path, os.X_OK), f"{command} is not executable")


class BashWritePathIsCoveredTests(unittest.TestCase):
    """references/hooks.md documents that a Bash-driven edit (`sed -i`,
    `echo >> file`) never trips an `Edit|Write` matcher, and SKILL.md's
    layer-routing table sells a hook plus a permission rule as the way to
    make a must-never guarantee real. The canonical fixture demonstrated
    that guarantee in exactly the form its own gotcha list calls incomplete.

    Whichever compensation the fixture picks, it has to pick one."""

    def setUp(self):
        self.data = json.loads(SETTINGS.read_text(encoding="utf-8"))

    def _pretooluse_matchers(self):
        return [g.get("matcher", "") for g in self.data.get("hooks", {}).get("PreToolUse", [])]

    def test_the_protective_hook_sees_bash(self):
        self.assertTrue(
            any("Bash" in m for m in self._pretooluse_matchers()),
            "an Edit|Write-only matcher leaves the Bash write path open",
        )

    def test_the_hook_script_inspects_the_bash_command(self):
        script = (FIXTURE / ".claude" / "hooks" / "protect-files.sh").read_text(encoding="utf-8")
        self.assertIn("command", script, "matching Bash without reading tool_input.command is a no-op")


class AgentWritePathIsStatedTests(unittest.TestCase):
    """An agent body replaces the system prompt entirely, so it is the only
    place the boundary can be stated -- and `tools:` does not state it for
    you when the role keeps `Bash`."""

    def test_an_agent_that_keeps_bash_says_what_bash_is_for(self):
        for path in sorted((FIXTURE / ".claude" / "agents").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            tools = re.search(r"^tools:\s*(.+)$", text, re.MULTILINE)
            if tools and re.search(r"\bBash\b", tools.group(1)):
                self.assertIn(
                    "`Bash`", text.split("---", 2)[-1],
                    f"{path.name} grants Bash without telling the agent what it is for",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
