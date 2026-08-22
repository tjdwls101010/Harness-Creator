#!/usr/bin/env python3
"""Self-test for validate_harness.py against tests/fixtures/{good,bad}-harness.

    python3 tests/test_validate_harness.py

stdlib unittest only, no pytest (per docs/plan/04-scripts-and-validation.md).
"""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_harness as vh  # noqa: E402


class GoodHarnessTests(unittest.TestCase):
    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "good-harness"
        self.findings, self.exit_code = vh.run(self.root, strict=False)

    def test_no_errors_or_warnings(self):
        self.assertEqual(self.findings, [])

    def test_exit_code_is_ok(self):
        self.assertEqual(self.exit_code, vh.hc.EXIT_OK)

    def test_strict_mode_still_passes(self):
        _, exit_code = vh.run(self.root, strict=True)
        self.assertEqual(exit_code, vh.hc.EXIT_OK)


class CliEdgeCaseTests(unittest.TestCase):
    """argparse shapes that are correct but look like omissions.

    Kept out of good-harness deliberately: that fixture is the canonical
    example a generated harness gets modelled on, and padding it with
    torture cases blunts what it teaches."""

    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "cli-edge-cases"
        self.findings, _ = vh.run(self.root, strict=False)

    def test_no_findings(self):
        self.assertEqual(self.findings, [])


class PackageClosureTests(unittest.TestCase):
    """A plugin-packaged skill travels as one directory. A pointer out of it
    resolves on the author's machine and nowhere else -- which is why this
    fires only when a plugin manifest actually ships the skill: a plain
    project skill sits inside the repo it points into, and `docs/design/notes.md`
    there is a working pointer, not a leak.

    The fixture deliberately mixes both kinds, because the risk this check
    carries is not missing a leak, it is firing on the target-project paths
    the skill legitimately names (WS2-6: a check that fires on a correct
    harness is worse than no check)."""

    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "plugin-package-closure"
        self.findings, self.exit_code = vh.run(self.root, strict=False)
        self.reported = [(loc, msg) for _, loc, msg in self.findings]

    def _leaked_paths(self):
        found = set()
        for _, msg in self.reported:
            m = re.search(r"names (\S+), which resolves in this repo", msg)
            if m:
                found.add(m.group(1))
        return found

    def test_a_path_that_resolves_in_the_repo_but_not_the_package_is_reported(self):
        self.assertIn("docs/design/notes.md", self._leaked_paths())

    def test_a_second_leak_in_a_different_tree_is_caught(self):
        self.assertIn("notes/internal-decisions.md", self._leaked_paths())

    def test_it_warns_rather_than_fails(self):
        """An adversarial pass built three correct plugins this flags: a
        skill telling the reader to check their own `docs/architecture.md`,
        their `.github/copilot-instructions.md`, their monorepo's
        `packages/web/CONTRIBUTING.md` -- each one correct, each one
        colliding with a path that also exists in the plugin's own repo.
        Nothing distinguishes those from a leak, and a check that fails a
        correct harness gets ignored and then catches nothing. So it warns,
        and a package that wants closure enforced runs --strict, which is
        what this repo does."""
        levels = {level for level, _, msg in self.findings if "which resolves in this repo" in msg}
        self.assertEqual(levels, {"W"})
        self.assertEqual(self.exit_code, vh.hc.EXIT_OK)
        self.assertEqual(vh.run(self.root, strict=True)[1], vh.hc.EXIT_LINT_FAILED)

    def test_a_leak_inside_a_bundled_script_is_caught(self):
        """This one reaches the end user: a module docstring is what
        `--help` prints."""
        self.assertTrue(
            any("tool.py" in loc for loc, _ in self.reported),
            f"expected a finding in scripts/tool.py, got {self.reported}",
        )

    def test_target_project_paths_are_not_leaks(self):
        """The paths a harness-building skill names constantly. Each one
        describes a file in the repo the skill is *run against*, and the
        signal that says so is that none of them resolve here.

        An earlier draft keyed the second half of this on .gitignore --
        a gitignored path cannot ship, so it looked like a strict
        improvement. It flagged all three of `node_modules/...`,
        `dist/index.md` and `docs/notes.md`, because a plugin repo's
        .gitignore describes *its* build products and the sentences
        describe the reader's."""
        for legit in (
            ".claude/settings.json", ".claude/rules/*.md", "CLAUDE.md",
            "packages/api/CLAUDE.md", ".github/copilot-instructions.md",
            "node_modules/some-pkg/README.md", "dist/index.md", "docs/notes.md",
            "references/real.md", "scripts/tool.py",
        ):
            self.assertNotIn(legit, self._leaked_paths(), legit)

    def test_a_project_skill_outside_a_plugin_is_not_checked(self):
        """good-harness has no plugin manifest, so the same shape of
        pointer there is a working pointer."""
        findings, _ = vh.run(REPO_ROOT / "tests" / "fixtures" / "good-harness", strict=False)
        self.assertEqual([f for f in findings if "which resolves in this repo" in f[2]], [])

    def test_a_url_query_value_is_not_a_pointer(self):
        """`https://docs.python.org/3/?source=references/install.md` names a
        query parameter, not a bundled file."""
        self.assertEqual(
            list(vh.iter_skill_pointers("https://x.dev/3/?source=references/install.md")), []
        )


