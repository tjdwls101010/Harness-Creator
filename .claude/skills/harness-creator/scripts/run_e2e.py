#!/usr/bin/env python3
"""Spawn a headless Claude Code session against a project and record what happened.

    python run_e2e.py --project <target-repo> --prompt "..." [--prompt-file f]
        [--model <id>] [--timeout 300] [--out <dir>] [--json]
        [--permission-mode acceptEdits] [--isolate]

This is the second, paid tier of validation (see references/e2e-testing.md);
run it only with the user's consent, per the Validation-stage interview
item. It does not grade anything itself -- it produces transcript.jsonl and
summary.json in --out, and a separate grading agent (or workflow phase)
reads those to judge trigger/behavior/artifact correctness against the
spec's expected scenario.

IMPORTANT -- read this before trusting this script's permission handling:
headless (`-p`) permission handling was NOT empirically verified when this
script was built (see references/e2e-testing.md's "Headless permission
handling" section) -- the sandbox that built it could not authenticate a
spawned `claude` process at all. `--isolate` + `--dangerously-skip-permissions`
is the documented best guess, not a confirmed-safe default. Treat your
first real invocation of this script as the actual verification, and only
ever pass `--isolate` when running anything other than a purely read-only
prompt.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_common as hc

IGNORE_PATTERNS = shutil.ignore_patterns(
    ".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache", "dist", "build"
)


def isolate_project(project_root):
    tmp_dir = Path(tempfile.mkdtemp(prefix="harness-e2e-"))
    dest = tmp_dir / project_root.name
    shutil.copytree(project_root, dest, ignore=IGNORE_PATTERNS)
    return dest


def build_command(prompt, model, permission_mode, skip_permissions):
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
    ]
    if model:
        cmd.extend(["--model", model])
    if skip_permissions:
        cmd.append("--dangerously-skip-permissions")
    elif permission_mode:
        cmd.extend(["--permission-mode", permission_mode])
    return cmd


def run_session(project_dir, prompt, model, permission_mode, skip_permissions, timeout):
    """Runs `claude -p` and returns (raw_lines, error). error is None on a
    clean process exit (which says nothing about whether the SESSION
    succeeded -- that's for the caller to determine from summarize())."""
    cmd = build_command(prompt, model, permission_mode, skip_permissions)
    # CLAUDECODE removal allows nesting claude -p inside this session --
    # verified technique, carried over from skill-creator's run_eval.py.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(
            cmd, cwd=project_dir, env=env,
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        partial = (e.stdout or b"").decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return partial.splitlines(), f"timed out after {timeout}s"
    except FileNotFoundError:
        return [], "the 'claude' executable was not found on PATH"

    lines = result.stdout.splitlines()
    if result.returncode != 0 and not lines:
        return [], f"claude exited {result.returncode} with no stdout; stderr: {result.stderr.strip()[:500]}"
    return lines, None


def parse_stream(lines):
    """Parse stream-json lines into a structured summary. Schema verified
    against a live `claude -p --output-format json` result envelope
    (type/subtype/result/usage/session_id/etc. fields) and against
    skill-creator's run_eval.py for the assistant/tool_use message shape --
    both are the same underlying Claude API message stream, just
    line-delimited here instead of a single final object."""
    tool_calls = []
    skill_invocations = []
    hook_evidence = []
    final_result = None

    for raw_line in lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        etype = event.get("type")

        if etype == "assistant":
            message = event.get("message", {})
            for item in message.get("content", []):
                if item.get("type") != "tool_use":
                    continue
                name = item.get("name", "")
                tool_input = item.get("input", {})
                tool_calls.append({"name": name, "input": tool_input})
                if name == "Skill":
                    skill_invocations.append(tool_input.get("skill") or tool_input.get("name") or str(tool_input))

        elif etype == "user":
            # Tool results surface here. Hook block/deny messages typically
            # show up as text inside a tool_result's content -- this is a
            # best-effort heuristic, not a guaranteed distinct event type
            # (no primary source documents a dedicated stream-json event
            # for "a hook fired"), so treat hook_evidence as suggestive,
            # not authoritative; confirm with test_hook.py or by inspecting
            # the isolated project's files for the hook's side effects.
            message = event.get("message", {})
            for item in message.get("content", []):
                if item.get("type") != "tool_result":
                    continue
                content = item.get("content", "")
                text = content if isinstance(content, str) else json.dumps(content)
                if any(marker in text.lower() for marker in ("hook", "blocked", "denied")):
                    hook_evidence.append(text[:500])

        elif etype == "result":
            final_result = event

    return {
        "tool_calls": tool_calls,
        "skill_invocations": skill_invocations,
        "hook_evidence": hook_evidence,
        "final_result": final_result,
    }


def write_outputs(out_dir, lines, summary):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "transcript.jsonl").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", required=True, help="path to the target project")
    parser.add_argument("--prompt", help="the prompt to send")
    parser.add_argument("--prompt-file", help="path to a file containing the prompt")
    parser.add_argument("--model", help="model id/alias to use (default: whatever the invoking session uses)")
    parser.add_argument("--timeout", type=int, default=300, help="seconds before giving up (default 300)")
    parser.add_argument("--out", default=None, help="directory to write transcript.jsonl and summary.json (default: a temp dir, path printed)")
    parser.add_argument("--json", action="store_true", help="print the summary as JSON to stdout too")
    parser.add_argument("--permission-mode", help="passed through to `claude -p --permission-mode`")
    parser.add_argument("--isolate", action="store_true", help="copy --project to a temp dir first and run there, so writes don't touch the original; implies --dangerously-skip-permissions unless --permission-mode is also given")
    args = parser.parse_args()

    if not args.prompt and not args.prompt_file:
        print("error: one of --prompt or --prompt-file is required", file=sys.stderr)
        return hc.EXIT_USAGE_ERROR
    prompt = args.prompt or Path(args.prompt_file).read_text(encoding="utf-8")

    project_root = Path(args.project).resolve()
    if not project_root.is_dir():
        print(f"error: --project '{args.project}' is not a directory", file=sys.stderr)
        return hc.EXIT_USAGE_ERROR

    run_dir = project_root
    isolated_tmp_parent = None
    if args.isolate:
        run_dir = isolate_project(project_root)
        isolated_tmp_parent = run_dir.parent

    skip_permissions = args.isolate and not args.permission_mode

    try:
        lines, err = run_session(
            run_dir, prompt, args.model, args.permission_mode, skip_permissions, args.timeout,
        )
    finally:
        pass  # isolated copy is left on disk deliberately for post-hoc inspection; caller/OS temp cleanup handles it

    summary = parse_stream(lines)
    summary["error"] = err
    summary["project"] = str(project_root)
    summary["isolated_copy"] = str(run_dir) if args.isolate else None
    summary["prompt"] = prompt

    out_dir = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="harness-e2e-out-"))
    write_outputs(out_dir, lines, summary)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Output written to: {out_dir}")
        if err:
            print(f"NOTE: {err}")
        fr = summary["final_result"]
        if fr:
            print(f"is_error: {fr.get('is_error')}  num_turns: {fr.get('num_turns')}  cost: ${fr.get('total_cost_usd', 0)}")
            print(f"result: {str(fr.get('result', ''))[:300]}")
        print(f"tool calls: {len(summary['tool_calls'])}, skill invocations: {summary['skill_invocations']}")
        if summary["hook_evidence"]:
            print(f"possible hook evidence ({len(summary['hook_evidence'])} match(es)) -- verify with test_hook.py, this is heuristic")

    return hc.EXIT_OK if not err else hc.EXIT_LINT_FAILED


if __name__ == "__main__":
    sys.exit(main())
