# Graph Report - harness-creator  (2026-09-08)

## Corpus Check
- 98 files · ~78,704 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1093 nodes · 1515 edges · 124 communities (51 shown, 61 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `345f7e39`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- validate_harness.py
- CI Pipeline
- harness_common.py
- BadHarnessTests
- test_hook.py
- Frontmatter and Skill Discovery Tests
- OutputTests
- run_e2e.py
- PositiveFixtureTests
- Example project instructions
- Fixture Consistency Tests
- read
- CheckTests
- QuizTests
- claims.py
- audit_harness.py
- PositiveFixtureTests
- PackageClosureTests
- run
- ConsequenceClauseTests
- probe.py
- InterfaceContradictionTests
- AtImportParsingTests
- HeuristicFalsePositiveTests
- DeadLinkCoverageTests
- PackageClosureRegressionTests
- Harness Creator
- HarnessHistoryTests
- SpecRecordTests
- test_skill_surface.py
- FindingCodeTests
- declared_plugin_skills_roots
- Community Contribution Policies
- BundledCliCoverageTests
- Frontmatter
- ._git
- NoSpecVocabularyTests
- walk_markdown
- Finding
- test_audit_harness.py
- mask_code
- CLAUDE.md as Advisory Instructions
- Custom Agent Eligibility Test
- DanglingPointerTests
- Skill Self-Containment Terms
- CliEdgeCaseTests
- _UnparsedBlock
- test_validate_harness.py
- WorkflowSyntaxProbeTests
- Thirty Hook Events Reference
- External Link Validation
- Golden source
- nightly.js
- Example skill
- Skill Listing Budget
- is_exact_matcher
- CLAUDE.md
- GoodHarnessAuditTests
- GuardrailTests
- is_known_tool_token
- TimeoutFactsTests
- DiscoveryPathTests
- Frontmatter Parser Tests
- broken-skill/SKILL.md
- Deterministic Enforcement Layer
- dead-link-skill/SKILL.md
- CLI self-description false-positive fixture
- broken.md
- NoOrphanedHeadingsTests
- PointerReaderTests
- AlwaysLoadedReportTests
- BlockReaderTests
- ModelFieldTests
- Parallel Execution Surfaces
- odd-paths.md
- Read-only security diff review
- gate.sh
- log.sh
- EmptyProjectAuditTests
- log-mentions-block.sh
- ._repo
- GoodHarnessImportTests
- Good-Harness Clean Pass Tests
- NearMissTests
- .test_a_shallow_clone_says_its_history_is_incomplete
- .test_a_target_inside_a_monorepo_searches_its_own_subtree_only
- .test_git_being_unavailable_is_not_reported_as_having_no_repository
- Instruction Persistence Across Compaction
- Path-Scoped Rules
- Broken Workflow Fixture
- Project Rule Fixtures
- Duplicate Reviewer Agent Fixtures
- Invalid Skill Hook Fixture
- noop.sh Hook Script
- Non-Executable Hook Script
- Test-Check Hook Script
- File Protection Hook Script
- Example Workflow Fixture
- Shared Audit Hook Script
- Target Check Shell Script
- Harness Scope and Placement
- Protected Claude Path Rules
- Harness Creator Hard Constraints
- Weekly Dependency Update Automation
- Release History Records
- Failure Feedback Routing
- Feature Request Form
- Internal Link and Image Validation
- Skill Without Description Fixture
- Unmatched Rule Glob Fixture
- Empty Skill Directory Fixture
- Nested Reviewer Agent

## God Nodes (most connected - your core abstractions)
1. `read()` - 42 edges
2. `BadHarnessTests` - 38 edges
3. `HarnessHistoryTests` - 30 edges
4. `add()` - 27 edges
5. `CheckTests` - 16 edges
6. `QuizTests` - 16 edges
7. `run()` - 12 edges
8. `PositiveFixtureTests` - 12 edges
9. `AtImportParsingTests` - 12 edges
10. `HeuristicFalsePositiveTests` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Audit Interview Route Generate Validate Loop` --semantically_similar_to--> `Harness Authoring Operating Loop`  [INFERRED] [semantically similar]
  README.md → .claude/skills/harness-creator/SKILL.md
- `extract()` --calls--> `add()`  [INFERRED]
  tools/claims.py → .claude/skills/harness-creator/scripts/validate_harness.py
- `Diátaxis Documentation Structure` --conceptually_related_to--> `Harness Creator`  [INFERRED]
  CONTRIBUTING.md → README.md
- `Harness Creator Repository Contract` --references--> `Harness Creator Meta-Skill`  [EXTRACTED]
  CLAUDE.md → .claude/skills/harness-creator/SKILL.md
- `Bug Report Form` --conceptually_related_to--> `Support Routing`  [INFERRED]
  .github/ISSUE_TEMPLATE/bug.yml → SUPPORT.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **E2E Run Grade Report Flow** — _claude_skills_harness_creator_references_e2e_testing_composed_e2e_workflow, _claude_skills_harness_creator_references_e2e_testing_evidence_citation_grading, _claude_skills_harness_creator_references_e2e_testing_failure_feedback_routing [EXTRACTED 1.00]
- **Packaged skill path classification** — tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_packaged_skill, tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_target_project_paths, tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_package_internal_pointers, tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_repository_path_leaks [EXTRACTED 1.00]
- **Parallel Work Surface Choice** — _claude_skills_harness_creator_references_agents_subagents, _claude_skills_harness_creator_references_agents_agent_view, _claude_skills_harness_creator_references_agents_agent_teams, _claude_skills_harness_creator_references_agents_dynamic_workflows [EXTRACTED 1.00]

## Communities (124 total, 61 thin omitted)

### Community 0 - "validate_harness.py"
Cohesion: 0.05
Nodes (80): _action_value(), add(), always_loaded_report(), _arg_label(), _block_scalar(), _BlockShapeError, check_agents(), _check_at_imports() (+72 more)

### Community 1 - "CI Pipeline"
Cohesion: 0.67
Nodes (3): CI Pipeline, Harness Validation Gate, Unit Test Gate

### Community 2 - "harness_common.py"
Cohesion: 0.15
Nodes (11): claude_md_paths(), iter_workflow_files(), print_findings_text(), Shared helpers for harness-creator's validation/audit/test scripts. Not a CLI…, Resolve an @import target to a Path, or None if it is not project-relative.…, Return the project-scope instruction files that exist at the root. A project…, Yield each `.claude/workflows/*.js` file under root., Return the settings.json paths that exist under root, in the order they're… (+3 more)

### Community 3 - "BadHarnessTests"
Cohesion: 0.08
Nodes (6): BadHarnessTests, v7 moved the anchor off "no tool_input", which described why the docs' rule…, references/skills.md's `hooks` row -- a skill's frontmatter declares hooks with…, references/hooks.md:150 -- a trailing `*` preceded by a space enforces a word…, references/hooks.md:110 -- file permission checks consult `Edit(path)` and…, references/hooks.md:140-144 -- since v2.1.142 a project settings.json setting…

### Community 4 - "test_hook.py"
Cohesion: 0.06
Nodes (17): build_sample_input(), cmd_matrix(), _event_fields(), find_matching_groups(), interpret(), main(), matches_matcher(), Approximate Claude Code's matcher evaluation (references/hooks.md): exact-… (+9 more)

### Community 5 - "Frontmatter and Skill Discovery Tests"
Cohesion: 0.07
Nodes (14): NestedFrontmatterTests, PluginSkillDiscoveryTests, references/hooks.md, skills.md and agents.md all teach a `hooks:` block in a…, v6. Refusing to guess at a nested shape and throwing the text away are…, `--model`'s help said "default: whatever the invoking session uses". Nothing…, A plugin's skills live at `./skills` unless plugin.json says otherwise, and…, `skills/` is an ordinary directory name. Without a plugin manifest it means…, Reference-to-reference pointers were scanned only in `*.md`, while a reference… (+6 more)

### Community 6 - "OutputTests"
Cohesion: 0.06
Nodes (28): event_names(), load(), main(), _preamble(), Yield (event_name, {column: cell}) for the dense reference table., Yield (event_name, section_text) for the expanded events., The shared input fields every event carries, which the per-event rows…, In lifecycle order, not alphabetical, from harness_common. The file supplies… (+20 more)

### Community 7 - "run_e2e.py"
Cohesion: 0.08
Nodes (17): build_command(), discard_isolated(), isolate_project(), main(), parse_stream(), Remove an isolated copy, including the mkdtemp parent that holds it. A copy of…, Runs `claude -p` and returns (raw_lines, error). error is None on a clean…, Parse stream-json lines into a structured summary: the line-delimited form of… (+9 more)

### Community 8 - "PositiveFixtureTests"
Cohesion: 0.05
Nodes (23): by_code(), ClaudeLocalGitignoreTests, LiveDocAgreementTests, NearMissTests, PositiveFixtureTests, skills, string substitutions: `${CLAUDE_SKILL_DIR}` is substituted in skill…, memory, rules: a rule's `paths` frontmatter is what scopes it, and a block the…, memory, Path-specific rules: the documented shape is a YAML list under… (+15 more)

### Community 9 - "Example project instructions"
Cohesion: 0.22
Nodes (9): Append-only database migrations, Database migration policy, Example project instructions, Protected-files hook, Raw SQL prohibition and query-builder rule, Test-gate hook, Public project overview, Deploy guard (+1 more)

### Community 10 - "Fixture Consistency Tests"
Cohesion: 0.11
Nodes (10): AgentWritePathIsStatedTests, BashWritePathIsCoveredTests, HookProseIsAnchoredToTheHookTests, references/hooks.md documents that a Bash-driven edit (`sed -i`, `echo >>…, An agent body replaces the system prompt entirely, so it is the only place the…, A sentence describing a hook must name the script that implements it. Not a…, test_hook.py executes these for real, and a non-executable hook fails at the…, sentences() (+2 more)

### Community 11 - "read"
Cohesion: 0.13
Nodes (11): NoModeVocabularyTests, OrchestrationChoiceTests, The four-mode classification (new/extend/improve/sync) and the I1-I5 stage…, v6. The skill covered subagents and workflows and never said which of the four…, 00-overview.md "Choose an approach": "Who coordinates the work?" with four…, 03-run-agent-teams.md:10,54 -- "disabled by default ... Without that variable,…, 00-overview.md "Do the tasks touch the same files?" -- "Agent teams don't…, 00-overview.md "Do the workers need to talk to each other?" -- subagents report… (+3 more)

### Community 12 - "CheckTests"
Cohesion: 0.11
Nodes (6): CheckTests, ExtractTests, HelpTests, The same rule this repo's validate_harness.py applies to bundled scripts,…, The heuristic misses "Every rule loads at launch." -- a claim with no marker. A…, run()

### Community 13 - "QuizTests"
Cohesion: 0.11
Nodes (9): ContrastTests, HelpTests, ProbeTestCase, QuizTests, --bare skips OAuth, so a machine without ANTHROPIC_API_KEY needs the documented…, The first real smoke run recorded `Not logged in` as a normal answer with error…, Same wrapper both times, so an observed difference is attributable to the…, What the fake claude saw, one dict per invocation. (+1 more)

### Community 14 - "claims.py"
Cohesion: 0.14
Nodes (25): anchor_count(), anchor_present(), check(), cmd_check(), cmd_extract(), extract(), _is_separator_row(), _load_claims() (+17 more)

### Community 15 - "audit_harness.py"
Cohesion: 0.15
Nodes (26): check_user_scope_conflicts(), _file_summary(), _foreign_instruction_files(), _git(), _git_root(), harness_history(), harness_history_paths(), hygiene_signals() (+18 more)

### Community 16 - "PositiveFixtureTests"
Cohesion: 0.10
Nodes (11): by_code(), NearMissTests, PositiveFixtureTests, hooks, Stop input: "The `stop_hook_active` field is `true` when Claude Code is…, hooks, exec form and shell form: "Set `args` whenever the hook references a…, Shapes that look like one of the five and are correct: a permission rule…, permissions: Read/Edit rules follow gitignore, where `*` does not cross a path…, permissions: "Rules are evaluated in order: deny, then ask, then allow. The… (+3 more)

### Community 17 - "PackageClosureTests"
Cohesion: 0.15
Nodes (7): PackageClosureTests, This one reaches the end user: a module docstring is what `--help` prints., The paths a harness-building skill names constantly. Each one describes a file…, good-harness has no plugin manifest, so the same shape of pointer there is a…, `https://docs.python.org/3/?source=references/install.md` names a query…, A plugin-packaged skill travels as one directory. A pointer out of it resolves…, An adversarial pass built three correct plugins this flags: a skill telling the…

### Community 18 - "run"
Cohesion: 0.13
Nodes (12): env_with_fake_claude(), HonestApproximationTests, NoPolicyOrHistoryInScriptsTests, test_hook.py approximates a JavaScript RegExp with Python `re`, and its input…, Mode combinations that cannot mean anything are refused by argparse, with exit…, run_e2e.py spawns `claude`; a usage-error test must never reach a real session,…, Every string constant inside an expression, so a help= built by concatenation…, (kind, text) for every string the user can read: module and function… (+4 more)

### Community 19 - "ConsequenceClauseTests"
Cohesion: 0.21
Nodes (6): ConsequenceClauseTests, v3 attached a consequence to the findings that could carry one, on the theory…, Documented: a rule loads only when Claude reads a file its `paths:` matches. A…, The documented reason for the 500-line guideline is that a skill's body stays…, Sourced in references/skills.md: an argument without `help=` prints as a bare…, The three the v3 plan wanted to annotate and the docs would not support.…

### Community 20 - "probe.py"
Cohesion: 0.21
Nodes (17): build_command(), Claude, cmd_contrast(), cmd_quiz(), contrast_prompt(), _drift(), _fresh_out_dir(), load_questions() (+9 more)

### Community 21 - "InterfaceContradictionTests"
Cohesion: 0.20
Nodes (6): InterfaceContradictionTests, v5. Prose that asserts how a bundled script *currently behaves* is a claim…, The fact the prose has to agree with. If this ever flips to opt-out, the prose…, `--permission-mode` exists and is the direct answer to the headless-permissions…, The same shape one file over. agents.md said `tools:` "already enforces" read-…, `--dangerously-skip-permissions` belongs to the `claude` CLI that run_e2e.py…

### Community 24 - "DeadLinkCoverageTests"
Cohesion: 0.24
Nodes (5): DeadLinkCoverageTests, B7. Hard line 1 claimed validate_harness.py checked pointers mechanically, but…, Every shipped reference is reachable, directly or through another reference, by…, v5. The pattern captured one path segment, so a pointer into a subdirectory was…, The mirror-image failure, and the worse one: a check that fires on a correct…

### Community 25 - "PackageClosureRegressionTests"
Cohesion: 0.24
Nodes (6): PackageClosureRegressionTests, v5 closed thirteen pointers that led out of the shipped package. Six were…, `D12` is not bad because it is short. It is bad because nothing in the…, The one case the shipped check structurally cannot see. Package closure asks…, Derived from the plan tree rather than hardcoded, so a pointer at any…, skills.md sent the reader to hooks.md's "Hooks in skills and agents", which is…

### Community 26 - "Harness Creator"
Cohesion: 0.08
Nodes (27): E2E Assertion Types, Composed E2E Workflow, Harness E2E Validation, Evidence-Citation Grading Doctrine, Isolated Headless Execution, Packaged Skill Self-Containment, Parameterized Bundled Scripts, Three-Stage Skill Disclosure (+19 more)

### Community 27 - "HarnessHistoryTests"
Cohesion: 0.14
Nodes (8): HarnessHistoryTests, The record of why a harness looks the way it does now lives in the commits that…, Three outcomes have to stay apart: no repository, a repository with no matching…, The distinction the whole report rests on. Work done *with* a harness edits the…, Feature work that adds a build command to CLAUDE.md really did change the…, Two definitions of "harness component" -- one that inventories the disk, one…, The history is about to become the record, and a record whose limits are…, A project can keep its reasons somewhere this search cannot reach. Saying the…

### Community 28 - "SpecRecordTests"
Cohesion: 0.20
Nodes (6): The spec is where a decision is recorded permanently, and the two things that…, D1 (delete the interview protocol), D7 (no new CLI, shape checks only) and D9…, Three headless runs, $5.30, watched once. Nothing regenerates this, and the…, `docs/plan/` is being removed. A spec that cites it as the binding record…, The one way this file can lie by omission: a tool built to justify deletions,…, SpecRecordTests

### Community 29 - "test_skill_surface.py"
Cohesion: 0.14
Nodes (9): FenceBalanceTests, GotchaCountTests, NoExternalToolNamesTests, Deleted references must not remain dependencies of the shipped package., v7 deleted interview.md: its protocol (modes, stages, scripts) was a rail the…, A count in a heading is a number that goes stale the moment someone adds or…, D14. The shipped skill is a self-contained plugin and must not name Claude Code…, B10. agents.md opened a ```markdown fence and never closed it, so renderers and… (+1 more)

### Community 30 - "FindingCodeTests"
Cohesion: 0.24
Nodes (4): FindingCodeTests, Checks added from v7 on carry a stable code so a fixture can assert exactly…, A code is an identifier a reader looks up, and reports quoting `V01` outlive…, The tests below assert how a code travels, not which one. They stop asserting…

### Community 31 - "declared_plugin_skills_roots"
Cohesion: 0.22
Nodes (9): declared_plugin_skills_roots(), iter_skill_dirs(), load_json_lenient(), plugin_skills_roots(), Parse a JSON file, returning (data, error_message). error_message is None on…, Skills roots a plugin manifest declares, or its default. A plugin ships its…, The declared roots that are directories right now. Split from the declaration…, Yield each skill directory under root. `.claude/skills/` always, plus whatever… (+1 more)

### Community 32 - "Community Contribution Policies"
Cohesion: 0.28
Nodes (9): Bug Report Form, Issue Routing Configuration, Pull Request Change Assurance, Contributor Covenant 3.0, Community Enforcement Ladder, Harness Creator Contribution Workflow, Private Vulnerability Reporting, Harness Creator Security Policy (+1 more)

### Community 33 - "BundledCliCoverageTests"
Cohesion: 0.29
Nodes (5): BundledCliCoverageTests, Bundled CLIs remain discoverable wherever the skill routes to them., Which bundled scripts are CLIs, read from the source rather than listed here --…, Follow shipped Markdown pointers from the skill's entry point., reachable_skill_pointers()

### Community 34 - "Frontmatter"
Cohesion: 0.29
Nodes (5): Frontmatter, parse_frontmatter(), Conservative frontmatter parser: stdlib has no real YAML parser, and a mis-…, Result of parsing a markdown file's YAML-ish frontmatter block. `data` is None…, _unquote()

### Community 35 - "._git"
Cohesion: 0.29
Nodes (3): Why the pathspec is directory patterns and not the files discovery finds today:…, Measured on this repository: five merges match the pathspec and all five list…, Deleting the last skill under a declared root removes the directory, and a path…

### Community 36 - "NoSpecVocabularyTests"
Cohesion: 0.33
Nodes (3): NoSpecVocabularyTests, The spec file is retired. What ships must not still ask for it. A grep for the…, Every surface a reader of the installed package meets: the skill body, its…

### Community 37 - "walk_markdown"
Cohesion: 0.33
Nodes (6): iter_agent_files(), iter_rule_files(), Yield every `.md` file at or below directory, following symlinks but visiting…, Yield each `.claude/agents/**/*.md` file under root., Yield each `.claude/rules/**/*.md` file under root. Rules are discovered…, walk_markdown()

### Community 38 - "Finding"
Cohesion: 0.40
Nodes (3): Finding, A lint finding. Unpacks as (level, location, message); `code` is an optional…, tuple

### Community 39 - "test_audit_harness.py"
Cohesion: 0.13
Nodes (6): BadHarnessAuditTests, The structured result is not what a pass reads. If the rendered report…, The report is bounded by a path list, and a reader who does not know the bounds…, The audit checks existence, not content. Saying so on every run is what keeps a…, run_cli(), ScopeAndJsonContractTests

### Community 40 - "mask_code"
Cohesion: 0.50
Nodes (4): mask_code(), parse_at_imports(), Return text with fenced code blocks and inline code spans replaced by spaces,…, Yield each `@path` import target in text, in order, skipping code. Returns raw…

### Community 41 - "CLAUDE.md as Advisory Instructions"
Cohesion: 0.67
Nodes (3): CLAUDE.md as Advisory Instructions, CLAUDE.md Content Eligibility Test, Filesystem-as-Inventory Pointer Policy

### Community 44 - "Skill Self-Containment Terms"
Cohesion: 0.25
Nodes (8): Packaged reference, Package-internal pointers, Packaged skill, Repository path leaks, Target-project paths, Plugin skill self-containment requirement, External design note, External internal-decision log

### Community 48 - "WorkflowSyntaxProbeTests"
Cohesion: 0.39
Nodes (3): B12, found while trimming the examples in WS6. The node syntax gate checked the…, The examples in references/ must survive the linter that this skill tells the…, WorkflowSyntaxProbeTests

### Community 49 - "Thirty Hook Events Reference"
Cohesion: 0.33
Nodes (6): Thirty Hook Events Reference, PostToolUse Hook Event, PreToolUse Hook Event, SessionStart Hook Event, Stop Hook Event, Hook Event Router

### Community 53 - "Example skill"
Cohesion: 0.67
Nodes (3): Example skill full procedure, Example skill, Retry-only API idempotency

### Community 58 - "GuardrailTests"
Cohesion: 0.29
Nodes (4): GuardrailTests, The do-not-cut list from the audit (audit-synthesis.md section 4), plus the…, R3. The event router is what makes the hooks.md/hooks-events.md split safe --…, This anchor was retired deliberately, which is the review signal the class…

### Community 64 - "Deterministic Enforcement Layer"
Cohesion: 0.40
Nodes (5): Deterministic Enforcement Layer, Hook Exit-Code Contract, Hook Eligibility Test, Hook Matcher Semantics, Permission Rule and Hook Pair

### Community 68 - "NoOrphanedHeadingsTests"
Cohesion: 0.47
Nodes (3): NoOrphanedHeadingsTests, v6. Two headings in agents.md announced a section and then handed the reader…, A container heading may hand straight to a deeper one -- `## The five stages`…

### Community 69 - "PointerReaderTests"
Cohesion: 0.29
Nodes (4): PointerReaderTests, v5 removed CLAUDE.md's pointer at `.claude/harness-spec.md`. The policy…, v7 (disposition C25) reworded the sentence this anchored: the ban is now on the…, The example is what a reader copies, so a registry line here would ship the…

### Community 73 - "Parallel Execution Surfaces"
Cohesion: 0.40
Nodes (5): Agent Teams, Agent View, Dynamic Workflows, Four Parallel-Work Surfaces, Subagents

### Community 80 - "._repo"
Cohesion: 0.13
Nodes (9): A throwaway repository. Real git, because the three things that actually broke…, No harness commit exists" and "this project has no history at all" lead a pass…, A hook whose settings entry never moves still changes what the harness…, A report that silently stops at N reads as a project with N harness commits.…, `_git` returns None when git cannot run at all -- a missing binary, or a log…, `@file` pulls another file into every session, so editing it changes what the…, A project set up before this tool kept its record in git has one file holding…, The framing bytes have to be ones the data cannot contain. A subject may hold… (+1 more)

### Community 90 - "Project Rule Fixtures"
Cohesion: 0.67
Nodes (3): Dot-claude project instructions, Always-loaded frontend style rule, Path-scoped TypeScript rule

## Knowledge Gaps
- **85 isolated node(s):** `noop.sh script`, `not-executable.sh script`, `meta`, `stamp`, `meta` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 504 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **61 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BadHarnessTests` connect `BadHarnessTests` to `test_validate_harness.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `HarnessHistoryTests` connect `HarnessHistoryTests` to `._git`, `test_audit_harness.py`, `._repo`, `.test_a_shallow_clone_says_its_history_is_incomplete`, `.test_a_target_inside_a_monorepo_searches_its_own_subtree_only`, `.test_git_being_unavailable_is_not_reported_as_having_no_repository`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `add()` connect `validate_harness.py` to `claims.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **What connects `noop.sh script`, `not-executable.sh script`, `meta` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `validate_harness.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Should `BadHarnessTests` be split into smaller, more focused modules?**
  _Cohesion score 0.08305647840531562 - nodes in this community are weakly interconnected._
- **Should `test_hook.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06342780026990553 - nodes in this community are weakly interconnected._