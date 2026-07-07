# FAQ & Troubleshooting

## General

### Is harness-creator itself a harness?
Partly. It's a Claude Code **skill** (with reference files and scripts), packaged as a **plugin**. It generates harnesses for *other* projects; it isn't a full harness of the kind it produces. The repo does dogfood its own output shape, though — the skill directory is simultaneously the plugin component and a project skill for this repo.

### Do I need to know all the Claude Code gotchas to use it?
No — that's the point. The gotchas are baked into the reference files the skill loads while generating each component. You describe what you want in plain language; it handles the mechanics.

### What does it cost to run?
The design and generation phases cost normal conversation tokens. The deterministic linter and hook unit-tests are free (local Python). The optional end-to-end validation spawns real headless Claude sessions and costs tokens — so it only runs with your explicit consent.

### Will it overwrite my existing `.claude/` setup?
No. Every invocation starts by auditing what already exists and branching into the right mode (new / extend / improve / sync) rather than regenerating from scratch. See [Re-entry Modes](Re-entry-Modes.md).

### Does it work on any project?
It's language- and stack-agnostic — it scouts your build system, test runner, and layout during the audit, and interviews you for the rest. It's most valuable on projects where Claude keeps making the same project-specific mistakes.

## Installation

### `/harness-creator` vs `/harness-creator:harness-creator` — which is it?
Depends on how you installed it. The **symlink** install exposes it as bare `/harness-creator`. The **plugin** install namespaces it as `/harness-creator:harness-creator`. Either way, natural-language auto-triggering works the same. See [Getting Started](Getting-Started.md).

### Can I use both install methods at once?
No — on the same machine, running the symlink and the plugin install together double-registers the skill under two different names. Pick one. Use the symlink for developing this repo; use the plugin for using it elsewhere.

### After installing the plugin, why is there a large folder in my plugin cache?
If you installed from a **local directory path** (e.g. `claude plugin marketplace add ./`), Claude Code copies the raw filesystem — including gitignored files like a local docs snapshot — into `~/.claude/plugins/cache/`. This is harmless and only happens with local-path installs; a GitHub-source install (`claude plugin marketplace add tjdwls101010/Harness-Creator`) only fetches git-tracked content and stays small. Note also that uninstalling doesn't always remove the cache folder — you can delete it by hand.

## Limitations

### The end-to-end validation permission handling is "a best guess" — what does that mean?
`run_e2e.py` launches headless `claude -p` sessions, and the exact permission flow it uses (`--isolate` to run against a throwaway copy, plus `--dangerously-skip-permissions`) was built from documented behavior but never confirmed to work end to end in the environment that built the skill — a spawned `claude` process there couldn't authenticate at all. It's very likely correct, but treat your **first real e2e run as the actual verification**, and prefer `--isolate` for anything that writes files so the run can't touch your real project. See [Validation & Testing](Validation.md).

### Can the interview itself be automatically tested?
No. `AskUserQuestion` — the tool that drives the structured interview — doesn't exist in headless or subagent contexts. So the *generated harness* can be e2e-tested, but the *interview that produces it* can only be validated by using it manually. A clean e2e report validates the output, not the conversation.

### Why doesn't it just generate everything automatically without asking me so much?
Because guessing your requirements is the failure mode. A harness built on wrong assumptions is worse than no harness — it actively misleads Claude. The interview is deliberately front-loaded so the spec (the written record of what you agreed to) is correct before any file is written. It does compress or skip stages when the answer is already clear, but it won't skip the spec-approval gate.

## Troubleshooting

### A generated hook isn't firing.
Reproduce it with [`test_hook.py`](Scripts.md) — it shows exactly which hook groups match a given event/tool and runs the hook against sample input. The usual culprits: a matcher that silently became a regex, an MCP matcher missing its trailing `.*`, or the wrong event. The tool explains the exit-code semantics for the specific event.

### A committed `allow` permission rule still prompts me right after cloning.
Project-scope `allow` rules only take effect after you accept the workspace-trust dialog for that directory. `deny` and `ask` rules apply immediately regardless. This is expected, not a broken harness.

### I edited `CLAUDE.md` mid-session and Claude didn't pick up the change.
`CLAUDE.md` is read once at session start. Edits take effect after `/clear`, `/compact`, or a restart. (Skills, by contrast, are re-read live.)

### `validate_harness.py` reports errors I don't understand.
Each finding names the file, the location, and the reason. Run with `--json` for machine-readable output. If it flags something you believe is correct, that's worth a bug report — cite the Claude Code behavior you observed.

### Where do I report a wrong or missing gotcha?
Open a GitHub issue citing the Claude Code behavior you observed. Because the skill's entire value is gotcha accuracy, a well-sourced correction is the most valuable contribution you can make. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Where to go next

- Understand the model: [Concepts](Concepts.md)
- Run it: [Getting Started](Getting-Started.md)
- See what it can build: [Generated Components](Generated-Components.md)
