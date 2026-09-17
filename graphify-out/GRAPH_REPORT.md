# Graph Report - harness-creator  (2026-09-17)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1123 nodes · 1613 edges · 122 communities (57 shown, 54 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.86)
- Token cost: 113,975 input · 1,973 output

## Graph Freshness
- Built from commit: `53ecd468`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Hook Event Reference Printer
- Hook Unit Testing CLI
- Harness Validation Checks
- Bad Harness Validation Tests
- Skill Interface Claim Tests
- Claims Extraction Checker Tests
- Headless E2E Session Runner
- Probe CLI Tests
- Shared Harness Script Utilities
- Reference Claims Freezer
- E2E and Workflow Doctrine
- Harness Inventory Audit
- Hook Permission Shape Tests
- Harness Git History Tests
- Script Ownership Boundary Tests
- Skill and Plugin Discovery
- Fixture Consistency Tests
- Orchestration Vocabulary Tests
- Harness Measurement Probe CLI
- Component Shape Code Tests
- Package Closure Leak Tests
- Shipped Skill Surface Tests
- Harness History Audit Tests
- Agent Frontmatter Validation
- Validator Self-Test Suite
- Audit Report Contract Tests
- Dead Pointer Link Tests
- Interface Contradiction Tests
- At-Import Parsing Tests
- Finding Consequence Clause Tests
- Heuristic False-Positive Tests
- Live Doc Agreement Tests
- Package Pointer Regression Tests
- Spec Decision Record Tests
- Finding Code Stability Tests
- Always-Loaded Context Report
- CLI Argparse Introspection
- Audit Script Self-Test
- Workflow Shape Checks
- Claude Local Gitignore Checks
- Repo Community Health Files
- Example Project Harness Fixtures
- Workflow Shape Boundary Tests
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
- Retired Reference Tests
- CLI Edge Case Fixtures
- CLAUDE.md Content Policy
- CI Gates
- Unparsed Frontmatter Block
- Broken Workflow Fixture
- Golden Source Fixture
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
- Compaction Instruction Persistence
- Path-Scoped Rules
- Config Scope Levels
- Failure Feedback Routing
- Protected Claude Paths
- Harness Creator Constraints
- CI Dependency Updates
- Feature Request Template
- Link and Image Validation
- Release History Changelog
- Rule Glob Test Fixtures
- Empty Skill Fixture
- Skill Metadata Fixtures
- Nested Reviewer Agent

## God Nodes (most connected - your core abstractions)
1. `read()` - 42 edges
2. `BadHarnessTests` - 38 edges
3. `HarnessHistoryTests` - 30 edges
4. `add()` - 27 edges
5. `read_text()` - 21 edges
6. `CheckTests` - 16 edges
7. `QuizTests` - 16 edges
8. `PositiveFixtureTests` - 12 edges
9. `AtImportParsingTests` - 12 edges
10. `HeuristicFalsePositiveTests` - 12 edges

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

## Communities (122 total, 54 thin omitted)

### Community 0 - "Hook Event Reference Printer"
Cohesion: 0.06
Nodes (30): event_names(), load(), main(), _preamble(), Print one hook event's schema from references/hooks-events.md. hook_event.py…, Yield (event_name, {column: cell}) for the dense reference table., Yield (event_name, section_text) for the expanded events., The shared input fields every event carries, which the per-event rows… (+22 more)

### Community 1 - "Hook Unit Testing CLI"
Cohesion: 0.05
Nodes (21): build_sample_input(), cmd_matrix(), _event_fields(), find_matching_groups(), interpret(), main(), matches_matcher(), Approximate Claude Code's matcher evaluation (references/hooks.md): exact-… (+13 more)

### Community 2 - "Harness Validation Checks"
Cohesion: 0.09
Nodes (45): add(), _check_at_imports(), _check_bare_mcp_matcher(), _check_catch_all_glob(), _check_claude_local_ignored(), check_claude_md(), _check_command_script_exists(), _check_deny_subsumes_allow() (+37 more)

### Community 3 - "Bad Harness Validation Tests"
Cohesion: 0.08
Nodes (6): BadHarnessTests, v7 moved the anchor off "no tool_input", which described why the docs' rule…, references/skills.md's `hooks` row -- a skill's frontmatter declares hooks with…, references/hooks.md:150 -- a trailing `*` preceded by a space enforces a word…, references/hooks.md:110 -- file permission checks consult `Edit(path)` and…, references/hooks.md:140-144 -- since v2.1.142 a project settings.json setting…

