# Graph Report - harness-creator  (2026-09-01)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1122 nodes · 1398 edges · 124 communities (79 shown, 45 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 53 edges (avg confidence: 0.86)
- Token cost: 57,386 input · 2,127 output

## Graph Freshness
- Built from commit: `a074a01e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Harness Validation CLI Checks
- Harness Design Principles
- Shared Harness Parsing Helpers
- Bad-Harness Validation Tests
- Hook Matcher Simulation CLI
- Frontmatter and Skill Discovery Tests
- Hook Event Reference Generator
- Headless E2E Session Runner
- Project Documentation and Concepts
- Example Harness Fixture Components
- Fixture Consistency Tests
- Orchestration Doctrine Tests
- Interview-to-Harness Generation Flow
- Skill Packaging and Spec Contract
- Interface Doctrine Tests
- Harness Audit CLI Inventory
- Documentation Discoverability Research
- Package Closure Leak Tests
- Spec Evidence and Drift Lifecycle
- Finding Consequence Clause Tests
- Verified Claude Code Mechanics
- Interface Contradiction Tests
- At-Import Parsing Tests
- Heuristic False-Positive Tests
- Dead Pointer Coverage Tests
- Package Closure Regression Tests
- E2E and Workflow Doctrine
- v2 Verification Plan Layers
- v3 Compression Revision Plan
- Skill Surface Lint Tests
- Always-Loaded Budget Tests
- Meta-Skill Doctrine Overview
- Community Contribution Policies
- CLI Interface Plan Generations
- v2 Audit and Guardrails
- Prose-Interface Boundary Doctrine
- Product Architecture Documentation
- Validation Evidence and Escalation
- Installation Paths and FAQ
- Audit Script Tests
- Spec-Not-On-Disk Drift Tests
- Spec Inventory and CLAUDE.md Policy
- Layer Routing and Agent Eligibility
- Interview Stages and Modes
- Skill Self-Containment Terms
- Bare-Name and Ghost Component Terms
- Harness Subtraction Tests
- Validator CLI Edge-Case Tests
- Workflow Syntax Probe Tests
- Hook Event Reference Docs
- Link Validation and Release Gates
- Distribution and Reddit Launch
- Competing Harness Factory Analysis
- Skill Creator Doctrine Lineage
- Harness Mental Model Layers
- Three-Axis Layer Routing
- Broken Harness Fixtures
- Good-Harness Audit Tests
- Do-Not-Cut Guardrail Tests
- Wrap-Up Ordering Tests
- Hook Timeout Fact Tests
- Component Discovery Path Tests
- Frontmatter Parser Tests
- Spec Mention Convention Tests
- Hook and Permission Enforcement
- Hook and Settings Semantics
- Claim-Loss Verification Protocol
- Harness CLI Script Inventory
- Orphaned Heading Tests
- Spec Pointer Policy Tests
- Always-Loaded Report Tests
- Frontmatter Block Reader Tests
- Model Field Validation Tests
- Parallel Execution Surfaces
- Spec Drift Row Detection
- Product Identity and Discoverability
- v2 Truth Repair Changes
- Claim A/B Workflow Script
- Empty Project Audit Tests
- Spec Drift Granularity Tests
- Spec Drift JSON Contract Tests
- Good-Harness Import Fixture Tests
- Good-Harness Clean Pass Tests
- Near-Miss False-Positive Tests
- Interface Ownership Doctrine
- Public Claim Boundaries
- Hooks Capability Map
- Hook Contract and Blind Spots
- Hook Testing CLIs
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
- Principles and Boundaries Diagram
- Subagent Context Isolation
- Approved Repository Metadata
- Subagent Execution Model
- Project Loop Surface
- Safe Mode Customization Disablement
- Interview Question Style
- Compatibility Support Policy
- Unmatched Rule Glob Fixture
- Empty Skill Directory Fixture
- Nested Reviewer Agent

## God Nodes (most connected - your core abstractions)
1. `read()` - 48 edges
2. `BadHarnessTests` - 39 edges
3. `add()` - 24 edges
4. `InterfaceDoctrineTests` - 12 edges
5. `AtImportParsingTests` - 12 edges
6. `HeuristicFalsePositiveTests` - 12 edges
7. `run()` - 12 edges
8. `run()` - 12 edges
9. `PackageClosureTests` - 11 edges
10. `Layer Routing Framework` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Deterministic Harness Lint` --semantically_similar_to--> `Harness Validation Gate`  [INFERRED] [semantically similar]
  docs/plan/04-scripts-and-validation.md → .github/workflows/ci.yml
- `Audit Interview Route Generate Validate Loop` --semantically_similar_to--> `Harness Authoring Operating Loop`  [INFERRED] [semantically similar]
  README.md → .claude/skills/harness-creator/SKILL.md
- `Harness Creator` --conceptually_related_to--> `AI Harness`  [INFERRED]
  README.md → docs/assets/brand/harness-creator-poster.png
