#!/usr/bin/env python3
"""Regression tests for the shipped skill surface itself (SKILL.md + references/).

    python3 tests/test_skill_surface.py

These cover the WS1 "truth repair" bugs. Most were classified as prose-only
in the plan, but each one has a mechanical shadow -- an ordering, a count, a
grep that must stay at zero -- and a check that runs on every commit is worth
more than a review note that runs once. stdlib unittest only, no pytest.
"""

import ast
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "harness-creator"
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_harness as vh  # noqa: E402

SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES = sorted((SKILL_DIR / "references").glob("*.md"))


def read(path):
    return path.read_text(encoding="utf-8")


class WrapUpOrderTests(unittest.TestCase):
    """B2. The Wrap-up ran validate_harness.py first, then edited the spec and
    CLAUDE.md -- so the state that actually got committed was never validated,
    and a line claimed the earlier run would 'independently catch' drift that
    did not exist yet when it ran."""

    def setUp(self):
        self.lines = read(SKILL_MD).splitlines()
        start = next(i for i, l in enumerate(self.lines) if "Wrap-up" in l)
        self.block = self.lines[start:start + 12]

    def _index_of(self, needle):
        for i, line in enumerate(self.block):
            if needle in line:
                return i
        self.fail(f"{needle!r} not found in the Wrap-up block")

    def test_validation_runs_after_the_edits_it_checks(self):
        change_history = self._index_of("Change history")
        pointers = self._index_of("update CLAUDE.md's pointers")
        validate = self._index_of("validate_harness.py")
        self.assertLess(change_history, validate)
        self.assertLess(pointers, validate)

    def test_commit_is_proposed_last(self):
        self.assertLess(self._index_of("validate_harness.py"), self._index_of("propose a commit"))

    def test_false_independence_claim_is_gone(self):
        self.assertNotIn("will independently catch", read(SKILL_MD))


class TimeoutFactsTests(unittest.TestCase):
    """B5. hooks-events.md called both MessageDisplay (10s) and SessionEnd
    (1.5s) 'the shortest of any event', hooks.md said 'two events' and listed
    two of three, and SessionEnd's 1.5s was labelled a per-hook default when
    the live docs call it a budget shared across all SessionEnd hooks."""

    def setUp(self):
        self.hooks = read(SKILL_DIR / "references" / "hooks.md")
        self.events = read(SKILL_DIR / "references" / "hooks-events.md")

    def test_only_one_shortest_of_any_event_claim_at_most(self):
        hits = sum(read(p).count("shortest of any event") for p in REFERENCES)
        self.assertLessEqual(hits, 1, "two events cannot both be the shortest")

    def test_session_end_is_described_as_a_shared_budget(self):
        for text, name in ((self.hooks, "hooks.md"), (self.events, "hooks-events.md")):
            self.assertRegex(text, r"budget shared across all|shared across all `SessionEnd`", name)

    def test_no_stale_two_events_count(self):
        self.assertNotIn("Two events break that pattern", self.hooks)

    def test_all_three_departing_events_are_named_together(self):
        section = self.hooks.split("Default timeouts are wildly uneven")[1][:1500]
        for event in ("UserPromptSubmit", "MessageDisplay", "SessionEnd"):
            self.assertIn(event, section, event)


class DanglingPointerTests(unittest.TestCase):
    """B8. Three pointers named a destination that did not exist: a 'see Hard
    lines' that said nothing about protected paths, a 'SKILL.md §3' when
    SKILL.md has no numbered sections, and a 'timeout column' in a table with
    no timeout column."""

    def test_no_dangling_pointers(self):
        pattern = re.compile(r"see Hard lines|SKILL\.md §|timeout column")
        for path in [SKILL_MD] + REFERENCES:
            self.assertIsNone(pattern.search(read(path)), path.name)

    def test_skill_md_still_has_no_numbered_sections(self):
        # The reason `SKILL.md §3` could never resolve. If numbered sections
        # are ever introduced, this test should be deleted, not worked around.
        self.assertNotIn("§", read(SKILL_MD))


