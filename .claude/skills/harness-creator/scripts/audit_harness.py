#!/usr/bin/env python3
"""Inventory a project's harness and the commits that shaped it.

    python audit_harness.py --path <target-repo> [--json]

Inventories CLAUDE.md files, rules, skills, agents, workflows and
settings.json. Also lists user-scope files that can collide with this
project's harness, and the lint counts from validate_harness.py.

Then lists the commits that changed a harness component -- hash, date,
subject and which component paths matched -- most recent first, capped. A
commit that merely used the harness edits the project, not the harness, so
the path filter never meets it. The report names the paths it searched, and
distinguishes what it found: no repository, git that would not run, no
commits, or no commit touching a component. A shallow clone is reported as
such, because its oldest entry lists files inherited rather than added.
Read a listed commit's reasons with `git show`.

Existence only. It does not compare contents: an edited CLAUDE.md, or a
rewritten skill body at a path it already knows, reads as unchanged.

Exit code is always 0 (an audit is a report, not a pass/fail check) unless
the arguments are invalid.
"""

import argparse
import json
import os
import subprocess
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
        # 'path' is the skill DIRECTORY, not SKILL.md itself: a skill is
        # addressed by its directory everywhere else in this report.
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


def _git_root(root):
    """(path, reason) for the repository containing root.

    Resolved by asking git rather than looking for `root/.git`: a target
    inside a monorepo has its repository several levels up, and a bare
    existence check reports that project as unversioned. The two ways this
    can come back empty stay apart -- git that would not run is a fact about
    the machine, and no repository is a fact about the project."""
    done = _git(root, "rev-parse", "--show-toplevel")
    if done is None:
        return None, "unavailable"
    if done.returncode != 0 or not done.stdout.strip():
        return None, "not_a_repository"
    return Path(done.stdout.strip()), None


def _git(cwd, *args):
    """Run git in cwd, or None when git cannot run at all.

    A missing git binary and a directory outside any repository are both
    ordinary here -- an audit reports what it could not see rather than
    failing the run."""
    try:
        return subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None


# The component paths whose history is the harness's record. Directory
# patterns rather than the files discovery finds today, so a commit that
# deleted a component still matches. Nothing else under `.claude/` belongs
# here, however harness-shaped it looks: a directory that ordinary feature
# work also writes into turns "changed the harness" back into "used it",
# which is the distinction this whole report rests on.
HARNESS_HISTORY_PATHS = (
    "CLAUDE.md",
    "CLAUDE.local.md",
    ".claude/CLAUDE.md",
    ".claude/rules",
    ".claude/skills",
    ".claude/agents",
    ".claude/workflows",
    ".claude/hooks",
    ".claude/settings.json",
    ".claude/settings.local.json",
    # Where a project set up before this tool read git kept its decisions.
    # No pass writes one now; dropping the path would retire the history
    # rather than the file, and for such a project that history is all of it.
    ".claude/harness-spec.md",
)

# A commit subject may hold any byte but NUL, and a path any byte but NUL and
# `/`, so NUL is the only framing byte the data cannot forge. `%x00` asks git
# to emit one; the null byte argv cannot carry is a different question.
_HISTORY_FIELD_SEP = "\x1f"

# A budget on this report, not a claim about the repository. Twenty covers
# several passes' worth of decisions without turning an audit into a
# changelog; when it binds, the report says so and names the paths it
# searched, which is what a reader needs to run git themselves. Raise it if
# a project's passes routinely span more than that.
HISTORY_LIMIT = 20


def harness_history_paths(root):
    """The pathspec to search, relative to root.

    Fixed component paths plus whatever skills roots this project's plugin
    manifest declares -- that field can point anywhere, so it cannot be a
    constant. A root that an earlier manifest declared and this one no longer
    does cannot be recovered from the manifest on disk, which is why the
    report states the paths it searched rather than claiming to be the whole
    record."""
    paths = list(HARNESS_HISTORY_PATHS)
    root = Path(root)
    extras = list(hc.declared_plugin_skills_roots(root))
    # `@file` puts another file in every session, so editing it changes what
    # the harness says while touching nothing on the fixed list. Only targets
    # inside this project: an import that reaches outside has no history here.
    for instruction_file in hc.claude_md_paths(root):
        for target in hc.parse_at_imports(hc.read_text(instruction_file)):
            resolved, external = hc.resolve_import(target, instruction_file)
            if not external:
                extras.append(resolved)
    for extra in extras:
        try:
            rel = Path(extra).relative_to(root).as_posix()
        except ValueError:
            continue
        if rel not in paths:
            paths.append(rel)
    return paths


def _run_history_log(root, paths, diff_merges=True):
    """The log call, with its one optional flag isolated.

    `--diff-merges` arrived in git 2.31. Without it a merge is listed with no
    files at all, so it is worth asking for -- and worth falling back when a
    git that does not know it refuses the whole command, because a report
    that lists merges without their paths still beats no report."""
    args = [
        # A directory whose name starts with `:` is a pathspec magic word to
        # git, and the mismatch is silent: the search returns nothing and the
        # report says no commit touched a component.
        "--literal-pathspecs",
        # --full-history because path-limited history simplification prunes
        # side branches: a decision that arrived on a merged branch is
        # otherwise absent from a report that claims to be the record.
        "log", "--full-history", "--name-only",
        # -z for the file list too: without it git hands back its display
        # form, which octal-escapes a non-ASCII path and quotes an awkward
        # one, so `matched` would name files that are not on disk.
        "-z",
        # One past the limit, so truncation is known without walking (and
        # paying for) a history the report is not going to print.
        "-n", str(HISTORY_LIMIT + 1),
        f"--format=%x00%h{_HISTORY_FIELD_SEP}%ad{_HISTORY_FIELD_SEP}%s",
        "--date=short", "--", *paths
    ]
    if diff_merges:
        # A merge is not diffed by default, so a resolution that changed a
        # component reads as a change with no files. Against the first parent
        # is the branch's own contribution, which is what a reader is after.
        args.insert(args.index("--name-only") + 1, "--diff-merges=first-parent")
    done = _git(root, *args)
    if diff_merges and (done is None or done.returncode != 0):
        return _run_history_log(root, paths, diff_merges=False)
    return done


