#!/usr/bin/env python3
"""Shape checks V02-V05 and V15 in validate_harness.py: hooks and permissions.

    python3 -m unittest discover -s tests -p "test_hook_permission_shapes.py" -q

Each check has a positive fixture (tests/fixtures/hook-permission-shapes)
that must raise exactly that code once, and near-miss shapes
(tests/fixtures/near-miss-harness, good-harness, this repo) that must raise
neither it nor any new code. A finding here predicts nothing about what a
session decides -- trust, mode, protected paths and cwd all enter that -- it
reports a shape the docs say cannot mean what it looks like it means.

Sources re-read live on 2026-09-02 (https://code.claude.com/docs/en/permissions,
https://code.claude.com/docs/en/hooks); excerpts sit on each test.
stdlib unittest only.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_harness as vh  # noqa: E402

POSITIVE = REPO_ROOT / "tests" / "fixtures" / "hook-permission-shapes"
NEAR_MISSES = [
    REPO_ROOT / "tests" / "fixtures" / "near-miss-harness",
    REPO_ROOT / "tests" / "fixtures" / "good-harness",
    REPO_ROOT / "tests" / "fixtures" / "plugin-package-closure",
    REPO_ROOT,
]
CODES = ("V02", "V03", "V04", "V05", "V15")


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

    def test_v02_deny_pattern_covers_an_allow_rule(self):
        """permissions: "Rules are evaluated in order: deny, then ask, then allow.
        The first match in that order determines the outcome, and rule
        specificity doesn't change the order. A broad deny rule like
        `Bash(aws *)` blocks every matching call, including calls that also
        match a narrower allow rule like `Bash(aws s3 ls)`, so a deny rule
        can't carry allowlist exceptions." """
        m = self._one("V02", "W")
        self.assertIn("Bash(aws *)", m)
        self.assertIn("Bash(aws s3 ls)", m)

    def test_v03_single_slash_anchors_at_the_settings_source(self):
        """permissions, Read/Edit pattern table: "`/path` -- Path relative to
        the settings source -- `Edit(/src/**/*.ts)` -- `<primary working
        directory>/src/**/*.ts` in project settings"; and "A pattern like
        `/Users/alice/file` isn't an absolute path. The single leading slash
        anchors at the settings source, not the filesystem root. Use
        `//Users/alice/file` for absolute paths." (The 2026-08 snapshot said
        `<project root>`; the live page says primary working directory.) The
        check fires only on a single slash followed by a filesystem-root
        directory name, the docs' own failure example; a plain `/src/**` is the
        documented anchor and is left alone."""
        m = self._one("V03", "W")
        self.assertIn("Edit(/Users/alice/src/**)", m)
        for anchor in ("//", "~/", "settings"):
            self.assertIn(anchor, m)

    def test_v03_leaves_the_documented_settings_source_anchor_alone(self):
        """`Edit(/src/**/*.ts)` is the docs' own example of the `/path` form, so
        it is correct as written; V03 fires only when the segment after the
        single slash is one that exists at the filesystem root."""
        findings = []
        vh._check_permissions_block("s.json", {"allow": ["Edit(/src/**/*.ts)", "Read(/docs/**)"]}, findings)
        self.assertEqual([f for f in findings if getattr(f, "code", None) == "V03"], [])

    def test_v04_bare_mcp_server_matcher_matches_nothing(self):
        """hooks: "To match every tool from a server, append `.*` to the server
        prefix. The `.*` is required: a matcher like `mcp__memory` or
        `mcp__brave-search` contains only exact-match characters, so it is
        compared as an exact string and matches no tool." Hook matchers only:
        a *permission* rule `mcp__puppeteer` covers the whole server
        (settings, MCP permission rules), so that shape is a near-miss."""
        m = self._one("V04", "E")
        self.assertIn("mcp__memory", m)
        self.assertIn("mcp__memory__.*", m)

    def test_v05_stop_hook_that_can_block_without_the_loop_guard(self):
        """hooks, Stop input: "The `stop_hook_active` field is `true` when
        Claude Code is already continuing as a result of a stop hook. Check
        this value or process the transcript to avoid blocking on a condition
        that will never resolve." Only for a script the linter can read that
        emits a block/decision; a Stop hook that merely logs has nothing to
        guard."""
        m = self._one("V05", "W")
        self.assertIn("gate.sh", m)
        self.assertIn("stop_hook_active", m)

    def test_v15_placeholder_in_shell_form_command(self):
        """hooks, exec form and shell form: "Set `args` whenever the hook
        references a path placeholder, since each element is passed as one
        argument with no quoting." A warning, not an error: the official
        examples also show shell-form commands carrying a placeholder."""
        m = self._one("V15", "W")
        self.assertIn("gate.sh", m)
        self.assertIn("args", m)

    def test_no_other_coded_finding_and_exit_reflects_the_error(self):
        self.assertEqual(set(self.coded), set(CODES))
        self.assertEqual(self.exit_code, vh.hc.EXIT_LINT_FAILED)  # V04 is an E


class NearMissTests(unittest.TestCase):
    """Shapes that look like one of the five and are correct: a permission
    rule `mcp__puppeteer`, `//` and `~/` anchors, a relative `Edit(docs/**)`,
    a matcher `mcp__memory__.*`, a Stop hook that only logs, exec-form
    commands with a placeholder, disjoint deny/allow rules."""

    def test_no_shape_code_fires_on_correct_harnesses(self):
        for root in NEAR_MISSES:
            findings, _ = vh.run(root, strict=False)
            self.assertEqual(set(by_code(findings)) & set(CODES), set(), root.name)

    def test_near_miss_fixture_stays_clean_under_strict(self):
        findings, code = vh.run(NEAR_MISSES[0], strict=True)
        self.assertEqual(findings, [])
        self.assertEqual(code, vh.hc.EXIT_OK)

    def test_v02_respects_glob_depth_identity_and_bare_tool_denies(self):
        """permissions: Read/Edit rules follow gitignore, where `*` does not
        cross a path separator and `**` does; a bare tool deny "removes the
        tool from Claude's context entirely"."""
        def codes(perms):
            findings = []
            vh._check_deny_subsumes_allow("s.json", perms, findings)
            return [f for f in findings if getattr(f, "code", None) == "V02"]
        self.assertEqual(codes({"deny": ["Read(src/*)"], "allow": ["Read(src/deep/file.py)"]}), [])
        self.assertEqual(len(codes({"deny": ["Read(src/**)"], "allow": ["Read(src/deep/file.py)"]})), 1)
        self.assertEqual(len(codes({"deny": ["Bash(aws *)"], "allow": ["Bash(aws *)"]})), 1)
        self.assertEqual(len(codes({"deny": ["Bash"], "allow": ["Bash(npm test)"]})), 1)
        self.assertEqual(codes({"deny": ["Bash(rm *)"], "allow": ["Bash(npm test)"]}), [])

    def test_v04_does_not_read_permission_rules(self):
        findings = []
        vh._check_permissions_block("s.json", {"allow": ["mcp__puppeteer"], "deny": []}, findings)
        self.assertEqual([f for f in findings if getattr(f, "code", None) == "V04"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
