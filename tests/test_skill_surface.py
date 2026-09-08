#!/usr/bin/env python3
"""Regression tests for the shipped skill surface itself (SKILL.md + references/).

    python3 tests/test_skill_surface.py

These cover shipped resource and interface regressions. Authoring judgment
is evaluated through real sessions and independent review, not prose pins.
stdlib unittest only, no pytest.
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


def reachable_skill_pointers():
    """Follow shipped Markdown pointers from the skill's entry point."""
    pending = [SKILL_MD]
    visited = set()
    pointers = set()
    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        for pointer in vh.iter_skill_pointers(read(path)):
            pointers.add(pointer)
            target = SKILL_DIR / pointer
            if target.suffix == ".md" and target.is_file():
                pending.append(target)
    return pointers


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
        """Every shipped reference is reachable, directly or through another
        reference, by a pointer the linter scans."""
        pointed = reachable_skill_pointers()
        for ref in REFERENCES:
            self.assertIn(f"references/{ref.name}", pointed, ref.name)
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


class RetiredReferenceTests(unittest.TestCase):
    """Deleted references must not remain dependencies of the shipped package."""

    def test_no_interview_file_and_nothing_points_at_one(self):
        """v7 deleted interview.md: its protocol (modes, stages, scripts) was
        a rail the model does not need, and its knowledge moved into SKILL.md
        as K1-K15. Nothing shipped may point at it or its predecessor."""
        for name in ("interview.md", "re-entry.md"):
            self.assertFalse((SKILL_DIR / "references" / name).exists(), name)
        for path in [SKILL_MD] + REFERENCES + sorted(SCRIPTS_DIR.glob("*.py")):
            self.assertNotIn("interview.md", read(path), path.name)
            self.assertNotIn("re-entry.md", read(path), path.name)


class NoModeVocabularyTests(unittest.TestCase):
    """The four-mode classification (new/extend/improve/sync) and the I1-I5
    stage numbers were the rail v7 removed. `extend` and `improve` looked
    identical on disk, so the audit could not tell them apart and SKILL.md
    had to say so -- a gotcha the classification itself created. The concept
    of syncing spec and disk stays; the mode names as a taxonomy do not."""

    MODE_NEAR_MARKER = re.compile(
        r"\b(new|extend|improve|sync)\b[- ]?(mode|pass|모드)|\b(mode|pass|모드)s?\b[^.\n]{0,20}\b(new|extend|improve|sync)\b"
        r"|`(new|extend|improve|sync)`",
        re.IGNORECASE,
    )
    STAGE_NUMBER = re.compile(r"\bI[1-5]\b")
    SHIPPED = [SKILL_MD] + REFERENCES + sorted(SCRIPTS_DIR.glob("*.py"))

    def test_no_mode_taxonomy_in_shipped_files(self):
        for path in self.SHIPPED:
            hits = [m.group(0) for m in self.MODE_NEAR_MARKER.finditer(read(path))]
            self.assertEqual(hits, [], f"{path.name} still classifies passes by mode")

    def test_no_stage_numbers_in_shipped_files(self):
        for path in self.SHIPPED:
            self.assertIsNone(self.STAGE_NUMBER.search(read(path)), f"{path.name} names an interview stage")

    def test_the_audit_does_not_suggest_a_mode(self):
        self.assertNotIn("suggested mode", read(SKILL_MD).lower())
        self.assertNotIn("suggested_mode", read(SCRIPTS_DIR / "audit_harness.py"))


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
            "permission rules",    # the agents get no prompt, so allow first
        ],
        # Retired in v7: "acceptEdits", which anchored "every workflow agent
        # runs in acceptEdits mode, unconditionally". The live docs say the
        # agents use your permission rules and take their mode from the
        # ordinary subagent rules. A guardrail can pin a false fact as
        # firmly as a true one, which is the failure mode to watch for here:
        # what makes an anchor worth keeping is that the mechanism is real
        # and silent, and only the second half was ever checked.
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