class BadHarnessTests(unittest.TestCase):
    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "bad-harness"
        self.findings, self.exit_code = vh.run(self.root, strict=False)
        self.by_location = {}
        for level, location, message in self.findings:
            self.by_location.setdefault(location, []).append((level, message))

    def _assert_error_contains(self, location_substr, message_substr):
        for location, entries in self.by_location.items():
            if location_substr in location:
                for level, message in entries:
                    if level == "E" and message_substr in message:
                        return
        self.fail(f"expected an error containing {message_substr!r} at a location containing {location_substr!r}")

    def _assert_warning_contains(self, location_substr, message_substr):
        for location, entries in self.by_location.items():
            if location_substr in location:
                for level, message in entries:
                    if level == "W" and message_substr in message:
                        return
        self.fail(f"expected a warning containing {message_substr!r} at a location containing {location_substr!r}")

    def test_exit_code_is_lint_failed(self):
        self.assertEqual(self.exit_code, vh.hc.EXIT_LINT_FAILED)

    def test_missing_hook_script_is_error(self):
        self._assert_error_contains("PreToolUse", "does not exist")

    def test_non_matcher_event_with_matcher_is_error(self):
        self._assert_error_contains("UserPromptSubmit", "does not support a 'matcher'")

    def test_unknown_hook_event_is_error(self):
        self._assert_error_contains("NotARealEvent", "unknown hook event")

    def test_non_executable_hook_script_is_error(self):
        self._assert_error_contains("PostToolUse", "not executable")

    def test_unknown_permission_tool_is_error(self):
        self._assert_error_contains("permissions.allow", "NotARealTool")

    def test_broken_skill_frontmatter_is_error(self):
        self._assert_error_contains("broken-skill", "frontmatter did not parse")

    def test_dead_reference_link_is_error(self):
        self._assert_error_contains("dead-link-skill", "references/nonexistent.md")

    def test_dead_script_link_is_error(self):
        self._assert_error_contains("dead-link-skill", "scripts/nonexistent.py")

    def test_argument_without_help_is_error(self):
        self._assert_error_contains("bad_cli.py", "help=")

    def test_unparseable_script_is_error(self):
        self._assert_error_contains("broken_cli.py", "syntax error")

    def test_parser_without_description_is_warning(self):
        self._assert_warning_contains("bad_cli.py", "description=")

    def test_subparser_without_help_is_error(self):
        self._assert_error_contains("subcommand_cli.py", "subcommand 'run'")

    def test_doc_description_without_docstring_is_warning(self):
        self._assert_warning_contains("docless_cli.py", "resolves to None")

    def test_missing_skill_md_is_error(self):
        self._assert_error_contains("empty-skill-dir", "no SKILL.md")

    def test_agent_unknown_tool_is_error(self):
        self._assert_error_contains("reviewer-a.md", "unknown tool")

    def test_duplicate_agent_name_is_error(self):
        self._assert_error_contains("reviewer-b.md", "duplicate agent name")

    def test_agent_missing_description_is_error(self):
        self._assert_error_contains("reviewer-b.md", "missing required 'description'")

    def test_workflow_missing_meta_is_error(self):
        self._assert_error_contains("broken-workflow.js", "export const meta")

    def test_workflow_date_now_is_error(self):
        self._assert_error_contains("broken-workflow.js", "Date.now()")

    def test_bad_glob_syntax_is_error(self):
        self._assert_error_contains("bad-glob.md", "unmatched")

    def test_bad_at_import_is_error(self):
        self._assert_error_contains("CLAUDE.md", "nonexistent-doc.md")

    def test_unanchored_matcher_is_warning(self):
        self._assert_warning_contains("PreToolUse", "UNANCHORED regex")

    def test_if_on_non_tool_event_is_warning(self):
        self._assert_warning_contains("UserPromptSubmit", "no tool_input")

    def test_broad_allow_is_warning(self):
        self._assert_warning_contains("permissions.allow", "broad allow rule")

    def test_no_description_is_warning(self):
        self._assert_warning_contains("no-desc-skill", "no 'description'")

    def test_unknown_model_is_warning(self):
        self._assert_warning_contains("reviewer-a.md", "unrecognized 'model'")

    def test_rule_without_paths_is_warning(self):
        self._assert_warning_contains("no-paths.md", "no 'paths:'")

    def test_claude_md_too_long_is_warning(self):
        self._assert_warning_contains("CLAUDE.md", "over the 200-line guideline")

    def test_component_inventory_listing_is_warning(self):
        self._assert_warning_contains("CLAUDE.md", "component inventory")

    def test_missing_harness_spec_is_warning(self):
        self._assert_warning_contains("harness-spec.md", "missing")


