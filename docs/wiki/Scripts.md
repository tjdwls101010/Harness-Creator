# The Scripts

harness-creator ships four command-line tools that do the mechanical, deterministic work the model shouldn't do by hand: linting a harness, auditing an existing one, unit-testing a hook, and driving a real headless session. This page is the reference for all four — their exact flags, output, exit codes, and when they run. A fifth file, `harness_common.py`, is a shared helper module, not a CLI.

All four are Python 3.10+ and use only the standard library, so there is nothing to install. Each is a parameterized CLI keyed off a path-like argument (`--path` for `validate_harness.py` and `audit_harness.py`, `--project` for `run_e2e.py`, and `--settings`/`--command` for `test_hook.py`), so nothing is hard-coded to this repo. The skill invokes them by absolute path as `${CLAUDE_SKILL_DIR}/scripts/<name>.py`; the examples below use the plain script name for readability, and you can run any of them yourself with `python3 <path-to-script> ...`.

## At a glance

| Tool | One-line purpose | Signature |
| --- | --- | --- |
| `validate_harness.py` | Deterministic lint of a harness | `--path <repo> [--json] [--strict]` |
| `audit_harness.py` | Phase-0 inventory + drift + suggested re-entry mode | `--path <repo> [--json]` |
| `test_hook.py` | Unit-test a hook without a live session | `(--settings <f> --event <E> [--tool <T>] [--input-field k=v] \| --command <script> --event <E> [--input <f>]) [--matrix] [--json]` |
| `run_e2e.py` | Spawn a headless `claude -p` session and record it | `--project <repo> --prompt "..." [--prompt-file f] [--model] [--timeout] [--out] [--json] [--permission-mode] [--isolate]` |

Exit-code convention across the scripts: `0` is the clean/expected outcome, `2` (`EXIT_USAGE_ERROR`) always means the script itself couldn't run — a bad `--path`, a missing required flag, unparseable JSON passed on the command line. The meaning of `1` differs per tool and is noted below.

## validate_harness.py

The free, always-run first tier of [Validation](Validation.md). It statically lints everything a harness can contain — `settings.json` hooks and permissions, skills, agents, workflows, rules, `CLAUDE.md`, and drift between what's on disk and `.claude/harness-spec.md` — and reports each finding as an error (`E`) or warning (`W`).

```
validate_harness.py --path /path/to/target-repo
validate_harness.py --path /path/to/target-repo --json
validate_harness.py --path /path/to/target-repo --strict
```

Default output is human-readable: an `== Errors ==` section, a `== Warnings ==` section, a `N error(s), M warning(s).` tally, and a final `PASS` or `FAIL`. `--json` emits `{"errors": N, "warnings": M, "findings": [...]}`. `--strict` promotes warnings to failures — use it in CI.

Exit codes: `0` = no errors (warnings can still be present unless `--strict`); `1` = at least one error, or under `--strict` at least one warning; `2` = the script couldn't run.

The skill runs this immediately after generating or editing any component and does not treat the work as done until it exits `0`; it runs again as a whole-harness pass at wrap-up. Run it yourself after hand-editing a harness, or wire `--strict` into CI to keep a harness from rotting.

## audit_harness.py

The Phase-0 inventory the skill runs before any interview, every single time it's invoked, so re-entry never guesses at what already exists. See [Re-entry Modes](Re-entry-Modes.md) for how the result steers the session.

```
audit_harness.py --path /path/to/target-repo
audit_harness.py --path /path/to/target-repo --json
```

