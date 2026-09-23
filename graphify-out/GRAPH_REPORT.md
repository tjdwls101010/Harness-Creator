# Graph Report - harness-creator  (2026-09-23)

## Corpus Check
- 92 files · ~75,646 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 2)

## Summary
- 999 nodes · 1390 edges · 116 communities (52 shown, 58 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `78abd10b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Hook Event Reference Printer
- InterpretTests
- validate_harness.py
- Bad Harness Validation Tests
- TestHookIsADeliveryGateTests
- test_hook.py
- run_e2e.py
- harness_common.py
- _check_hooks_block
- Harness Creator
- add
- Hook Permission Shape Tests
- ._repo
- Script Ownership Boundary Tests
- check_skills
- test_fixture_consistency.py
- Orchestration Vocabulary Tests
- _check_one_claude_md
- PositiveFixtureTests
- Package Closure Leak Tests
- test_skill_surface.py
- HarnessHistoryTests
- _read_block_node
- test_validate_harness.py
- Audit Report Contract Tests
- Dead Pointer Link Tests
- Interface Contradiction Tests
- At-Import Parsing Tests
- Finding Consequence Clause Tests
- Heuristic False-Positive Tests
- Live Doc Agreement Tests
- Package Pointer Regression Tests
- GoodHarnessImportTests
- Finding Code Stability Tests
- always_loaded_report
- CLI Argparse Introspection
- Audit Script Self-Test
- DanglingPointerTests
- .test_a_commit_that_only_used_the_harness_is_not_found
- Repo Community Health Files
- Example Project Harness Fixtures
- .test_a_hook_body_change_counts
- Hook Timeout Fact Tests
- Packaged Skill Closure Concepts
- Bundled CLI Reachability Tests
- Workflow Example Syntax Tests
- Good Harness Audit Tests
- Component History Pathspec Tests
- Do-Not-Cut Guardrail Tests
- Spec Vocabulary Removal Tests
- Component Registry Pointer Tests
- Component Discovery Path Tests
- Frontmatter Parser Tests
- Hook Events Reference
- Orphaned Heading Tests
- Always-Loaded Report Tests
- Frontmatter Block Reader Tests
- Agent Model Field Tests
- Parallel Work Surfaces
- Hook Enforcement Semantics
- Good Harness Validation Tests
- Near-Miss False-Positive Guard
- CLAUDE.md Content Policy
- CI Gates
- Broken Workflow Fixture
- Nightly Workflow Fixture
- Example Skill Fixture
- Project Rule Fixtures
- Git Failure Handling Test
- Custom Agent Eligibility
- Skill Description Budget
- Link Validation CI
- Duplicate Agent Fixtures
- Invalid Skill Hook Fixture
- Bad Project CLAUDE.md Fixture
- Noop Hook Script Fixture
- Non-Executable Hook Fixture
- Broken Skill Fixture
- Dead Link Skill Fixture
- CLI Self-Description Fixture
- Unreadable Frontmatter Fixture
- Odd Rule Paths Fixture
- Security Reviewer Agent Fixture
- Test Gate Hook Script
- Protected Files Hook Script
- Example Workflow Fixture
- Gate Hook Script Fixture
- Log Hook Script Fixture
- Transcript Stop Gate Fixture
- Block Logging Hook Fixture
- Shared Audit Hook Fixture
- Target Check Hook Fixture
- tool.py
- Compaction Instruction Persistence
- Path-Scoped Rules
- Config Scope Levels
- Failure Feedback Routing
- Protected Claude Paths
- Harness Creator Constraints
- CI Dependency Updates
- Feature Request Template
- Link and Image Validation
- Rule Glob Test Fixtures
- Empty Skill Fixture
- Skill Metadata Fixtures
- subcommand_cli.py
- stdin_helper.py
- versioned_cli.py
- run.py
- Nested Reviewer Agent

## God Nodes (most connected - your core abstractions)
1. `read()` - 38 edges
2. `BadHarnessTests` - 38 edges
3. `HarnessHistoryTests` - 30 edges
4. `add()` - 27 edges
5. `read_text()` - 21 edges
6. `run()` - 12 edges
7. `parse_frontmatter()` - 12 edges
8. `run()` - 12 edges
9. `PositiveFixtureTests` - 12 edges
10. `AtImportParsingTests` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Audit Interview Route Generate Validate Loop` --semantically_similar_to--> `Harness Authoring Operating Loop`  [INFERRED] [semantically similar]
  README.md → .claude/skills/harness-creator/SKILL.md
- `Diátaxis Documentation Structure` --conceptually_related_to--> `Harness Creator`  [INFERRED]
  CONTRIBUTING.md → README.md
- `Harness Creator Repository Contract` --references--> `Harness Creator Meta-Skill`  [EXTRACTED]
  CLAUDE.md → .claude/skills/harness-creator/SKILL.md
- `Documentation Issue Form` --conceptually_related_to--> `Diátaxis Documentation Structure`  [INFERRED]
  .github/ISSUE_TEMPLATE/documentation.yml → CONTRIBUTING.md
- `Graphify Project Guidance` --references--> `Harness Creator`  [EXTRACTED]
  AGENTS.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **E2E Run Grade Report Flow** — _claude_skills_harness_creator_references_e2e_testing_composed_e2e_workflow, _claude_skills_harness_creator_references_e2e_testing_evidence_citation_grading, _claude_skills_harness_creator_references_e2e_testing_failure_feedback_routing [EXTRACTED 1.00]
- **Packaged skill path classification** — tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_packaged_skill, tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_target_project_paths, tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_package_internal_pointers, tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_repository_path_leaks [EXTRACTED 1.00]
- **Parallel Work Surface Choice** — _claude_skills_harness_creator_references_agents_subagents, _claude_skills_harness_creator_references_agents_agent_view, _claude_skills_harness_creator_references_agents_agent_teams, _claude_skills_harness_creator_references_agents_dynamic_workflows [EXTRACTED 1.00]

## Communities (116 total, 58 thin omitted)

### Community 0 - "Hook Event Reference Printer"
Cohesion: 0.06
Nodes (30): event_names(), load(), main(), _preamble(), Print one hook event's schema from references/hooks-events.md. hook_event.py…, Yield (event_name, {column: cell}) for the dense reference table., Yield (event_name, section_text) for the expanded events., The shared input fields every event carries, which the per-event rows… (+22 more)

### Community 1 - "InterpretTests"
Cohesion: 0.06
Nodes (7): EndToEndGoodHarnessTests, InterpretTests, MatcherMatchingTests, Self-test for test_hook.py against tests/fixtures/good-harness. python3…, v9. Overrides are top-level by design (the test above), and a hook reads its…, The example is the thing that was wrong, so assert on it directly: prose in…, SampleInputTests

### Community 2 - "validate_harness.py"
Cohesion: 0.16
Nodes (14): _check_claude_local_ignored(), check_claude_md(), _git_says_ignored(), _gitignore_covers(), is_plausible_model(), _node_available(), Rewrite a workflow script into a form node can syntax-check. Two things are…, (ignored, tracked) from git itself, or None when git is unavailable. (+6 more)

### Community 3 - "Bad Harness Validation Tests"
Cohesion: 0.08
Nodes (6): BadHarnessTests, v7 moved the anchor off "no tool_input", which described why the docs' rule…, references/skills.md's `hooks` row -- a skill's frontmatter declares hooks with…, references/hooks.md:150 -- a trailing `*` preceded by a space enforces a word…, references/hooks.md:110 -- file permission checks consult `Edit(path)` and…, references/hooks.md:140-144 -- since v2.1.142 a project settings.json setting…

### Community 4 - "TestHookIsADeliveryGateTests"
Cohesion: 0.07
Nodes (15): NestedFrontmatterTests, PluginSkillDiscoveryTests, references/hooks.md, skills.md and agents.md all teach a `hooks:` block in a…, v6. Refusing to guess at a nested shape and throwing the text away are…, `--model`'s help said "default: whatever the invoking session uses". Nothing…, Claims the package makes about its own code, checked against the code. python3…, A plugin's skills live at `./skills` unless plugin.json says otherwise, and…, `skills/` is an ordinary directory name. Without a plugin manifest it means… (+7 more)

### Community 5 - "test_hook.py"
Cohesion: 0.18
Nodes (16): is_exact_matcher(), True if `matcher` stays in exact-string/list mode; False if any character…, build_sample_input(), cmd_matrix(), _event_fields(), find_matching_groups(), interpret(), main() (+8 more)

### Community 6 - "run_e2e.py"
Cohesion: 0.07
Nodes (19): build_command(), discard_isolated(), isolate_project(), main(), parse_stream(), Spawn a headless Claude Code session against a project and record what…, Remove an isolated copy, including the mkdtemp parent that holds it. A copy of…, Runs `claude -p` and returns (raw_lines, error). error is None on a clean… (+11 more)

### Community 8 - "harness_common.py"
Cohesion: 0.05
Nodes (60): check_user_scope_conflicts(), _file_summary(), _foreign_instruction_files(), _git(), _git_root(), harness_history(), harness_history_paths(), hygiene_signals() (+52 more)

### Community 9 - "_check_hooks_block"
Cohesion: 0.17
Nodes (12): _check_bare_mcp_matcher(), _check_command_script_exists(), _check_hooks_block(), _check_stop_loop_guard(), _has_unquoted_placeholder(), _hook_script_path(), `once_honored` is True only for a skill's frontmatter; settings files and agent…, A placeholder inside double quotes survives shell re-tokenization; a bare one… (+4 more)

### Community 10 - "Harness Creator"
Cohesion: 0.07
Nodes (28): E2E Assertion Types, Composed E2E Workflow, Harness E2E Validation, Evidence-Citation Grading Doctrine, Isolated Headless Execution, Packaged Skill Self-Containment, Parameterized Bundled Scripts, Three-Stage Skill Disclosure (+20 more)

### Community 11 - "add"
Cohesion: 0.20
Nodes (18): is_known_tool_token(), load_json_lenient(), Parse a JSON file, returning (data, error_message). error_message is None on…, True if `token` is a canonical tool name or an mcp__ pattern -- used to avoid…, read_text(), add(), check_agents(), _check_catch_all_glob() (+10 more)

### Community 12 - "Hook Permission Shape Tests"
Cohesion: 0.09
Nodes (12): by_code(), NearMissTests, PositiveFixtureTests, hooks, Stop input: "The `stop_hook_active` field is `true` when Claude Code is…, hooks, exec form and shell form: "Set `args` whenever the hook references a…, Shapes that look like one of the five and are correct: a permission rule…, permissions: Read/Edit rules follow gitignore, where `*` does not cross a path…, Shape checks V02-V05 and V15 in validate_harness.py: hooks and permissions.… (+4 more)

### Community 13 - "._repo"
Cohesion: 0.13
Nodes (9): A throwaway repository. Real git, because the three things that actually broke…, No harness commit exists" and "this project has no history at all" lead a pass…, Measured: a pathspec that matches from one directory matches nothing from…, Feature work that adds a build command to CLAUDE.md really did change the…, A report that silently stops at N reads as a project with N harness commits.…, A project set up before this tool kept its record in git has one file holding…, At a shallow boundary git treats the cut-off commit as a root, so every file in…, There is no repository here" is a fact about the project; "git did not run" is… (+1 more)

### Community 14 - "Script Ownership Boundary Tests"
Cohesion: 0.12
Nodes (13): env_with_fake_claude(), HonestApproximationTests, NoPolicyOrHistoryInScriptsTests, test_hook.py approximates a JavaScript RegExp with Python `re`, and its input…, Mode combinations that cannot mean anything are refused by argparse, with exit…, The five bundled CLIs own what is valid, what they do and what they print; the…, run_e2e.py spawns `claude`; a usage-error test must never reach a real session,…, Every string constant inside an expression, so a help= built by concatenation… (+5 more)

### Community 15 - "check_skills"
Cohesion: 0.19
Nodes (13): iter_skill_dirs(), Yield each skill directory under root. `.claude/skills/` always, plus whatever…, _check_dead_links(), _check_package_closure(), check_skill_scripts(), check_skills(), iter_skill_pointers(), packaged_skill_dirs() (+5 more)

### Community 16 - "test_fixture_consistency.py"
Cohesion: 0.11
Nodes (11): AgentWritePathIsStatedTests, BashWritePathIsCoveredTests, HookProseIsAnchoredToTheHookTests, references/hooks.md documents that a Bash-driven edit (`sed -i`, `echo >>…, An agent body replaces the system prompt entirely, so it is the only place the…, Consistency tests for tests/fixtures/good-harness. python3 -m unittest discover…, A sentence describing a hook must name the script that implements it. Not a…, test_hook.py executes these for real, and a non-executable hook fails at the… (+3 more)

### Community 17 - "Orchestration Vocabulary Tests"
Cohesion: 0.13
Nodes (11): NoModeVocabularyTests, OrchestrationChoiceTests, The four-mode classification (new/extend/improve/sync) and the I1-I5 stage…, v6. The skill covered subagents and workflows and never said which of the four…, 00-overview.md "Choose an approach": "Who coordinates the work?" with four…, 03-run-agent-teams.md:10,54 -- "disabled by default ... Without that variable,…, 00-overview.md "Do the tasks touch the same files?" -- "Agent teams don't…, 00-overview.md "Do the workers need to talk to each other?" -- subagents report… (+3 more)

### Community 18 - "_check_one_claude_md"
Cohesion: 0.22
Nodes (9): iter_agent_files(), Yield each `.claude/agents/**/*.md` file under root., _check_at_imports(), _check_generic_advice(), _check_inventory_listing(), _check_one_claude_md(), _normalize_advice(), Every @import in an instruction file has to resolve, because a missing one… (+1 more)

### Community 19 - "PositiveFixtureTests"
Cohesion: 0.07
Nodes (18): by_code(), ClaudeLocalGitignoreTests, NearMissTests, PositiveFixtureTests, skills, string substitutions: `${CLAUDE_SKILL_DIR}` is substituted in skill…, memory, rules: a rule's `paths` frontmatter is what scopes it, and a block the…, memory, Path-specific rules: the documented shape is a YAML list under…, One invalid shape per case, plus valid shapes that look invalid. (+10 more)

### Community 20 - "Package Closure Leak Tests"
Cohesion: 0.15
Nodes (7): PackageClosureTests, This one reaches the end user: a module docstring is what `--help` prints., The paths a harness-building skill names constantly. Each one describes a file…, good-harness has no plugin manifest, so the same shape of pointer there is a…, `https://docs.python.org/3/?source=references/install.md` names a query…, A plugin-packaged skill travels as one directory. A pointer out of it resolves…, An adversarial pass built three correct plugins this flags: a skill telling the…

### Community 21 - "test_skill_surface.py"
Cohesion: 0.13
Nodes (10): FenceBalanceTests, GotchaCountTests, NoExternalToolNamesTests, B10. agents.md opened a ```markdown fence and never closed it, so renderers and…, Deleted references must not remain dependencies of the shipped package., v7 deleted interview.md: its protocol (modes, stages, scripts) was a rail the…, Regression tests for the shipped skill surface itself (SKILL.md + references/).…, A count in a heading is a number that goes stale the moment someone adds or… (+2 more)

### Community 22 - "HarnessHistoryTests"
Cohesion: 0.14
Nodes (8): HarnessHistoryTests, The record of why a harness looks the way it does now lives in the commits that…, Three outcomes have to stay apart: no repository, a repository with no matching…, Two definitions of "harness component" -- one that inventories the disk, one…, The history is about to become the record, and a record whose limits are…, `@file` pulls another file into every session, so editing it changes what the…, A project can keep its reasons somewhere this search cannot reach. Saying the…, The framing bytes have to be ones the data cannot contain. A subject may hold…

### Community 23 - "_read_block_node"
Cohesion: 0.24
Nodes (10): _block_scalar(), _BlockShapeError, _check_skill_frontmatter_hooks(), The block is outside the subset below. Never a guess -- a wrong reading reports…, Read the nested mapping/sequence subset a frontmatter `hooks:` block uses.…, A skill's frontmatter declares hooks with the same event/matcher/handler shape…, _read_block(), _read_block_node() (+2 more)

### Community 24 - "test_validate_harness.py"
Cohesion: 0.17
Nodes (5): CliEdgeCaseTests, MatcherHelperTests, MessageRepairTests, Self-test for validate_harness.py against tests/fixtures/{good,bad}-harness.…, argparse shapes that are correct but look like omissions. Kept out of good-…

### Community 25 - "Audit Report Contract Tests"
Cohesion: 0.17
Nodes (5): The structured result is not what a pass reads. If the rendered report…, The report is bounded by a path list, and a reader who does not know the bounds…, The audit checks existence, not content. Saying so on every run is what keeps a…, run_cli(), ScopeAndJsonContractTests

### Community 26 - "Dead Pointer Link Tests"
Cohesion: 0.24
Nodes (5): DeadLinkCoverageTests, B7. Hard line 1 claimed validate_harness.py checked pointers mechanically, but…, Every shipped reference is reachable, directly or through another reference, by…, v5. The pattern captured one path segment, so a pointer into a subdirectory was…, The mirror-image failure, and the worse one: a check that fires on a correct…

### Community 27 - "Interface Contradiction Tests"
Cohesion: 0.20
Nodes (6): InterfaceContradictionTests, v5. Prose that asserts how a bundled script *currently behaves* is a claim…, The fact the prose has to agree with. If this ever flips to opt-out, the prose…, `--permission-mode` exists and is the direct answer to the headless-permissions…, The same shape one file over. agents.md said `tools:` "already enforces" read-…, `--dangerously-skip-permissions` belongs to the `claude` CLI that run_e2e.py…

### Community 29 - "Finding Consequence Clause Tests"
Cohesion: 0.21
Nodes (6): ConsequenceClauseTests, v3 attached a consequence to the findings that could carry one, on the theory…, Documented: a rule loads only when Claude reads a file its `paths:` matches. A…, The documented reason for the 500-line guideline is that a skill's body stays…, Sourced in references/skills.md: an argument without `help=` prints as a bare…, The three the v3 plan wanted to annotate and the docs would not support.…

### Community 31 - "Live Doc Agreement Tests"
Cohesion: 0.18
Nodes (6): LiveDocAgreementTests, Gate B, 2026-09-04. Three checks and one message had drifted from the…, code.claude.com/docs/en/sub-agents#available-tools (2026-09-04) lists nine…, `ExitPlanMode` survives the filter only in a subagent whose `permissionMode` is…, docs/en/hooks#hook-handler-fields: "On other events, a hook with `if` set never…, docs/en/skills#frontmatter-reference: "If omitted, uses the first paragraph of…

### Community 32 - "Package Pointer Regression Tests"
Cohesion: 0.24
Nodes (6): PackageClosureRegressionTests, v5 closed thirteen pointers that led out of the shipped package. Six were…, `D12` is not bad because it is short. It is bad because nothing in the…, The one case the shipped check structurally cannot see. Package closure asks…, Derived from the plan tree rather than hardcoded, so a pointer at any…, skills.md sent the reader to hooks.md's "Hooks in skills and agents", which is…

### Community 34 - "Finding Code Stability Tests"
Cohesion: 0.24
Nodes (4): FindingCodeTests, Checks added from v7 on carry a stable code so a fixture can assert exactly…, A code is an identifier a reader looks up, and reports quoting `V01` outlive…, The tests below assert how a code travels, not which one. They stop asserting…

### Community 35 - "always_loaded_report"
Cohesion: 0.40
Nodes (6): findings_to_json(), always_loaded_report(), add_file(), main(), print_always_loaded_report(), Measure what enters context on every session, before the first prompt. A…

### Community 36 - "CLI Argparse Introspection"
Cohesion: 0.22
Nodes (10): _action_value(), _arg_label(), _check_cli_self_description(), _is_module_doc(), _is_parser_construction(), _keyword(), The flag or positional name an add_argument call declares., `argparse.ArgumentParser(...)` in either import style. (+2 more)

### Community 37 - "Audit Script Self-Test"
Cohesion: 0.20
Nodes (3): BadHarnessAuditTests, EmptyProjectAuditTests, Self-test for audit_harness.py against tests/fixtures/{good,bad}-harness.…

### Community 40 - "Repo Community Health Files"
Cohesion: 0.28
Nodes (9): Bug Report Form, Issue Routing Configuration, Pull Request Change Assurance, Contributor Covenant 3.0, Community Enforcement Ladder, Harness Creator Contribution Workflow, Private Vulnerability Reporting, Harness Creator Security Policy (+1 more)

### Community 41 - "Example Project Harness Fixtures"
Cohesion: 0.22
Nodes (9): Append-only database migrations, Database migration policy, Example project instructions, Protected-files hook, Raw SQL prohibition and query-builder rule, Test-gate hook, Public project overview, Deploy guard (+1 more)

### Community 43 - "Hook Timeout Fact Tests"
Cohesion: 0.22
Nodes (3): B5. hooks-events.md called both MessageDisplay (10s) and SessionEnd (1.5s) 'the…, v9. The count itself is the recurring defect, not any particular value of it:…, TimeoutFactsTests

### Community 44 - "Packaged Skill Closure Concepts"
Cohesion: 0.25
Nodes (8): Packaged reference, Package-internal pointers, Packaged skill, Repository path leaks, Target-project paths, Plugin skill self-containment requirement, External design note, External internal-decision log

### Community 45 - "Bundled CLI Reachability Tests"
Cohesion: 0.29
Nodes (5): BundledCliCoverageTests, Follow shipped Markdown pointers from the skill's entry point., Bundled CLIs remain discoverable wherever the skill routes to them., Which bundled scripts are CLIs, read from the source rather than listed here --…, reachable_skill_pointers()

### Community 46 - "Workflow Example Syntax Tests"
Cohesion: 0.39
Nodes (3): B12, found while trimming the examples in WS6. The node syntax gate checked the…, The examples in references/ must survive the linter that this skill tells the…, WorkflowSyntaxProbeTests

### Community 48 - "Component History Pathspec Tests"
Cohesion: 0.29
Nodes (3): Why the pathspec is directory patterns and not the files discovery finds today:…, Measured on this repository: five merges match the pathspec and all five list…, Deleting the last skill under a declared root removes the directory, and a path…

### Community 49 - "Do-Not-Cut Guardrail Tests"
Cohesion: 0.29
Nodes (4): GuardrailTests, The do-not-cut list from the audit (audit-synthesis.md section 4), plus the…, R3. The event router is what makes the hooks.md/hooks-events.md split safe --…, This anchor was retired deliberately, which is the review signal the class…

### Community 50 - "Spec Vocabulary Removal Tests"
Cohesion: 0.33
Nodes (3): NoSpecVocabularyTests, The spec file is retired. What ships must not still ask for it. A grep for the…, Every surface a reader of the installed package meets: the skill body, its…

### Community 51 - "Component Registry Pointer Tests"
Cohesion: 0.29
Nodes (4): PointerReaderTests, v5 removed CLAUDE.md's pointer at `.claude/harness-spec.md`. The policy…, v7 (disposition C25) reworded the sentence this anchored: the ban is now on the…, The example is what a reader copies, so a registry line here would ship the…

### Community 54 - "Hook Events Reference"
Cohesion: 0.33
Nodes (6): Thirty Hook Events Reference, PostToolUse Hook Event, PreToolUse Hook Event, SessionStart Hook Event, Stop Hook Event, Hook Event Router

### Community 55 - "Orphaned Heading Tests"
Cohesion: 0.47
Nodes (3): NoOrphanedHeadingsTests, v6. Two headings in agents.md announced a section and then handed the reader…, A container heading may hand straight to a deeper one -- `## The five stages`…

### Community 59 - "Parallel Work Surfaces"
Cohesion: 0.40
Nodes (5): Agent Teams, Agent View, Dynamic Workflows, Four Parallel-Work Surfaces, Subagents

### Community 60 - "Hook Enforcement Semantics"
Cohesion: 0.40
Nodes (5): Deterministic Enforcement Layer, Hook Exit-Code Contract, Hook Eligibility Test, Hook Matcher Semantics, Permission Rule and Hook Pair

### Community 65 - "CLAUDE.md Content Policy"
Cohesion: 0.67
Nodes (3): CLAUDE.md as Advisory Instructions, CLAUDE.md Content Eligibility Test, Filesystem-as-Inventory Pointer Policy

### Community 66 - "CI Gates"
Cohesion: 0.67
Nodes (3): CI Pipeline, Harness Validation Gate, Unit Test Gate

### Community 71 - "Example Skill Fixture"
Cohesion: 0.67
Nodes (3): Example skill full procedure, Example skill, Retry-only API idempotency

### Community 72 - "Project Rule Fixtures"
Cohesion: 0.67
Nodes (3): Dot-claude project instructions, Always-loaded frontend style rule, Path-scoped TypeScript rule

## Knowledge Gaps
- **83 isolated node(s):** `noop.sh script`, `not-executable.sh script`, `meta`, `stamp`, `meta` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 498 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **58 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HarnessHistoryTests` connect `HarnessHistoryTests` to `Audit Script Self-Test`, `.test_a_commit_that_only_used_the_harness_is_not_found`, `Git Failure Handling Test`, `.test_a_hook_body_change_counts`, `._repo`, `Component History Pathspec Tests`, `Audit Report Contract Tests`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `BadHarnessTests` connect `Bad Harness Validation Tests` to `test_validate_harness.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `read()` connect `Orchestration Vocabulary Tests` to `Package Pointer Regression Tests`, `DanglingPointerTests`, `Hook Timeout Fact Tests`, `Bundled CLI Reachability Tests`, `Do-Not-Cut Guardrail Tests`, `Spec Vocabulary Removal Tests`, `Component Registry Pointer Tests`, `test_skill_surface.py`, `Orphaned Heading Tests`, `Dead Pointer Link Tests`, `Interface Contradiction Tests`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **What connects `noop.sh script`, `not-executable.sh script`, `meta` to the rest of the system?**
  _83 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Hook Event Reference Printer` be split into smaller, more focused modules?**
  _Cohesion score 0.05585106382978723 - nodes in this community are weakly interconnected._
- **Should `InterpretTests` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
- **Should `Bad Harness Validation Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.08305647840531562 - nodes in this community are weakly interconnected._