class ConsequenceClauseTests(unittest.TestCase):
    """v3 attached a consequence to the findings that could carry one, on the
    theory that a check's failure message is an interface: it is read at
    exactly the moment it matters and costs nothing the rest of the time, so
    it can hold what would otherwise be a paragraph in a reference file.

    These assertions anchor the phrasing. Without them the clause is prose
    like any other and erodes on the next pass -- which is the specific way
    the v2 compression lost four claims.

    Findings that could NOT be given a consequence are listed at the bottom of
    this class, with the reason. That list is as load-bearing as the ones
    above: an unsourced consequence in a linter is a fabricated gotcha, and
    this skill's whole value proposition is that its gotchas are real."""

    @classmethod
    def setUpClass(cls):
        findings, _ = vh.run(REPO_ROOT / "tests" / "fixtures" / "bad-harness", strict=False)
        cls.messages = [m for _, _, m in findings]

    def _message_containing(self, needle):
        for m in self.messages:
            if needle in m:
                return m
        self.fail(f"no finding containing {needle!r}")

    def test_glob_error_says_the_rule_never_fires(self):
        """Documented: a rule loads only when Claude reads a file its `paths:`
        matches. A pattern that cannot parse therefore costs nothing at launch
        and silently never fires -- the failure has no runtime signal at all."""
        m = self._message_containing("unmatched")
        self.assertIn("never fire", m)

    def test_missing_spec_says_drift_detection_goes_quiet(self):
        """check_spec_drift returns empty lists in both directions when there
        is no spec, so the absence disables the check rather than failing it."""
        m = self._message_containing("a generated harness should carry a spec")
        self.assertIn("no drift in either direction", m)

    def test_skill_body_length_says_the_cost_recurs(self):
        """The documented reason for the 500-line guideline is that a skill's
        body stays in context once it triggers, so length is a recurring cost
        rather than a one-time one."""
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp())
        try:
            skill = tmp / ".claude" / "skills" / "long-skill"
            skill.mkdir(parents=True)
            body = "\n".join(f"line {i}" for i in range(vh.MAX_SKILL_BODY_LINES + 1))
            (skill / "SKILL.md").write_text(
                f"---\nname: long-skill\ndescription: triggers on x\n---\n{body}\n",
                encoding="utf-8",
            )
            findings, _ = vh.run(tmp, strict=False)
            m = next(msg for _, _, msg in findings if "-line guideline" in msg)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertIn("stays in context", m)
        self.assertIn("recurring cost", m)
        self.assertIn("references/", m)

    def test_missing_arg_help_says_the_model_reads_the_source(self):
        """Sourced in references/skills.md: an argument without `help=` prints
        as a bare flag name, so the model opens the source to learn what it
        takes and the interface reverts to the document it replaced. The
        consequence is the whole reason this is an E and not a style nit."""
        m = self._message_containing("has no help=")
        self.assertIn("open this script's source", m)

    def test_findings_without_a_sourced_consequence_stay_bare(self):
        """The three the v3 plan wanted to annotate and the docs would not
        support. Leaving them bare is the finding, not an omission.

        * agent frontmatter that does not parse -- documented for skills
          ("loads the body with empty metadata"), but the subagent docs never
          say what happens, and the two are not symmetric by assumption.
        * a missing @import target -- expansion timing is documented, the
          missing-file behaviour is not, anywhere, including /errors.
        * an unrecognized `model:` -- only the org-allowlist case is
          documented (falls back to inherit). A plain typo is not."""
        for needle, forbidden in (
            ("frontmatter did not parse", "silently"),
            ("import target does not exist", "session"),
        ):
            m = self._message_containing(needle)
            if needle == "frontmatter did not parse" and "skill body still loads" in m:
                continue                          # the skills one IS documented
            self.assertNotIn(forbidden, m, f"unsourced consequence crept into: {m}")