- `Structural, hook, and session validation layers` --semantically_similar_to--> `Five-layer verification stack`  [INFERRED] [semantically similar]
  docs/wiki/explanation/architecture.md → docs/plan/v2/02-verification.md
- `Feature Request Form` --conceptually_related_to--> `Layer Routing Framework`  [INFERRED]
  .github/ISSUE_TEMPLATE/feature.yml → docs/plan/02-skill-design.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Harness Creator Operating System** — docs_plan_02_skill_design_operating_loop, docs_plan_02_skill_design_layer_routing_framework, docs_plan_02_skill_design_harness_spec, docs_plan_04_scripts_and_validation_deterministic_harness_lint [EXTRACTED 1.00]
- **Two-Layer Validation Flow** — docs_plan_04_scripts_and_validation_deterministic_harness_lint, docs_plan_04_scripts_and_validation_hook_unit_testing, docs_plan_04_scripts_and_validation_headless_e2e_runner, docs_plan_04_scripts_and_validation_e2e_run_grade_report [EXTRACTED 1.00]
- **Claim-preserving compression system** — docs_plan_v3_02_compression_tabulate_then_compress_cells, docs_plan_v3_02_compression_scaffolding_deletion, docs_plan_v3_02_compression_no_paraphrase_compression, docs_plan_v3_02_compression_do_not_cut_claim_categories, docs_plan_v3_03_verification_claim_ab_protocol [EXTRACTED 1.00]
- **Cumulative Harness Validation Ladder** — docs_wiki_how_to_validate_a_harness_cumulative_evidence_levels, docs_wiki_how_to_validate_a_harness_structural_validation, docs_wiki_how_to_validate_a_harness_command_hook_testing, docs_wiki_how_to_validate_a_harness_behavioral_e2e_validation, docs_wiki_how_to_validate_a_harness_validation_record [EXTRACTED 1.00]
- **AI Agent Composition** — docs_assets_brand_harness_creator_poster_ai_agent, docs_assets_brand_harness_creator_poster_ai_model, docs_assets_brand_harness_creator_poster_ai_harness [EXTRACTED 1.00]
- **Harness Component System** — docs_assets_brand_harness_creator_poster_ai_harness, docs_assets_brand_harness_creator_poster_claude_md_config, docs_assets_brand_harness_creator_poster_rules_guardrails, docs_assets_brand_harness_creator_poster_hooks_automations, docs_assets_brand_harness_creator_poster_skills_capabilities [EXTRACTED 1.00]
- **E2E Run Grade Report Flow** — _claude_skills_harness_creator_references_e2e_testing_composed_e2e_workflow, _claude_skills_harness_creator_references_e2e_testing_evidence_citation_grading, _claude_skills_harness_creator_references_e2e_testing_failure_feedback_routing [EXTRACTED 1.00]
- **Good harness layered components** — tests_fixtures_good_harness__claude_harness_spec_example_project_harness, tests_fixtures_good_harness__claude_agents_security_reviewer_security_reviewer, tests_fixtures_good_harness__claude_rules_db_migrations_append_only_migrations, tests_fixtures_good_harness__claude_skills_example_skill_skill_example_skill, tests_fixtures_good_harness__claude_harness_spec_example_workflow [EXTRACTED 1.00]
- **Seven-Layer Harness Architecture** — _claude_skills_harness_creator_references_claude_md_and_rules_advisory_instructions, _claude_skills_harness_creator_references_claude_md_and_rules_path_scoped_rules, _claude_skills_harness_creator_references_skills_skill_trigger_description, _claude_skills_harness_creator_references_hooks_deterministic_enforcement, _claude_skills_harness_creator_references_agents_context_isolated_role, _claude_skills_harness_creator_references_workflows_fixed_shape_workflow, _claude_harness_spec_harness_spec [EXTRACTED 1.00]
- **Hook execution and enforcement semantics** — docs_plan_research_research_hooks_reference_pretooluse_enforcement, docs_plan_research_research_hooks_reference_exit_code_contract, docs_plan_research_research_hooks_reference_parallel_execution_semantics, docs_plan_research_research_hooks_reference_hook_blind_spots [EXTRACTED 1.00]
- **Harness Creation Workflow** — docs_assets_figures_intent_to_autonomy_audit, docs_assets_figures_intent_to_autonomy_interview, docs_assets_figures_intent_to_autonomy_route, docs_assets_figures_intent_to_autonomy_generate, docs_assets_figures_intent_to_autonomy_validate [EXTRACTED 1.00]
- **Harness Generation Inputs** — docs_assets_figures_intent_to_autonomy_project_facts, docs_assets_figures_intent_to_autonomy_user_intent, docs_assets_figures_intent_to_autonomy_non_negotiable_constraints, docs_assets_figures_intent_to_autonomy_input_synthesis_funnel [EXTRACTED 1.00]
- **Interview-to-Generation Lifecycle** — docs_wiki_reference_interview_and_reentry_phase_zero_audit, docs_wiki_reference_interview_and_reentry_interview_stages, docs_wiki_reference_interview_and_reentry_reentry_modes, docs_wiki_reference_interview_and_reentry_approval_gates, docs_wiki_reference_interview_and_reentry_wrap_up [EXTRACTED 1.00]
- **Packaged skill path classification** — tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_packaged_skill, tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_target_project_paths, tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_package_internal_pointers, tests_fixtures_plugin_package_closure__claude_skills_packaged_skill_repository_path_leaks [EXTRACTED 1.00]
- **Parallel Work Surface Choice** — _claude_skills_harness_creator_references_agents_subagents, _claude_skills_harness_creator_references_agents_agent_view, _claude_skills_harness_creator_references_agents_agent_teams, _claude_skills_harness_creator_references_agents_dynamic_workflows [EXTRACTED 1.00]
- **Specification and disk artifact drift cases** — tests_fixtures_spec_claims_missing_skill__claude_harness_spec_spec_disk_drift_specification, tests_fixtures_spec_claims_missing_skill__claude_skills_real_skill_skill_real_skill, tests_fixtures_spec_claims_missing_skill__claude_harness_spec_ghost_skill, tests_fixtures_spec_claims_missing_skill__claude_harness_spec_ghost_agent, tests_fixtures_spec_claims_missing_skill__claude_harness_spec_artifact_status_semantics [EXTRACTED 1.00]
- **Three-Axis Layer Routing Flow** — docs_wiki_explanation_layer_routing_need_first_routing, docs_wiki_explanation_layer_routing_authority_routing, docs_wiki_explanation_layer_routing_load_timing_routing, docs_wiki_explanation_layer_routing_cost_aware_routing, docs_wiki_reference_harness_routing_summary [EXTRACTED 1.00]
- **Harness Creator v2 revision workstreams** — docs_plan_v2_01_changes_truth_repair, docs_plan_v2_01_changes_auto_memory_scope_axis, docs_plan_v2_01_changes_silent_failure_mechanics, docs_plan_v2_01_changes_domain_narrative_removal, docs_plan_v2_01_changes_external_edit_survival, docs_plan_v2_01_changes_interview_reentry_split [EXTRACTED 1.00]
- **Adaptive behavior governance** — docs_assets_figures_principles_and_verified_boundaries_model_judgment, docs_assets_figures_principles_and_verified_boundaries_adapt_to_the_case, docs_assets_figures_principles_and_verified_boundaries_hooks_permissions_tests, docs_assets_figures_principles_and_verified_boundaries_block_or_verify, docs_assets_figures_principles_and_verified_boundaries_adaptable_behavior_within_verified_boundaries [INFERRED 0.85]
- **Community Tooling Story** — docs_assets_brand_harness_creator_poster_shin_chan, docs_assets_brand_harness_creator_poster_dev_mentor, docs_assets_brand_harness_creator_poster_community_contribution, readme_harness_creator [INFERRED 0.85]
- **Discoverability Overhaul System** — docs_plan_advertise_02_positioning_and_messaging_product_identity, docs_plan_advertise_03_documentation_architecture_readme_front_door, docs_plan_advertise_05_community_and_distribution_staged_distribution, docs_plan_advertise_06_launch_and_measurement_snapshot_schedule [INFERRED 0.95]

