#!/usr/bin/env python3
"""The five bundled CLIs own what is valid, what they do and what they print;
the skill's prose owns when to run them, why, and what they cost.

    python3 -m unittest discover -s tests -p "test_script_ownership.py" -q

Two shapes of leak are pinned here. Policy in `--help` (consent, ordering,
"before any interview") is a copy of SKILL.md that goes stale on its own.
Development history in a docstring ("previously", "used to", a date) is
written for the author and printed to the user. stdlib unittest only.
"""

import ast
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
SCRIPTS = sorted(SCRIPTS_DIR.glob("*.py"))

# Vocabulary that marks policy or history. Case-insensitive, matched against
# module docstrings, every function docstring, every `help=` and
# `description=` string, and comments.
LEAK_WORDS = (
    "consent",
    "before any interview",
    "before ANY",
    "immediately after",
    "should pass this before",
    "previously",
    "used to",
    "carried over",
    "caught two",
    "2026-08-22",
    "skill-creator",
    "interview.md",
    "re-entry",
    "Hard line",
)


def run(script, *args, **kw):
    return subprocess.run([sys.executable, str(SCRIPTS_DIR / script), *args],
                          capture_output=True, text=True, timeout=60, **kw)


def env_with_fake_claude():
    """run_e2e.py spawns `claude`; a usage-error test must never reach a real
    session, so PATH gets a `claude` that refuses to run."""
    import os, stat, tempfile
    bin_dir = Path(tempfile.mkdtemp(prefix="fake-claude-"))
    fake = bin_dir / "claude"
    fake.write_text("#!/bin/sh\necho 'fake claude must not run' >&2\nexit 97\n", encoding="utf-8")
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    return env


def user_facing_strings(path):
    """(kind, text) for every string the user can read: module and function
    docstrings, `help=`/`description=` keywords, and comments."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    out = []
    doc = ast.get_docstring(tree)
    if doc:
        out.append(("module docstring", doc))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            d = ast.get_docstring(node)
            if d:
                out.append((f"docstring of {node.name}", d))
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg in ("help", "description") and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    out.append((f"{kw.arg}= at line {node.lineno}", kw.value.value))
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#") and not stripped.startswith("#!"):
            out.append((f"comment at line {i}", stripped))
    return out


class NoPolicyOrHistoryInScriptsTests(unittest.TestCase):
    def test_no_leak_vocabulary_anywhere_a_user_reads(self):
        leaks = []
        for path in SCRIPTS:
            for kind, text in user_facing_strings(path):
                for word in LEAK_WORDS:
                    if word.lower() in text.lower():
                        leaks.append(f"{path.name}: {kind} contains {word!r}")
        self.assertEqual(leaks, [])

    def test_every_help_still_says_what_the_script_does(self):
        for name in ("audit_harness.py", "validate_harness.py", "hook_event.py", "test_hook.py", "run_e2e.py"):
            proc = run(name, "--help")
            self.assertEqual(proc.returncode, 0, name)
            self.assertGreater(len(proc.stdout.split()), 40, name)


class HonestApproximationTests(unittest.TestCase):
    """test_hook.py approximates a JavaScript RegExp with Python `re`, and
    its input is a sample it built. It may say so; it may not say `exactly`."""

    def test_docstrings_do_not_claim_exactness(self):
        source = (SCRIPTS_DIR / "test_hook.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        texts = [ast.get_docstring(tree) or ""] + [
            ast.get_docstring(n) or "" for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))
        ]
        joined = "\n".join(texts)
        self.assertNotRegex(joined, r"\bexactly\b")
        self.assertIn("approximat", joined.lower())
        self.assertIn("RegExp", joined)

    def test_output_and_json_say_a_real_session_is_final(self):
        hook = SCRIPTS_DIR.parent.parent.parent.parent / "tests" / "fixtures" / "good-harness" / ".claude" / "hooks" / "protect-files.sh"
        proc = run("test_hook.py", "--command", str(hook), "--event", "PreToolUse", "--tool", "Edit")
        self.assertIn("real session", proc.stdout.lower())
        proc = run("test_hook.py", "--command", str(hook), "--event", "PreToolUse", "--tool", "Edit", "--json")
        self.assertIn("real session", proc.stdout.lower())


class UsageErrorTests(unittest.TestCase):
    """Mode combinations that cannot mean anything are refused by argparse,
    with exit 2, rather than half-handled."""

    def test_test_hook_rejects_an_unknown_event(self):
        proc = run("test_hook.py", "--command", "/bin/true", "--event", "Bogus")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("invalid choice", proc.stderr)
        self.assertIn("PreToolUse", proc.stderr)

    def test_test_hook_settings_and_command_are_exclusive_and_one_is_required(self):
        settings = REPO_ROOT / "tests" / "fixtures" / "good-harness" / ".claude" / "settings.json"
        self.assertEqual(run("test_hook.py", "--settings", str(settings), "--command", "/bin/true", "--event", "PreToolUse").returncode, 2)
        self.assertEqual(run("test_hook.py", "--event", "PreToolUse").returncode, 2)

    def test_test_hook_matrix_needs_settings(self):
        self.assertEqual(run("test_hook.py", "--matrix", "--command", "/bin/true").returncode, 2)

    def test_hook_event_event_and_list_are_exclusive_and_one_is_required(self):
        self.assertEqual(run("hook_event.py").returncode, 2)
        self.assertEqual(run("hook_event.py", "--event", "Stop", "--list").returncode, 2)
        self.assertEqual(run("hook_event.py", "--list").returncode, 0)

    def test_run_e2e_prompt_sources_are_exclusive_and_one_is_required(self):
        project = REPO_ROOT / "tests" / "fixtures" / "good-harness"
        env = env_with_fake_claude()
        self.assertEqual(run("run_e2e.py", "--project", str(project), env=env).returncode, 2)
        proc = run("run_e2e.py", "--project", str(project), "--prompt", "x", "--prompt-file", "y", env=env)
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("fake claude must not run", proc.stdout + proc.stderr)

    def test_run_e2e_keep_isolated_needs_isolate(self):
        project = REPO_ROOT / "tests" / "fixtures" / "good-harness"
        proc = run("run_e2e.py", "--project", str(project), "--prompt", "x", "--keep-isolated", env=env_with_fake_claude())
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--isolate", proc.stderr)
        self.assertNotIn("fake claude must not run", proc.stdout + proc.stderr)

    def test_audit_template_and_path_are_exclusive(self):
        self.assertEqual(run("audit_harness.py", "--template", "--path", ".").returncode, 2)
        self.assertEqual(run("audit_harness.py").returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