Default output is a Markdown report with five sections: a component inventory (`CLAUDE.md`, rules, skills, agents, workflows, settings), `harness-spec.md` drift (components on disk the spec never mentions), user-scope conflict candidates (a user-level `~/.claude/CLAUDE.md` or a same-named user skill that could shadow the project's), hygiene signals (dead links, duplicate agent names, non-executable hook scripts, and the lint error/warning counts — it calls `validate_harness.py` internally for these), and a suggested mode. `--json` emits the same data as a nested object.

The suggested mode is one of `new`, `extend`, `improve`, or `sync`, chosen from what the audit finds — but the audit says outright that it cannot distinguish `extend` from `improve` on its own, so the skill confirms that choice with you.

Exit code is always `0`; an audit is a report, not a pass/fail check. The only non-zero exit is `2` when `--path` itself is invalid.

## test_hook.py

Unit-tests a single hook, or a whole `settings.json`, without spawning a live session. It reproduces Claude Code's matcher evaluation exactly (exact-string/list mode unless a non-exact character flips the matcher to an unanchored regex), runs the hook's command with a realistic sample input built for the chosen event, then interprets the exit code and output in plain English against that event's exit-code contract.

```
# Look up matching hooks in settings.json and run them:
test_hook.py --settings .claude/settings.json --event PreToolUse \
    --tool Bash --input-field command="rm -rf /"

# Run one script directly with a specific input file:
test_hook.py --command .claude/hooks/guard.sh --event PreToolUse \
    --input sample.json

# Show the matcher matrix without executing anything:
test_hook.py --settings .claude/settings.json --matrix
```

Flags: `--settings` (look hooks up in a settings file) or `--command` (run one script directly); `--event` (required unless `--matrix`); `--tool` (for matcher evaluation and to shape a realistic `tool_input`, default `Bash`); `--input` (a JSON file to use as stdin); `--input-field k=v` (repeatable override of one field, parsed as JSON first so nested objects work); `--matrix` (print which hook groups match which representative tools, executing nothing — requires `--settings`); `--json`.

Default output prints the event, the sample input, and per hook: the command, exit code, stdout, stderr, and one or more `=> ...` interpretation lines — for example, that exit `2` blocks and stderr is the reason Claude sees, that exit `1` does not block, or that JSON on stdout is discarded on any nonzero exit. Exit codes are just `0` when the tool ran and `2` on a usage error; a hook that "fails" isn't reported by process exit but explained in the interpretation lines.

The skill runs this on every hook it generates or wires before considering the hook delivered. Run it yourself whenever you're unsure whether a matcher fires or whether a hook actually blocks.

## run_e2e.py

The second, paid tier of validation: it spawns a real headless `claude -p` session against a project, captures the streamed transcript, and writes it out for a separate grading agent to judge. It does not grade anything itself. Because it costs tokens and touches a live model, the skill only runs it with your consent, composing the prompts from the spec's Validation scenarios.

```
run_e2e.py --project /path/to/target-repo --prompt "set up a harness for this project"
run_e2e.py --project /path/to/target-repo --prompt-file prompt.txt --out ./e2e-out --json
run_e2e.py --project /path/to/target-repo --prompt "..." --isolate --model claude-sonnet-5
```

Flags: `--project` (required); `--prompt` or `--prompt-file` (one is required); `--model`; `--timeout` (seconds, default `300`); `--out` (directory for the outputs, default a printed temp dir); `--json`; `--permission-mode` (passed through to `claude -p`); `--isolate` (copy the project to a temp dir first so writes don't touch the original). It removes `CLAUDECODE` from the environment so a nested `claude -p` can run inside the current session.

Output is always two files in `--out`: `transcript.jsonl` (the raw stream) and `summary.json` (parsed tool calls, skill invocations, heuristic hook evidence, and the final result envelope). Stdout prints a short summary, or the full summary with `--json`. Exit code is `0` when the session ran cleanly, `1` when it errored (timeout, `claude` not on PATH, a nonzero exit with no output), and `2` on a usage error.

Caveat, stated in the script itself: its headless permission handling was never empirically verified when the script was built. `--isolate` combined with `--dangerously-skip-permissions` (which `--isolate` implies unless you also pass `--permission-mode`) is the documented best guess, not a confirmed-safe default — so treat your first real run as the actual verification, and only pass `--isolate` for a prompt that writes files rather than a purely read-only one.

## harness_common.py (shared helper, not a CLI)

The four scripts import this module so they all agree on the same facts instead of each re-implementing them and silently disagreeing. It holds a single conservative frontmatter parser (which returns "could not verify" rather than guess on YAML it can't safely parse), the canonical tool-name list, the table of all 30 hook events (including which ones accept a matcher and which carry a tool context), the matcher-exactness helper, the shared exit-code constants, a lenient JSON loader, and the filesystem iterators for skills, agents, workflows, rules, and settings. You never invoke it directly.

## See also

- [Validation](Validation.md) — how the two validation tiers fit together
- [Re-entry Modes](Re-entry-Modes.md) — how `audit_harness.py`'s suggested mode drives a return visit
- [Generated Components](Generated-Components.md) — what these scripts are checking the shape of
