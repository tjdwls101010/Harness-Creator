#!/usr/bin/env python3
"""Deterministic lint for a generated Claude Code harness.

    python validate_harness.py --path <target-repo> [--json] [--strict]

This is the free, always-run first tier of validation (see
references/e2e-testing.md for the second, paid tier). harness-creator runs
this immediately after generating or editing any component and does not
declare the work done until it exits 0 -- a checklist that isn't
mechanically enforced is exactly the failure mode this script exists to
close (see docs/plan/00-overview.md's revfactory postmortem).

Exit codes: 0 = no errors (warnings still possible unless --strict),
1 = at least one error (or, under --strict, at least one warning),
2 = the script itself couldn't run (bad --path, bad arguments).
"""

import argparse
import json
import re
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_common as hc

MAX_CLAUDE_MD_LINES = 200
MAX_SKILL_BODY_LINES = 500
MAX_DESCRIPTION_CHARS = 1536

# Allow patterns that auto mode drops -- generating these is dead weight,
# not a correctness bug, so this is a warning, not an error.
_BROAD_ALLOW_RE = re.compile(
    r"^(Bash|PowerShell)\((\*|[a-zA-Z0-9_.\-]+\*)\)$|^Agent(\(.*\))?$"
)

_AT_IMPORT_RE = re.compile(r"(?<!`)@([\w./\-]+\.\w+)(?!`)")
_TRIGGER_PHRASE_RE = re.compile(
    r"\b(use|when|whenever|trigger|invoke)\b|할\s*때|사용", re.IGNORECASE
)
_BULLET_NAME_RE = re.compile(r"^\s*[-*]\s+`?([A-Za-z0-9_\-]+)`?\s*$")


def add(findings, level, location, message):
    findings.append((level, location, message))


def check_settings(root, findings):
    hook_events_seen = set()
    for settings_path in hc.settings_paths(root):
        rel = settings_path.relative_to(root)
        data, err = hc.load_json_lenient(settings_path)
        if err:
            add(findings, "E", str(rel), err)
            continue
        if not isinstance(data, dict):
            add(findings, "E", str(rel), "top level of settings.json must be an object")
            continue

        _check_hooks_block(root, rel, data.get("hooks", {}), findings)
        _check_permissions_block(rel, data.get("permissions", {}), findings)


