#!/usr/bin/env python3
"""Measure what the model already knows, before a reference paragraph is cut.

    probe.py quiz --questions <jsonl> --out <dir> [--runs 3] [--model M] [--isolation bare|safe-mode]
    probe.py contrast --task <file> --reference <file> --out <dir> [--runs 1] [--model M] [--isolation ...]

Every run is `claude -p --tools "" --output-format json` in a freshly
created, empty temporary directory, under one of two isolation flags:
`--bare` (default) skips discovery of hooks, skills, plugins, MCP servers,
auto memory and CLAUDE.md, and also skips OAuth, so it needs
ANTHROPIC_API_KEY; `--safe-mode` disables the same customizations while
keeping normal authentication. Either way no tools are available, so the
only thing the model can answer from is itself. The argv, the cwd and its
listing at launch, the claude version, the models the envelope reports and
the cost are written into every result file -- those recorded facts are the
isolation evidence, not the transcript. A run whose envelope reports an
error (an auth failure, say) is recorded as an error and fails the exit code.

`quiz` asks each question `--runs` times and writes one JSON per run under
`<out>/<question id>/`, plus `summary.json` pairing every answer, with its
provenance, beside its answer key. The answer key is never sent to the
model, and nothing here grades: correctness is judged by whoever reads
`summary.json`.

`contrast` runs one task under two arms, `--runs` times each, alternating
arm by arm: the same prompt wrapper both times, with the reference file's
text in the `<reference>` slot for `with/` and that slot empty for
`without/`. `summary.json` records both arms and flags any model or CLI
version drift between runs.

`--out` must not already contain files. Question ids are slugs
(`[A-Za-z0-9._-]+`) and must be unique. Python 3.10+, stdlib only.
"""

import argparse
import json
import os
import re
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


ISOLATION_FLAGS = {"bare": "--bare", "safe-mode": "--safe-mode"}

# Environment variables that can change which model answers or how, recorded
# (values included) when set. Anything whose name suggests a credential is
# recorded by name only.
_ENV_PREFIXES = ("ANTHROPIC_", "CLAUDE_CODE_", "CLAUDE_")
_SECRET_RE = re.compile(r"KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL", re.IGNORECASE)


def _probe_env():
    return {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}


def _recorded_env(env):
    out = {}
    for k, v in sorted(env.items()):
        if k.startswith(_ENV_PREFIXES):
            out[k] = "<set, not recorded>" if _SECRET_RE.search(k) else v
    return out


class Claude:
    """One resolved executable, one environment, for every run in a session."""

    def __init__(self, env=None):
        self.env = env if env is not None else _probe_env()
        self.path = shutil.which("claude", path=self.env.get("PATH"))
        self.version = self._version()

    def _version(self):
        if not self.path:
            return None
        try:
            out = subprocess.run([self.path, "--version"], capture_output=True, text=True,
                                 timeout=30, env=self.env, stdin=subprocess.DEVNULL)
            return (out.stdout or out.stderr).strip() or None
        except (OSError, subprocess.TimeoutExpired):
            return None


def build_command(prompt, model, isolation="bare", executable="claude"):
    cmd = [executable, ISOLATION_FLAGS[isolation], "-p", prompt, "--tools", "", "--output-format", "json"]
    if model:
        cmd.extend(["--model", model])
    return cmd


def run_isolated(prompt, model, timeout, isolation="bare", claude=None):
    """One headless call in an empty temp cwd. Returns the record dict."""
    claude = claude or Claude()
    cwd = Path(tempfile.mkdtemp(prefix="probe-cwd-"))
    cmd = build_command(prompt, model, isolation, claude.path or "claude")
    record = {
        "argv": cmd,
        "isolation": isolation,
        "cwd": str(cwd),
        "cwd_listing_at_launch": None,
        "stdin": "devnull",
        "env_recorded": _recorded_env(claude.env),
        "claude_version": claude.version,
        "prompt": prompt,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    t0 = time.monotonic()
    try:
        record["cwd_listing_at_launch"] = sorted(os.listdir(cwd))
        proc = subprocess.run(cmd, cwd=cwd, env=claude.env, capture_output=True, text=True,
                              timeout=timeout, stdin=subprocess.DEVNULL)
        record["exit_code"] = proc.returncode
        record["stderr"] = proc.stderr[-2000:]
        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError:
            envelope = None
            record["stdout"] = proc.stdout[-4000:]
        record["envelope"] = envelope
        ok = isinstance(envelope, dict)
        record["result"] = envelope.get("result") if ok else None
        usage = envelope.get("modelUsage") if ok else None
        record["model"] = sorted(usage) if isinstance(usage, dict) else None
        record["total_cost_usd"] = envelope.get("total_cost_usd") if ok else None
        if not ok:
            record["error"] = f"claude exited {proc.returncode} without a JSON envelope"
        elif envelope.get("is_error") or proc.returncode != 0:
            record["error"] = f"claude reported an error (exit {proc.returncode}): {str(record['result'])[:200]}"
        else:
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


_SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def load_questions(path):
    questions = []
    seen = set()
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        q = json.loads(line)
        for key in ("id", "question", "answer_key"):
            if not isinstance(q.get(key), str) or not q[key]:
                raise ValueError(f"line {n}: question is missing '{key}'")
        if not _SLUG_RE.match(q["id"]) or q["id"] in (".", ".."):
            raise ValueError(f"line {n}: id {q['id']!r} is not a slug ([A-Za-z0-9._-]+)")
        if q["id"] in seen:
            raise ValueError(f"line {n}: duplicate id {q['id']!r}")
        seen.add(q["id"])
        questions.append(q)
    return questions


def _fresh_out_dir(path):
    out = Path(path)
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"--out {out} already has files; use a new directory per run")
    out.mkdir(parents=True, exist_ok=True)
    return out