class ModelFieldTests(unittest.TestCase):
    """Regression for a validator that went wrong on its own as models shipped.

    The check enumerated model ids, so it rejected two values that were valid
    when this was found -- the documented alias `fable` and the id
    `claude-opus-5` -- while still accepting `claude-opus-4-8`. A false
    positive here is worse than a miss: it fails a correct harness at the
    delivery gate, which is exactly the class of bug B1 was in v0.2.0."""

    def test_documented_aliases_pass(self):
        for alias in ("inherit", "sonnet", "opus", "haiku", "fable"):
            self.assertTrue(vh.is_plausible_model(alias), alias)

    def test_claude_prefixed_ids_pass_without_being_enumerated(self):
        for model_id in ("claude-opus-5", "claude-sonnet-5", "claude-fable-5",
                         "claude-opus-4-8", "claude-haiku-4-5-20251001",
                         "claude-some-model-that-does-not-exist-yet-9"):
            self.assertTrue(vh.is_plausible_model(model_id), model_id)

    def test_typos_and_other_vendors_still_warn(self):
        for bad in ("sonnett", "gpt-4o", "opus-5", "", None, 5):
            self.assertFalse(vh.is_plausible_model(bad), repr(bad))

    def test_message_names_the_rule_it_applied(self):
        findings = []
        vh.add(findings, "W", "a.md",
               f"unrecognized 'model' value 'x' -- not one of "
               f"{'/'.join(vh.MODEL_ALIASES)} and not a 'claude-' prefixed id")
        self.assertIn("fable", findings[0][2])


class FrontmatterParserTests(unittest.TestCase):
    def test_simple_fields(self):
        fm = vh.hc.parse_frontmatter("---\nname: x\ndescription: y\n---\nbody\n")
        self.assertTrue(fm.ok)
        self.assertEqual(fm.data["name"], "x")
        self.assertEqual(fm.body.strip(), "body")

    def test_folded_scalar(self):
        fm = vh.hc.parse_frontmatter("---\ndescription: >\n  line one\n  line two\n---\n")
        self.assertTrue(fm.ok)
        self.assertEqual(fm.data["description"], "line one line two")

    def test_list_field(self):
        fm = vh.hc.parse_frontmatter("---\ntools:\n  - Read\n  - Bash\n---\n")
        self.assertTrue(fm.ok)
        self.assertEqual(fm.data["tools"], ["Read", "Bash"])

    def test_unclosed_fence_fails_conservatively(self):
        fm = vh.hc.parse_frontmatter("---\nname: x\n")
        self.assertFalse(fm.ok)

    def test_flow_style_rejected_conservatively(self):
        fm = vh.hc.parse_frontmatter("---\ntools: [Read, Bash]\n---\n")
        self.assertFalse(fm.ok)

    def test_no_fence_at_all(self):
        fm = vh.hc.parse_frontmatter("# just a heading\nno frontmatter here\n")
        self.assertFalse(fm.ok)