### Community 4 - "Skill Interface Claim Tests"
Cohesion: 0.07
Nodes (14): NestedFrontmatterTests, PluginSkillDiscoveryTests, references/hooks.md, skills.md and agents.md all teach a `hooks:` block in a…, v6. Refusing to guess at a nested shape and throwing the text away are…, `--model`'s help said "default: whatever the invoking session uses". Nothing…, A plugin's skills live at `./skills` unless plugin.json says otherwise, and…, `skills/` is an ordinary directory name. Without a plugin manifest it means…, Reference-to-reference pointers were scanned only in `*.md`, while a reference… (+6 more)

### Community 5 - "Claims Extraction Checker Tests"
Cohesion: 0.11
Nodes (7): CheckTests, ExtractTests, HelpTests, Tests for tools/claims.py at its CLI seam, against a hand-read golden source.…, The same rule this repo's validate_harness.py applies to bundled scripts,…, The heuristic misses "Every rule loads at launch." -- a claim with no marker. A…, run()

### Community 6 - "Headless E2E Session Runner"
Cohesion: 0.07
Nodes (18): build_command(), discard_isolated(), isolate_project(), main(), parse_stream(), Spawn a headless Claude Code session against a project and record what…, Remove an isolated copy, including the mkdtemp parent that holds it. A copy of…, Runs `claude -p` and returns (raw_lines, error). error is None on a clean… (+10 more)

### Community 7 - "Probe CLI Tests"
Cohesion: 0.11
Nodes (10): ContrastTests, HelpTests, ProbeTestCase, QuizTests, --bare skips OAuth, so a machine without ANTHROPIC_API_KEY needs the documented…, The first real smoke run recorded `Not logged in` as a normal answer with error…, Tests for tools/probe.py, the gotcha knowledge probe. python3 -m unittest…, Same wrapper both times, so an observed difference is attributable to the… (+2 more)

### Community 8 - "Shared Harness Script Utilities"
Cohesion: 0.08
Nodes (25): Finding, Frontmatter, is_exact_matcher(), iter_agent_files(), iter_rule_files(), iter_workflow_files(), mask_code(), parse_at_imports() (+17 more)

### Community 9 - "Reference Claims Freezer"
Cohesion: 0.13
Nodes (26): anchor_count(), anchor_present(), check(), cmd_check(), cmd_extract(), extract(), _is_separator_row(), _load_claims() (+18 more)

### Community 10 - "E2E and Workflow Doctrine"
Cohesion: 0.08
Nodes (27): E2E Assertion Types, Composed E2E Workflow, Harness E2E Validation, Evidence-Citation Grading Doctrine, Isolated Headless Execution, Packaged Skill Self-Containment, Parameterized Bundled Scripts, Three-Stage Skill Disclosure (+19 more)

### Community 11 - "Harness Inventory Audit"
Cohesion: 0.16
Nodes (26): check_user_scope_conflicts(), _file_summary(), _foreign_instruction_files(), _git(), _git_root(), harness_history(), hygiene_signals(), inventory_agents() (+18 more)

### Community 12 - "Hook Permission Shape Tests"
Cohesion: 0.09
Nodes (12): by_code(), NearMissTests, PositiveFixtureTests, hooks, Stop input: "The `stop_hook_active` field is `true` when Claude Code is…, hooks, exec form and shell form: "Set `args` whenever the hook references a…, Shapes that look like one of the five and are correct: a permission rule…, permissions: Read/Edit rules follow gitignore, where `*` does not cross a path…, Shape checks V02-V05 and V15 in validate_harness.py: hooks and permissions.… (+4 more)

### Community 13 - "Harness Git History Tests"
Cohesion: 0.11
Nodes (11): A throwaway repository. Real git, because the three things that actually broke…, The distinction the whole report rests on. Work done *with* a harness edits the…, No harness commit exists" and "this project has no history at all" lead a pass…, Measured: a pathspec that matches from one directory matches nothing from…, A hook whose settings entry never moves still changes what the harness…, Feature work that adds a build command to CLAUDE.md really did change the…, A report that silently stops at N reads as a project with N harness commits.…, A project set up before this tool kept its record in git has one file holding… (+3 more)

### Community 14 - "Script Ownership Boundary Tests"
Cohesion: 0.12
Nodes (13): env_with_fake_claude(), HonestApproximationTests, NoPolicyOrHistoryInScriptsTests, test_hook.py approximates a JavaScript RegExp with Python `re`, and its input…, Mode combinations that cannot mean anything are refused by argparse, with exit…, The five bundled CLIs own what is valid, what they do and what they print; the…, run_e2e.py spawns `claude`; a usage-error test must never reach a real session,…, Every string constant inside an expression, so a help= built by concatenation… (+5 more)