def _check_hooks_block(root, rel, hooks, findings):
    if not hooks:
        return
    if not isinstance(hooks, dict):
        add(findings, "E", str(rel), "'hooks' must be an object keyed by event name")
        return

    per_tool_pretooluse_matchers = {}

    for event, groups in hooks.items():
        if event not in hc.HOOK_EVENTS:
            add(findings, "E", f"{rel}#hooks.{event}", f"unknown hook event '{event}'")
            continue
        if not isinstance(groups, list):
            add(findings, "E", f"{rel}#hooks.{event}", "event value must be a list of matcher groups")
            continue

        for gi, group in enumerate(groups):
            if not isinstance(group, dict):
                add(findings, "E", f"{rel}#hooks.{event}[{gi}]", "matcher group must be an object")
                continue

            matcher = group.get("matcher")
            if matcher is not None:
                if event in hc.NON_MATCHER_EVENTS:
                    add(
                        findings, "E", f"{rel}#hooks.{event}[{gi}]",
                        f"'{event}' does not support a 'matcher' field -- it fires "
                        "unconditionally, so this matcher is silently ignored",
                    )
                elif not hc.is_exact_matcher(matcher) and not re.match(r"^\^.*\$$", matcher):
                    add(
                        findings, "W", f"{rel}#hooks.{event}[{gi}]",
                        f"matcher '{matcher}' contains a character outside "
                        "[A-Za-z0-9_-,| ], which makes it an UNANCHORED regex "
                        "(e.g. it also matches substrings) -- anchor with ^...$ "
                        "if that's intended, otherwise this may match more than you want",
                    )

            hook_list = group.get("hooks")
            if not isinstance(hook_list, list) or not hook_list:
                add(findings, "E", f"{rel}#hooks.{event}[{gi}]", "'hooks' must be a non-empty list")
                continue

            for hi, hook in enumerate(hook_list):
                loc = f"{rel}#hooks.{event}[{gi}].hooks[{hi}]"
                if not isinstance(hook, dict):
                    add(findings, "E", loc, "hook entry must be an object")
                    continue
                htype = hook.get("type")
                if htype not in hc.HOOK_HANDLER_TYPES:
                    add(findings, "E", loc, f"unknown or missing handler type '{htype}'")
                    continue
                if htype == "command":
                    command = hook.get("command")
                    if not command:
                        add(findings, "E", loc, "command hook missing 'command' field")
                    elif "args" in hook or "/" in command:
                        # exec form (args present) always names a real executable
                        # path; shell form is only checked when it looks like a
                        # path too -- a bare command like "echo hi" isn't a
                        # script reference and shouldn't be flagged as one.
                        _check_command_script_exists(root, loc, command, findings)
                if "if" in hook and event not in hc.TOOL_CONTEXT_EVENTS:
                    add(
                        findings, "W", loc,
                        f"'if' field is set but '{event}' carries no tool_input to "
                        "filter on -- this condition can never match and the hook "
                        "always fires (or never does, depending on your 'if' logic's "
                        "default), silently",
                    )

            if event == "PreToolUse" and matcher:
                for tool in re.split(r"[|,]", matcher):
                    tool = tool.strip()
                    if not tool:
                        continue
                    prior = per_tool_pretooluse_matchers.setdefault(tool, [])
                    prior.append((gi, len(hook_list)))

    for tool, groups in per_tool_pretooluse_matchers.items():
        if len(groups) > 1:
            add(
                findings, "W", f"{rel}#hooks.PreToolUse",
                f"multiple PreToolUse hook groups match tool '{tool}' -- if more than "
                "one of them returns updatedInput, the last one to finish wins "
                "non-deterministically (see references/hooks.md); this can't be "
                "confirmed statically, so verify with test_hook.py if any of these "
                "hooks rewrites input",
            )


def _check_command_script_exists(root, loc, command, findings):
    resolved = command.replace("${CLAUDE_PROJECT_DIR}", str(root))
    if resolved.startswith("$") or "${" in resolved:
        return  # unresolved env var we don't know the value of -- skip, don't guess
    path = Path(resolved)
    if not path.is_absolute():
        path = root / path
    if not path.exists():
        add(findings, "E", loc, f"hook command references a script that does not exist: {command}")
        return
    if path.is_file() and not (path.stat().st_mode & stat.S_IXUSR):
        add(findings, "E", loc, f"hook script exists but is not executable: {path.relative_to(root)}")


def _check_permissions_block(rel, permissions, findings):
    if not permissions:
        return
    if not isinstance(permissions, dict):
        add(findings, "E", str(rel), "'permissions' must be an object")
        return
    for bucket in ("allow", "deny", "ask"):
        rules = permissions.get(bucket, [])
        if not isinstance(rules, list):
            add(findings, "E", f"{rel}#permissions.{bucket}", "must be a list of rule strings")
            continue
        for rule in rules:
            if not isinstance(rule, str):
                continue
            tool_name = re.split(r"[(\s]", rule, 1)[0]
            if tool_name and not hc.is_known_tool_token(tool_name):
                add(
                    findings, "E", f"{rel}#permissions.{bucket}",
                    f"'{rule}' references unknown tool '{tool_name}'",
                )
            if bucket == "allow" and _BROAD_ALLOW_RE.match(rule):
                add(
                    findings, "W", f"{rel}#permissions.allow",
                    f"'{rule}' is a broad allow rule that gets dropped when the "
                    "session enters auto mode -- it has no durable value; prefer "
                    "narrow rules (see references/hooks.md)",
                )