class AtImportParsingTests(unittest.TestCase):
    """B1. The old regex required a dot-extension and only guarded against
    backticks, so it read `ops@acme.com` and `react@18.2.0` as imports and
    raised an E for each -- which made Hard line 2 unsatisfiable for any
    CLAUDE.md that named a maintainer or pinned a version. It also missed the
    documented extensionless `@README` form and matched inside fenced blocks."""

    def _parse(self, text):
        return list(vh.hc.parse_at_imports(text))

    def test_email_address_is_not_an_import(self):
        self.assertEqual(self._parse("contact ops@acme.com"), [])

    def test_pinned_version_is_not_an_import(self):
        self.assertEqual(self._parse("stay on react@18.2.0"), [])

    def test_extensionless_target_is_an_import(self):
        self.assertEqual(
            self._parse("See @README for project overview and @package.json too."),
            ["README", "package.json"],
        )

    def test_backticked_target_is_literal(self):
        self.assertEqual(self._parse("see `@docs/x.md` literally"), [])

    def test_fenced_block_is_skipped(self):
        text = "before @docs/real.md\n```\n@docs/nope.md\n```\nafter @docs/two.md\n"
        self.assertEqual(self._parse(text), ["docs/real.md", "docs/two.md"])

    def test_tilde_fence_is_skipped(self):
        self.assertEqual(self._parse("~~~\n@docs/nope.md\n~~~\n"), [])

    def test_trailing_sentence_punctuation_is_stripped(self):
        self.assertEqual(self._parse("read @docs/foo.md."), ["docs/foo.md"])
        self.assertEqual(self._parse("read (@docs/bar.md) now"), ["docs/bar.md"])

    def test_home_import_is_external_and_not_root_relative(self):
        path, external = vh.hc.resolve_import(
            "~/.claude/notes.md", REPO_ROOT / "CLAUDE.md"
        )
        self.assertTrue(external)
        self.assertNotIn("~", str(path))

    def test_relative_import_resolves_against_the_containing_file(self):
        path, external = vh.hc.resolve_import(
            "notes.md", REPO_ROOT / ".claude" / "CLAUDE.md"
        )
        self.assertFalse(external)
        self.assertEqual(path, REPO_ROOT / ".claude" / "notes.md")


class GoodHarnessImportTests(unittest.TestCase):
    """The good-harness fixture carries all four traps in one file. It must
    exit 0 and resolve exactly one real import."""

    def setUp(self):
        self.claude_md = (
            REPO_ROOT / "tests" / "fixtures" / "good-harness" / "CLAUDE.md"
        )
        self.text = self.claude_md.read_text(encoding="utf-8")

    def test_fixture_still_contains_every_trap(self):
        for trap in ("ops@acme.com", "react@18.2.0", "@docs/nope.md", "@README.md"):
            self.assertIn(trap, self.text, trap)

    def test_exactly_one_import_target(self):
        self.assertEqual(list(vh.hc.parse_at_imports(self.text)), ["README.md"])