## Communities (124 total, 45 thin omitted)

### Community 0 - "Harness Validation CLI Checks"
Cohesion: 0.06
Nodes (65): _action_value(), add(), always_loaded_report(), _arg_label(), _block_scalar(), _BlockShapeError, check_agents(), _check_at_imports() (+57 more)

### Community 1 - "Harness Design Principles"
Cohesion: 0.05
Nodes (47): Instruction Persistence Across Compaction, Path-Scoped Rules, CI Pipeline, Harness Validation Gate, Unit Test Gate, Dynamic Workflow Routing Decision, Enforcement Layering, Harness Creator Meta-Harness (+39 more)

### Community 2 - "Shared Harness Parsing Helpers"
Cohesion: 0.05
Nodes (39): claude_md_paths(), Frontmatter, is_exact_matcher(), is_known_tool_token(), iter_agent_files(), iter_rule_files(), iter_skill_dirs(), iter_workflow_files() (+31 more)

### Community 3 - "Bad-Harness Validation Tests"
Cohesion: 0.08
Nodes (5): BadHarnessTests, references/skills.md's `hooks` row -- a skill's frontmatter declares hooks with…, references/hooks.md:150 -- a trailing `*` preceded by a space enforces a word…, references/hooks.md:110 -- file permission checks consult `Edit(path)` and…, references/hooks.md:140-144 -- since v2.1.142 a project settings.json setting…