def harness_history(root):
    """Commits that changed this project's harness.

    Pathspecs are resolved by git against its own working directory, so the
    query runs with `-C root`: the same relative path from the repository
    root matches nothing when the target is a subdirectory."""
    git_root, reason = _git_root(root)
    if git_root is None:
        return {"status": reason, "commits": [], "truncated": False, "shallow": False, "paths": []}
    paths = harness_history_paths(root)
    # A shallow clone cuts ancestry off, and git presents the boundary commit
    # as a root: its whole tree reads as files that commit added. So the
    # oldest entry here can credit a commit with creating a component it only
    # inherited, and anything below the cut is invisible rather than absent.
    depth = _git(root, "rev-parse", "--is-shallow-repository")
    shallow = depth is not None and depth.stdout.strip() == "true"
    # Before the log, not after: a repository with no commits makes `git log`
    # exit non-zero, and reading that as "git failed" turns "nothing has been
    # recorded yet" into "the record could not be read".
    head = _git(root, "rev-parse", "--verify", "-q", "HEAD")
    if head is None or head.returncode != 0:
        return {"status": "no_history", "commits": [], "truncated": False,
                "shallow": shallow, "paths": paths}
    done = _run_history_log(root, paths)
    if done is None or done.returncode != 0:
        return {"status": "unavailable", "commits": [], "truncated": False,
                "shallow": shallow, "paths": paths}

    commits = []
    # Under `-z` each commit arrives as an empty field, then the formatted
    # header, then its paths. The first path carries git's own newline
    # between the two, and exactly one leading newline is that separator
    # rather than part of a filename.
    expect_header = True
    for token in (done.stdout or "").split("\x00"):
        if not token:
            expect_header = True
            continue
        if expect_header:
            parts = token.split(_HISTORY_FIELD_SEP, 2)
            if len(parts) != 3:
                continue
            commits.append({
                "hash": parts[0], "date": parts[1], "subject": parts[2], "matched": [],
            })
            expect_header = False
        elif commits:
            commits[-1]["matched"].append(token[1:] if token.startswith("\n") else token)
    truncated = len(commits) > HISTORY_LIMIT
    commits = commits[:HISTORY_LIMIT]
    return {
        "status": "searched" if commits else "no_match",
        "commits": commits, "truncated": truncated, "shallow": shallow, "paths": paths,
    }


# What the drift check reads and what it is blind to. Printed on every run,
# because a clean report otherwise reads as "nothing changed".
SCOPE = {
    "detects": [
        "component files present on disk: skills, agents, workflows, rules, hooks and settings",
        "user-scope files that can collide with this project's harness",
        "commits that changed a harness component, with the paths that matched",
    ],
    "does_not_detect": [
        "edits to CLAUDE.md or any instruction file (inventoried, not diffed)",
        "edits inside a component's body -- a rewritten skill at a known path reads as unchanged",
        "whether any hook, rule or skill behaves the way it is meant to",
        "a decision that did not change any file -- a candidate declined, or an "
        "interview that ended before it generated, leaves no commit to find",
        "reasons kept only in a pull request rather than in the commit body, which "
        "an offline clone does not have",
        "history under a plugin skills root that an earlier manifest declared and this one no longer does",
        "whether a revert withdrew a decision or only its implementation",
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
    conflicts = check_user_scope_conflicts(root, inventory, user_root)
    hygiene = hygiene_signals(root)
    history = harness_history(root)
    return {
        "inventory": inventory,
        "harness_history": history,
        "user_scope_conflicts": conflicts, "hygiene": hygiene,
        "scope": SCOPE,
        "user_config_root": str(user_root), "user_config_root_source": user_root_source,
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

    print("- Scope: existence only. Detects: " + "; ".join(result["scope"]["detects"]) + ".")
    print("  Does not detect: " + "; ".join(result["scope"]["does_not_detect"]) + ".")

    print("\n## Harness change history\n")
    history = result["harness_history"]
    if history["status"] == "not_a_repository":
        print("- Not a git repository, so there is no commit history to search here.")
    elif history["status"] == "no_history":
        print("- The repository has no commits yet, so there is no history to search.")
    elif history["status"] == "unavailable":
        print("- The history could not be read: git did not answer. Everything above still holds.")
    elif history["status"] == "no_match":
        print("- No commit in this repository has touched a harness component.")
    else:
        for c in history["commits"]:
            print(f"- {c['hash']} {c['date']} {c['subject']}")
            if c["matched"]:
                print(f"  - matched: {', '.join(c['matched'])}")
        if history["truncated"]:
            print(f"- Capped at {len(history['commits'])}; older harness commits exist. "
                  "Read a commit's reasons with `git show <hash>`.")
    if history["shallow"]:
        print("- This clone is shallow, so its history stops at a boundary git presents as a "
              "root: the oldest entry above lists files it inherited rather than added, and "
              "anything before the cut is out of reach here rather than absent.")
    if history["paths"]:
        print("- Searched: " + ", ".join(history["paths"]) + ".")

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
    parser.add_argument("--path", required=True, help="path to the target repo root to audit")
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
