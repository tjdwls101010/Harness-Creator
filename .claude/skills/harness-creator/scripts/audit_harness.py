#!/usr/bin/env python3
"""Inventory a project's harness and compare it with its harness-spec.md.

    python audit_harness.py --path <target-repo> [--json]
    python audit_harness.py --template

Inventories CLAUDE.md files, rules, skills, agents, workflows and
settings.json, then reports drift in both directions: inventory rows whose
status claims a file that is not on disk, and components on disk the spec
never mentions. Also lists user-scope files that can collide with this
project's harness, and the lint counts from validate_harness.py.

Existence only. It does not compare contents: an edited CLAUDE.md, or a
rewritten skill body at the path the spec names, reads as in sync.

--template prints the harness-spec.md skeleton this script's parser reads,
with the inventory columns and status vocabulary it recognises, so a spec
started from it round-trips with zero drift.

Exit code is always 0 (an audit is a report, not a pass/fail check) unless
the arguments are invalid.
"""

import argparse
import json
import os
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
    """Every project-scope instruction file, not just ./CLAUDE.md."""
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
        # 'path' is the skill DIRECTORY, not SKILL.md itself -- the spec
        # template names skills by directory, and drift detection below
        # depends on this field staying the directory path.
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


def _spec_rows_without_files(root, spec_text, on_disk):
    """Rows in the Behavior inventory whose status claims a file exists,
    where no such file is on disk. `generated` with no matching file means
    generation was interrupted, or something deleted the component out from
    under the spec; `validated` means it existed and passed, then vanished."""
    missing = []
    disk_names = {Path(p.rstrip("/")).name for p in on_disk}
    disk_stems = {Path(p.rstrip("/")).stem for p in on_disk}

    for row in hc.iter_inventory_rows(spec_text):
        if len(row) < 5:
            continue
        component, status = row[3], row[4].strip("`")
        if status not in hc.STATUSES_CLAIMING_A_FILE:
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


# Kept for callers that imported the private name; the parser lives in
# harness_common so validate_harness.py reads the same rows.
_iter_inventory_rows = hc.iter_inventory_rows


def user_config_root(env=None):
    """(path, source) for the user's Claude Code configuration directory:
    CLAUDE_CONFIG_DIR when set, else ~/.claude."""
    env = os.environ if env is None else env
    configured = env.get("CLAUDE_CONFIG_DIR")
    if configured:
        return Path(configured).expanduser(), "CLAUDE_CONFIG_DIR"
    return Path.home() / ".claude", "default"