### Community 4 - "Hook Matcher Simulation CLI"
Cohesion: 0.06
Nodes (17): build_sample_input(), cmd_matrix(), _event_fields(), find_matching_groups(), interpret(), main(), matches_matcher(), Reproduce Claude Code's matcher evaluation exactly (references/hooks.md):… (+9 more)

### Community 5 - "Frontmatter and Skill Discovery Tests"
Cohesion: 0.07
Nodes (14): NestedFrontmatterTests, PluginSkillDiscoveryTests, references/hooks.md, skills.md and agents.md all teach a `hooks:` block in a…, v6. Refusing to guess at a nested shape and throwing the text away are…, `--model`'s help said "default: whatever the invoking session uses". Nothing…, A plugin's skills live at `./skills` unless plugin.json says otherwise, and…, `skills/` is an ordinary directory name. Without a plugin manifest it means…, Reference-to-reference pointers were scanned only in `*.md`, while a reference… (+6 more)

### Community 6 - "Hook Event Reference Generator"
Cohesion: 0.08
Nodes (22): event_names(), load(), main(), _preamble(), Yield (event_name, {column: cell}) for the dense reference table., Yield (event_name, section_text) for the expanded events., The shared input fields every event carries, which the per-event rows…, In lifecycle order, not alphabetical. The file enumerates the events in the… (+14 more)

### Community 7 - "Headless E2E Session Runner"
Cohesion: 0.08
Nodes (17): build_command(), discard_isolated(), isolate_project(), main(), parse_stream(), Parse stream-json lines into a structured summary. Schema verified against a…, Remove an isolated copy, including the mkdtemp parent that holds it. A copy of…, Runs `claude -p` and returns (raw_lines, error). error is None on a clean… (+9 more)

### Community 8 - "Project Documentation and Concepts"
Cohesion: 0.11
Nodes (23): Documentation Issue Form, Graphify Project Guidance, Diátaxis Documentation Structure, AI Agent, AI Harness, AI Model, CLAUDE.md Configuration, Community Contribution (+15 more)

### Community 9 - "Example Harness Fixture Components"
Cohesion: 0.10
Nodes (21): CLI self-description false-positive fixture, Edge-case skill, Read-only security diff review, Security reviewer, Example project harness specification, Example fan-out and verify workflow, Hook and deny-rule pairing, Append-only database migrations (+13 more)