### Community 15 - "Skill and Plugin Discovery"
Cohesion: 0.10
Nodes (23): harness_history_paths(), The pathspec to search, relative to root. Fixed component paths plus whatever…, declared_plugin_skills_roots(), iter_skill_dirs(), load_json_lenient(), plugin_skills_roots(), Parse a JSON file, returning (data, error_message). error_message is None on…, Resolve an @import target to a Path, or None if it is not project-relative.… (+15 more)

### Community 16 - "Fixture Consistency Tests"
Cohesion: 0.11
Nodes (10): AgentWritePathIsStatedTests, BashWritePathIsCoveredTests, HookProseIsAnchoredToTheHookTests, references/hooks.md documents that a Bash-driven edit (`sed -i`, `echo >>…, An agent body replaces the system prompt entirely, so it is the only place the…, A sentence describing a hook must name the script that implements it. Not a…, test_hook.py executes these for real, and a non-executable hook fails at the…, sentences() (+2 more)

### Community 17 - "Orchestration Vocabulary Tests"
Cohesion: 0.13
Nodes (11): NoModeVocabularyTests, OrchestrationChoiceTests, The four-mode classification (new/extend/improve/sync) and the I1-I5 stage…, v6. The skill covered subagents and workflows and never said which of the four…, 00-overview.md "Choose an approach": "Who coordinates the work?" with four…, 03-run-agent-teams.md:10,54 -- "disabled by default ... Without that variable,…, 00-overview.md "Do the tasks touch the same files?" -- "Agent teams don't…, 00-overview.md "Do the workers need to talk to each other?" -- subagents report… (+3 more)

### Community 18 - "Harness Measurement Probe CLI"
Cohesion: 0.20
Nodes (18): build_command(), Claude, cmd_contrast(), cmd_quiz(), contrast_prompt(), _drift(), _fresh_out_dir(), load_questions() (+10 more)

### Community 19 - "Component Shape Code Tests"
Cohesion: 0.15
Nodes (9): PositiveFixtureTests, skills, string substitutions: `${CLAUDE_SKILL_DIR}` is substituted in skill…, memory, rules: a rule's `paths` frontmatter is what scopes it, and a block the…, memory, Path-specific rules: the documented shape is a YAML list under…, sub-agents, Available tools: "The following tools depend on the main…, hooks, handler fields: "`once` -- If `true`, runs once per session then is…, sub-agents, memory: "When memory is enabled: ... Read, Write, and Edit tools…, Agent SDK TypeScript reference, Workflow tool: "Must begin with `export const… (+1 more)

### Community 20 - "Package Closure Leak Tests"
Cohesion: 0.15
Nodes (7): PackageClosureTests, This one reaches the end user: a module docstring is what `--help` prints., The paths a harness-building skill names constantly. Each one describes a file…, good-harness has no plugin manifest, so the same shape of pointer there is a…, `https://docs.python.org/3/?source=references/install.md` names a query…, A plugin-packaged skill travels as one directory. A pointer out of it resolves…, An adversarial pass built three correct plugins this flags: a skill telling the…

### Community 21 - "Shipped Skill Surface Tests"
Cohesion: 0.13
Nodes (9): DanglingPointerTests, FenceBalanceTests, GotchaCountTests, NoExternalToolNamesTests, B10. agents.md opened a ```markdown fence and never closed it, so renderers and…, Regression tests for the shipped skill surface itself (SKILL.md + references/).…, A count in a heading is a number that goes stale the moment someone adds or…, D14. The shipped skill is a self-contained plugin and must not name Claude Code… (+1 more)

### Community 22 - "Harness History Audit Tests"
Cohesion: 0.14
Nodes (8): HarnessHistoryTests, The record of why a harness looks the way it does now lives in the commits that…, Three outcomes have to stay apart: no repository, a repository with no matching…, Two definitions of "harness component" -- one that inventories the disk, one…, The history is about to become the record, and a record whose limits are…, `@file` pulls another file into every session, so editing it changes what the…, A project can keep its reasons somewhere this search cannot reach. Saying the…, A plugin manifest names a directory; git reads a pathspec. A name starting with…

### Community 23 - "Agent Frontmatter Validation"
Cohesion: 0.18
Nodes (13): is_known_tool_token(), True if `token` is a canonical tool name or an mcp__ pattern -- used to avoid…, _block_scalar(), _BlockShapeError, check_agents(), is_plausible_model(), The block is outside the subset below. Never a guess -- a wrong reading reports…, Read the nested mapping/sequence subset a frontmatter `hooks:` block uses.… (+5 more)

### Community 24 - "Validator Self-Test Suite"
Cohesion: 0.15
Nodes (5): GoodHarnessImportTests, MatcherHelperTests, MessageRepairTests, Self-test for validate_harness.py against tests/fixtures/{good,bad}-harness.…, The good-harness fixture carries all four traps in one file. It must exit 0 and…

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

### Community 33 - "Spec Decision Record Tests"
Cohesion: 0.20
Nodes (6): The spec is where a decision is recorded permanently, and the two things that…, D1 (delete the interview protocol), D7 (no new CLI, shape checks only) and D9…, Three headless runs, $5.30, watched once. Nothing regenerates this, and the…, `docs/plan/` is being removed. A spec that cites it as the binding record…, The one way this file can lie by omission: a tool built to justify deletions,…, SpecRecordTests

### Community 34 - "Finding Code Stability Tests"
Cohesion: 0.24
Nodes (4): FindingCodeTests, Checks added from v7 on carry a stable code so a fixture can assert exactly…, A code is an identifier a reader looks up, and reports quoting `V01` outlive…, The tests below assert how a code travels, not which one. They stop asserting…

### Community 35 - "Always-Loaded Context Report"
Cohesion: 0.22
Nodes (10): claude_md_paths(), findings_to_json(), print_findings_text(), Return the project-scope instruction files that exist at the root. A project…, findings: list of (level, location, message) where level is 'E' or 'W'. Human-…, always_loaded_report(), add_file(), main() (+2 more)

### Community 36 - "CLI Argparse Introspection"
Cohesion: 0.22
Nodes (10): _action_value(), _arg_label(), _check_cli_self_description(), _is_module_doc(), _is_parser_construction(), _keyword(), The flag or positional name an add_argument call declares., `argparse.ArgumentParser(...)` in either import style. (+2 more)

### Community 37 - "Audit Script Self-Test"
Cohesion: 0.20
Nodes (3): BadHarnessAuditTests, EmptyProjectAuditTests, Self-test for audit_harness.py against tests/fixtures/{good,bad}-harness.…

### Community 38 - "Workflow Shape Checks"
Cohesion: 0.20
Nodes (4): NearMissTests, Shape checks V06-V14 in validate_harness.py (agents, workflows, rules,…, workflows, save locations: "If a project workflow and a personal workflow share…, WorkflowNameCollisionTests

### Community 39 - "Claude Local Gitignore Checks"
Cohesion: 0.40
Nodes (3): by_code(), ClaudeLocalGitignoreTests, memory, CLAUDE.md locations: "Local instructions -- `./CLAUDE.local.md` --…

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

### Community 63 - "Retired Reference Tests"
Cohesion: 0.50
Nodes (3): Deleted references must not remain dependencies of the shipped package., v7 deleted interview.md: its protocol (modes, stages, scripts) was a rail the…, RetiredReferenceTests

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
- **85 isolated node(s):** `meta`, `stamp`, `Loading`, `files`, `meta` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 528 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **54 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HarnessHistoryTests` connect `Harness History Audit Tests` to `Audit Script Self-Test`, `Git Failure Handling Test`, `Harness Git History Tests`, `Component History Pathspec Tests`, `Audit Report Contract Tests`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `read()` connect `Orchestration Vocabulary Tests` to `Package Pointer Regression Tests`, `Spec Decision Record Tests`, `Hook Timeout Fact Tests`, `Bundled CLI Reachability Tests`, `Do-Not-Cut Guardrail Tests`, `Spec Vocabulary Removal Tests`, `Component Registry Pointer Tests`, `Shipped Skill Surface Tests`, `Orphaned Heading Tests`, `Dead Pointer Link Tests`, `Interface Contradiction Tests`, `Retired Reference Tests`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `BadHarnessTests` connect `Bad Harness Validation Tests` to `Validator Self-Test Suite`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **What connects `meta`, `stamp`, `Loading` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Hook Event Reference Printer` be split into smaller, more focused modules?**
  _Cohesion score 0.05585106382978723 - nodes in this community are weakly interconnected._
- **Should `Hook Unit Testing CLI` be split into smaller, more focused modules?**
  _Cohesion score 0.05217391304347826 - nodes in this community are weakly interconnected._
- **Should `Harness Validation Checks` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._