class BundledCliCoverageTests(unittest.TestCase):
    """Bundled CLIs remain discoverable wherever the skill routes to them."""

    def _argparse_clis(self):
        """Which bundled scripts are CLIs, read from the source rather than
        listed here -- adding an unreachable CLI should fail."""
        names = []
        for path in sorted(SCRIPTS_DIR.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            if any(isinstance(n, ast.Attribute) and n.attr == "ArgumentParser"
                   for n in ast.walk(tree)):
                names.append(path.name)
        return names

    def test_every_bundled_cli_is_reachable(self):
        pointers = reachable_skill_pointers()
        for name in self._argparse_clis():
            self.assertIn(f"scripts/{name}", pointers, name)

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
        """v7 (disposition C25) reworded the sentence this anchored: the ban
        is now on the bare inventory rather than on naming a component at
        all, because SKILL.md tells the builder to say why a hook exists,
        which names one. The anchor moved to the clause that still carries
        the reason -- the client is what announces existence, so a prose
        registry buys nothing and drifts."""
        text = read(self.CMR)
        self.assertIn("the client already announces existence", text)
        # The pointer principle itself is stated once, in SKILL.md, and
        # test_a_pointer_inherits_its_targets_reader pins it there. What this
        # file has to keep is that a pointer does not evade the ban.
        self.assertIn("moves who pays, not whether", text)

    def test_the_canonical_example_carries_no_component_registry(self):
        """The example is what a reader copies, so a registry line here
        would ship the very thing the section bans. Checking only for one
        filename made this vacuous: an adversarial review pasted an ordinary
        component list into the example and it stayed green."""
        block = read(self.CMR).split("```markdown")[1].split("```")[0]
        live = "\n".join(l for l in block.splitlines() if not l.strip().startswith("<!--"))
        for registry in ("Harness components:", "Components:", "Skills:", "Agents:", "Hooks:"):
            self.assertNotIn(registry, live, f"the example ships a registry: {registry}")
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
        any generation's plan file fails, not just the one v5 removed. With no
        plan tree there is nothing to derive from, so the pin skips and
        returns on its own if one reappears."""
        plan_tree = REPO_ROOT / "docs" / "plan"
        if not plan_tree.is_dir():
            self.skipTest("docs/plan/ is gone; nothing to derive the pin from")
        plan_docs = {p.name for p in plan_tree.rglob("[0-9][0-9]-*.md")}
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


class OrchestrationChoiceTests(unittest.TestCase):
    """v6. The skill covered subagents and workflows and never said which of
    the four parallel-work surfaces an interview answer should land on --
    agent teams appeared exactly once, as an antipattern with no honest
    opposite.

    Each test below pins a sentence *this skill wrote*, not a product fact:
    a substring check cannot notice the product changing underneath it. The
    source line in every docstring is what makes the drift checkable by hand,
    and it is there because the first draft of this section got one of these
    claims wrong -- it said team permissions were fixed at spawn, when the
    source says they start from the lead's and can be changed individually
    afterward. Re-read the cited lines before editing any claim here.

    Snapshot the claims were written against: `.tmp/docs_claude/
    02-build-with-claude-code/01-agents-and-parallel-work/` (gitignored, not
    part of this repo's history)."""

    AGENTS = SKILL_DIR / "references" / "agents.md"
    WORKFLOWS = SKILL_DIR / "references" / "workflows.md"

    def test_the_discriminant_is_who_decides_what_runs_next(self):
        """00-overview.md "Choose an approach": "Who coordinates the work?"
        with four bullets -- Claude in one conversation / you hand off / Claude
        plans and supervises / a script holds the plan."""
        text = read(self.AGENTS)
        self.assertIn("who decides what runs next", text)
        # The phrase appears in the heading and again in the sentence that
        # introduces the table, so take the last occurrence, not the first.
        table = text.split("who decides what runs next")[-1].split("\n## ")[0]
        rows = [r for r in table.splitlines() if r.startswith("| ") and "---" not in r]
        # Four surfaces, each on its own row, each paired with what it makes the
        # harness contain -- a list of names elsewhere in the file is not this.
        for surface in ("subagents", "agent view", "agent teams", "dynamic workflows"):
            matching = [r for r in rows if surface in r]
            self.assertEqual(len(matching), 1, surface)
            self.assertEqual(matching[0].count("|"), 4, f"{surface} row is not 3 cells")

    def test_teams_are_off_until_an_env_var_is_set(self):
        """03-run-agent-teams.md:10,54 -- "disabled by default ... Without that
        variable, no team is set up at session start ... Claude does not spawn
        or propose teammates"."""
        text = read(self.AGENTS)
        self.assertIn("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", text)
        bullet = next(
            line for line in text.splitlines()
            if "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" in line
        )
        # The name alone is a setting; the consequence is why it is a cost.
        self.assertIn("does not spawn or propose", bullet)

    def test_teams_do_not_isolate_files(self):
        """00-overview.md "Do the tasks touch the same files?" -- "Agent teams
        don't isolate teammates in worktrees, so partition the work"; and
        03-run-agent-teams.md:360 "Avoid file conflicts"."""
        text = read(self.AGENTS)
        self.assertIn("No file isolation", text)
        self.assertIn("worktrees", text)

    def test_teammates_message_each_other_and_subagents_do_not(self):
        """00-overview.md "Do the workers need to talk to each other?" --
        subagents report back to the spawning conversation, agent view sessions
        report only to you, teammates share a task list and message directly."""
        text = read(self.AGENTS)
        self.assertIn("message each other directly", text)
        # The contrast is the whole claim: without the other half, "teammates
        # message each other" reads as a feature rather than a discriminant.
        self.assertIn("report only to whoever spawned them", text)

    def test_team_permissions_are_not_described_as_fixed_at_spawn(self):
        """03-run-agent-teams.md:255-259 and :420 -- "Teammates start with the
        lead's permission settings ... After spawning, you can change
        individual teammate modes, but you can't set per-teammate modes at
        spawn time." The first draft of this section said "fixed at spawn",
        which is the half of that sentence that is not true."""
        text = read(self.AGENTS)
        self.assertIn("cannot be set per-teammate at spawn", text)
        self.assertIn("changed afterward", text)

    def test_plugin_workflow_distribution_is_stated_correctly(self):
        """This pin held the *weaker* claim on purpose -- v6 wrote "no
        documented way for a plugin to ship a workflow" rather than "plugins
        cannot", so that the product adding it would make the sentence stale
        instead of false. v7 read the live docs and found it documented: a
        plugin ships a workflow from a `workflows/` directory at its root, or
        wherever its manifest points, and it runs as `/<plugin>:<name>`.

        So the anchor is retired deliberately, which is the review signal the
        class docstring asks for, and the caution it encoded is worth keeping
        in words: absence of documentation was never evidence, and the reason
        the weaker phrasing was right is exactly why this test could be
        updated by reading rather than by argument."""
        text = read(self.AGENTS)
        self.assertIn("A plugin ships one from a `workflows/` directory", text)
        self.assertNotIn("no documented way for a plugin to ship a workflow", text)
        self.assertNotIn("plugins cannot ship", text)

    def test_workflows_md_points_at_the_four_way_choice(self):
        self.assertIn("references/agents.md", read(self.WORKFLOWS))


class NoOrphanedHeadingsTests(unittest.TestCase):
    """v6. Two headings in agents.md announced a section and then handed the
    reader straight to the next heading -- their content had migrated into the
    frontmatter table below without the heading being removed. A heading is a
    promise about what follows, and one that promises nothing costs the reader
    a lookup and costs the table of contents its accuracy.

    This is the mechanical shadow of an edit nobody re-reads top to bottom:
    moving a paragraph out is a diff a reviewer sees, and the heading left
    behind is a diff nobody sees."""

    HEADING = re.compile(r"^(#{2,})\s")

    def _orphans(self, path):
        """A container heading may hand straight to a deeper one -- `## The
        five stages` above `### I1` promises the subsections and delivers them.
        What has no reading is a heading whose next heading is at its own depth
        or shallower: it promised a section and the section is somewhere else."""
        lines = read(path).splitlines()
        found = []
        for i, line in enumerate(lines):
            here = self.HEADING.match(line)
            if not here:
                continue
            body = next((nxt for nxt in lines[i + 1:] if nxt.strip()), "")
            after = self.HEADING.match(body)
            if not body or (after and len(after.group(1)) <= len(here.group(1))):
                found.append(f"{path.name}:{i + 1} {line}")
        return found

    def test_every_heading_is_followed_by_body_text(self):
        orphans = [o for path in REFERENCES for o in self._orphans(path)]
        self.assertEqual(orphans, [], "heading with no body before the next one")

    def test_skill_md_has_none_either(self):
        self.assertEqual(self._orphans(SKILL_MD), [])


class NoExternalToolNamesTests(unittest.TestCase):
    """D14. The shipped skill is a self-contained plugin and must not name
    Claude Code UI commands."""

    def test_no_ui_command_names(self):
        pattern = re.compile(r"doctor|checkup", re.IGNORECASE)
        for path in [SKILL_MD] + REFERENCES:
            self.assertIsNone(pattern.search(read(path)), path.name)


class NoSpecVocabularyTests(unittest.TestCase):
    """The spec file is retired. What ships must not still ask for it.

    A grep for the filename is not enough: most of the dependency was
    phrased without it -- "the spec's Validation section", "copied verbatim
    from the spec", "the record is this repo's spec" -- so a clean filename
    search is compatible with shipped instructions requiring a file no pass
    will ever write. An adversarial review found the third of those still
    shipping while an earlier version of this test passed.

    The pattern is bounded by the cases below rather than by intuition,
    because both directions cost: a miss ships a dead instruction, and a
    false positive would forbid the references from discussing rationale at
    all, which they still have to do."""

    RETIRED = re.compile(
        r"harness[-_]spec"
        r"|\bspecs?\b(?![-_ ]?(?:ify|ific))"
        r"|Behavior inventory"
        r"|Design rationale section"
        r"|inventory row"
        r"|spec drift",
        re.IGNORECASE,
    )

    MUST_MATCH = (
        "the spec's Validation section",
        "copied verbatim from the spec",
        "the record is this repo's spec",
        "before it goes in the spec",
        "read your spec before generation",
        "one row per behaviour in the Behavior inventory",
        "`.claude/harness-spec.md`",
    )
    MUST_NOT_MATCH = (
        "Explain the design rationale for this hook.",
        "state the rationale in the handoff",
        "the scenarios that count as proof",
        "a specific tool, not a general one",
        "graphify-out/ holds the generated graph",
        "Validation is what run_e2e.py does",
    )

    def test_the_pattern_catches_what_it_claims_to(self):
        for phrase in self.MUST_MATCH:
            self.assertRegex(phrase, self.RETIRED, f"would ship undetected: {phrase!r}")

    def test_the_pattern_leaves_legitimate_prose_alone(self):
        for phrase in self.MUST_NOT_MATCH:
            self.assertIsNone(self.RETIRED.search(phrase), f"false positive: {phrase!r}")

    def _shipped_text_surfaces(self):
        """Every surface a reader of the installed package meets: the skill
        body, its references, and the scripts' own docstrings, which are
        what `--help` prints."""
        for path in [SKILL_MD] + REFERENCES:
            yield path.name, read(path)
        for script in sorted((SKILL_DIR / "scripts").glob("*.py")):
            doc = ast.get_docstring(ast.parse(read(script))) or ""
            yield f"{script.name} docstring", doc

    def test_no_shipped_surface_asks_for_a_spec(self):
        surfaces = list(self._shipped_text_surfaces())
        # An empty or silently-shrunk scan passes this check while proving
        # nothing, which is the failure this whole class exists to avoid.
        self.assertGreaterEqual(len(surfaces), 1 + len(REFERENCES) + 5, surfaces)
        self.assertTrue(all(text.strip() for _, text in surfaces), surfaces)
        offenders = []
        for name, text in surfaces:
            for i, line in enumerate(text.splitlines(), 1):
                if self.RETIRED.search(line):
                    offenders.append(f"{name}:{i}: {line.strip()[:90]}")
        self.assertEqual(offenders, [], "\n".join(offenders))


class SpecRecordTests(unittest.TestCase):
    """The spec is where a decision is recorded permanently, and the two
    things that rot out of it first are the alternatives that were weighed
    and the evidence from a run nobody will repeat.

    A rationale entry that states only what was chosen reads, one
    generation later, as the only thing anyone thought of -- which is how a
    settled decision gets reopened and re-decided from scratch. And a
    verification record is the one part of this file that cannot be
    reconstructed: the sessions cost money and are gone."""

    SPEC = REPO_ROOT / ".claude" / "harness-spec.md"

    def _rationale(self):
        text = read(self.SPEC)
        return text.split("## Design rationale")[1].split("\n## ")[0]

    def test_the_three_v7_decisions_name_what_they_rejected(self):
        """D1 (delete the interview protocol), D7 (no new CLI, shape checks
        only) and D9 (measure what the model knows) each turned on an
        alternative that was live enough to need refusing."""
        rationale = self._rationale()
        for decision, anchor in (
            ("D1 interview protocol", "keeping `interview.md` as a file"),
            ("D7 no new CLI", "withdrawn"),
            ("D9 probe", "treating a transcript as evidence of isolation"),
        ):
            self.assertIn(anchor, rationale, f"{decision} lost its rejected alternative")
        self.assertGreaterEqual(
            rationale.count("Rejected:"), 2,
            "the rationale states no rejected alternatives in the marked form",
        )

    def test_the_2026_08_22_verification_record_survives(self):
        """Three headless runs, $5.30, watched once. Nothing regenerates
        this, and the interface doctrine rests on it."""
        text = read(self.SPEC)
        for anchor in (
            "Behavioural verification of the interface doctrine (2026-08-22)",
            "PASS, 3/3",
            "$5.30",
            "closes v1's risk R3",
        ):
            self.assertIn(anchor, text, anchor)

    def test_the_spec_does_not_depend_on_a_deleted_plan_tree(self):
        """`docs/plan/` is being removed. A spec that cites it as the
        binding record points at nothing; the binding record is this
        file."""
        self.assertNotIn("docs/plan", read(self.SPEC))

    def test_the_probe_result_is_recorded_as_run_or_not_run(self):
        """The one way this file can lie by omission: a tool built to
        justify deletions, with no statement of whether it ever ran."""
        text = read(self.SPEC)
        self.assertIn("probe", text.lower())
        self.assertRegex(text, r"not run|was \*\*not\*\* run|미실행")


if __name__ == "__main__":
    unittest.main(verbosity=2)
