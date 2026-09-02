#!/usr/bin/env python3
"""Unit-test a single hook (or a whole settings.json) without a real session.

    # Find hooks matching an event/tool in settings.json and run them:
    python test_hook.py --settings .claude/settings.json --event PreToolUse \\
        --tool Bash --input-field command="rm -rf /"

    # Run one script directly with a specific input file:
    python test_hook.py --command .claude/hooks/guard.sh --event PreToolUse \\
        --input sample.json

    # Show the matcher matrix without executing anything:
    python test_hook.py --settings .claude/settings.json --matrix

Runs a hook's command with a sample stdin built from the documented input
shape for the event, then explains what its exit code and output mean for
that event. Matcher evaluation is a documentation-based approximation:
Claude Code tests a non-exact matcher with a JavaScript RegExp, and this
script approximates that with Python `re`. The sample input is representative,
not a recording. What a real session does is final; PASS here means the hook
ran and its exit code is one the event can act on.
"""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_common as hc

DEFAULT_TIMEOUT = 10

# Representative tool names for --matrix mode and for building a plausible
# `tool_name` when the user doesn't pass --tool.
REPRESENTATIVE_TOOLS = ["Bash", "Edit", "Write", "Read", "WebFetch", "NotebookEdit"]

COMMON_FIELDS = {
    "session_id": "test-session-0001",
    "transcript_path": "/tmp/test-hook/transcript.jsonl",
    "cwd": str(Path.cwd()),
    "permission_mode": "default",
}


def _event_fields(event, tool):
    """Return event-specific sample fields, layered on COMMON_FIELDS. Field
    shapes follow references/hooks-events.md."""
    tool = tool or "Bash"
    tool_inputs = {
        "Bash": {"command": "echo hello"},
        "Edit": {"file_path": "/tmp/example.txt", "old_string": "a", "new_string": "b"},
        "Write": {"file_path": "/tmp/example.txt", "content": "hello"},
        "Read": {"file_path": "/tmp/example.txt"},
        "WebFetch": {"url": "https://example.com", "prompt": "summarize"},
        "NotebookEdit": {"notebook_path": "/tmp/example.ipynb", "new_source": "print(1)"},
    }
    tool_input = tool_inputs.get(tool, {"arg": "value"})

    table = {
        "SessionStart": {"hook_event_name": "SessionStart", "source": "startup", "model": "claude-sonnet-5"},
        "Setup": {"hook_event_name": "Setup", "trigger": "init"},
        "InstructionsLoaded": {"hook_event_name": "InstructionsLoaded", "file_path": "CLAUDE.md", "memory_type": "Project", "load_reason": "session_start"},
        "UserPromptSubmit": {"hook_event_name": "UserPromptSubmit", "prompt": "Write a function to calculate factorial"},
        "UserPromptExpansion": {"hook_event_name": "UserPromptExpansion", "expansion_type": "slash_command", "command_name": "deploy", "command_args": "", "command_source": "project", "prompt": "/deploy"},
        "MessageDisplay": {"hook_event_name": "MessageDisplay", "turn_id": "t1", "message_id": "m1", "index": 0, "final": True, "delta": "Hello"},
        "PreToolUse": {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input, "tool_use_id": "tool-0001"},
        "PermissionRequest": {"hook_event_name": "PermissionRequest", "tool_name": tool, "tool_input": tool_input},
        "PermissionDenied": {"hook_event_name": "PermissionDenied", "tool_name": tool, "tool_input": tool_input, "tool_use_id": "tool-0001", "reason": "classifier denied"},
        "PostToolUse": {"hook_event_name": "PostToolUse", "tool_name": tool, "tool_input": tool_input, "tool_use_id": "tool-0001", "tool_response": {"output": "ok"}},
        "PostToolUseFailure": {"hook_event_name": "PostToolUseFailure", "tool_name": tool, "tool_input": tool_input, "error": "boom", "duration_ms": 12},
        "PostToolBatch": {"hook_event_name": "PostToolBatch", "tool_calls": [{"tool_name": tool, "tool_input": tool_input, "tool_use_id": "tool-0001", "tool_response": "ok"}]},
        "Notification": {"hook_event_name": "Notification", "notification_type": "permission_prompt", "message": "Claude wants to run a command"},
        "SubagentStart": {"hook_event_name": "SubagentStart", "agent_type": "general-purpose", "agent_id": "agent-0001"},
        "SubagentStop": {"hook_event_name": "SubagentStop", "agent_type": "general-purpose", "agent_id": "agent-0001", "stop_hook_active": False},
        "TaskCreated": {"hook_event_name": "TaskCreated", "task_id": "task-0001", "task_subject": "Fix bug"},
        "TaskCompleted": {"hook_event_name": "TaskCompleted", "task_id": "task-0001", "task_subject": "Fix bug"},
        "Stop": {"hook_event_name": "Stop", "stop_hook_active": False, "last_assistant_message": "Done."},
        "StopFailure": {"hook_event_name": "StopFailure", "error": "rate_limit"},
        "TeammateIdle": {"hook_event_name": "TeammateIdle", "teammate_name": "reviewer"},
        "ConfigChange": {"hook_event_name": "ConfigChange", "source": "project_settings", "file_path": ".claude/settings.json"},
        "CwdChanged": {"hook_event_name": "CwdChanged", "old_cwd": "/tmp/a", "new_cwd": "/tmp/b"},
        "FileChanged": {"hook_event_name": "FileChanged", "file_path": ".env", "event": "change"},
        "WorktreeCreate": {"hook_event_name": "WorktreeCreate", "name": "feature-x"},
        "WorktreeRemove": {"hook_event_name": "WorktreeRemove", "worktree_path": "/tmp/worktree-x"},
        "PreCompact": {"hook_event_name": "PreCompact", "trigger": "auto"},
        "PostCompact": {"hook_event_name": "PostCompact", "trigger": "auto", "compact_summary": "Summarized 40 messages."},
        "SessionEnd": {"hook_event_name": "SessionEnd", "reason": "clear"},
        "Elicitation": {"hook_event_name": "Elicitation", "mcp_server_name": "example-server", "message": "Provide API key", "mode": "form"},
        "ElicitationResult": {"hook_event_name": "ElicitationResult", "mcp_server_name": "example-server", "action": "accept", "content": {"key": "value"}},
    }
    fields = dict(COMMON_FIELDS)
    fields.update(table.get(event, {"hook_event_name": event}))
    return fields