### Community 10 - "Fixture Consistency Tests"
Cohesion: 0.11
Nodes (10): AgentWritePathIsStatedTests, BashWritePathIsCoveredTests, HookProseIsAnchoredToTheHookTests, references/hooks.md documents that a Bash-driven edit (`sed -i`, `echo >>…, An agent body replaces the system prompt entirely, so it is the only place the…, A sentence describing a hook must name the script that implements it. Not a…, test_hook.py executes these for real, and a non-executable hook fails at the…, sentences() (+2 more)

### Community 11 - "Orchestration Doctrine Tests"
Cohesion: 0.14
Nodes (11): DanglingPointerTests, OrchestrationChoiceTests, v6. The skill covered subagents and workflows and never said which of the four…, 00-overview.md "Choose an approach": "Who coordinates the work?" with four…, 03-run-agent-teams.md:10,54 -- "disabled by default ... Without that variable,…, 00-overview.md "Do the tasks touch the same files?" -- "Agent teams don't…, 00-overview.md "Do the workers need to talk to each other?" -- subagents report…, 03-run-agent-teams.md:255-259 and :420 -- "Teammates start with the lead's… (+3 more)

### Community 12 - "Interview-to-Harness Generation Flow"
Cohesion: 0.13
Nodes (19): Audit, Boundaries Enforced, Generate, Input Synthesis Funnel, Intent-to-Autonomy Harness Generation Diagram, Interview, Judgment Preserved, Non-negotiable Constraints (+11 more)

### Community 13 - "Skill Packaging and Spec Contract"
Cohesion: 0.11
Nodes (19): Harness Spec as Single Source of Truth, Re-entrant Operating Modes, Duplicate Skill Registration Risk, Generated Harness Structure, Local Marketplace Cache Leakage, Plugin Marketplace Packaging, Protected Path Writes, Symlink Development Loop (+11 more)

### Community 14 - "Interface Doctrine Tests"
Cohesion: 0.15
Nodes (7): InterfaceDoctrineTests, v5 gave the interface boundary its second direction, and retired the…, Which bundled scripts are CLIs, read from the source rather than listed here --…, Both halves, because naming only the tool's half is what let the prose copy…, The clause that makes the rule operable on a case nobody listed., The specific regression. A flag in this table is a copy of `--help`, and the…, Judgment is the half that stays. Dropping the column must not drop the row.

### Community 15 - "Harness Audit CLI Inventory"
Cohesion: 0.27
Nodes (15): check_user_scope_conflicts(), _file_summary(), _foreign_instruction_files(), hygiene_signals(), inventory_agents(), inventory_claude_md(), inventory_rules(), inventory_settings() (+7 more)

### Community 16 - "Documentation Discoverability Research"
Cohesion: 0.12
Nodes (16): CHAOSS Starter Project Health Model, Diátaxis, Documentation Discovery Evidence, Evidence-Bounded Discovery Strategy, Open-Source Trust Evidence, README Correlation Studies, Canonical Diátaxis Documentation, README Front Door (+8 more)

### Community 17 - "Package Closure Leak Tests"
Cohesion: 0.15
Nodes (7): PackageClosureTests, The paths a harness-building skill names constantly. Each one describes a file…, good-harness has no plugin manifest, so the same shape of pointer there is a…, `https://docs.python.org/3/?source=references/install.md` names a query…, A plugin-packaged skill travels as one directory. A pointer out of it resolves…, An adversarial pass built three correct plugins this flags: a skill telling the…, This one reaches the end user: a module docstring is what `--help` prints.

### Community 18 - "Spec Evidence and Drift Lifecycle"
Cohesion: 0.15
Nodes (14): Persisted Rationale and Evidence, Deliberate Declines, Sync Mode Drift Reconciliation, Validation Drift Reconciliation, Validation Evidence Record, Harness Component Specifications, Evidence, Drift, and Change History, Harness Spec Contract (+6 more)

### Community 19 - "Finding Consequence Clause Tests"
Cohesion: 0.19
Nodes (7): ConsequenceClauseTests, v3 attached a consequence to the findings that could carry one, on the theory…, Documented: a rule loads only when Claude reads a file its `paths:` matches. A…, check_spec_drift returns empty lists in both directions when there is no spec,…, The documented reason for the 500-line guideline is that a skill's body stays…, Sourced in references/skills.md: an argument without `help=` prints as a bare…, The three the v3 plan wanted to annotate and the docs would not support.…

### Community 20 - "Verified Claude Code Mechanics"
Cohesion: 0.15
Nodes (13): Always-loaded surface budget, Live verification for version-sensitive mechanics, Re-entry load gating, Auto-memory and personal/team scope axis, Interview and re-entry split, Silent-failure mechanics workstream, Auto-memory loading and scope model, Compaction survival matrix (+5 more)

### Community 21 - "Interface Contradiction Tests"
Cohesion: 0.18
Nodes (6): InterfaceContradictionTests, v5. Prose that asserts how a bundled script *currently behaves* is a claim…, The fact the prose has to agree with. If this ever flips to opt-out, the prose…, `--permission-mode` exists and is the direct answer to the headless-permissions…, The same shape one file over. agents.md said `tools:` "already enforces" read-…, `--dangerously-skip-permissions` belongs to the `claude` CLI that run_e2e.py…

### Community 24 - "Dead Pointer Coverage Tests"
Cohesion: 0.27
Nodes (4): DeadLinkCoverageTests, B7. Hard line 1 claimed validate_harness.py checked pointers mechanically, but…, v5. The pattern captured one path segment, so a pointer into a subdirectory was…, The mirror-image failure, and the worse one: a check that fires on a correct…

### Community 25 - "Package Closure Regression Tests"
Cohesion: 0.24
Nodes (6): PackageClosureRegressionTests, v5 closed thirteen pointers that led out of the shipped package. Six were…, `D12` is not bad because it is short. It is bad because nothing in the…, The one case the shipped check structurally cannot see. Package closure asks…, Derived from the plan tree rather than hardcoded, so a pointer at any…, skills.md sent the reader to hooks.md's "Hooks in skills and agents", which is…

### Community 26 - "E2E and Workflow Doctrine"
Cohesion: 0.20
Nodes (10): E2E Assertion Types, Composed E2E Workflow, Harness E2E Validation, Evidence-Citation Grading Doctrine, Isolated Headless Execution, Harness Ablation Protocol, Fan-Out Verify Synthesize Pattern, Fixed-Shape Workflow (+2 more)

### Community 27 - "v2 Verification Plan Layers"
Cohesion: 0.20
Nodes (10): Exact schema and directory conventions, Human-in-the-loop evaluation, Output-quality evaluation loop, Five-layer verification stack, Generated-quality A/B verification, Manual interview dogfooding, Regression and false-positive fixture testing, Harness Creator v2 verification plan (+2 more)

### Community 28 - "v3 Compression Revision Plan"
Cohesion: 0.27
Nodes (10): Harness Creator v3 revision plan, Doctrine correction and interface PR1, Claim-preserving compression specification, Long-paragraph density metric, No paraphrase-compression rule, Scaffolding deletion, Tabulate then compress cells, R1 v3 guardrail (+2 more)

### Community 29 - "Skill Surface Lint Tests"
Cohesion: 0.20
Nodes (6): FenceBalanceTests, GotchaCountTests, NoExternalToolNamesTests, B10. agents.md opened a ```markdown fence and never closed it, so renderers and…, A count in a heading is a number that goes stale the moment someone adds or…, D14. The shipped skill is a self-contained plugin and must not name Claude Code…

### Community 30 - "Always-Loaded Budget Tests"
Cohesion: 0.20
Nodes (5): AlwaysLoadedBudgetTests, The headline metric of the v2 revision. SKILL.md was 2,185 words but the true…, WS8 step 2. If SKILL.md ever tells the model to load interview.md on every…, Replaces WS8's test_sync_path_does_not_require_interview_md, which asserted the…, Hard line 1: nothing may point at a file that isn't there.

### Community 31 - "Meta-Skill Doctrine Overview"
Cohesion: 0.22
Nodes (9): Always-Loaded Context Budget, Packaged Skill Self-Containment, Three-Stage Skill Disclosure, Conviction over Compliance, Harness Creator Meta-Skill, Harness Authoring Operating Loop, Progressive Disclosure as an Optimum, Harness Creator Repository Contract (+1 more)

### Community 32 - "Community Contribution Policies"
Cohesion: 0.28
Nodes (9): Bug Report Form, Issue Routing Configuration, Pull Request Change Assurance, Contributor Covenant 3.0, Community Enforcement Ladder, Harness Creator Contribution Workflow, Private Vulnerability Reporting, Harness Creator Security Policy (+1 more)

### Community 33 - "CLI Interface Plan Generations"
Cohesion: 0.22
Nodes (9): CLAUDE.md pointer-not-context policy, Argparse AST validation, Self-describing bundled CLI, Single public validation seam, Harness Creator v4 CLI self-description plan, Ablation-based subtraction doctrine, Plugin package closure, Harness Creator v5 interface-subtraction plan (+1 more)

### Community 34 - "v2 Audit and Guardrails"
Cohesion: 0.22
Nodes (9): Harness Creator v2 revision plan, Harness-internal interface principle, Truthfulness over compression, Coverage-and-truthfulness verdict, Do-not-cut guardrails, Five-lens adversarial audit synthesis, Do-not-cut claim categories N1-N6, Project-specific layer routing (+1 more)

### Community 35 - "Prose-Interface Boundary Doctrine"
Cohesion: 0.22
Nodes (9): Interface as compression, Check failure message as interface, One-way lint pairs, Prose owns decisions, checks own consequences, Bidirectional interface boundary, Falsifiability placement test, Prose-interface drift, Mechanical check gap F1-F4 (+1 more)

### Community 36 - "Product Architecture Documentation"
Cohesion: 0.28
Nodes (9): Dual-purpose skill directory, End-to-end generation flow, Harness Creator architecture, Structural, hook, and session validation layers, Five-part operating loop, Harness Creator product overview, Consent-gated behavioral E2E, Harness Creator documentation index (+1 more)

### Community 37 - "Validation Evidence and Escalation"
Cohesion: 0.25
Nodes (9): Authority Routing, Evidence-Driven Escalation, Maintenance Validation Evidence, Inconclusive E2E Handling, Behavioral E2E Validation, Cumulative Validation Evidence Levels, run_e2e.py CLI, Validation and Automation Boundaries (+1 more)

### Community 38 - "Installation Paths and FAQ"
Cohesion: 0.28
Nodes (9): Active Installation Path Verification, Development Symlink Installation, Claude Code Plugin Installation, Single Active Installation Path, Skills CLI Installation, Installation Diagnostics, Harness Creator FAQ, Operational Boundaries (+1 more)

### Community 41 - "Spec Inventory and CLAUDE.md Policy"
Cohesion: 0.25
Nodes (8): Behavior Inventory, Harness Spec, Spec-to-Disk Consistency, CLAUDE.md as Advisory Instructions, CLAUDE.md Content Eligibility Test, Filesystem-as-Inventory Pointer Policy, Skill Listing Budget, Skill Description Trigger

### Community 42 - "Layer Routing and Agent Eligibility"
Cohesion: 0.25
Nodes (8): Custom Agent Eligibility Test, Context-Isolated Agent Role, Failure Feedback Routing, Feature Request Form, Four Routing Questions, Layer Routing Framework, Deliberate-Home Completeness Definition, Interview-Driven Value Proposition

### Community 43 - "Interview Stages and Modes"
Cohesion: 0.25
Nodes (8): Behavior Inventory Stage, Harness Spec Status Lifecycle, Layer Routing Stage, New Extend Improve Sync Modes, Staged Approval Gates, Structured Harness Interview, Sync Drift Reconciliation, Validation Planning Stage

### Community 44 - "Skill Self-Containment Terms"
Cohesion: 0.25
Nodes (8): Packaged reference, Package-internal pointers, Packaged skill, Repository path leaks, Target-project paths, Plugin skill self-containment requirement, External design note, External internal-decision log

### Community 45 - "Bare-Name and Ghost Component Terms"
Cohesion: 0.25
Nodes (8): Bare-name component convention, Bare-name harness specification, Bare-named skill, Artifact status semantics, Ghost agent, Ghost skill, Spec-versus-disk drift specification, Real skill

### Community 46 - "Harness Subtraction Tests"
Cohesion: 0.25
Nodes (4): v5. A harness only grows unless something makes it shrink, and improve mode had…, The slice runs from the improve opening to the next top-level heading, so it…, The guard that makes the rest safe to state. Ablating a hook means observing…, SubtractionTests

### Community 47 - "Validator CLI Edge-Case Tests"
Cohesion: 0.25
Nodes (3): CliEdgeCaseTests, MatcherHelperTests, argparse shapes that are correct but look like omissions. Kept out of good-…

### Community 48 - "Workflow Syntax Probe Tests"
Cohesion: 0.39
Nodes (3): B12, found while trimming the examples in WS6. The node syntax gate checked the…, The examples in references/ must survive the linter that this skill tells the…, WorkflowSyntaxProbeTests

### Community 49 - "Hook Event Reference Docs"
Cohesion: 0.29
Nodes (7): Markdown Lookup with Query Script, Thirty Hook Events Reference, PostToolUse Hook Event, PreToolUse Hook Event, SessionStart Hook Event, Stop Hook Event, Hook Event Router

### Community 50 - "Link Validation and Release Gates"
Cohesion: 0.29
Nodes (7): External Link Validation, Pull Request Soft Failure, Internal Link and Image Validation, Link Validation Policy, Discoverability Acceptance Gates, Discoverability Implementation Checklist, Post-Merge Distribution Gates

### Community 51 - "Distribution and Reddit Launch"
Cohesion: 0.29
Nodes (7): Distribution Execution Record, Supported Install Surfaces, Staged Distribution Sequence, Future Feed Post Variant, Karma Eligibility Gate, Megathread Comment Draft, Reddit Project Showcase Strategy

### Community 52 - "Competing Harness Factory Analysis"
Cohesion: 0.29
Nodes (7): Agent Teams as default execution mode, Boundary-mismatch QA, Eight-phase harness factory workflow, revfactory/harness, Structured elicitation gap, Trigger-eval doctrine, Trigger-description optimization

### Community 53 - "Skill Creator Doctrine Lineage"
Cohesion: 0.29
Nodes (7): Conviction over compliance, Progressive disclosure as an optimum, Skill Creator meta-skill, Rich references, Apply the keep/cut filter to the why, Doctrine single source, Progressive loading architecture

### Community 54 - "Harness Mental Model Layers"
Cohesion: 0.29
Nodes (7): Empirical Rule Reduction, Harness Mental Model, Harness as a System of Surfaces, Judgment and Verified Boundaries, Progressive Disclosure, Harness Completeness, Seven Harness Layers

### Community 55 - "Three-Axis Layer Routing"
Cohesion: 0.29
Nodes (7): Cost-Aware Routing, Load-Timing Routing, Need-First Routing, Three-Axis Layer Routing, Extend Mode, Surgical Harness Delta Review, Harness Layer Routing Summary

### Community 56 - "Broken Harness Fixtures"
Cohesion: 0.33
Nodes (7): Rule Without Paths Frontmatter Fixture, Broken Skill Frontmatter Fixture, Dead-Link Skill Fixture, Missing Skill Reference Targets, Skill Without Description Fixture, Bad Project Always-Loaded Context Fixture, nonexistent-doc.md Missing Reference

### Community 58 - "Do-Not-Cut Guardrail Tests"
Cohesion: 0.29
Nodes (4): GuardrailTests, The do-not-cut list from the audit (audit-synthesis.md section 4), plus the…, R3. The event router is what makes the hooks.md/hooks-events.md split safe --…, This anchor was retired deliberately, which is the review signal the class…

### Community 64 - "Hook and Permission Enforcement"
Cohesion: 0.33
Nodes (6): Deterministic Enforcement Layer, Hook Exit-Code Contract, Hook Eligibility Test, Hook Matcher Semantics, Permission Rule and Hook Pair, Permission Evaluation Order

### Community 65 - "Hook and Settings Semantics"
Cohesion: 0.33
Nodes (6): Hook and Permission Pairing, Hook Unit Testing, Hook I/O Protocol, Settings Precedence, Auto Mode Constraints, Sandbox and Permission Interaction

### Community 66 - "Claim-Loss Verification Protocol"
Cohesion: 0.33
Nodes (6): Claim loss over word count, Atomic claim taxonomy, Blind claim extraction, Claim A/B verification protocol, Seeded claim-loss test, Rewrite license paired with claim-loss audit

### Community 67 - "Harness CLI Script Inventory"
Cohesion: 0.40
Nodes (6): Harness Drift Audit, Structural Harness Validation, audit_harness.py CLI, harness_common.py Internal Helper, validate_harness.py CLI, CLI Self-Description False-Positive Fixture

### Community 68 - "Orphaned Heading Tests"
Cohesion: 0.47
Nodes (3): NoOrphanedHeadingsTests, v6. Two headings in agents.md announced a section and then handed the reader…, A container heading may hand straight to a deeper one -- `## The five stages`…

### Community 69 - "Spec Pointer Policy Tests"
Cohesion: 0.33
Nodes (3): PointerReaderTests, v5 removed CLAUDE.md's pointer at `.claude/harness-spec.md`. The policy…, An HTML comment is allowed and is the point: block comments are stripped before…

### Community 73 - "Parallel Execution Surfaces"
Cohesion: 0.40
Nodes (5): Agent Teams, Agent View, Dynamic Workflows, Four Parallel-Work Surfaces, Subagents

### Community 74 - "Spec Drift Row Detection"
Cohesion: 0.40
Nodes (5): check_spec_drift(), _iter_inventory_rows(), Rows in the Behavior inventory whose status claims a file exists, where no such…, Yield the data rows of the `## Behavior inventory` markdown table as lists of…, _spec_rows_without_files()

### Community 75 - "Product Identity and Discoverability"
Cohesion: 0.40
Nodes (5): AI Agent = Model + Harness Heuristic, Harness Creator Product Identity, Harness Creator Discoverability Overhaul, Immutable Product Boundary, Discover–Understand–Verify–Install–Run Journey

### Community 76 - "v2 Truth Repair Changes"
Cohesion: 0.40
Nodes (5): Domain-narrative removal from examples, External-edit survival, False-positive-first linting, Truth repair workstream, Harness Creator v2 change specification

### Community 77 - "Claim A/B Workflow Script"
Cohesion: 0.40
Nodes (4): CLAIM_SCHEMA, meta, origClaims, VERDICT_SCHEMA

### Community 84 - "Interface Ownership Doctrine"
Cohesion: 0.50
Nodes (4): Interface Ownership Boundary, Behavioral Verification of Interface Doctrine, Parameterized Bundled Scripts, Interface over Instruction

### Community 85 - "Public Claim Boundaries"
Cohesion: 0.50
Nodes (4): Anthropic Steering Guide, Context Engineering Claim Boundaries, Public Claim Boundaries, Category-Based Comparison Frame

### Community 86 - "Hooks Capability Map"
Cohesion: 0.50
Nodes (4): Claude Code Hooks capability map, Five hook handler types, Thirty-event hook lifecycle, Hook-event query interface

### Community 87 - "Hook Contract and Blind Spots"
Cohesion: 0.50
Nodes (4): Hook exit-code and JSON contract, Hook enforcement blind spots, Parallel hook execution semantics, PreToolUse deterministic enforcement

### Community 88 - "Hook Testing CLIs"
Cohesion: 0.67
Nodes (4): Hook Blocking Diagnostics, Command Hook Testing, hook_event.py CLI, test_hook.py CLI

### Community 90 - "Project Rule Fixtures"
Cohesion: 0.67
Nodes (3): Dot-claude project instructions, Always-loaded frontend style rule, Path-scoped TypeScript rule

## Knowledge Gaps
- **174 isolated node(s):** `Rule Without Paths Frontmatter Fixture`, `Missing Skill Reference Targets`, `nonexistent-doc.md Missing Reference`, `check-target.sh script`, `CLAIM_SCHEMA` (+169 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **45 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read()` connect `Orchestration Doctrine Tests` to `Orphaned Heading Tests`, `Spec Pointer Policy Tests`, `Interface Doctrine Tests`, `Harness Subtraction Tests`, `Interface Contradiction Tests`, `Dead Pointer Coverage Tests`, `Package Closure Regression Tests`, `Do-Not-Cut Guardrail Tests`, `Wrap-Up Ordering Tests`, `Hook Timeout Fact Tests`, `Skill Surface Lint Tests`, `Always-Loaded Budget Tests`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `ConsequenceClauseTests` connect `Finding Consequence Clause Tests` to `Validator CLI Edge-Case Tests`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `BadHarnessTests` connect `Bad-Harness Validation Tests` to `Validator CLI Edge-Case Tests`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **What connects `Rule Without Paths Frontmatter Fixture`, `Missing Skill Reference Targets`, `nonexistent-doc.md Missing Reference` to the rest of the system?**
  _174 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Harness Validation CLI Checks` be split into smaller, more focused modules?**
  _Cohesion score 0.06340326340326341 - nodes in this community are weakly interconnected._
- **Should `Harness Design Principles` be split into smaller, more focused modules?**
  _Cohesion score 0.045328399629972246 - nodes in this community are weakly interconnected._
- **Should `Shared Harness Parsing Helpers` be split into smaller, more focused modules?**
  _Cohesion score 0.05391120507399577 - nodes in this community are weakly interconnected._