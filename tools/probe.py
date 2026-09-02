#!/usr/bin/env python3
"""Measure what the model already knows, before a reference paragraph is cut.

    probe.py quiz --questions <jsonl> --out <dir> [--runs 3] [--model M]
    probe.py contrast --task <file> --reference <file> --out <dir> [--runs 1] [--model M]

Every run is `claude --bare -p --tools ""` in a freshly created, empty
temporary directory: no CLAUDE.md, skills, hooks, plugins, MCP servers or
auto memory are discovered, and no tools are available, so the only thing
the model can answer from is itself. The argv, the cwd and its listing at
launch, the claude version, and the model the envelope reports are written
into every result file -- those recorded facts are the isolation evidence,
not the transcript.

`quiz` asks each question `--runs` times and writes one JSON per run under
`<out>/<question id>/`, plus `summary.json` with every answer beside its
answer key. The answer key is never sent to the model. Grading is done by a
person against the frozen key; this prints nothing about correctness.

`contrast` runs the same task twice, `--runs` times each: once with the
prompt alone (`without/`), once with the reference file inlined ahead of it
(`with/`). Both arms are the same isolated shape. Compare the two arms'
outputs by hand; a gotcha the model gets right in both arms is a candidate
for deletion, one it gets right only with the reference is not.

Each run spends real tokens. Python 3.10+, stdlib only.
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

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2

QUIZ_SUFFIX = (
    "\n\nAnswer from your own knowledge of Claude Code. Be specific and brief: "
    "at most four sentences. If you are not sure, say what you are unsure about."
)


def claude_version():
    try:
        out = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=30)
        return (out.stdout or out.stderr).strip() or None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def build_command(prompt, model):
    cmd = ["claude", "--bare", "-p", prompt, "--tools", "", "--output-format", "json"]
    if model:
        cmd.extend(["--model", model])
    return cmd


def run_isolated(prompt, model, timeout):
    """One headless call in an empty temp cwd. Returns the record dict."""
    cwd = Path(tempfile.mkdtemp(prefix="probe-cwd-"))
    cwd_listing = sorted(os.listdir(cwd))
    cmd = build_command(prompt, model)
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    record = {
        "argv": cmd,
        "cwd": str(cwd),
        "cwd_listing_at_launch": cwd_listing,
        "claude_version": claude_version(),
        "prompt": prompt,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
        record["exit_code"] = proc.returncode
        record["stderr"] = proc.stderr[-2000:]
        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError:
            envelope = None
            record["stdout"] = proc.stdout[-4000:]
        record["envelope"] = envelope
        record["result"] = envelope.get("result") if isinstance(envelope, dict) else None
        usage = envelope.get("modelUsage") if isinstance(envelope, dict) else None
        record["model"] = sorted(usage) if isinstance(usage, dict) else None
        record["error"] = None
    except subprocess.TimeoutExpired:
        record.update({"exit_code": None, "envelope": None, "result": None, "model": None,
                       "error": f"timed out after {timeout}s"})
    except FileNotFoundError:
        record.update({"exit_code": None, "envelope": None, "result": None, "model": None,
                       "error": "the 'claude' executable was not found on PATH"})
    finally:
        record["duration_s"] = round(time.monotonic() - t0, 1)
        shutil.rmtree(cwd, ignore_errors=True)
    return record


def load_questions(path):
    questions = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        q = json.loads(line)
        for key in ("id", "question", "answer_key"):
            if key not in q:
                raise ValueError(f"line {n}: question is missing '{key}'")
        questions.append(q)
    return questions


def cmd_quiz(args):
    try:
        questions = load_questions(args.questions)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    if args.only:
        wanted = set(args.only)
        questions = [q for q in questions if q["id"] in wanted]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {"runs": args.runs, "model_requested": args.model, "questions": []}
    failures = 0
    for q in questions:
        qdir = out / q["id"]
        qdir.mkdir(parents=True, exist_ok=True)
        answers = []
        for i in range(1, args.runs + 1):
            rec = run_isolated(q["question"] + QUIZ_SUFFIX, args.model, args.timeout)
            rec["question_id"] = q["id"]
            rec["source"] = q.get("source")
            (qdir / f"run-{i}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
            answers.append(rec["result"])
            if rec["error"] or rec["result"] is None:
                failures += 1
            status = "ERROR " + rec["error"] if rec["error"] else f"{rec['duration_s']}s"
            print(f"{q['id']} run {i}: {status}", file=sys.stderr)
        summary["questions"].append({
            "id": q["id"], "source": q.get("source"), "question": q["question"],
            "answer_key": q["answer_key"], "answers": answers,
        })
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(out / "summary.json"))
    return EXIT_FAILED if failures else EXIT_OK


def cmd_contrast(args):
    task = Path(args.task)
    reference = Path(args.reference)
    for p in (task, reference):
        if not p.is_file():
            print(f"error: {p} is not a file", file=sys.stderr)
            return EXIT_USAGE
    task_text = task.read_text(encoding="utf-8")
    ref_text = reference.read_text(encoding="utf-8")
    with_prompt = (
        "Read this reference first, then do the task below it.\n\n"
        f"<reference>\n{ref_text}\n</reference>\n\n{task_text}"
    )
    out = Path(args.out)
    failures = 0
    summary = {"runs": args.runs, "model_requested": args.model, "task": str(task),
               "reference": str(reference), "arms": {}}
    for arm, prompt in (("without", task_text), ("with", with_prompt)):
        arm_dir = out / arm
        arm_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for i in range(1, args.runs + 1):
            rec = run_isolated(prompt, args.model, args.timeout)
            rec["arm"] = arm
            (arm_dir / f"run-{i}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
            results.append(rec["result"])
            if rec["error"] or rec["result"] is None:
                failures += 1
            status = "ERROR " + rec["error"] if rec["error"] else f"{rec['duration_s']}s"
            print(f"{arm} run {i}: {status}", file=sys.stderr)
        summary["arms"][arm] = results
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(out / "summary.json"))
    return EXIT_FAILED if failures else EXIT_OK


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False, description="options shared by quiz and contrast")
    common.add_argument("--out", required=True, help="directory for per-run JSON files and summary.json")
    common.add_argument("--model", help="model id/alias passed to `claude --model`; omitted, the spawned claude picks its own default")
    common.add_argument("--timeout", type=int, default=180, help="seconds per run before it is recorded as timed out (default 180)")

    p_quiz = sub.add_parser("quiz", parents=[common], help="ask each question in isolation, N times, and record the answers beside their keys")
    p_quiz.add_argument("--questions", required=True, help="JSONL file; each line has id, question, answer_key, and optionally source")
    p_quiz.add_argument("--runs", type=int, default=3, help="answers to collect per question (default 3)")
    p_quiz.add_argument("--only", nargs="*", help="question ids to run; others in the file are skipped")
    p_quiz.set_defaults(func=cmd_quiz)

    p_contrast = sub.add_parser("contrast", parents=[common], help="run one task with and without a reference inlined, N times each")
    p_contrast.add_argument("--task", required=True, help="file holding the task prompt")
    p_contrast.add_argument("--reference", required=True, help="reference file inlined ahead of the task in the `with` arm")
    p_contrast.add_argument("--runs", type=int, default=1, help="runs per arm (default 1)")
    p_contrast.set_defaults(func=cmd_contrast)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