def build_sample_input(event, tool, overrides):
    data = _event_fields(event, tool)
    for key, value in overrides.items():
        data[key] = value
    return data


def matches_matcher(matcher, candidate):
    """Approximate Claude Code's matcher evaluation (references/hooks.md):
    exact-string/list mode unless a non-exact character is present, in which
    case Claude Code runs an UNANCHORED JavaScript RegExp test, approximated
    here with Python `re.search`."""
    if matcher is None or matcher == "":
        return True
    if hc.is_exact_matcher(matcher):
        options = [m.strip() for m in matcher.replace(",", "|").split("|")]
        return candidate in options
    import re
    try:
        return re.search(matcher, candidate) is not None
    except re.error:
        return False


def find_matching_groups(settings, event, tool):
    hooks = settings.get("hooks", {})
    groups = hooks.get(event, [])
    matched = []
    for gi, group in enumerate(groups):
        matcher = group.get("matcher")
        if matcher is None or matches_matcher(matcher, tool or ""):
            matched.append((gi, group))
    return matched


def run_hook_command(hook_entry, input_data, settings_dir):
    htype = hook_entry.get("type")
    if htype != "command":
        return None, None, None, f"skipping non-command handler type '{htype}' -- test_hook.py only executes 'command' hooks directly"

    command = hook_entry.get("command", "")
    command = command.replace("${CLAUDE_PROJECT_DIR}", str(settings_dir))
    args = hook_entry.get("args")

    stdin_text = json.dumps(input_data)
    try:
        if args is not None:
            argv = [command] + list(args)
            result = subprocess.run(argv, input=stdin_text, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        else:
            result = subprocess.run(command, shell=True, input=stdin_text, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, None, None, f"hook timed out after {DEFAULT_TIMEOUT}s"
    except FileNotFoundError as e:
        return None, None, None, f"could not execute: {e}"
    except PermissionError:
        return None, None, None, "permission denied -- is the script marked executable (chmod +x)?"

    return result.returncode, result.stdout, result.stderr, None


def interpret(event, exit_code, stdout, stderr):
    """Turn a raw exit code + stdout/stderr into the plain-English meaning
    a generator needs, per the exit-code contract in references/hooks.md."""
    lines = []
    decision_json = None
    if stdout.strip():
        try:
            decision_json = json.loads(stdout)
        except json.JSONDecodeError:
            if exit_code == 0:
                lines.append("exit 0 with non-JSON stdout -- stdout is added as plain visible context (only a few events treat plain stdout as context at all; see the event's row in hooks-events.md), not parsed as a decision.")
    # decision_json is only read by Claude Code on exit 0 -- on any other
    # exit code it is discarded, which the exit_code == 2 branch reports.
    if exit_code != 0:
        stdout_json_for_exit2 = decision_json
        decision_json = None
    else:
        stdout_json_for_exit2 = None

    if event == "WorktreeCreate":
        if exit_code != 0:
            lines.append(f"exit {exit_code} -- WorktreeCreate is the one event where ANY nonzero exit (not just 2) fails creation.")
        elif not stdout.strip():
            lines.append("exit 0 but empty stdout -- WorktreeCreate must print the created worktree's path on stdout, or creation fails.")
        else:
            lines.append(f"exit 0, path returned: {stdout.strip()!r} -- worktree creation proceeds.")
        return lines

    if exit_code == 2:
        lines.append(f"exit 2 -- BLOCKS the action for events that support blocking. stderr is what Claude sees as the reason: {stderr.strip()!r}")
        if stdout_json_for_exit2 is not None:
            lines.append("Note: stdout also contained JSON, but it is DISCARDED on exit 2 -- only stderr is read. Pick one channel: exit 2+stderr, or exit 0+JSON, not both.")
    elif exit_code == 1:
        lines.append(f"exit 1 -- does NOT block anything (only exit 2 does). This is a non-blocking hook error; the action proceeds. If you intended to block, this hook has a bug. stderr: {stderr.strip()!r}")
    elif exit_code == 0:
        if decision_json is not None:
            hso = decision_json.get("hookSpecificOutput", {})
            decision = decision_json.get("decision")
            if decision == "block":
                lines.append(f"exit 0, JSON decision:block -- blocks/keeps-going depending on the event. reason: {decision_json.get('reason', '')!r}")
            perm = hso.get("decision", {}) if isinstance(hso.get("decision"), dict) else None
            if perm and perm.get("behavior") == "deny":
                lines.append("exit 0, hookSpecificOutput.decision.behavior:deny -- blocks the tool call.")
            if hso.get("additionalContext") or decision_json.get("additionalContext"):
                lines.append("exit 0, additionalContext present -- injected as an invisible system reminder (make sure it reads as a fact, not a command, or it may trip prompt-injection defenses).")
            if not any("block" in l or "deny" in l or "additionalContext" in l for l in lines):
                lines.append(f"exit 0, JSON output present but no recognized decision field for this event -- double check the field name against this event's row in hooks-events.md. Raw: {json.dumps(decision_json)[:300]}")
        else:
            lines.append("exit 0, no JSON output -- hook ran successfully with no side effect on the decision channel (fine for a pure side-effect hook like a formatter).")
    else:
        lines.append(f"exit {exit_code} -- non-2 nonzero exit, same as exit 1: does NOT block. stderr: {stderr.strip()!r}")

    return lines


def cmd_matrix(settings, tools=None):
    tools = tools or REPRESENTATIVE_TOOLS
    hooks = settings.get("hooks", {})
    rows = []
    for event, groups in hooks.items():
        if event not in hc.HOOK_EVENTS:
            rows.append((event, "?", f"unknown event -- see validate_harness.py"))
            continue
        if event in hc.NON_MATCHER_EVENTS:
            rows.append((event, "(any)", f"{len(groups)} group(s), fires unconditionally"))
            continue
        for tool in tools:
            matched_groups = [gi for gi, g in enumerate(groups) if matches_matcher(g.get("matcher"), tool)]
            if matched_groups:
                rows.append((event, tool, f"matches group(s) {matched_groups}"))
    return rows


def verdict(results, quiet=False):
    """Not "the hook exited 0": a blocking hook exits 2 on the path it exists
    to block, and that is the hook working. What fails is a hook that could
    not be exercised, or one whose exit code makes it a no-op --
    references/hooks.md documents exit 1 as the mistake that leaves a policy
    silently doing nothing."""
    failures = []
    for r in results:
        if "error" in r:
            failures.append(r["error"])
        elif r["exit_code"] not in (0, 2):
            failures.append(
                f"exit {r['exit_code']}: a nonzero code other than 2 is a "
                "NON-BLOCKING error -- the action proceeds and the notice is "
                "easy to miss. Exit 2 to block, 0 to allow."
            )
    if not results:
        failures.append("no hook was executed, so nothing was verified")
    if failures:
        if not quiet:
            print("\nFAIL")
            for f in failures:
                print(f"  - {f}")
        return hc.EXIT_LINT_FAILED
    if not quiet:
        print("\nPASS " + FINALITY_NOTE)
    return hc.EXIT_OK


FINALITY_NOTE = (
    "(sample input, matcher approximated with Python re; what a real session does is final)"
)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--settings", help="path to settings.json to look up hooks in")
    source.add_argument("--command", help="run this script directly, bypassing settings.json lookup")
    parser.add_argument("--event", choices=sorted(hc.HOOK_EVENTS), metavar="EVENT",
                        help="hook event name; one of: " + ", ".join(sorted(hc.HOOK_EVENTS)))
    parser.add_argument("--tool", help="tool name, for matcher evaluation and building tool_input (default: Bash)")
    parser.add_argument("--input", help="path to a JSON file to use as the hook's stdin input")
    parser.add_argument("--input-field", action="append", default=[], metavar="k=v", help="override/add a field in the sample input; repeatable")
    parser.add_argument("--matrix", action="store_true", help="print the matcher matrix for --settings without executing anything")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    args = parser.parse_args()

    overrides = {}
    for kv in args.input_field:
        if "=" not in kv:
            print(f"error: --input-field must be k=v, got: {kv}", file=sys.stderr)
            return hc.EXIT_USAGE_ERROR
        k, v = kv.split("=", 1)
        try:
            # tool_input etc. are usually objects -- try JSON first so
            # --input-field 'tool_input={"file_path": "x"}' produces a real
            # nested object instead of a JSON-encoded string.
            overrides[k] = json.loads(v)
        except json.JSONDecodeError:
            overrides[k] = v

    if args.matrix:
        if not args.settings:
            parser.error("--matrix requires --settings")
        data, err = hc.load_json_lenient(Path(args.settings))
        if err:
            print(f"error: {err}", file=sys.stderr)
            return hc.EXIT_USAGE_ERROR
        rows = cmd_matrix(data, tools=[args.tool] if args.tool else None)
        if args.json:
            print(json.dumps([{"event": e, "tool": t, "result": r} for e, t, r in rows], indent=2))
        else:
            for e, t, r in rows:
                print(f"{e:20s} {t:15s} {r}")
        return hc.EXIT_OK

    if not args.event:
        parser.error("--event is required (unless using --matrix)")

    if args.input:
        input_data, err = hc.load_json_lenient(Path(args.input))
        if err:
            print(f"error: {err}", file=sys.stderr)
            return hc.EXIT_USAGE_ERROR
        input_data.update(overrides)
    else:
        input_data = build_sample_input(args.event, args.tool, overrides)

    results = []

    if args.command:
        settings_dir = Path.cwd()
        hook_entry = {"type": "command", "command": args.command, "args": []}
        exit_code, stdout, stderr, err = run_hook_command(hook_entry, input_data, settings_dir)
        if err:
            print(f"error: {err}", file=sys.stderr)
            return hc.EXIT_LINT_FAILED
        interpretation = interpret(args.event, exit_code, stdout, stderr)
        results.append({
            "command": args.command, "exit_code": exit_code,
            "stdout": stdout, "stderr": stderr, "interpretation": interpretation,
        })
    elif args.settings:
        settings_path = Path(args.settings)
        settings_dir = settings_path.resolve().parent.parent if settings_path.parent.name == ".claude" else Path.cwd()
        data, err = hc.load_json_lenient(settings_path)
        if err:
            print(f"error: {err}", file=sys.stderr)
            return hc.EXIT_USAGE_ERROR
        matched = find_matching_groups(data, args.event, args.tool or "Bash")
        if not matched:
            print(
                f"No hook groups in '{args.event}' match tool "
                f"'{args.tool or 'Bash'}' -- nothing ran, so nothing was verified. "
                "A matcher that matches no tool is a silent zero-match, not a "
                "clean result; check it with --matrix."
            )
            return hc.EXIT_LINT_FAILED
        for gi, group in matched:
            for hi, hook_entry in enumerate(group.get("hooks", [])):
                exit_code, stdout, stderr, err = run_hook_command(hook_entry, input_data, Path(args.settings).resolve().parent.parent)
                if err:
                    results.append({"group": gi, "hook": hi, "error": err})
                    continue
                interpretation = interpret(args.event, exit_code, stdout, stderr)
                results.append({
                    "group": gi, "hook": hi, "command": hook_entry.get("command"),
                    "exit_code": exit_code, "stdout": stdout, "stderr": stderr,
                    "interpretation": interpretation,
                })

    if args.json:
        print(json.dumps({"event": args.event, "input": input_data, "results": results,
                          "note": FINALITY_NOTE}, indent=2))
    else:
        print(f"Event: {args.event}  Tool: {args.tool or '(default: Bash)'}")
        print(f"Sample input: {json.dumps(input_data)}")
        for r in results:
            print("---")
            if "error" in r:
                print(f"  ERROR: {r['error']}")
                continue
            print(f"  command: {r.get('command', args.command)}")
            print(f"  exit code: {r['exit_code']}")
            if r["stdout"].strip():
                print(f"  stdout: {r['stdout'].strip()}")
            if r["stderr"].strip():
                print(f"  stderr: {r['stderr'].strip()}")
            for line in r["interpretation"]:
                print(f"  => {line}")

    return verdict(results, quiet=args.json)


if __name__ == "__main__":
    sys.exit(main())
