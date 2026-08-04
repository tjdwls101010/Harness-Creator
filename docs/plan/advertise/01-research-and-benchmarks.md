# Research and benchmarks

This synthesis separates established guidance, correlational evidence, product-mechanics sources, and project-specific decisions.

## 1. Documentation discovery

[GitHub's README guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) says a repository front page should explain what a project does, why it is useful, how to start, where to get help, and who maintains it. It also recommends relative links for clone-friendly navigation and moving depth out of the README. That supports a concise front door linked to canonical repository docs.

[Diátaxis](https://diataxis.fr/start-here/) separates tutorials, how-to guides, reference, and explanation because each serves a different user need. Harness Creator adopts those four task shapes under `docs/wiki/` rather than treating the documentation as one long handbook.

[The Good Docs Project](https://www.thegooddocsproject.dev/) reinforces template-driven completeness and user enablement. [Google's audience guidance](https://developers.google.com/tech-writing/one/audience) adds the key constraint for this repository: write for Claude Code users who do not already know harness vocabulary, and explain only the knowledge gap between their current state and a successful task.

## 2. Open-source strategy and trust

[Mozilla's open-source archetypes](https://blog.mozilla.org/blogarchive/blog/2018/05/15/whats-your-open-source-strategy-here-are-10-answers/) argues that governance and community choices should follow explicit strategic intent rather than an assumed universal model. Harness Creator is a maintainer-led utility seeking adoption, feedback, and focused contributions; it is not presented as a community-governed platform.

[Open Source Guides](https://opensource.guide/bn/starting-a-project/) recommends a license, README, contribution guide, and code of conduct as baseline expectation-setting surfaces. The [Linux Foundation's starting guide](https://www.linuxfoundation.org/resources/open-source-guides/starting-an-open-source-project) likewise emphasizes planning for maintenance, documentation, governance, and community operations rather than treating publication as the end of the work.

The repository therefore adds explicit support and security routes, structured issue intake, a pull-request template, and honest best-effort maintenance language without response-time promises.

## 3. Discovery and health signals

[GitHub topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics) improve classification and topic-page discovery. The approved topics span ecosystem, domain, and form rather than repeating synonyms.

[GitHub repository traffic](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-traffic-to-a-repository) provides a rolling fourteen-day view of clones, visitors, referrers, and popular content. These are short-window observations, so the metrics log takes dated snapshots instead of pretending GitHub provides a permanent analytics history.

The [CHAOSS starter project-health model](https://www.chaoss.community/starter-project-health-metrics-model/) highlights time to first response, change-request closure ratio, bus factor, and release frequency. At this repository's current scale, those are maintenance-health context; views, visitors, clones, and install signals remain the more direct discovery indicators.

## 4. Empirical README studies

Liu, Noei, and Lyons studied [14,901 open-source Java repositories](https://enoei.github.io/papers/liu2022readme.pdf). README structures containing elements such as project name, installation, usage, license, code snippets, and image links were associated with higher star counts.

Wang, Wang, and Chen studied [5,000 sampled GitHub repositories across more than twenty languages](https://petertsehsun.github.io/papers/jss_2023_readme.pdf), with filtering producing the analyzed popular and non-popular groups. They found associations between popularity and factors including lists, links, and update frequency after controlling for repository characteristics.

Both studies are correlational, not causal. The second paper states this explicitly. They justify making the README clearer and maintainable; they do not show that a documentation rewrite will cause stars, installs, or adoption.

## 5. Context engineering and verified boundaries

[Anthropic's context-engineering guidance](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) reports that more than 80% of the Claude Code system prompt was removed for newer models with no measurable loss on Anthropic's coding evaluations. The engineering lesson is empirical deletion of redundant constraints while retaining product context, tools, references, and evaluation—not indiscriminate prompt minimization and not a claim that every harness should shrink by the same percentage.

[Anthropic's steering guide](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) distinguishes always-loaded context, path-scoped rules, on-demand skills, isolated subagents, and deterministic hooks. It explicitly routes reliable blocking to hooks and permissions rather than prose.

[Claude's Constitution](https://www.anthropic.com/constitution) describes the role of principles, operator context, and judgment when instructions cannot enumerate every case. It supports the general rationale for principle-based behavior, not any performance claim about this project.

In the [Amanda Askell interview](https://podcast.newcomer.co/episode/amanda-askell-on-ai-consciousness-claude-amp-silicon-valleys-biggest-fear), the relevant engineering point is that models encounter novel situations requiring judgment and that evaluation of judgment-heavy behavior remains difficult. The interview is not used here to make claims about consciousness, emotions, model welfare, or respectful treatment improving output.

Boris Cherny's public account of prompt reduction is treated consistently with Anthropic's published context-engineering article: remove empirically redundant constraints, preserve useful product context, and evaluate the result. Harness Creator does not claim an “80% improvement.”

## 6. Distribution mechanics

[Claude plugin creation and submission guidance](https://code.claude.com/docs/en/plugins) documents local validation and the reviewed `claude-community` submission path. It also states that the official marketplace is curated separately and has no application process.

[Claude plugin discovery guidance](https://code.claude.com/docs/en/discover-plugins) explains the two-step custom-marketplace flow: add the marketplace, then install a plugin. It also warns that plugins are trusted code and users should inspect their source.

[skills.sh documentation](https://www.skills.sh/docs) documents `npx skills add`, public discovery, and anonymous install telemetry. The README includes the install path but deliberately omits an install-count badge.

## 7. Peer repository observations

Peer repositories are named only in this internal dossier. `revfactory/harness` demonstrates demand for harness generation and strong launch packaging, but also illustrates risks of fixed-shape generation, marketing claims ahead of verification, and unbacked process promises. `anthropics/skills` and the Claude community marketplace are useful distribution and packaging references. `hesreallyhim/awesome-claude-code` is a later discovery channel, not a product benchmark.

Public comparison copy therefore uses categories—manual configuration, static templates, component collections, and Harness Creator—rather than named competitors.

## 8. Research conclusion

The defensible strategy is to reduce first-visit uncertainty, show the workflow visually, provide an immediately executable install path, separate learning from reference, publish maintenance and security expectations, and observe changes over time. None of the research supports guaranteeing growth or attributing later traffic to one change.