class FenceBalanceTests(unittest.TestCase):
    """B10. agents.md opened a ```markdown fence and never closed it, so
    renderers and parsers swallowed the rest of the file as a code block."""

    def test_every_file_has_balanced_fences(self):
        for path in [SKILL_MD] + REFERENCES:
            count = len(re.findall(r"^```", read(path), re.MULTILINE))
            self.assertEqual(count % 2, 0, f"{path.name} has {count} fences")


class DeadLinkCoverageTests(unittest.TestCase):
    """B7. Hard line 1 claimed validate_harness.py checked pointers
    mechanically, but the check matched only backtick-wrapped forms and ran
    only against SKILL.md -- one pointer out of dozens."""

    def _scan(self, text):
        return list(vh.iter_skill_pointers(text))

    def test_pointers_in_both_skill_md_and_references_are_scanned(self):
        self.assertGreater(len(self._scan(read(SKILL_MD))), 10)
        ref_hits = sum(len(self._scan(read(p))) for p in REFERENCES)
        self.assertGreater(ref_hits, 0, "reference-to-reference pointers must be scanned")

    def test_bare_prose_and_markdown_link_forms_are_caught(self):
        for form in (
            "see references/hooks.md for detail",
            "[hooks](references/hooks.md)",
            "`references/hooks.md`",
            'python "${CLAUDE_SKILL_DIR}/scripts/run_e2e.py"',
        ):
            self.assertTrue(self._scan(form), form)

    def test_target_project_paths_and_globs_are_not_pointers(self):
        for form in (
            'command: "./scripts/security-check.sh"',
            "each `references/template-*.md` holds",
            "use `${CLAUDE_SKILL_DIR}/scripts/...` never a bare path",
        ):
            self.assertEqual(self._scan(form), [], form)

    def test_a_nested_pointer_is_checked_whole(self):
        """v5. The pattern captured one path segment, so a pointer into a
        subdirectory was only ever checked as far as the directory --
        `references/platform/missing.md` passed as long as `references/platform`
        existed, which is precisely when a nested pointer goes wrong."""
        self.assertEqual(self._scan("see references/platform/missing.md"),
                         ["references/platform/missing.md"])

    def test_a_sentence_ending_period_is_not_part_of_the_filename(self):
        """The mirror-image failure, and the worse one: a check that fires
        on a correct harness. A pointer at the end of a sentence was read as
        a file named `tool.py.` and reported missing."""
        self.assertEqual(self._scan("the CLI is scripts/tool.py."), ["scripts/tool.py"])

    def test_every_pointer_in_the_shipped_skill_resolves(self):
        findings = []
        for path in [SKILL_MD] + REFERENCES:
            vh._check_dead_links(SKILL_DIR, path.name, read(path), findings)
        self.assertEqual([f for f in findings if f[0] == "E"], [])


class AlwaysLoadedBudgetTests(unittest.TestCase):
    """The headline metric of the v2 revision. SKILL.md was 2,185 words but
    the true always-loaded surface was 4,833, because SKILL.md instructed an
    unconditional load of interview.md and reached into it during Phase 0 --
    so the progressive-disclosure seam between them bought nothing.

    The ceiling that matters is compaction: auto-compaction re-attaches only
    the first 5,000 tokens of a skill, and everything past that vanishes
    silently rather than degrading.

    Only HARD_CEILING is a product fact. WORD_BUDGET is a self-imposed target,
    and v3 raised it from 2,500 to 2,650 rather than cut the compression
    doctrine down to fit: 2,500 was the number v2 landed on while *removing*
    an unconditional interview.md load, and v3 is adding four pieces of
    doctrine that every generated harness inherits. Holding a number whose
    justification had changed is the rail-wearing-a-digit failure this skill
    warns about, and the density metric v3 actually targets moved the right
    way -- words trapped in >=110-word paragraphs went 788 -> 580. Raise this
    again only with the same kind of reason written down; the ceiling below
    is the one that must not move."""

    WORD_BUDGET = 2650          # self-imposed; see docstring and D34/C15
    HARD_CEILING = 3750         # ~5,000 tokens; past here content is dropped

    def test_skill_md_within_budget(self):
        words = len(read(SKILL_MD).split())
        self.assertLess(words, self.WORD_BUDGET, f"SKILL.md is {words} words")

    def test_skill_md_under_the_compaction_ceiling(self):
        self.assertLess(len(read(SKILL_MD).split()), self.HARD_CEILING)

    def test_interview_md_is_not_loaded_unconditionally(self):
        """WS8 step 2. If SKILL.md ever tells the model to load interview.md
        on every invocation again, the always-loaded surface doubles and this
        whole workstream is undone."""
        text = read(SKILL_MD)
        for phrase in (
            "load it before Phase 1 of any invocation",
            "load references/interview.md)",
        ):
            self.assertNotIn(phrase, text, phrase)

    def test_sync_path_does_not_require_interview_md(self):
        """WS8 step 1. The sync procedure has to live somewhere reachable
        without loading interview.md, or gating the load strands sync mode."""
        re_entry = SKILL_DIR / "references" / "re-entry.md"
        self.assertTrue(re_entry.is_file(), "references/re-entry.md must exist")
        text = read(re_entry)
        for concept in ("sync", "status", "generated", "validated", "Change history"):
            self.assertIn(concept, text, concept)

    def test_skill_md_routes_to_re_entry(self):
        self.assertIn("re-entry.md", read(SKILL_MD))