def check_skills(root, findings):
    total_description_chars = 0
    for skill_dir in hc.iter_skill_dirs(root):
        rel = skill_dir.relative_to(root)
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            add(findings, "E", str(rel), "skill directory has no SKILL.md")
            continue

        text = hc.read_text(skill_md)
        fm = hc.parse_frontmatter(text)
        loc = str(skill_md.relative_to(root))
        if not fm.ok:
            add(
                findings, "E", loc,
                "frontmatter did not parse (" + "; ".join(fm.warnings) + ") -- "
                "the skill body still loads, but auto-triggering is silently dead",
            )
        else:
            description = fm.data.get("description") or ""
            when_to_use = fm.data.get("when_to_use") or ""
            combined = description + when_to_use
            if not description:
                add(findings, "W", loc, "no 'description' -- this skill can never auto-trigger")
            elif len(combined) > MAX_DESCRIPTION_CHARS:
                add(
                    findings, "W", loc,
                    f"description+when_to_use is {len(combined)} chars, truncated at "
                    f"{MAX_DESCRIPTION_CHARS} in the skill listing -- put the "
                    "triggering-critical clause first",
                )
            total_description_chars += len(combined)

        body_lines = fm.body.splitlines() if fm.ok else text.splitlines()
        if len(body_lines) > MAX_SKILL_BODY_LINES:
            add(findings, "W", loc, f"SKILL.md body is {len(body_lines)} lines, over the {MAX_SKILL_BODY_LINES}-line guideline")

        _check_dead_links(skill_dir, loc, text, findings)

    if total_description_chars > 0:
        # ~1% of a 200k-token window in characters, as a rough budget signal
        # (references/skills.md) -- an estimate, so this is always a W.
        estimated_budget_chars = 200_000 * 4 * 0.01
        if total_description_chars > estimated_budget_chars:
            add(
                findings, "W", ".claude/skills/",
                f"combined skill description+when_to_use is ~{total_description_chars} "
                f"chars, over the rough ~1%-of-context-window budget estimate -- "
                "consider consolidating skills (see references/skills.md)",
            )


def _check_dead_links(skill_dir, loc, text, findings):
    for m in re.finditer(r"`references/([\w.\-]+)`|`scripts/([\w.\-]+)`", text):
        rel_name = m.group(1) or m.group(2)
        subdir = "references" if m.group(1) else "scripts"
        target = skill_dir / subdir / rel_name
        if not target.exists():
            add(findings, "E", loc, f"references a {subdir} file that does not exist: {subdir}/{rel_name}")


def check_agents(root, findings):
    seen_names = {}
    for agent_file in hc.iter_agent_files(root):
        loc = str(agent_file.relative_to(root))
        text = hc.read_text(agent_file)
        fm = hc.parse_frontmatter(text)
        if not fm.ok:
            add(findings, "E", loc, "frontmatter did not parse (" + "; ".join(fm.warnings) + ")")
            continue
        name = fm.data.get("name")
        description = fm.data.get("description")
        if not name:
            add(findings, "E", loc, "missing required 'name' field")
        else:
            if name in seen_names:
                add(
                    findings, "E", loc,
                    f"duplicate agent name '{name}' (also declared in {seen_names[name]}) "
                    "-- only one silently loads",
                )
            else:
                seen_names[name] = loc
        if not description:
            add(findings, "E", loc, "missing required 'description' field")

        model = fm.data.get("model")
        if model and model not in ("inherit", "sonnet", "opus", "haiku",
                                    "claude-sonnet-5", "claude-opus-4-8",
                                    "claude-haiku-4-5-20251001", "claude-fable-5"):
            add(findings, "W", loc, f"unrecognized 'model' value '{model}' -- verify this is a real model id/alias")

        tools = fm.data.get("tools")
        if isinstance(tools, list):
            for t in tools:
                if not hc.is_known_tool_token(t):
                    add(findings, "E", loc, f"'tools' references unknown tool '{t}'")
        elif isinstance(tools, str):
            for t in tools.split(","):
                t = t.strip()
                if t and not hc.is_known_tool_token(t):
                    add(findings, "E", loc, f"'tools' references unknown tool '{t}'")