def check_user_scope_conflicts(root, inventory, user_root=None):
    user_root = user_root if user_root is not None else user_config_root()[0]
    conflicts = []
    user_claude_md = user_root / "CLAUDE.md"
    if user_claude_md.is_file() and inventory["claude_md"]:
        conflicts.append(f"user-level {user_claude_md} exists alongside a project CLAUDE.md -- both concatenate with no override, check for contradictions")
    user_skills = user_root / "skills"
    if user_skills.is_dir():
        for s in inventory["skills"]:
            candidate = user_skills / s["name"]
            if candidate.exists():
                conflicts.append(f"a user-scope skill named '{s['name']}' also exists at {candidate} -- verify this isn't an unintentional shadow/duplicate")

    # User rules apply to every project on this machine and load before
    # project rules. One without `paths:` is in context for this session
    # whether or not it has anything to do with this repo.
    user_rules = user_root / "rules"
    unscoped = []
    for f in hc.walk_markdown(user_rules):
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

    user_workflows = user_root / "workflows"
    if user_workflows.is_dir():
        for w in inventory["workflows"]:
            candidate = user_workflows / Path(w["path"]).name
            if candidate.exists():
                conflicts.append(
                    f"a personal workflow named '{candidate.stem}' also exists at {candidate} -- when a "
                    "project workflow and a personal one share a name, the project one runs, so the "
                    "personal one is shadowed in this repo"
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


# What the drift check reads and what it is blind to. Printed on every run,
# because a clean report otherwise reads as "nothing changed".
SCOPE = {
    "detects": [
        "component files present on disk (skills, agents, workflows, rules) that the spec never mentions",
        f"inventory rows at status {'/'.join(sorted(hc.STATUSES_CLAIMING_A_FILE))} whose component path is not on disk",
        "user-scope files that can collide with this project's harness",
    ],
    "does_not_detect": [
        "edits to CLAUDE.md or any instruction file (inventoried, not diffed)",
        "edits inside a component's body -- a rewritten skill at the path the spec names is in sync",
        "whether any hook, rule or skill behaves as the spec describes",
    ],
}


def run(root):
    inventory = {
        "claude_md": inventory_claude_md(root),
        "rules": inventory_rules(root),
        "skills": inventory_skills(root),
        "agents": inventory_agents(root),
        "workflows": inventory_workflows(root),
        "settings": inventory_settings(root),
    }
    user_root, user_root_source = user_config_root()
    drift = check_spec_drift(root, inventory)
    conflicts = check_user_scope_conflicts(root, inventory, user_root)
    hygiene = hygiene_signals(root)
    return {
        "inventory": inventory, "spec_drift": drift,
        "user_scope_conflicts": conflicts, "hygiene": hygiene,
        "scope": SCOPE,
        "user_config_root": str(user_root), "user_config_root_source": user_root_source,
    }


def spec_template():
    """The harness-spec.md skeleton, from the same constants the parsers read.
    Example rows sit inside HTML comments so the parser ignores them and a
    fresh copy round-trips with zero drift."""
    header = "| " + " | ".join(hc.INVENTORY_COLUMNS) + " |"
    separator = "|" + "|".join("-" * (len(c) + 2) for c in hc.INVENTORY_COLUMNS) + "|"
    statuses = ", ".join(f"`{s}`" for s in hc.SPEC_STATUSES)
    claiming = " and ".join(f"`{s}`" for s in sorted(hc.STATUSES_CLAIMING_A_FILE))
    guidance = {
        "Context": "Language(s), build system, test runner, team size, and how much Claude Code vocabulary the user brought.",
        "Goals": "What this harness should change about how Claude behaves here, in the user's own words where they are sharper than a paraphrase.",
        "Behavior inventory": (
            f"One row per behaviour, piece of knowledge, or constraint. `component` is a backticked repo-relative path. `status` is one of {statuses}: "
            "`proposed` (surfaced, not yet approved) -> `approved` (locked as intent, nothing generated) -> `generated` (a file exists on disk) -> "
            "`validated` (lint passed, and e2e too if it was run); `declined` (deliberately not built) and `retired` (deliberately removed) are terminal. "
            f"Only {claiming} assert that the file exists, and the drift check reads exactly those two, so a `generated` row with no file means an interrupted "
            "generation and a `validated` one means something removed it. Keep `declined` and `retired` rows: they are what stops the next pass re-proposing the same idea."
        ),
        "Component specs": "Per component, what generation needs and the spec uniquely knows: hooks need event/matcher/action/failure policy; skills need where their reference material comes from and any bundled scripts. Do not copy a skill's description here -- it lives in the frontmatter and the copy is the half that drifts.",
        "Design rationale": "Each routing decision and the alternatives rejected, and stop there. A rejected alternative is the expensive thing to lose; the sentences defending a choice are not. When a later pass supersedes a decision, rewrite the entry to its outcome instead of stacking.",
        "Validation": "The scenarios that count as proof, and the result of the most recent run.",
        "Change history": "Date and what changed, one entry per pass. Keep in full what a re-entering pass can still act on and any entry recording someone else's edit; fold everything older to one line each.",
    }
    lines = ["# Harness Spec — <project>", ""]
    for section in hc.SPEC_SECTIONS:
        lines += [f"## {section}", "", f"<!-- {guidance[section]} -->", ""]
        if section == hc.INVENTORY_HEADING:
            lines += [header, separator,
                      "<!-- | B1 | Must pass tests before commit | hook | `.claude/hooks/pre-commit-test.sh` | proposed | -->", ""]
        elif section == "Change history":
            lines += ["<!-- - YYYY-MM-DD: what changed. -->", ""]
    return "\n".join(lines)


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
        print("- No harness-spec.md found at .claude/harness-spec.md. `--template` prints the skeleton to start one from.")
    else:
        if drift["in_spec_not_on_disk"]:
            print("- Spec claims these components exist, but they are not on disk:")
            for row in drift["in_spec_not_on_disk"]:
                print(f"  - {row['component']} (row {row['id']}, status: {row['status']})")
        if drift["on_disk_not_in_spec"]:
            print("- Components on disk but not mentioned in the spec:")
            for p in drift["on_disk_not_in_spec"]:
                print(f"  - {p}")
        if not drift["in_spec_not_on_disk"] and not drift["on_disk_not_in_spec"]:
            print("- No drift detected in either direction.")
    print("- Scope: existence only. Detects: " + "; ".join(result["scope"]["detects"]) + ".")
    print("  Does not detect: " + "; ".join(result["scope"]["does_not_detect"]) + ".")

    print(f"\n## User-scope conflict candidates ({result['user_config_root']}, from {result['user_config_root_source']})\n")
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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    what = parser.add_mutually_exclusive_group(required=True)
    what.add_argument("--path", help="path to the target repo root to audit")
    what.add_argument("--template", action="store_true", help="print the harness-spec.md skeleton this script's parser reads, and exit")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output (with --path only)")
    args = parser.parse_args()

    if args.template:
        if args.json:
            parser.error("--template prints markdown; --json applies to --path")
        print(spec_template())
        return hc.EXIT_OK

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