class DiscoveryPathTests(unittest.TestCase):
    """B3. Both scripts hardcoded ./CLAUDE.md, and rules/agents globs were
    non-recursive -- so a project using .claude/CLAUDE.md inventoried as
    having no instructions at all, and a nested rule that loads at launch was
    invisible to the linter, the inventory, and the drift check."""

    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "harness-in-dot-claude"

    def test_dot_claude_location_is_discovered(self):
        names = [p.name for p in vh.hc.claude_md_paths(self.root)]
        self.assertIn("CLAUDE.md", names)
        self.assertTrue(
            any(p.parent.name == ".claude" for p in vh.hc.claude_md_paths(self.root))
        )

    def test_nested_rule_is_discovered(self):
        rels = [str(p.relative_to(self.root)) for p in vh.hc.iter_rule_files(self.root)]
        self.assertIn(".claude/rules/frontend/style.md", rels)

    def test_nested_agent_is_discovered(self):
        rels = [str(p.relative_to(self.root)) for p in vh.hc.iter_agent_files(self.root)]
        self.assertIn(".claude/agents/sub/reviewer.md", rels)

    def test_walk_terminates_on_a_symlink_cycle(self):
        import tempfile, shutil, os
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / "a").mkdir()
            (tmp / "a" / "note.md").write_text("x", encoding="utf-8")
            try:
                os.symlink(tmp, tmp / "a" / "loop")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            found = [p.name for p in vh.hc.walk_markdown(tmp)]
            self.assertIn("note.md", found)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class AlwaysLoadedReportTests(unittest.TestCase):
    """The measurement a harness author needs and almost never has. Printed
    unconditionally, so it must be right on a correct harness too."""

    def test_counts_claude_md_and_unscoped_rules_only(self):
        root = REPO_ROOT / "tests" / "fixtures" / "harness-in-dot-claude"
        report = vh.always_loaded_report(root)
        paths = {e["path"] for e in report["entries"]}
        self.assertIn(".claude/CLAUDE.md", paths)
        self.assertIn(".claude/rules/frontend/style.md", paths)
        # A path-scoped rule loads on a matching read, not at launch.
        self.assertNotIn(".claude/rules/scoped.md", paths)

    def test_expands_imports(self):
        root = REPO_ROOT / "tests" / "fixtures" / "good-harness"
        report = vh.always_loaded_report(root)
        entry = next(e for e in report["entries"] if e["path"] == "README.md")
        self.assertIn("import", entry["note"])

    def test_names_what_it_cannot_count(self):
        report = vh.always_loaded_report(REPO_ROOT / "tests" / "fixtures" / "good-harness")
        joined = " ".join(report["uncounted"]).lower()
        for surface in ("user scope", "ancestor", "auto memory"):
            self.assertIn(surface, joined)

    def test_totals_match_the_entries(self):
        report = vh.always_loaded_report(REPO_ROOT / "tests" / "fixtures" / "good-harness")
        self.assertEqual(report["total_lines"], sum(e["lines"] for e in report["entries"]))


class HeuristicFalsePositiveTests(unittest.TestCase):
    """A check that fires on a correct harness is worse than no check, so
    every heuristic gets its must-not-fire case first."""

    def _advice(self, text):
        findings = []
        vh._check_generic_advice("CLAUDE.md", text, findings)
        return findings

    def test_generic_advice_fires_on_generic_advice(self):
        self.assertTrue(self._advice("Write clean code. Handle errors properly.\n"))
        self.assertTrue(self._advice("- Follow best practices\n"))

    def test_generic_advice_silent_on_project_specific_lines(self):
        for line in (
            "Be consistent with the existing handler naming (`handleFooRequest`).",
            "Handle errors properly by returning a `Result`, never by throwing across FFI.",
            "Write clean code in `src/legacy/` only after checking the migration guide.",
        ):
            self.assertEqual(self._advice(line), [], line)

    def _deny_allow(self, permissions):
        findings = []
        vh._check_deny_subsumes_allow("settings.json", permissions, findings)
        return findings

    def test_deny_subsumes_allow_fires(self):
        self.assertTrue(
            self._deny_allow({"deny": ["Bash(aws *)"], "allow": ["Bash(aws s3 ls)"]})
        )

    def test_deny_subsumes_allow_silent_on_disjoint_rules(self):
        self.assertEqual(
            self._deny_allow({"deny": ["Bash(rm *)"], "allow": ["Bash(npm test)"]}), []
        )
        # An allow identical to the deny is a different (already-reported) problem.
        self.assertEqual(
            self._deny_allow({"deny": ["Bash(aws *)"], "allow": ["Bash(aws *)"]}), []
        )

    def _glob(self, pattern):
        findings = []
        vh._check_catch_all_glob("rule.md", pattern, findings)
        return findings

    def test_catch_all_glob_fires(self):
        for pattern in ("**", "**/*", "*"):
            self.assertTrue(self._glob(pattern), pattern)

    def test_catch_all_glob_silent_on_a_real_scope(self):
        for pattern in ("src/**/*.ts", "docs/*.md", "src/api/**"):
            self.assertEqual(self._glob(pattern), [], pattern)

    def test_catch_all_message_does_not_claim_launch_loading(self):
        # The obvious phrasing is wrong: a catch-all glob loads on the first
        # matching read, not at launch. Shipping the wrong reason repeats B5.
        message = self._glob("**")[0][2]
        self.assertIn("first matching file read", message)