def _positive(name, value):
    if value < 1:
        raise ValueError(f"{name} must be a positive integer, got {value}")


def _provenance(rec, path):
    return {
        "answer": rec["result"], "model": rec["model"], "claude_version": rec["claude_version"],
        "exit_code": rec["exit_code"], "error": rec["error"], "file": str(path),
    }


def _drift(records):
    """Which (model, version) pairs the runs reported; more than one is drift."""
    seen = sorted({(json.dumps(r["model"]), r["claude_version"] or "") for r in records})
    return {"distinct_model_version_pairs": len(seen), "pairs": seen, "drift_detected": len(seen) > 1}


def cmd_quiz(args):
    try:
        _positive("--runs", args.runs)
        _positive("--timeout", args.timeout)
        questions = load_questions(args.questions)
        if args.only:
            unknown = sorted(set(args.only) - {q["id"] for q in questions})
            if unknown:
                raise ValueError(f"--only names ids not in the file: {', '.join(unknown)}")
            questions = [q for q in questions if q["id"] in set(args.only)]
        out = _fresh_out_dir(args.out)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    claude = Claude()
    summary = {"runs": args.runs, "model_requested": args.model, "isolation": args.isolation,
               "claude_executable": claude.path, "questions": []}
    failures = 0
    all_records = []
    for q in questions:
        qdir = out / q["id"]
        qdir.mkdir(parents=True, exist_ok=True)
        answers = []
        for i in range(1, args.runs + 1):
            rec = run_isolated(q["question"] + QUIZ_SUFFIX, args.model, args.timeout, args.isolation, claude)
            rec["question_id"] = q["id"]
            rec["source"] = q.get("source")
            path = qdir / f"run-{i}.json"
            path.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
            answers.append(_provenance(rec, path))
            all_records.append(rec)
            if rec["error"] or rec["result"] is None:
                failures += 1
            status = "ERROR " + rec["error"] if rec["error"] else f"{rec['duration_s']}s"
            print(f"{q['id']} run {i}: {status}", file=sys.stderr)
        summary["questions"].append({
            "id": q["id"], "source": q.get("source"), "question": q["question"],
            "answer_key": q["answer_key"], "answers": answers,
        })
    summary["provenance"] = _drift(all_records)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(out / "summary.json"))
    return EXIT_FAILED if failures else EXIT_OK


CONTRAST_TEMPLATE = (
    "If the reference block below is not empty, read it first; then do the task.\n\n"
    "<reference>\n{reference}\n</reference>\n\n<task>\n{task}\n</task>"
)


def contrast_prompt(task_text, reference_text):
    return CONTRAST_TEMPLATE.format(reference=reference_text.strip(), task=task_text.strip())


def cmd_contrast(args):
    task = Path(args.task)
    reference = Path(args.reference)
    try:
        _positive("--runs", args.runs)
        _positive("--timeout", args.timeout)
        for p in (task, reference):
            if not p.is_file():
                raise ValueError(f"{p} is not a file")
        out = _fresh_out_dir(args.out)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    task_text = task.read_text(encoding="utf-8")
    ref_text = reference.read_text(encoding="utf-8")
    prompts = {"without": contrast_prompt(task_text, ""), "with": contrast_prompt(task_text, ref_text)}
    claude = Claude()
    failures = 0
    summary = {"runs": args.runs, "model_requested": args.model, "isolation": args.isolation,
               "claude_executable": claude.path, "task": str(task), "reference": str(reference),
               "arms": {"without": [], "with": []}}
    all_records = []
    for arm in ("without", "with"):
        (out / arm).mkdir(parents=True, exist_ok=True)
    for i in range(1, args.runs + 1):
        for arm in ("without", "with"):
            rec = run_isolated(prompts[arm], args.model, args.timeout, args.isolation, claude)
            rec["arm"] = arm
            path = out / arm / f"run-{i}.json"
            path.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
            summary["arms"][arm].append(_provenance(rec, path))
            all_records.append(rec)
            if rec["error"] or rec["result"] is None:
                failures += 1
            status = "ERROR " + rec["error"] if rec["error"] else f"{rec['duration_s']}s"
            print(f"{arm} run {i}: {status}", file=sys.stderr)
    summary["provenance"] = _drift(all_records)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(out / "summary.json"))
    return EXIT_FAILED if failures else EXIT_OK


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False, description="options shared by quiz and contrast")
    common.add_argument("--out", required=True, help="directory for per-run JSON files and summary.json; must be new or empty")
    common.add_argument("--model", help="model id/alias passed to `claude --model`; omitted, the spawned claude picks its own default")
    common.add_argument("--timeout", type=int, default=180, help="seconds per run before it is recorded as timed out (default 180)")
    common.add_argument("--isolation", choices=sorted(ISOLATION_FLAGS), default="bare",
                        help="which claude flag isolates the run: bare skips discovery and OAuth (needs ANTHROPIC_API_KEY); safe-mode disables the same customizations and keeps normal auth (default bare)")

    p_quiz = sub.add_parser("quiz", parents=[common], help="ask each question in isolation, N times, and record the answers beside their keys")
    p_quiz.add_argument("--questions", required=True, help="JSONL file; each line has id, question, answer_key, and optionally source")
    p_quiz.add_argument("--runs", type=int, default=3, help="answers to collect per question (default 3)")
    p_quiz.add_argument("--only", nargs="+", metavar="ID", help="question ids to run; others in the file are skipped; an id not in the file is an error")
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
