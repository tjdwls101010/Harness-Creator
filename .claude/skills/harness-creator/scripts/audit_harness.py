#!/usr/bin/env python3
"""Phase-0 inventory of an existing (or nonexistent) harness, for re-entry.

    python audit_harness.py --path <target-repo> [--json]

harness-creator runs this before ANY interview, every single time it's
invoked -- re-entrancy is a first-class supported path (see
references/interview.md), not an edge case, and guessing at what already
exists instead of running this is how a re-invocation ends up generating
duplicate components. This script is the fast, consistent, drift-aware
substitute for a human eyeballing `ls` and `cat`.

Exit code is always 0 (an audit is a report, not a pass/fail check) unless
--path itself is invalid.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_common as hc
import validate_harness as vh


def _file_summary(path, root):
    stat = path.stat()
    return {
        "path": str(path.relative_to(root)),
        "size_bytes": stat.st_size,
        "lines": len(hc.read_text(path).splitlines()) if path.suffix in (".md", ".js") else None,
        "mtime": stat.st_mtime,
    }


def inventory_claude_md(root):
    """Every project-scope instruction file, not just ./CLAUDE.md.

    Returns a list. A project using only `.claude/CLAUDE.md` previously
    inventoried as having no CLAUDE.md at all, which made the audit report
    it absent and -- worse -- made suggest_mode classify an established
    harness as `new`."""
    out = []
    for path in hc.claude_md_paths(root):
        summary = _file_summary(path, root)
        summary["over_200_lines"] = (summary["lines"] or 0) > vh.MAX_CLAUDE_MD_LINES
        out.append(summary)
    return out


def inventory_rules(root):
    out = []
    for f in hc.iter_rule_files(root):
        text = hc.read_text(f)
        fm = hc.parse_frontmatter(text)
        entry = _file_summary(f, root)
        entry["has_paths"] = bool(fm.ok and fm.data.get("paths"))
        out.append(entry)
    return out


def inventory_skills(root):
    out = []
    for d in hc.iter_skill_dirs(root):
        skill_md = d / "SKILL.md"
        # 'path' is the skill DIRECTORY, not SKILL.md itself -- specs and
        # harness-spec.md's Component specs section reference skills by
        # directory (see references/interview.md's template), and drift
        # detection below depends on this field staying the directory path.
        entry = {"name": d.name, "path": str(d.relative_to(root))}
        if not skill_md.is_file():
            entry["error"] = "no SKILL.md"
            out.append(entry)
            continue
        text = hc.read_text(skill_md)
        fm = hc.parse_frontmatter(text)
        s = _file_summary(skill_md, root)
        s.pop("path", None)
        entry.update(s)
        entry["skill_md_path"] = str(skill_md.relative_to(root))
        if fm.ok:
            desc = fm.data.get("description", "")
            entry["description"] = (desc[:120] + "...") if len(desc) > 120 else desc
        else:
            entry["frontmatter_error"] = "; ".join(fm.warnings)
        entry["has_references"] = (d / "references").is_dir()
        entry["has_scripts"] = (d / "scripts").is_dir()
        out.append(entry)
    return out


def inventory_agents(root):
    out = []
    for f in hc.iter_agent_files(root):
        text = hc.read_text(f)
        fm = hc.parse_frontmatter(text)
        entry = _file_summary(f, root)
        if fm.ok:
            entry["name"] = fm.data.get("name")
            desc = fm.data.get("description", "")
            entry["description"] = (desc[:120] + "...") if len(desc) > 120 else desc
            entry["model"] = fm.data.get("model", "inherit")
        else:
            entry["frontmatter_error"] = "; ".join(fm.warnings)
        out.append(entry)
    return out


def inventory_workflows(root):
    out = []
    for f in hc.iter_workflow_files(root):
        entry = _file_summary(f, root)
        text = hc.read_text(f)
        import re
        m = re.search(r"description\s*:\s*['\"](.*?)['\"]", text)
        entry["description"] = m.group(1) if m else None
        out.append(entry)
    return out


def inventory_settings(root):
    out = {}
    for settings_path in hc.settings_paths(root):
        data, err = hc.load_json_lenient(settings_path)
        rel = str(settings_path.relative_to(root))
        if err:
            out[rel] = {"error": err}
            continue
        hooks = data.get("hooks", {})
        permissions = data.get("permissions", {})
        out[rel] = {
            "hook_events": sorted(hooks.keys()),
            "hook_group_count": sum(len(v) for v in hooks.values() if isinstance(v, list)),
            "permissions_allow": len(permissions.get("allow", [])),
            "permissions_deny": len(permissions.get("deny", [])),
            "permissions_ask": len(permissions.get("ask", [])),
        }
    return out


def check_spec_drift(root, inventory):
    spec_path = root / ".claude" / "harness-spec.md"
    if not spec_path.is_file():
        return {"spec_exists": False, "in_spec_not_on_disk": [], "on_disk_not_in_spec": []}

    spec_text = hc.read_text(spec_path)
    on_disk = set()
    for s in inventory["skills"]:
        on_disk.add(s["path"])
    for a in inventory["agents"]:
        on_disk.add(a["path"])
    for w in inventory["workflows"]:
        on_disk.add(w["path"])
    for r in inventory["rules"]:
        on_disk.add(r["path"])

    # Lenient membership: a spec may reference a skill's directory with or
    # without a trailing slash, or reference the containing directory of a
    # rule/agent/workflow file rather than the exact filename -- so check
    # both the exact path and its directory-name/file-stem against the
    # spec text rather than demanding an exact substring match.
    on_disk_not_in_spec = [
        p for p in sorted(on_disk)
        if p not in spec_text and p.rstrip("/") not in spec_text
        and Path(p).name not in spec_text and Path(p).stem not in spec_text
    ]
    return {
        "spec_exists": True,
        "on_disk_not_in_spec": on_disk_not_in_spec,
        "in_spec_not_on_disk": _spec_rows_without_files(root, spec_text, on_disk),
    }


# Only these two statuses assert that a file exists. `proposed` and
# `approved` are intent, not artifacts, so a row at either is not drift --
# reporting them would fire on every harness mid-interview.
_STATUSES_CLAIMING_A_FILE = frozenset({"generated", "validated"})


def _spec_rows_without_files(root, spec_text, on_disk):
    """Rows in the Behavior inventory whose status claims a file exists,
    where no such file is on disk.

    The other half of drift. Previously declined here on the grounds that the
    spec is free-form prose, but it is not: the Behavior inventory table's
    columns are fixed by the spec template that this skill itself writes
    (see references/interview.md), and the status column exists precisely so
    this check can be made. `status` stuck at `generated` with no matching
    file is the signal that generation was interrupted, or that something
    deleted the component out from under the spec."""
    missing = []
    disk_names = {Path(p.rstrip("/")).name for p in on_disk}
    disk_stems = {Path(p.rstrip("/")).stem for p in on_disk}

    for row in _iter_inventory_rows(spec_text):
        if len(row) < 5:
            continue
        component, status = row[3], row[4].lower()
        if status not in _STATUSES_CLAIMING_A_FILE:
            continue
        # The spec convention is a backticked repo-relative path, but accept
        # a bare name too rather than reporting a false "missing" against a
        # spec written before that convention was documented.
        name = component.strip().strip("`").rstrip("/")
        if not name or name.startswith("<"):
            continue
        # The claim under test is "the spec says this exists and it doesn't",
        # so a path that is simply present on disk settles it -- regardless of
        # whether it is one of the component-level paths this script
        # inventories. A spec may legitimately name a file *inside* a
        # component (a skill's SKILL.md, one of its references) at a finer
        # granularity than the inventory's unit, and reporting those as
        # missing would fire on a correct harness.
        if (Path(root) / name).exists():
            continue
        stem = Path(name).stem
        if name in on_disk or Path(name).name in disk_names or stem in disk_stems:
            continue
        missing.append({"id": row[0].strip(), "component": name, "status": status})
    return missing


def _iter_inventory_rows(spec_text):
    """Yield the data rows of the `## Behavior inventory` markdown table as
    lists of cell strings, skipping the header and separator rows."""
    in_section = False
    for line in spec_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            # A new heading ends the section; match on the heading text so a
            # different heading level doesn't break the parse.
            in_section = stripped.lstrip("#").strip().lower() == "behavior inventory"
            continue
        if not in_section or not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: "):
            continue  # separator row
        if cells[0].lower() == "id":
            continue  # header row
        yield cells


def check_user_scope_conflicts(root, inventory):
    home = Path.home()
    conflicts = []
    user_claude_md = home / ".claude" / "CLAUDE.md"
    if user_claude_md.is_file() and inventory["claude_md"]:
        conflicts.append(f"user-level {user_claude_md} exists alongside a project CLAUDE.md -- both concatenate with no override, check for contradictions")
    user_skills = home / ".claude" / "skills"
    if user_skills.is_dir():
        for s in inventory["skills"]:
            candidate = user_skills / s["name"]
            if candidate.exists():
                conflicts.append(f"a user-scope skill named '{s['name']}' also exists at {candidate} -- verify this isn't an unintentional shadow/duplicate")

    # User rules apply to every project on this machine and load before
    # project rules. One without `paths:` is in context for this session
    # whether or not it has anything to do with this repo.
    user_rules = home / ".claude" / "rules"
    unscoped = []
    for f in hc.iter_rule_files(home):
        fm = hc.parse_frontmatter(hc.read_text(f))
        if not (fm.ok and fm.data.get("paths")):
            unscoped.append(f.name)
    if unscoped:
        conflicts.append(
            f"{len(unscoped)} user-level rule(s) in {user_rules} have no 'paths:' and so load "
            f"into every project including this one ({', '.join(sorted(unscoped)[:5])}"
            f"{', ...' if len(unscoped) > 5 else ''}) -- check they don't contradict what "
            "this harness is about to say"
        )

    for name, path in _foreign_instruction_files(root):
        conflicts.append(
            f"{name} exists at {path} -- another coding agent's instructions. Claude Code does "
            "not read it, so its content is interview material rather than a component; if the "
            "project wants one source of truth, make '@" + name + "' the first line of CLAUDE.md"
        )
    return conflicts


# Reported, never parsed, and never treated as harness components: these
# belong to other tools, and the audit's job here is to surface that a second
# set of instructions exists so the interview can ask about it.
_FOREIGN_INSTRUCTION_PATHS = (
    "AGENTS.md",
    ".cursorrules",
    ".cursor/rules",
    ".github/copilot-instructions.md",
    ".windsurfrules",
    ".windsurf/rules",
    ".clinerules",
)


def _foreign_instruction_files(root):
    for rel in _FOREIGN_INSTRUCTION_PATHS:
        path = Path(root) / rel
        if path.exists():
            yield rel, path


def hygiene_signals(root):
    findings, _ = vh.run(root, strict=False)
    dead_links = [f for f in findings if "does not exist" in f[2] and ("references" in f[2] or "scripts" in f[2])]
    duplicate_agents = [f for f in findings if "duplicate agent name" in f[2]]
    non_executable = [f for f in findings if "not executable" in f[2]]
    return {
        "dead_link_count": len(dead_links),
        "duplicate_agent_name_count": len(duplicate_agents),
        "non_executable_hook_count": len(non_executable),
        "total_lint_errors": sum(1 for f in findings if f[0] == "E"),
        "total_lint_warnings": sum(1 for f in findings if f[0] == "W"),
    }


def suggest_mode(inventory, drift, hygiene):
    has_any_component = bool(
        inventory["claude_md"] or inventory["rules"] or inventory["skills"]
        or inventory["agents"] or inventory["workflows"] or inventory["settings"]
    )
    if not has_any_component:
        return "new -- no harness components found at all."
    if not drift["spec_exists"]:
        return "improve or sync -- components exist but there's no harness-spec.md; treat the first pass as recovering a spec from what's actually on disk."
    if drift["in_spec_not_on_disk"]:
        return "sync -- the spec claims components that aren't on disk; generation was interrupted, or something removed them. Confirm with the user before regenerating."
    if drift["on_disk_not_in_spec"]:
        return "sync -- components exist on disk that the spec doesn't mention; confirm with the user whether to update the spec or these files."
    if hygiene["total_lint_errors"] > 0:
        return "improve -- validate_harness.py finds real errors in the existing harness; likely an improve-mode pass to fix them."
    return "extend or improve -- ask the user directly ('what's new you want' vs 'what's been uncomfortable') per references/interview.md's re-entry variants; the audit alone can't distinguish these two."


def run(root):
    inventory = {
        "claude_md": inventory_claude_md(root),
        "rules": inventory_rules(root),
        "skills": inventory_skills(root),
        "agents": inventory_agents(root),
        "workflows": inventory_workflows(root),
        "settings": inventory_settings(root),
    }
    drift = check_spec_drift(root, inventory)
    conflicts = check_user_scope_conflicts(root, inventory)
    hygiene = hygiene_signals(root)
    mode = suggest_mode(inventory, drift, hygiene)
    return {
        "inventory": inventory, "spec_drift": drift,
        "user_scope_conflicts": conflicts, "hygiene": hygiene,
        "suggested_mode": mode,
    }


def print_markdown(result):
    inv = result["inventory"]
    print("# Harness audit\n")

    print("## Component inventory\n")
    if inv["claude_md"]:
        for entry in inv["claude_md"]:
            print(f"- {entry['path']}: present, {entry['lines']} lines")
    else:
        print("- CLAUDE.md: absent (checked ./CLAUDE.md, ./.claude/CLAUDE.md, ./CLAUDE.local.md)")
    print(f"- rules/: {len(inv['rules'])} file(s)")
    for r in inv["rules"]:
        print(f"  - {r['path']} ({'has paths' if r['has_paths'] else 'NO paths -- loads at launch'})")
    print(f"- skills/: {len(inv['skills'])} skill(s)")
    for s in inv["skills"]:
        if "error" in s:
            print(f"  - {s['name']}: ERROR -- {s['error']}")
        else:
            desc = s.get("description") or s.get("frontmatter_error") or "(no description)"
            print(f"  - {s['name']}: {desc}")
    print(f"- agents/: {len(inv['agents'])} agent(s)")
    for a in inv["agents"]:
        print(f"  - {a.get('name', a['path'])}: {a.get('description') or a.get('frontmatter_error') or '(no description)'}")
    print(f"- workflows/: {len(inv['workflows'])} workflow(s)")
    for w in inv["workflows"]:
        print(f"  - {w['path']}: {w.get('description') or '(no description found)'}")
    print("- settings.json:")
    for name, s in inv["settings"].items():
        if "error" in s:
            print(f"  - {name}: ERROR -- {s['error']}")
        else:
            print(f"  - {name}: hooks on {s['hook_events']}, permissions allow={s['permissions_allow']} deny={s['permissions_deny']} ask={s['permissions_ask']}")

    print("\n## harness-spec.md drift\n")
    drift = result["spec_drift"]
    if not drift["spec_exists"]:
        print("- No harness-spec.md found.")
    else:
        if drift["in_spec_not_on_disk"]:
            print("- Spec claims these components exist, but they are not on disk:")
            for row in drift["in_spec_not_on_disk"]:
                print(f"  - {row['component']} (row {row['id']}, status: {row['status']})")
        if drift["on_disk_not_in_spec"]:
            print("- Components on disk but not mentioned in the spec:")
            for p in drift["on_disk_not_in_spec"]:
                print(f"  - {p}")
            print("    (a component here may be a normal edit made outside this flow, not")
            print("     corruption -- ask before proposing to regenerate or remove anything)")
        if not drift["in_spec_not_on_disk"] and not drift["on_disk_not_in_spec"]:
            print("- No drift detected in either direction.")

    print("\n## User-scope conflict candidates\n")
    if result["user_scope_conflicts"]:
        for c in result["user_scope_conflicts"]:
            print(f"- {c}")
    else:
        print("- None found.")

    print("\n## Hygiene signals\n")
    h = result["hygiene"]
    print(f"- Dead links: {h['dead_link_count']}")
    print(f"- Duplicate agent names: {h['duplicate_agent_name_count']}")
    print(f"- Non-executable hook scripts: {h['non_executable_hook_count']}")
    print(f"- validate_harness.py: {h['total_lint_errors']} error(s), {h['total_lint_warnings']} warning(s)")

    print(f"\n## Suggested mode\n\n{result['suggested_mode']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", required=True, help="path to the target repo root")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: --path '{args.path}' is not a directory", file=sys.stderr)
        return hc.EXIT_USAGE_ERROR

    result = run(root)
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_markdown(result)
    return hc.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