class SpecMentionConventionTests(unittest.TestCase):
    """B9. The lint required a backticked repo-relative path before a
    component counted as 'mentioned', while the audit accepted a bare stem --
    so the same repo could get opposite verdicts, and a spec written with bare
    names drew a false 'isn't mentioned in the spec' on a correct harness."""

    def setUp(self):
        self.root = REPO_ROOT / "tests" / "fixtures" / "spec-bare-name-skill"
        self.findings, _ = vh.run(self.root, strict=False)
        self.messages = [f[2] for f in self.findings]

    def test_bare_name_is_not_reported_as_missing(self):
        for message in self.messages:
            self.assertNotIn("isn't mentioned in the spec", message)

    def test_bare_name_draws_a_convention_nudge_instead(self):
        self.assertTrue(any("bare name" in m for m in self.messages), self.messages)

    def test_both_scripts_agree_the_component_is_accounted_for(self):
        import audit_harness as ah
        drift = ah.check_spec_drift(self.root, ah.run(self.root)["inventory"])
        self.assertEqual(drift["in_spec_not_on_disk"], [])
        self.assertEqual(drift["on_disk_not_in_spec"], [])

    def test_a_genuinely_absent_component_is_still_reported(self):
        findings = []
        vh.check_harness_spec(REPO_ROOT / "tests" / "fixtures" / "good-harness", findings)
        # good-harness's spec names every component, so nothing should be
        # reported as missing there either -- the control for this check.
        self.assertEqual(
            [f for f in findings if "isn't mentioned in the spec" in f[2]], []
        )


class WorkflowSyntaxProbeTests(unittest.TestCase):
    """B12, found while trimming the examples in WS6. The node syntax gate
    checked the workflow file as a bare module, so a top-level `return` --
    which the workflow runtime supports, and which BOTH of this skill's own
    reference examples use -- was reported as an E. That made Hard line 2
    unsatisfiable for a correct workflow, the same shape of bug as B1."""

    def _check(self, source):
        import shutil, subprocess
        if not shutil.which("node"):
            self.skipTest("node unavailable")
        return subprocess.run(
            ["node", "--input-type=module", "--check"],
            input=vh._workflow_syntax_probe(source),
            capture_output=True, text=True, timeout=10,
        ).returncode

    def test_top_level_return_is_valid(self):
        source = (
            "export const meta = { name: 'x', description: 'y' }\n"
            "const r = await agent('go', { schema: {} })\n"
            "if (!r) return { ok: false }\n"
            "return { ok: true }\n"
        )
        self.assertEqual(self._check(source), 0)

    def test_top_level_await_is_valid(self):
        self.assertEqual(
            self._check("export const meta = { name: 'x' }\nconst a = await agent('go')\n"), 0
        )

    def test_a_real_syntax_error_is_still_caught(self):
        self.assertNotEqual(
            self._check("export const meta = { name: 'x' }\nconst r = await agent('go'\n"), 0
        )

    def test_shipped_examples_pass_the_gate(self):
        """The examples in references/ must survive the linter that this skill
        tells the model to run. They didn't."""
        import re as _re
        for name in ("workflows.md", "e2e-testing.md"):
            text = (SCRIPTS_DIR.parent / "references" / name).read_text(encoding="utf-8")
            for i, block in enumerate(_re.findall(r"```javascript\n(.*?)```", text, _re.S)):
                self.assertEqual(self._check(block), 0, f"{name} block {i}")


class MatcherHelperTests(unittest.TestCase):
    def test_exact_matchers(self):
        for m in ("Bash", "Edit|Write", "code-reviewer", "a,b,c"):
            self.assertTrue(vh.hc.is_exact_matcher(m), m)

    def test_regex_matchers(self):
        for m in ("Edit.*", "^Edit$", "mcp__server__.*"):
            self.assertFalse(vh.hc.is_exact_matcher(m), m)


if __name__ == "__main__":
    unittest.main(verbosity=2)