class GuardrailTests(unittest.TestCase):
    """The do-not-cut list from the audit (audit-synthesis.md section 4), plus
    the mechanics added in WS5. Each entry is a product mechanism with a named
    silent failure mode: cutting it degrades generated harnesses without
    degrading the prose, so nothing here should quietly disappear during the
    example-trimming pass.

    Anchors are distinctive technical tokens rather than sentences, so
    legitimate rewording doesn't trip them. If a rewrite genuinely retires an
    anchor, change it here deliberately -- that edit is the review signal."""

    GUARDRAILS = {
        "hooks.md": [
            "exit 2",              # only exit 2 blocks; exit 1 proceeds silently
            "stop_hook_active",    # unguarded Stop hook is an infinite loop
            "NotebookEdit",        # Edit.* matcher also matches NotebookEdit
            "additionalContext",   # imperative phrasing trips injection defenses
            "workspace trust",     # the enforcing half is inert on a fresh clone
            "bypassPermissions",   # hook deny holds; hook allow never loosens
            "protected",           # .claude/ writes can't be pre-approved
            "dontAsk",             # protected-path writes are denied outright
            "defaultMode",         # "auto" is ignored in project settings
            "asyncRewake",         # the middle path for a slow Stop check
        ],
        "skills.md": [
            "once: true",
            "!`",                  # !`command` always runs, it is preprocessing
        ],
        "agents.md": [
            "Explore and Plan",    # they skip CLAUDE.md and git status
            "skills:",             # preloads full skill bodies, not descriptions
            "once: true",
            "AskUserQuestion",     # does not exist inside a subagent
            "v2.1.218",            # frontmatter hooks are trust-gated
            "agent-memory",        # memory: project writes a committed directory
        ],
        "claude-md-and-rules.md": [
            "paths:",              # a rule without paths: loads at launch
            "@",                   # imports expand at launch, saving nothing
            "200",                 # the line guideline, with its exception
            "CLAUDE.local.md",     # the destination for per-machine facts
            "autoMemoryEnabled",   # auto memory can be switched off entirely
            "MEMORY.md",           # a second always-loaded surface
            "AGENTS.md",           # Claude Code does not read it
            "compaction",          # the survival matrix
        ],
        "workflows.md": [
            "meta",                # must be a pure literal, read before execution
            "Date.now()",          # outright rejection, not a warning
            "acceptEdits",         # every workflow agent runs in this mode
        ],
        "e2e-testing.md": [
            "AskUserQuestion",     # the interview can never be e2e-tested
        ],
        "hooks-events.md": [
            "stop_hook_active",
            "SessionEnd",
        ],
    }

    def test_guardrail_facts_survive(self):
        # Case-insensitive on purpose. These anchor *concepts* that must not be
        # deleted, not exact wording -- a heading capitalizing a term is a
        # rewrite, and this test exists to catch removal.
        for filename, anchors in self.GUARDRAILS.items():
            text = read(SKILL_DIR / "references" / filename).lower()
            for anchor in anchors:
                self.assertIn(anchor.lower(), text, f"{filename} lost {anchor!r}")

    def test_hooks_router_survives(self):
        """R3. The event router is what makes the hooks.md/hooks-events.md
        split safe -- without it the model loads ~3,800 words to pick one
        event, turning a staged split into a routing failure."""
        text = read(SKILL_DIR / "references" / "hooks.md")
        events = re.findall(r"`(PreToolUse|PostToolUse|Stop|SessionEnd|UserPromptSubmit)`", text)
        self.assertGreater(len(set(events)), 3)
        self.assertIn("hooks-events.md", text)

    def test_run_e2e_honesty_survives(self):
        """This anchor was retired deliberately, which is the review signal
        the class docstring asks for. It held the phrase "best guess" from
        v1 through v4, because run_e2e.py's headless permission handling had
        never been watched to succeed and deleting the caveat would have
        turned an honest guess into an implied guarantee.

        Three runs on 2026-08-22 settled it. What survives is the half that
        is still true: auth is per-machine, so a confirmed run here says
        nothing about the next environment. If that clause ever goes, the
        script reads as unconditionally proven, which it is not."""
        text = read(SKILL_MD) + read(SKILL_DIR / "references" / "e2e-testing.md")
        self.assertIn("auth is per-machine", text)
        self.assertNotIn("best guess", read(SKILL_MD),
                         "the caveat was retired; do not reintroduce it as prose")