def check_workflows(root, findings):
    for wf_file in hc.iter_workflow_files(root):
        loc = str(wf_file.relative_to(root))
        text = hc.read_text(wf_file)

        if not re.search(r"export\s+const\s+meta\s*=\s*\{", text):
            add(findings, "E", loc, "missing 'export const meta = {...}' literal")
        else:
            meta_match = re.search(r"export\s+const\s+meta\s*=\s*\{(.*?)\n\}", text, re.DOTALL)
            if meta_match and not re.search(r"\bname\s*:", meta_match.group(1)):
                add(findings, "E", loc, "'meta' object is missing a 'name' field")

        for label, bad_call in (
            ("Date.now()", r"Date\.now\s*\("),
            ("Math.random()", r"Math\.random\s*\("),
            ("argless new Date()", r"new\s+Date\s*\(\s*\)"),
        ):
            if re.search(bad_call, text):
                add(
                    findings, "E", loc,
                    f"calls {label} -- workflow validation rejects this "
                    "(breaks resume determinism); pass timestamps via args instead",
                )

        node = _node_available()
        if node:
            _check_workflow_syntax(loc, wf_file, findings)
        else:
            add(findings, "W", loc, "node not available -- skipped ESM syntax check")


_NODE_CHECKED = None


def _node_available():
    global _NODE_CHECKED
    if _NODE_CHECKED is None:
        import shutil
        _NODE_CHECKED = shutil.which("node") is not None
    return _NODE_CHECKED


def _check_workflow_syntax(loc, wf_file, findings):
    import subprocess
    # Plain `node --check` false-fails on ESM `export` syntax when the
    # target project's package.json declares "type": "commonjs" -- force
    # ESM parsing explicitly instead (docs/plan/06-milestones.md fix).
    try:
        result = subprocess.run(
            ["node", "--input-type=module", "--check"],
            input=hc.read_text(wf_file),
            capture_output=True, text=True, timeout=10,
        )
    except Exception as e:
        add(findings, "W", loc, f"could not run node syntax check: {e}")
        return
    if result.returncode != 0:
        add(findings, "E", loc, f"JavaScript syntax error: {result.stderr.strip()[:300]}")


def check_rules(root, findings):
    for rule_file in hc.iter_rule_files(root):
        loc = str(rule_file.relative_to(root))
        text = hc.read_text(rule_file)
        fm = hc.parse_frontmatter(text)
        # A rule with no frontmatter at all has no 'paths' just as surely as
        # one with frontmatter but no 'paths' key -- both loads at launch,
        # so both get the same warning below. Only the glob-syntax check
        # needs parsed data to run at all.
        paths = fm.data.get("paths") if fm.ok else None
        if paths is None:
            add(
                findings, "W", loc,
                "no 'paths:' frontmatter -- this rule loads at launch just like "
                "CLAUDE.md, same as if it weren't split out at all",
            )
        elif isinstance(paths, list):
            for p in paths:
                _check_glob_syntax(loc, p, findings)
        elif isinstance(paths, str):
            _check_glob_syntax(loc, paths, findings)


def _check_glob_syntax(loc, pattern, findings):
    depth = 0
    for ch in pattern:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                add(findings, "E", loc, f"paths glob '{pattern}' has an unmatched '}}'")
                return
    if depth != 0:
        add(findings, "E", loc, f"paths glob '{pattern}' has an unmatched '{{'")


