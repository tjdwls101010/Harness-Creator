# Community and distribution

## 1. Trust surfaces

The repository provides:

- a best-effort security policy using GitHub private vulnerability reporting;
- Contributor Covenant 3.0 with the maintainer's existing public Git author email as the confidential reporting route;
- a support router for FAQ, troubleshooting, bugs, features, documentation, and security;
- structured bug, feature, and documentation Issue Forms;
- blank issues disabled;
- a pull-request template;
- contribution guidance grounded in the repository's actual checks.

No support, response, or fix SLA is promised.

## 2. Install surfaces

The recommended current path is the repository's Claude Code marketplace. The skills CLI is secondary. A development symlink is documented for contributors. Users are warned to keep only one path active because the same skill can otherwise register more than once under different names.

## 3. Post-merge distribution sequence

1. Apply the approved GitHub description, topics, feature settings, and private vulnerability reporting.
2. Perform one isolated skills CLI installation in a temporary directory and remove it afterward.
3. Confirm the public skills.sh page is indexed and available.
4. With separate approval, submit to Anthropic's `claude-community` marketplace.
5. Wait at least 72 hours, then with separate approval submit the human-only web Issue Form for `hesreallyhim/awesome-claude-code`.
6. Wait another 72 hours, then with separate approval post an r/ClaudeCode Weekly Showcase comment.
7. Do not submit to `claude-plugins-official`; Anthropic documents no application process for it.
8. If the community marketplace approves the plugin, open a small follow-up pull request that promotes that install path over the personal marketplace.

No marketplace, awesome-list, Reddit, release, tag, social preview, or website action belongs in the documentation pull request.