class InterfaceDoctrineTests(unittest.TestCase):
    """v5 gave the interface boundary its second direction, and retired the
    `Signature` column that the missing direction had permitted.

    The one-way version constrained only the interface author -- "don't put
    when/why in a signature" -- so writing both a signature and a prose copy
    of it broke no rule, and this skill did exactly that until two rows of
    the copy went wrong. Anchored here for the same reason as
    ConsequenceClauseTests in test_validate_harness.py: without an assertion
    the clause is prose like any other and erodes on the next pass."""

    def _scripts_section(self):
        return read(SKILL_MD).split("## Scripts")[1].split("\n## ")[0]

    def _table_rows(self):
        return [l for l in self._scripts_section().splitlines() if l.startswith("|")]

    def _argparse_clis(self):
        """Which bundled scripts are CLIs, read from the source rather than
        listed here -- adding one without a 'Run it when' row should fail."""
        names = []
        for path in sorted(SCRIPTS_DIR.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            if any(isinstance(n, ast.Attribute) and n.attr == "ArgumentParser"
                   for n in ast.walk(tree)):
                names.append(path.name)
        return names

    def test_boundary_names_both_owners(self):
        """Both halves, because naming only the tool's half is what let the
        prose copy exist. An adversarial read of an earlier draft that
        forbade prose from "asserting how the tool currently behaves" also
        forbade "run this only with consent, it spends real tokens" -- while
        a --help string saying the same thing was forbidden by the other
        half. Splitting on ownership instead leaves nowhere unreachable."""
        text = read(SKILL_MD)
        self.assertIn("the tool owns what is *valid*, what it does, and what it prints", text)
        self.assertIn("the project owns when to reach for it, what it costs, and why it was chosen", text)
        self.assertIn("Neither side restates the other.", text)

    def test_the_falsifiability_test_is_stated(self):
        """The clause that makes the rule operable on a case nobody listed."""
        self.assertIn(
            "If editing the tool would make the sentence false, the sentence belongs in the tool.",
            read(SKILL_MD),
        )

    def test_a_pointer_inherits_its_targets_reader(self):
        self.assertIn("A pointer inherits its target's reader", read(SKILL_MD))

    def test_the_script_table_has_no_signature_column(self):
        header = self._table_rows()[0]
        self.assertNotIn("Signature", header)
        self.assertEqual(header.count("|"), 3, header)

    def test_the_script_table_carries_no_flags(self):
        """The specific regression. A flag in this table is a copy of
        `--help`, and the copy is the half nothing checks."""
        for row in self._table_rows():
            self.assertNotRegex(row, r"--[a-z]", row)

    def test_every_bundled_cli_still_says_when_to_run_it(self):
        """Judgment is the half that stays. Dropping the column must not
        drop the row."""
        rows = "\n".join(self._table_rows())
        for name in self._argparse_clis():
            self.assertIn(name, rows, name)

    def test_the_canonical_skill_example_points_instead_of_restating(self):
        self.assertNotIn("script's signature", read(SKILL_DIR / "references" / "skills.md"))


class InterfaceContradictionTests(unittest.TestCase):
    """v5. Prose that asserts how a bundled script *currently behaves* is a
    claim about code, and nothing contrasted it against the code -- so it
    went false silently while the `--help` beside it stayed right.

    This one was a safety bug, not a tidiness one. e2e-testing.md called an
    isolated project copy "the one `run_e2e.py` implements as its default";
    `--isolate` is `store_true`, so the actual default is the user's real
    project. A reader who trusted the prose and dropped the flag would point
    a headless agent session at it.

    The interface half of each pair below is read out of the source rather
    than restated here, so editing the flag is what breaks the test."""

    E2E = SKILL_DIR / "references" / "e2e-testing.md"

    def _run_e2e_argument(self, flag):
        tree = ast.parse((SCRIPTS_DIR / "run_e2e.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument"):
                continue
            if node.args and getattr(node.args[0], "value", None) == flag:
                return {kw.arg: getattr(kw.value, "value", None) for kw in node.keywords}
        self.fail(f"run_e2e.py declares no {flag} argument")

    def test_isolation_is_opt_in_in_the_interface(self):
        """The fact the prose has to agree with. If this ever flips to
        opt-out, the prose assertions below are the ones to revisit."""
        self.assertEqual(self._run_e2e_argument("--isolate").get("action"), "store_true")

    def test_prose_does_not_claim_the_script_isolates_by_default(self):
        text = read(self.E2E) + read(SKILL_MD)
        for claim in ("implements as its default", "isolates by default", "isolated by default"):
            self.assertNotIn(claim, text, claim)

    def test_prose_states_that_passing_the_flag_is_the_decision(self):
        self.assertIn("`--isolate` is opt-in", read(self.E2E))

    def test_permission_mode_flag_is_not_hidden_from_the_reader(self):
        """`--permission-mode` exists and is the direct answer to the
        headless-permissions caveat printed right beside it. Prose that
        apologises for a guess while the flag that settles it goes unnamed
        is worse than prose that names neither."""
        self.assertIsNotNone(self._run_e2e_argument("--permission-mode"))
        self.assertIn("--permission-mode", read(self.E2E))

    def test_tools_frontmatter_is_not_sold_as_a_write_sandbox(self):
        """The same shape one file over. agents.md said `tools:` "already
        enforces" read-only while its own example keeps `Bash` (it needs
        `git diff`) -- and hooks.md, in this package, documents `sed -i` and
        `echo >> file` as the way a Bash-driven edit skips Edit|Write. The
        skill contradicted itself, and the losing side was the one a
        generated agent inherits."""
        text = read(SKILL_DIR / "references" / "agents.md")
        self.assertNotIn("already enforces it", text)
        examples_with_bash = [
            block for block in re.findall(r"```markdown\n(.*?)```", text, re.S)
            if re.search(r"^tools:.*\bBash\b", block, re.M)
        ]
        if examples_with_bash:
            self.assertIn("`Bash` writes files", text)

    def test_flags_are_not_attributed_to_the_wrong_cli(self):
        """`--dangerously-skip-permissions` belongs to the `claude` CLI that
        run_e2e.py spawns, not to run_e2e.py."""
        declared = ast.parse((SCRIPTS_DIR / "run_e2e.py").read_text(encoding="utf-8"))
        flags = {
            node.args[0].value
            for node in ast.walk(declared)
            if isinstance(node, ast.Call)
            and getattr(node.func, "attr", "") == "add_argument"
            and node.args
            and isinstance(getattr(node.args[0], "value", None), str)
        }
        self.assertNotIn("--dangerously-skip-permissions", flags)
        for path in [SKILL_MD] + REFERENCES:
            for m in re.finditer(r"`run_e2e\.py[^`]*`", read(path)):
                self.assertNotIn("--dangerously-skip-permissions", m.group(0), path.name)


class SubtractionTests(unittest.TestCase):
    """v5. A harness only grows unless something makes it shrink, and improve
    mode had no downward arrow: every row of the feedback-routing table ended
    in a repair or a promotion to a stronger layer.

    The retirement doctrine that did exist covered *components*, and only
    fired once you already suspected one. A stale *line* has no such tell --
    a rule written to fight a model's old default reads exactly like one
    still fighting the current default."""

    RE_ENTRY = SKILL_DIR / "references" / "re-entry.md"
    E2E = SKILL_DIR / "references" / "e2e-testing.md"

    def test_improve_asks_what_is_unnecessary_alongside_what_is_wanted(self):
        text = read(self.RE_ENTRY)
        improve = text.split("## Improve")[1].split("\n## ")[0]
        self.assertIn("what is now unnecessary", improve)

    def test_ablation_is_a_proposal_not_an_action(self):
        self.assertIn("it is a proposal, not an action", read(self.RE_ENTRY))

    def test_hooks_and_permissions_are_excluded_from_ablation(self):
        """The guard that makes the rest safe to state. Ablating a hook means
        observing the failure the hook exists to prevent."""
        self.assertIn("never ablate a hook or a permission rule", read(self.RE_ENTRY).lower())

    def test_the_routing_table_has_a_row_that_ends_in_removal(self):
        rows = [l for l in read(self.E2E).splitlines() if l.startswith("| ")]
        self.assertTrue(
            any("Ablate" in r for r in rows),
            "every repair target pointed at more machinery",
        )


class GotchaCountTests(unittest.TestCase):
    """A count in a heading is a number that goes stale the moment someone
    adds or removes an item, and this skill's own doctrine calls a number
    without a live justification a rail wearing a digit. v5 merged one of
    six gotchas into the frontmatter row it duplicated; the heading is now
    checked against the section instead of trusted."""

    WORDS = {4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight"}

    def test_the_heading_count_matches_the_section(self):
        text = read(SKILL_DIR / "references" / "skills.md")
        heading = next(l for l in text.splitlines() if "gotchas you cannot derive" in l)
        section = text.split(heading)[1].split("\n## ")[0]
        actual = len([l for l in section.splitlines() if l.startswith("**")])
        self.assertIn(self.WORDS[actual], heading, f"heading says otherwise; section has {actual}")


class PointerReaderTests(unittest.TestCase):
    """v5 removed CLAUDE.md's pointer at `.claude/harness-spec.md`.

    The policy forbidding an inventory argued that a hand-maintained prose
    list drifts -- and then sent the reader to the spec, whose Behavior
    inventory is a hand-maintained prose list with its own drift check. The
    pointer did not remove the drift, it moved it one hop, and it moved a
    working session onto a maintenance document to do it.

    All three assertions live together on purpose. The pointer was written
    into prose, into the canonical example, and into a linter message that
    actively recommended it; fixing any one of them leaves the other two to
    put it back."""

    CMR = SKILL_DIR / "references" / "claude-md-and-rules.md"

    def test_the_policy_names_the_client_as_what_already_announces_components(self):
        text = read(self.CMR)
        self.assertIn("the client already does", text)
        self.assertIn("A pointer inherits its target's reader", text)

    def test_the_canonical_example_has_no_live_pointer_at_the_spec(self):
        """An HTML comment is allowed and is the point: block comments are
        stripped before injection, so a maintainer's way in costs the
        session nothing."""
        block = read(self.CMR).split("```markdown")[1].split("```")[0]
        for line in block.splitlines():
            if "harness-spec.md" in line:
                self.assertTrue(
                    line.strip().startswith("<!--"),
                    f"the example points a session at the spec: {line.strip()!r}",
                )

    def test_the_linter_no_longer_recommends_the_pointer(self):
        findings, _ = vh.run(REPO_ROOT / "tests" / "fixtures" / "bad-harness", strict=False)
        message = next(m for _, _, m in findings if "component inventory" in m)
        self.assertNotIn("harness-spec.md", message)
        self.assertIn("the client already surfaces every component", message)


class PackageClosureRegressionTests(unittest.TestCase):
    """v5 closed thirteen pointers that led out of the shipped package.

    Six were paths, and validate_harness.py now catches those for any
    plugin-packaged skill. The rest are shapes no general check can see
    without firing on correct harnesses -- a bare decision-log code, a bare
    filename, a quoted section title -- so they are pinned here instead, the
    way NoExternalToolNamesTests pins a word list. These are facts about
    this package, not a rule worth shipping to users.

    The `.tmp/` two were the worst of the set: gitignored, so absent from
    every clone, and one of them sat in a module docstring that `--help`
    prints to the end user."""

    def _shipped_files(self):
        return [SKILL_MD] + REFERENCES + sorted(SCRIPTS_DIR.glob("*.py"))

    def test_no_unresolvable_decision_log_codes(self):
        """`D12` is not bad because it is short. It is bad because nothing in
        the installed package defines it, so the reader cannot expand it.
        The package's own codes (I1-I5, V1-V4, B1) are all defined inside it
        and are deliberately not matched here."""
        for path in self._shipped_files():
            hits = re.findall(r"\bD[0-9]{1,2}\b", read(path))
            self.assertEqual(hits, [], f"{path.name} cites {hits}")

    def test_no_gitignored_path_is_cited(self):
        """The one case the shipped check structurally cannot see.

        Package closure asks whether a path resolves here and not in the
        package -- and `.tmp/` resolves nowhere on a fresh clone, so on CI
        that check goes quiet on exactly the worst leak: gitignored, absent
        for every user, and in this repo it sat in a module docstring that
        `--help` prints. Keying the check on .gitignore instead was tried
        and reverted; it flagged `dist/index.md` and `node_modules/.../README.md`
        in correct harnesses, because a plugin repo's .gitignore describes
        its own build products while those sentences describe the reader's.
        So the general rule stays general and this repo's own names are
        pinned here."""
        ignored = [
            line.strip().lstrip("/").rstrip("/")
            for line in read(REPO_ROOT / ".gitignore").splitlines()
            if line.strip() and not line.startswith(("#", "!", "*"))
        ]
        self.assertIn(".tmp", ignored, "this pin assumes .gitignore still lists .tmp")
        for path in self._shipped_files():
            for name in ignored:
                self.assertNotIn(f"{name}/", read(path), f"{path.name} cites {name}/")

    def test_no_plan_document_is_named(self):
        """Derived from the plan tree rather than hardcoded, so a pointer at
        any generation's plan file fails, not just the one v5 removed."""
        plan_docs = {
            p.name for p in (REPO_ROOT / "docs" / "plan").rglob("[0-9][0-9]-*.md")
        }
        self.assertTrue(plan_docs, "the plan tree should not be empty")
        for path in self._shipped_files():
            text = read(path)
            for name in sorted(plan_docs):
                self.assertNotIn(name, text, f"{path.name} names the plan document {name}")

    def test_quoted_section_titles_resolve(self):
        """skills.md sent the reader to hooks.md's "Hooks in skills and
        agents", which is not a heading in hooks.md or anywhere else. A
        pointer at a section is as dead as a pointer at a file, and the
        dead-link check cannot see it -- the file it names does exist."""
        for path in [SKILL_MD] + REFERENCES:
            for m in re.finditer(r"([a-z][\w-]*\.md)'s \"([^\"]+)\"", read(path)):
                target = SKILL_DIR / "references" / m.group(1)
                self.assertTrue(target.is_file(), f"{path.name} -> {m.group(1)}")
                headings = re.findall(r"^#+\s+(.*)$", read(target), re.MULTILINE)
                self.assertIn(m.group(2), headings, f"{path.name} quotes a missing heading")


class NoExternalToolNamesTests(unittest.TestCase):
    """D14. The shipped skill is a self-contained plugin and must not name
    Claude Code UI commands."""

    def test_no_ui_command_names(self):
        pattern = re.compile(r"doctor|checkup", re.IGNORECASE)
        for path in [SKILL_MD] + REFERENCES:
            self.assertIsNone(pattern.search(read(path)), path.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