def check_claude_md(root, findings):
    claude_md = root / "CLAUDE.md"
    if not claude_md.is_file():
        return
    loc = "CLAUDE.md"
    text = hc.read_text(claude_md)
    lines = text.splitlines()
    if len(lines) > MAX_CLAUDE_MD_LINES:
        add(
            findings, "W", loc,
            f"{len(lines)} lines, over the {MAX_CLAUDE_MD_LINES}-line guideline -- "
            "compliance tends to drop as length grows (exception: a monorepo that "
            "still overflows after splitting into rules/)",
        )

    for m in re.finditer(_AT_IMPORT_RE, text):
        target = root / m.group(1)
        if not target.exists():
            add(findings, "E", loc, f"@{m.group(1)} import target does not exist")

    known_names = {d.name for d in hc.iter_skill_dirs(root)} | {
        f.stem for f in hc.iter_agent_files(root)
    }
    _check_inventory_listing(loc, lines, known_names, findings)


def _check_inventory_listing(loc, lines, known_names, findings):
    if not known_names:
        return
    run = []
    for line in lines + [""]:
        m = _BULLET_NAME_RE.match(line)
        if m and m.group(1) in known_names and not _TRIGGER_PHRASE_RE.search(line):
            run.append(m.group(1))
        else:
            if len(run) >= 3:
                add(
                    findings, "W", loc,
                    f"bullet list of bare component names ({', '.join(run)}) looks like "
                    "a component inventory -- the filesystem is the source of truth for "
                    "what exists; point to harness-spec.md instead of enumerating "
                    "(lines with trigger phrasing like '... use X when Y' are exempt)",
                )
            run = []


def check_harness_spec(root, findings):
    spec = root / ".claude" / "harness-spec.md"
    has_any_component = (
        list(hc.iter_skill_dirs(root)) or list(hc.iter_agent_files(root))
        or list(hc.iter_workflow_files(root)) or list(hc.iter_rule_files(root))
        or hc.settings_paths(root)
    )
    if not spec.is_file():
        if has_any_component:
            add(findings, "W", ".claude/harness-spec.md", "missing -- a generated harness should carry a spec as its source of truth")
        return

    text = hc.read_text(spec)
    referenced = set(re.findall(r"`([\w./\-]+)`", text))
    actual = set()
    for d in hc.iter_skill_dirs(root):
        actual.add(f".claude/skills/{d.name}/")
    for f in hc.iter_agent_files(root):
        actual.add(f".claude/agents/{f.name}")
    for f in hc.iter_workflow_files(root):
        actual.add(f".claude/workflows/{f.name}")

    missing_from_spec = [a for a in sorted(actual) if not any(a.rstrip("/") in r for r in referenced)]
    for m in missing_from_spec:
        add(findings, "W", ".claude/harness-spec.md", f"component exists on disk but isn't mentioned in the spec: {m}")


def run(root, strict):
    findings = []
    check_settings(root, findings)
    check_skills(root, findings)
    check_agents(root, findings)
    check_workflows(root, findings)
    check_rules(root, findings)
    check_claude_md(root, findings)
    check_harness_spec(root, findings)

    has_error = any(level == "E" for level, _, _ in findings)
    has_warning = any(level == "W" for level, _, _ in findings)
    exit_code = hc.EXIT_LINT_FAILED if (has_error or (strict and has_warning)) else hc.EXIT_OK
    return findings, exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", required=True, help="path to the target repo root")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures (exit 1); for CI")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: --path '{args.path}' is not a directory", file=sys.stderr)
        return hc.EXIT_USAGE_ERROR

    findings, exit_code = run(root, args.strict)

    if args.json:
        errors = sum(1 for level, _, _ in findings if level == "E")
        warnings = sum(1 for level, _, _ in findings if level == "W")
        print(json.dumps({
            "errors": errors, "warnings": warnings,
            "findings": hc.findings_to_json(findings),
        }, indent=2))
    else:
        errors = [f for f in findings if f[0] == "E"]
        warnings = [f for f in findings if f[0] == "W"]
        hc.print_findings_text(errors, "Errors")
        hc.print_findings_text(warnings, "Warnings")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")
        if exit_code == hc.EXIT_OK:
            print("PASS" + (" (strict: warnings would fail)" if warnings and not args.strict else ""))
        else:
            print("FAIL")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
