#!/usr/bin/env python3
"""Deterministic lint for a Claude Code harness.

    python validate_harness.py --path <target-repo> [--json] [--strict]

Checks the shape of what is on disk: settings.json hooks and permission
rules, skill frontmatter and pointers, bundled-script CLI self-description,
agent frontmatter, workflow meta and syntax, rule globs, CLAUDE.md length
and @imports, harness-spec.md inventory rows, and package closure for
plugin-shipped skills. Prints the always-loaded budget for the project scope.

What it cannot see: behaviour. It does not know whether a hook ran, whether
a description triggers on the prompts it should, or whether prose is
followed -- only that the structure is well-formed. Findings that carry a
code (V01, ...) are the checks a fixture pins by code.

Exit codes: 0 = no errors (warnings still possible unless --strict),
1 = at least one error (or, under --strict, at least one warning),
2 = the script itself couldn't run (bad --path, bad arguments).
"""

import argparse
import ast
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

# Documented aliases for a subagent's `model:`, plus `inherit` (also what an
# omitted field means).
MODEL_ALIASES = ("inherit", "sonnet", "opus", "haiku", "fable")


def is_plausible_model(value):
    """An alias, or any `claude-`-prefixed id.

    Shape, not membership: the docs describe the rule as an alias, an id
    this Claude Code version knows, or an id starting with `claude-`, and
    only the first and third are knowable from outside the running client.
    Enumerating ids would fail a correct harness every time a model ships."""
    return isinstance(value, str) and (
        value in MODEL_ALIASES or value.startswith("claude-")
    )

# Allow patterns that auto mode drops -- generating these is dead weight,
# not a correctness bug, so this is a warning, not an error.
_BROAD_ALLOW_RE = re.compile(
    r"^(Bash|PowerShell)\((\*|[a-zA-Z0-9_.\-]+\*)\)$|^Agent(\(.*\))?$"
)

_TRIGGER_PHRASE_RE = re.compile(
    r"\b(use|when|whenever|trigger|invoke)\b|할\s*때|사용", re.IGNORECASE
)
_BULLET_NAME_RE = re.compile(r"^\s*[-*]\s+`?([A-Za-z0-9_\-]+)`?\s*$")
_SKILL_POINTER_RE = re.compile(
    # Not after `=`, `?` or `&`: `...?source=references/install.md` is a URL
    # query value, not a pointer into this skill.
    r"(?<![=?&])"
    r"(?P<prefix>\$\{CLAUDE_SKILL_DIR\}/|\./|/)?"
    r"(?P<subdir>references|scripts)/"
    r"(?P<name>[A-Za-z0-9_.*\-]+(?:/[A-Za-z0-9_.*\-]+)*)"
)


# A slash-bearing path naming a document. Package closure only cares about
# things a reader is sent to read, so binaries, config, and source are out.
_DOC_PATH_RE = re.compile(r"(?<![\w./\-])([\w.\-]+(?:/[\w.*\-]+)+\.(?:md|txt|rst))")

# Files the target project owns. A skill that builds harnesses names these
# constantly and is not pointing into its own package when it does.
_HARNESS_NAMESPACE = frozenset(
    {"CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", "MEMORY.md", "SKILL.md", "harness-spec.md"}
)


def add(findings, level, location, message, code=None):
    findings.append(hc.Finding(level, location, message, code))


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
        if isinstance(data.get("permissions"), dict):
            _check_deny_subsumes_allow(str(rel), data["permissions"], findings)


def _check_hooks_block(root, rel, hooks, findings, base_dir=None, once_honored=False):
    """`once_honored` is True only for a skill's frontmatter; settings files
    and agent frontmatter accept the field and ignore it."""
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
                if event not in hc.NON_MATCHER_EVENTS:
                    _check_bare_mcp_matcher(rel, event, gi, matcher, findings)
                if event in hc.NON_MATCHER_EVENTS:
                    add(
                        findings, "E", f"{rel}#hooks.{event}[{gi}]",
                        f"'{event}' does not support a 'matcher' field -- it fires "
                        "unconditionally, so this matcher is silently ignored",
                    )
                elif (not hc.is_exact_matcher(matcher) and not re.match(r"^\^.*\$$", matcher)
                      and not _DOCUMENTED_MCP_MATCHER_RE.match(matcher)):
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
                if hook.get("once") is True and not once_honored:
                    add(
                        findings, "E", loc,
                        "'once: true' is honored only for hooks declared in a skill's frontmatter; here it is "
                        "accepted and ignored, so this hook runs on every matching event -- move the hook into "
                        "a skill, or drop the field and build the one-shot behaviour into the script",
                        code="V07",
                    )
                if htype == "command":
                    command = hook.get("command")
                    if not command:
                        add(findings, "E", loc, "command hook missing 'command' field")
                    elif "/" in command or "${" in command:
                        # Checked only when the command looks like a path. A bare
                        # name (`python3`, `echo`) resolves on PATH in either form
                        # and is not a script reference.
                        _check_command_script_exists(root, loc, command, findings, base_dir)
                    if command and "args" not in hook and _has_unquoted_placeholder(command):
                        add(
                            findings, "W", loc,
                            f"'{command}' carries an unquoted path placeholder in shell form (no 'args') -- the "
                            "shell re-tokenizes the substituted path, so a directory with a space or an "
                            "apostrophe breaks it; add \"args\": [] to switch to exec form, where the "
                            "placeholder is substituted as one argument, or double-quote it",
                            code="V15",
                        )
                    if command and event in ("Stop", "SubagentStop"):
                        _check_stop_loop_guard(root, loc, command, hook.get("args"), findings, base_dir)
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


_PLACEHOLDER_RE = re.compile(r"\$\{[A-Z_]+\}")


def _has_unquoted_placeholder(command):
    """A placeholder inside double quotes survives shell re-tokenization; a
    bare one does not. Tokenize on whitespace outside quotes and look for a
    token that carries a placeholder without being wrapped in quotes."""
    for token in command.split():
        if _PLACEHOLDER_RE.search(token) and not (token.startswith('"') or token.startswith("'")):
            return True
    return False
_BARE_MCP_MATCHER_RE = re.compile(r"^mcp__[A-Za-z0-9_-]+$")
# `mcp__<server>__.*` is the documented way to match every tool from a server;
# it is a regex by construction, so the unanchored-regex warning would fire on
# the exact shape the docs prescribe.
_DOCUMENTED_MCP_MATCHER_RE = re.compile(r"^mcp__[A-Za-z0-9_.*-]+__[A-Za-z0-9_.*-]+$")
# A Stop-hook script that can keep Claude working: it emits a decision,
# additionalContext, or a blocking exit. Scripts that only log have nothing
# to guard. Matched against the script with comments removed.
_STOP_BLOCK_RE = re.compile(
    r'["\']decision["\']\s*:|\bdecision\b\s*[:=]|["\']block["\']|additionalContext|exit\s+2\b|SystemExit\(\s*2\s*\)|sys\.exit\(\s*2\s*\)'
)
# Either is a loop guard the docs accept: reading the field, or reading the
# transcript ("Check this value or process the transcript").
_STOP_GUARD_RE = re.compile(r"stop_hook_active|transcript_path")
_COMMENT_RE = re.compile(r"(^|\s)#[^\n]*")


def _hook_script_path(root, command, args, base_dir):
    """The file a command hook runs: the command itself when it is a path,
    else the first path-shaped operand (exec-form `args` first, then the
    shell-form command's tokens). None when nothing resolvable is named."""
    candidates = [command] + [a for a in (args or []) if isinstance(a, str)]
    if not args:
        candidates += command.split()
    for token in candidates:
        token = token.strip().strip("\"'")
        if not token or "${" in token.replace("${CLAUDE_PROJECT_DIR}", ""):
            continue
        resolved = token.replace("${CLAUDE_PROJECT_DIR}", str(root))
        if "/" not in resolved and not resolved.endswith((".sh", ".py", ".js")):
            continue
        path = Path(resolved)
        if not path.is_absolute():
            path = Path(base_dir) / path if base_dir else root / path
        if path.is_file():
            return path
    return None


def _check_bare_mcp_matcher(rel, event, gi, matcher, findings):
    """V04. A hook matcher is exact-string unless it has a regex character;
    `mcp__memory` has none, so it is compared as a literal tool name that no
    tool has. Hook matchers only -- a *permission* rule `mcp__memory` means
    the whole server, a different grammar."""
    for token in re.split(r"[|,]", matcher):
        token = token.strip()
        if _BARE_MCP_MATCHER_RE.match(token) and token.count("__") == 1:
            add(
                findings, "E", f"{rel}#hooks.{event}[{gi}]",
                f"matcher '{token}' names an MCP server with no tool part and no '.*', so it is "
                f"compared as an exact tool name and matches nothing -- write '{token}__.*' for every "
                f"tool from that server, or '{token}__<tool>' for one",
                code="V04",
            )


def _check_stop_loop_guard(root, loc, command, args, findings, base_dir):
    """V05. A Stop/SubagentStop script that can block but reads neither
    `stop_hook_active` nor the transcript blocks every stop until the
    built-in cap ends the turn. Only when the script is a readable file that
    visibly emits a decision; comments are ignored on both sides, and a
    script the linter cannot resolve is not judged."""
    path = _hook_script_path(root, command, args, base_dir)
    if path is None:
        return
    try:
        text = _COMMENT_RE.sub(" ", hc.read_text(path))
    except (OSError, UnicodeDecodeError):
        return
    if _STOP_GUARD_RE.search(text) or not _STOP_BLOCK_RE.search(text):
        return
    add(
        findings, "W", loc,
        f"{path.name} can block a stop but reads neither stop_hook_active nor the transcript -- when the "
        "condition stays unmet it blocks every stop until Claude Code's consecutive-block cap gives up, "
        "and the turn ends unvalidated; read stop_hook_active first and exit 0 when it is true",
        code="V05",
    )


def _check_command_script_exists(root, loc, command, findings, base_dir=None):
    """`base_dir` is what a relative command path resolves against. It is the
    project root for a settings.json hook and the skill's own directory for a
    hook declared in a skill's frontmatter -- the same string means two
    different files depending on where it was written."""
    base = Path(base_dir) if base_dir else root
    # A shell-form command may quote the path; the quotes are shell syntax,
    # not part of the file name.
    resolved = command.strip().strip("\"'").replace("${CLAUDE_PROJECT_DIR}", str(root))
    if resolved.startswith("$") or "${" in resolved:
        return  # unresolved env var we don't know the value of -- skip, don't guess
    path = Path(resolved)
    if not path.is_absolute():
        path = base / path
    if not path.exists():
        add(findings, "E", loc, f"hook command references a script that does not exist: {command}")
        return
    if path.is_file() and not (path.stat().st_mode & stat.S_IXUSR):
        add(findings, "E", loc, f"hook script exists but is not executable: {path.relative_to(root)}")


class _BlockShapeError(Exception):
    """The block is outside the subset below. Never a guess -- a wrong reading
    reports a correct hook as broken, which is worse than declining to read."""


# A quoted key is ordinary YAML and has to be read, not declined.
_BLOCK_KEY = re.compile(r"^\"?'?([A-Za-z_][A-Za-z0-9_-]*)'?\"?:\s*(.*)$")


def _block_scalar(text):
    if text in ("true", "false"):
        return text == "true"
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    return text or None


def _read_block(lines):
    """Read the nested mapping/sequence subset a frontmatter `hooks:` block
    uses. `harness_common.parse_frontmatter` deliberately does not guess at
    nested shapes and keeps the raw lines instead; this is the caller that
    knows one specific shape reading them, so frontmatter still has one parser
    and this one never has to decide where the block begins or ends.

    Returns (value, error). Flow collections, multi-line scalars and anything
    else outside the subset come back as an error, not a partial reading."""
    items = [
        (len(raw) - len(raw.lstrip()), raw.strip())
        for raw in lines
        if raw.strip() and not raw.strip().startswith("#")
    ]
    if not items:
        return None, None
    try:
        return _read_block_node(items), None
    except _BlockShapeError as exc:
        return None, str(exc)


def _read_block_node(items):
    base = items[0][0]
    if items[0][1] == "-" or items[0][1].startswith("- "):
        return _read_block_sequence(items, base)

    result = {}
    i = 0
    while i < len(items):
        indent, text = items[i]
        if indent != base:
            raise _BlockShapeError(f"unexpected indentation at: {text!r}")
        m = _BLOCK_KEY.match(text)
        if not m:
            raise _BlockShapeError(f"expected 'key: value', got: {text!r}")
        key, rest = m.group(1), m.group(2).strip()
        i += 1
        child = []
        # A sequence may sit at its key's own indent, so take same-indent list
        # items as children too -- but only when the key had no inline value.
        while i < len(items) and (
            items[i][0] > base
            or (not rest and items[i][0] == base and items[i][1].startswith("- "))
        ):
            child.append(items[i])
            i += 1
        if rest and child:
            raise _BlockShapeError(f"'{key}' has both an inline value and a nested block")
        result[key] = _read_block_node(child) if child else _block_scalar(rest)
    return result


def _read_block_sequence(items, base):
    result = []
    i = 0
    while i < len(items):
        indent, text = items[i]
        if indent != base or not (text == "-" or text.startswith("- ")):
            raise _BlockShapeError(f"expected a list item, got: {text!r}")
        inner = []
        rest = text[1:].strip()
        if rest:
            if not text.startswith("- "):
                raise _BlockShapeError(f"list item needs a space after '-': {text!r}")
            inner.append((base + 2, rest))
        i += 1
        while i < len(items) and items[i][0] > base:
            inner.append(items[i])
            i += 1
        result.append(_read_block_node(inner) if inner else None)
    return result


# Edit(path) also governs Write and NotebookEdit; Read(path) also governs Grep
# and Glob. A path rule written against any of the governed tools is accepted
# and then never consulted -- see references/hooks.md.
_INERT_PATH_RULE_FIX = {
    "Write": "Edit",
    "NotebookEdit": "Edit",
    "MultiEdit": "Edit",
    "Glob": "Read",
}
# `Bash(ls *)` requires a space or end-of-string after the prefix; `Bash(ls*)`
# does not, and so also matches `lsof` -- see references/hooks.md.
_UNBOUNDED_PREFIX_RE = re.compile(r"^(Bash|PowerShell)\(([a-zA-Z0-9_.\-]+)\*\)$")

# `/path` is the documented settings-source anchor, so a single slash alone is
# not a defect. What is: a single slash in front of a segment that only makes
# sense from the filesystem root -- the docs' own example is `/Users/alice/file`.
_SINGLE_SLASH_PATH_RULE_RE = re.compile(
    r"^(Read|Edit)\((/(?:Users|home|etc|tmp|var|opt|root|private|usr|Volumes)(?:/.*)?)\)$"
)

_INERT_PATH_RULE_RE = re.compile(
    r"^(" + "|".join(_INERT_PATH_RULE_FIX) + r")\((.+)\)$"
)


def _check_permissions_block(rel, permissions, findings):
    if not permissions:
        return
    if not isinstance(permissions, dict):
        add(findings, "E", str(rel), "'permissions' must be an object")
        return
    if permissions.get("defaultMode") == "auto":
        add(
            findings, "W", f"{rel}#permissions.defaultMode",
            "'defaultMode: \"auto\"' is ignored in a project settings file -- the session starts "
            "in 'default' with no error, so this harness reads as configured and "
            "behaves as if it weren't; a repository cannot grant itself auto mode -- "
            "only the user's own ~/.claude/settings.json or managed settings can "
            "(see references/hooks.md)",
        )
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
            anchored = _SINGLE_SLASH_PATH_RULE_RE.match(rule)
            if anchored:
                add(
                    findings, "W", f"{rel}#permissions.{bucket}",
                    f"'{rule}' starts with a single '/' but names a filesystem-root directory -- a single "
                    f"'/' anchors at the settings file's own root (the primary working directory, for a project "
                    f"settings file), so this matches '<project>{anchored.group(2)}'. For the filesystem root "
                    f"write '{anchored.group(1)}(/{anchored.group(2)})'; '~/' is the home directory",
                    code="V03",
                )
            inert = _INERT_PATH_RULE_RE.match(rule)
            if inert:
                add(
                    findings, "E", f"{rel}#permissions.{bucket}",
                    f"'{rule}' is parsed and then never consulted -- file "
                    f"permission checks read Edit(path) and Read(path) rules "
                    f"only, so this protects nothing. Write "
                    f"{_INERT_PATH_RULE_FIX[inert.group(1)]}({inert.group(2)}) "
                    f"instead (see references/hooks.md)",
                )
            if bucket == "allow" and _BROAD_ALLOW_RE.match(rule):
                message = (
                    f"'{rule}' is a broad allow rule that gets dropped when the "
                    "session enters auto mode -- it has no durable value; prefer "
                    "narrow rules (see references/hooks.md)"
                )
                boundary = _UNBOUNDED_PREFIX_RE.match(rule)
                if boundary:
                    tool, prefix = boundary.groups()
                    message += (
                        f". A space before the trailing '*' also restores the word "
                        f"boundary: '{tool}({prefix} *)' matches '{prefix}' and its "
                        f"arguments, where '{rule}' also matches any command merely "
                        f"starting with those characters"
                    )
                add(findings, "W", f"{rel}#permissions.allow", message)


def _check_skill_frontmatter_hooks(root, skill_dir, loc, fm, findings):
    """A skill's frontmatter declares hooks with the same event/matcher/handler
    shape settings.json uses, so it gets the same checks. The one thing that
    differs is where a relative command path resolves: against this
    directory, not the project root."""
    raw = fm.raw_blocks.get("hooks")
    if not raw:
        return
    hooks, error = _read_block(raw)
    if error:
        add(
            findings, "W", f"{loc}#hooks",
            f"frontmatter 'hooks:' block could not be read ({error}) -- it is "
            "therefore unchecked, not confirmed correct",
        )
        return
    _check_hooks_block(root, f"{loc}", hooks, findings, base_dir=skill_dir, once_honored=True)


def check_skills(root, findings):
    total_description_chars = 0
    packaged = packaged_skill_dirs(root)
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
            _check_skill_frontmatter_hooks(root, skill_dir, loc, fm, findings)

        body_lines = fm.body.splitlines() if fm.ok else text.splitlines()
        if len(body_lines) > MAX_SKILL_BODY_LINES:
            add(
                findings, "W", loc,
                f"SKILL.md body is {len(body_lines)} lines, over the "
                f"{MAX_SKILL_BODY_LINES}-line guideline -- the body stays in "
                "context for the rest of the session once the skill triggers, "
                "so every line past what each run needs is a recurring cost; "
                "move per-path material into references/",
            )

        _check_dead_links(skill_dir, loc, text, findings)
        if skill_dir in packaged:
            _check_package_closure(root, skill_dir, loc, text, findings)

        # Reference-to-reference pointers are as load-bearing as the ones in
        # SKILL.md. There are only a handful of files, so this is cheap.
        refs_dir = skill_dir / "references"
        if refs_dir.is_dir():
            for ref in sorted(p for p in refs_dir.rglob("*") if p.suffix in (".md", ".txt", ".rst")):
                ref_text = hc.read_text(ref)
                ref_loc = str(ref.relative_to(root))
                _check_dead_links(skill_dir, ref_loc, ref_text, findings)
                if skill_dir in packaged:
                    _check_package_closure(root, skill_dir, ref_loc, ref_text, findings)

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


def packaged_skill_dirs(root):
    """Skill directories a plugin manifest ships as part of its package.

    Only these are held to package closure. A plain project skill lives in
    the repository it points into, so `docs/design/notes.md` there resolves
    for everyone who has the repo; the same line inside a plugin resolves
    only for whoever wrote it."""
    manifest = root / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        return set()
    data, err = hc.load_json_lenient(manifest)
    if err or not isinstance(data, dict):
        return set()
    field = data.get("skills")
    entries = [field] if isinstance(field, str) else field if isinstance(field, list) else []

    roots = []
    for entry in entries:
        if isinstance(entry, str) and not Path(entry).is_absolute():
            roots.append((root / entry).resolve())

    packaged = set()
    for skill_dir in hc.iter_skill_dirs(root):
        resolved = skill_dir.resolve()
        for base in roots:
            if resolved == base or base in resolved.parents:
                packaged.add(skill_dir)
                break
    return packaged


def _check_package_closure(root, skill_dir, loc, text, findings):
    """Every document a packaged skill sends its reader to must ship with it.

    The test is resolution, not shape: the path has to resolve *here* and
    not inside the package. That is what separates a broken pointer from
    the target-project paths a harness-building skill names constantly --
    `dist/index.md` or `docs/notes.md` in a sentence about the reader's own
    repo describes a file that was never supposed to be in this one."""
    for m in _DOC_PATH_RE.finditer(text):
        path = m.group(1)
        parts = path.split("/")
        if "*" in path or parts[-1] in _HARNESS_NAMESPACE or parts[0] == ".claude":
            continue
        if (skill_dir / path).exists() or not (root / path).exists():
            continue
        add(
            findings, "W", loc,
            f"names {path}, which resolves in this repo but is not in the skill "
            "package -- a plugin installs as its own directory, so if this is a "
            "pointer the reader is meant to follow, it is already broken for "
            "everyone who installs it. Move what they need into references/, or "
            "cite a public source. If instead it describes a file in the project "
            "the skill is *run against*, it is correct and this repo just happens "
            "to have the same path; nothing here can tell those apart, which is "
            "why this warns rather than fails",
        )


def iter_skill_pointers(text):
    """Every pointer into a skill's own bundled references/ or scripts/.

    Deliberately wrapper-agnostic: a pointer is just as dead when it is
    written as bare prose ("see references/hooks.md"), as a markdown link,
    or inside a ${CLAUDE_SKILL_DIR} invocation as it is inside backticks."""
    for m in re.finditer(_SKILL_POINTER_RE, text):
        # A `./`- or `/`-anchored path belongs to the target project, not to
        # this skill -- hook commands in the examples are exactly that shape.
        if m.group("prefix") in ("./", "/"):
            continue
        # Prose ends in a period and filenames contain them, so the two run
        # together: `scripts/tool.py.` is one pointer and one full stop.
        name = m.group("name").rstrip(".")
        # A glob is a pattern, not a pointer; `...` is an ellipsis, not a file.
        if "*" in name or not name:
            continue
        yield f"{m.group('subdir')}/{name}"


def _check_dead_links(skill_dir, loc, text, findings):
    """Every pointer to a bundled reference or script must resolve."""
    for pointer in iter_skill_pointers(text):
        if not (skill_dir / pointer).exists():
            add(findings, "E", loc, f"references a file that does not exist: {pointer}")


def check_skill_scripts(root, findings):
    """A bundled script's CLI is an interface only if it describes itself.

    argparse hands every script a --help for free; what it cannot supply is
    what each argument means. That gap is invisible from the outside -- the
    script runs, the flag works, and only a model trying to call it pays the
    cost (see references/skills.md)."""
    packaged = packaged_skill_dirs(root)
    for skill_dir in hc.iter_skill_dirs(root):
        for path in sorted(skill_dir.glob("scripts/**/*.py")):
            loc = str(path.relative_to(root))
            _check_cli_self_description(path, loc, findings)
            if skill_dir in packaged:
                _check_package_closure(root, skill_dir, loc, hc.read_text(path), findings)


def _arg_label(node):
    """The flag or positional name an add_argument call declares."""
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return repr(arg.value)
    return "an argument"


def _is_parser_construction(node):
    """`argparse.ArgumentParser(...)` in either import style."""
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr == "ArgumentParser"
    return isinstance(func, ast.Name) and func.id == "ArgumentParser"


def _keyword(node, name):
    """The `name=` argument of a call, as an AST node, or None if absent."""
    for kw in node.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _action_value(node):
    """The literal `action=` of an add_argument call, if it is a plain string."""
    action = _keyword(node, "action")
    return action.value if isinstance(action, ast.Constant) else None


def _is_module_doc(value):
    return isinstance(value, ast.Name) and value.id == "__doc__"


def _check_cli_self_description(path, loc, findings):
    try:
        tree = ast.parse(hc.read_text(path))
    except SyntaxError as exc:
        # Swallowing this would let a script that cannot run at all pass as a
        # working interface, and one bad file would otherwise abort the lint
        # and hide every other finding.
        add(
            findings, "E", loc,
            f"Python syntax error on line {exc.lineno} -- the script cannot run, "
            "so neither its --help nor the command it backs will work",
        )
        return
    has_docstring = ast.get_docstring(tree) is not None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _is_parser_construction(node):
            description = _keyword(node, "description")
            if description is None:
                add(
                    findings, "W", loc,
                    "the parser has no description= -- --help opens with the usage "
                    "line alone, so what the script is for isn't knowable without "
                    "reading it",
                )
            elif _is_module_doc(description) and not has_docstring:
                add(
                    findings, "W", loc,
                    "the parser passes description=__doc__ but this module has no "
                    "docstring, so the description resolves to None and --help reads "
                    "exactly as if it had been left out",
                )
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr == "add_parser":
            if not any(kw.arg == "help" for kw in node.keywords):
                add(
                    findings, "E", loc,
                    f"subcommand {_arg_label(node)} has no help= -- it still appears "
                    "in the parent's {choices} list, but with no line explaining what "
                    "it does, so choosing between subcommands means reading the source",
                )
            continue
        if node.func.attr != "add_argument":
            continue
        if any(kw.arg == "help" for kw in node.keywords):
            continue
        # argparse's own _VersionAction/_HelpAction ship a default help string,
        # so these two read correctly in --help with no help= of their own.
        if _action_value(node) in ("version", "help"):
            continue
        add(
            findings, "E", loc,
            f"{_arg_label(node)} has no help= -- --help prints the flag name and "
            "nothing else, so the model has to open this script's source to learn "
            "what the argument takes",
        )


# Tools tied to the main conversation's UI or session state; a subagent
# cannot use them even when its `tools` field lists them.
_UI_BOUND_TOOLS = frozenset({"AskUserQuestion", "EnterPlanMode", "ScheduleWakeup", "WaitForMcpServers"})


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
        if model and not is_plausible_model(model):
            add(
                findings, "W", loc,
                f"unrecognized 'model' value '{model}' -- not one of "
                f"{'/'.join(MODEL_ALIASES)} and not a 'claude-' prefixed id",
            )

        tools = fm.data.get("tools")
        tool_list = None
        if isinstance(tools, list):
            tool_list = [str(t).strip() for t in tools]
        elif isinstance(tools, str):
            tool_list = [t.strip() for t in tools.split(",") if t.strip()]
        for t in tool_list or []:
            if not hc.is_known_tool_token(t):
                add(findings, "E", loc, f"'tools' references unknown tool '{t}'")
            elif t in _UI_BOUND_TOOLS:
                add(
                    findings, "E", loc,
                    f"'tools' lists {t}, which depends on the main conversation's UI or session state and is "
                    "not available to a subagent even when listed -- an agent whose job needs it has to stay in "
                    "the main conversation or work from a brief handed to it up front",
                    code="V06",
                )
        if fm.data.get("memory") and tool_list is not None:
            missing = [t for t in ("Read", "Write", "Edit") if t not in tool_list]
            if missing:
                add(
                    findings, "W", loc,
                    f"'memory: {fm.data.get('memory')}' automatically enables Read, Write and Edit so the agent "
                    f"can manage its memory files, while 'tools' withholds {', '.join(missing)} -- the docs do "
                    "not say which wins, so an agent that must not have those tools should leave memory unset",
                    code="V08",
                )
        raw_hooks = fm.raw_blocks.get("hooks")
        if raw_hooks:
            hooks, error = _read_block(raw_hooks)
            if error:
                add(findings, "W", f"{loc}#hooks",
                    f"frontmatter 'hooks:' block could not be read ({error}) -- it is therefore unchecked, not confirmed correct")
            else:
                _check_hooks_block(root, loc, hooks, findings, base_dir=agent_file.parent)


# A meta value that is not a literal: an identifier (not true/false/null), a
# call, or a template string. Object/array values are fine.
_META_NON_LITERAL_RE = re.compile(
    r":\s*(?!true\b|false\b|null\b)[A-Za-z_$][\w$]*\s*(?:[,}\n.\[]|\()|:\s*`"
)
# Matched against the source with string literals and comments blanked, so a
# prompt that *mentions* `import fs` is not a hit. Module specifiers survive
# the blanking as their quotes, hence the `["']["']` shapes below.
_WORKFLOW_IO_RE = re.compile(
    r"\brequire\(\s*\bMOD_(?:fs|fs_promises|child_process)\b\s*\)"
    r"|\bfrom\s+MOD_(?:fs|fs_promises|child_process)\b"
    r"|\bimport\(\s*MOD_(?:fs|fs_promises|child_process)\b\s*\)"
    r"|\b(?:execSync|spawnSync|execFileSync)\s*\("
)
_JS_MODULE_SPECIFIER_RE = re.compile(r"""(['"])(?:node:)?(fs/promises|fs|child_process)\1""")


def _strip_js_strings_and_comments(source):
    """Blank string literals, template strings and comments, keeping the
    module specifiers the IO check needs as `MOD_<name>` tokens. Not a
    parser: an unbalanced quote inside a regex literal can mis-blank a line,
    which errs toward silence, not toward a false finding."""
    source = _JS_MODULE_SPECIFIER_RE.sub(lambda m: "MOD_" + m.group(2).replace("/", "_"), source)
    out = []
    i, n = 0, len(source)
    while i < n:
        ch = source[i]
        if source.startswith("//", i):
            j = source.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i)); i = j
        elif source.startswith("/*", i):
            j = source.find("*/", i + 2)
            j = n if j == -1 else j + 2
            out.append(re.sub(r"[^\n]", " ", source[i:j])); i = j
        elif ch in "'\"`":
            j = i + 1
            while j < n and source[j] != ch:
                j += 2 if source[j] == "\\" else 1
            j = min(j + 1, n)
            out.append(ch + re.sub(r"[^\n]", " ", source[i + 1:j - 1]) + (ch if j - 1 < n else ""))
            i = j
        else:
            out.append(ch); i += 1
    return "".join(out)


def check_workflows(root, findings):
    for wf_file in hc.iter_workflow_files(root):
        loc = str(wf_file.relative_to(root))
        text = hc.read_text(wf_file)

        code_only = _strip_js_strings_and_comments(text)
        if not re.search(r"export\s+const\s+meta\s*=\s*\{", text):
            add(findings, "E", loc, "missing 'export const meta = {...}' literal")
        else:
            meta_match = re.search(r"export\s+const\s+meta\s*=\s*\{(.*?)\}", code_only, re.DOTALL)
            body = meta_match.group(1) if meta_match else ""
            if meta_match and not re.search(r"\bname\s*:", body):
                add(findings, "E", loc, "'meta' object is missing a 'name' field")
            problems = []
            if meta_match and not re.search(r"\bdescription\s*:", body):
                problems.append("has no 'description'")
            if meta_match and _META_NON_LITERAL_RE.search(body):
                problems.append("is not a pure literal (a value is an identifier, a call or a template string)")
            first = re.sub(r"^\s+", "", code_only)
            if not first.startswith("export const meta") and not re.match(r"export\s+const\s+meta\b", first):
                problems.append("is not the file's first statement")
            if problems:
                add(
                    findings, "E", loc,
                    "'meta' " + " and ".join(problems) + " -- the runtime reads meta from the file before "
                    "executing anything, so it must be `export const meta = { name, description }` written out "
                    "as literals",
                    code="V09",
                )

        io_hits = sorted({m.group(0) for m in _WORKFLOW_IO_RE.finditer(code_only)})
        if io_hits:
            add(
                findings, "E", loc,
                f"the script touches the filesystem or shell directly ({', '.join(io_hits)}) -- a workflow "
                "script has no filesystem or shell access; only the agents it spawns read, write and run "
                "commands, so move this into an agent() prompt",
                code="V10",
            )
        if "${CLAUDE_SKILL_DIR}" in text:
            add(
                findings, "W", loc,
                "'${CLAUDE_SKILL_DIR}' appears in the workflow source -- it is substituted in a skill's "
                "markdown and allowed-tools, and nothing documents a substitution inside a workflow, so it "
                "most likely arrives as literal text; resolve the absolute path in the composing session and "
                "pass it through args",
                code="V11",
            )

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


def _workflow_syntax_probe(source):
    """Rewrite a workflow script into a form node can syntax-check.

    Two things are legal in a workflow body and illegal in a bare module, so
    checking the file as-is reports syntax errors that aren't: a **top-level
    `return`** (the body runs inside an async function, and returning a result
    is the documented way to hand data back) and top-level `await`. Wrapping
    the body in an async function makes both legal while leaving every real
    syntax error in place. `export` is stripped because it is illegal inside a
    function -- the separate meta check is what verifies it was there."""
    stripped = re.sub(r"^export\s+", "", source, flags=re.MULTILINE)
    return "async function __workflow__() {\n" + stripped + "\n}\n"


def _check_workflow_syntax(loc, wf_file, findings):
    import subprocess
    # Plain `node --check` false-fails on ESM `export` syntax when the
    # target project's package.json declares "type": "commonjs" -- force
    # ESM parsing explicitly instead.
    try:
        result = subprocess.run(
            ["node", "--input-type=module", "--check"],
            input=_workflow_syntax_probe(hc.read_text(wf_file)),
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
        if not fm.ok and text.lstrip().startswith("---"):
            add(
                findings, "E", loc,
                "frontmatter did not parse (" + "; ".join(fm.warnings) + ") -- whether this rule is "
                "path-scoped or loads at launch cannot be read, so it is neither confirmed nor reported as unscoped",
                code="V12",
            )
            continue
        # A rule with no frontmatter at all has no 'paths' just as surely as
        # one with frontmatter but no 'paths' key -- both load at launch,
        # so both get the same warning below. Only the glob-syntax check
        # needs parsed data to run at all.
        paths = fm.data.get("paths") if fm.ok else None
        if paths is hc.UNPARSED_BLOCK or (paths is not None and not isinstance(paths, (list, str))):
            add(
                findings, "W", loc,
                "'paths:' is neither a list of globs nor a single glob string -- the documented shape is a "
                "YAML list, and a mapping or other structure is not read as a scope",
                code="V13",
            )
        elif paths is None:
            add(
                findings, "W", loc,
                "no 'paths:' frontmatter -- this rule loads at launch just like "
                "CLAUDE.md, same as if it weren't split out at all",
            )
        elif isinstance(paths, list):
            for p in paths:
                _check_glob_syntax(loc, p, findings)
                _check_catch_all_glob(loc, p, findings)
        elif isinstance(paths, str):
            _check_glob_syntax(loc, paths, findings)
            _check_catch_all_glob(loc, paths, findings)


_CATCH_ALL_GLOBS = frozenset({"**", "**/*", "*", "./**", "**/**"})


def _check_catch_all_glob(loc, pattern, findings):
    """A `paths:` that matches everything scopes nothing.

    Note the precise cost, because the obvious phrasing is wrong: unlike a
    rule with no `paths:` at all, this does NOT load at launch -- it loads on
    the first matching file read, which in practice is the first file of any
    kind. So it is slightly cheaper than an unscoped rule and entirely
    unpredictable about when it arrives, which is the worse property."""
    if not isinstance(pattern, str) or pattern.strip() not in _CATCH_ALL_GLOBS:
        return
    add(
        findings, "W", loc,
        f"paths glob '{pattern}' matches every file, so it scopes nothing. It loads on the "
        "first matching file read rather than at launch, which makes its arrival time "
        "unpredictable rather than free. Either narrow it to the paths this rule is really "
        "about, or drop the 'paths:' key and accept that it loads at launch like CLAUDE.md",
    )


# A rule loads only when Claude reads a file its `paths:` matches, so a
# pattern that doesn't parse costs nothing at launch and simply never fires.
# Nothing reports that at runtime, which is why this one is worth an error.
_GLOB_CONSEQUENCE = "a rule only loads when Claude reads a file this matches, so it will never fire"


def _check_glob_syntax(loc, pattern, findings):
    depth = 0
    for ch in pattern:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                add(findings, "E", loc, f"paths glob '{pattern}' has an unmatched '}}' -- {_GLOB_CONSEQUENCE}")
                return
    if depth != 0:
        add(findings, "E", loc, f"paths glob '{pattern}' has an unmatched '{{' -- {_GLOB_CONSEQUENCE}")


def _git_says_ignored(root, name):
    """(ignored, tracked) from git itself, or None when git is unavailable."""
    import shutil, subprocess
    if not shutil.which("git"):
        return None
    try:
        ignored = subprocess.run(["git", "-C", str(root), "check-ignore", "-q", name],
                                 capture_output=True, timeout=10).returncode == 0
        tracked = subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", name],
                                 capture_output=True, timeout=10).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return None
    return ignored, tracked


def _gitignore_covers(root, name):
    patterns = []
    for gi in (Path(root) / ".gitignore", Path(root) / ".git" / "info" / "exclude"):
        if gi.is_file():
            patterns += [l.strip() for l in hc.read_text(gi).splitlines() if l.strip() and not l.startswith("#")]
    import fnmatch
    for pat in patterns:
        if pat.startswith("!"):
            continue
        candidate = pat.lstrip("/").rstrip("/")
        if candidate == name or fnmatch.fnmatch(name, candidate):
            return True
    return False


def _check_claude_local_ignored(root, findings):
    """V14. `CLAUDE.local.md` holds one person's project preferences and the
    docs say to gitignore it; committed, it becomes everyone's instructions."""
    local = Path(root) / "CLAUDE.local.md"
    if not local.is_file():
        return
    in_repo = (Path(root) / ".git").exists()
    verdict = _git_says_ignored(root, "CLAUDE.local.md") if in_repo else None
    if verdict is not None:
        ignored, tracked = verdict
        if ignored and not tracked:
            return
        why = "is tracked by git" if tracked else "is not gitignored"
    else:
        if _gitignore_covers(root, "CLAUDE.local.md"):
            return
        why = "is not gitignored"
    add(
        findings, "E" if in_repo else "W", "CLAUDE.local.md",
        f"{why} -- it is the per-person instructions file, and committed it loads for every clone as if it "
        "were CLAUDE.md; add `CLAUDE.local.md` to .gitignore" + (" and `git rm --cached` it" if verdict and verdict[1] else "")
        + ("" if in_repo else " (no .git here, so this is advisory)"),
        code="V14",
    )


def check_claude_md(root, findings):
    _check_claude_local_ignored(root, findings)
    paths = hc.claude_md_paths(root)
    if len(paths) > 1 and {p.name for p in paths} >= {"CLAUDE.md"} and any(
        p.parent.name == ".claude" for p in paths
    ) and any(p.parent == Path(root) and p.name == "CLAUDE.md" for p in paths):
        add(
            findings, "W", "CLAUDE.md",
            "both ./CLAUDE.md and ./.claude/CLAUDE.md exist -- both load and concatenate "
            "with no override, so a reader looking at one is seeing half the instructions; "
            "pick one location unless the split is deliberate",
        )
    for path in paths:
        _check_one_claude_md(root, path, findings)


def _check_one_claude_md(root, claude_md, findings):
    loc = str(claude_md.relative_to(root))
    text = hc.read_text(claude_md)
    lines = text.splitlines()
    if len(lines) > MAX_CLAUDE_MD_LINES:
        add(
            findings, "W", loc,
            f"{len(lines)} lines, over the {MAX_CLAUDE_MD_LINES}-line guideline -- "
            "compliance tends to drop as length grows (exception: a monorepo that "
            "still overflows after splitting into rules/)",
        )

    _check_at_imports(root, claude_md, loc, text, findings)

    known_names = {d.name for d in hc.iter_skill_dirs(root)} | {
        f.stem for f in hc.iter_agent_files(root)
    }
    _check_inventory_listing(loc, lines, known_names, findings)
    _check_generic_advice(loc, text, findings)


def _check_at_imports(root, containing_file, loc, text, findings):
    """Every @import in an instruction file has to resolve, because a
    missing one expands to nothing at launch and the instruction it was
    carrying is silently absent."""
    root = Path(root).resolve()
    for target in hc.parse_at_imports(text):
        path, external = hc.resolve_import(target, containing_file)
        if external:
            # A home-directory or absolute import is machine-local by
            # design -- the docs recommend exactly this shape for sharing
            # personal notes across worktrees -- so its absence here says
            # nothing about whether the harness is correct. What is worth
            # saying once is that it triggers an approval dialog whose
            # decline is permanent and never re-offered.
            add(
                findings, "W", loc,
                f"@{target} resolves outside the project -- Claude Code shows a "
                "one-time approval dialog for external imports in a project memory "
                "file, and declining disables them permanently with no repeat "
                "prompt (imports in user-scope files skip the dialog)",
            )
            continue
        if not path.exists():
            add(findings, "E", loc, f"@{target} import target does not exist")


# Anchored to a whole sentence or bullet, never a substring. "Write clean
# code." should fire; "Be consistent with the existing handler naming
# (`handleFooRequest`)" must not, and it would under substring matching.
_GENERIC_ADVICE = (
    "write clean code",
    "write clean, maintainable code",
    "follow best practices",
    "use best practices",
    "handle errors properly",
    "handle errors appropriately",
    "write good tests",
    "write meaningful tests",
    "keep it simple",
    "follow solid principles",
    "write readable code",
    "add comments where necessary",
    "be consistent",
    "avoid technical debt",
    "write maintainable code",
    "use descriptive variable names",
    "keep functions small",
    "dont repeat yourself",
    "follow the dry principle",
)


def _normalize_advice(fragment):
    text = fragment.strip().strip("-*# ").strip()
    text = re.sub(r"`[^`]*`", "", text)          # a backticked example makes it specific
    text = re.sub(r"[^a-z\s]", "", text.lower())  # drop punctuation, keep word shape
    return " ".join(text.split())


def _check_generic_advice(loc, text, findings):
    """A line a capable model already follows spends context without changing
    behavior. Prose said so; nothing enforced it."""
    hits = []
    for line in text.splitlines():
        if line.strip().startswith(("|", ">")):
            continue
        for fragment in re.split(r"(?<=[.!?])\s+", line):
            normalized = _normalize_advice(fragment)
            if normalized in _GENERIC_ADVICE:
                hits.append(fragment.strip().strip("-*# ").strip())
    if hits:
        unique = sorted(set(hits))[:3]
        add(
            findings, "W", loc,
            "generic engineering advice a capable model already follows ("
            + "; ".join(f'"{h}"' for h in unique)
            + ") -- costs context every session without changing behavior. Replace with the "
            "project-specific version of the same idea, or cut it",
        )


def _check_deny_subsumes_allow(loc, permissions, findings):
    """A deny rule that swallows an allow rule the same harness ships. Deny is
    evaluated first and wins regardless of specificity, so the allow rule is
    dead weight that reads as an exception."""
    denies = [d for d in permissions.get("deny", []) if isinstance(d, str)]
    allows = [a for a in permissions.get("allow", []) if isinstance(a, str)]
    for deny in denies:
        deny = deny.strip()
        m = re.match(r"^([A-Za-z_]+)\((.*)\)$", deny)
        bare_tool = deny if re.fullmatch(r"[A-Za-z_]+", deny) else None
        for allow in allows:
            allow = allow.strip()
            am = re.match(r"^([A-Za-z_]+)\((.*)\)$", allow)
            if bare_tool:
                # A bare tool deny removes the tool entirely, so every scoped
                # allow for it is dead.
                covered = allow == bare_tool or (am is not None and am.group(1) == bare_tool)
            elif not m or not am or am.group(1) != m.group(1):
                continue
            elif allow == deny:
                covered = True
            elif m.group(1) in ("Read", "Edit"):
                # gitignore semantics: only `**` crosses path segments, so a
                # `*` prefix proves nothing about a deeper path.
                covered = m.group(2).endswith("**") and am.group(2).startswith(m.group(2)[:-2]) and am.group(2) != m.group(2)
            else:
                # Bash-style prefix rules: `X *` covers every `X ...`.
                covered = m.group(2).endswith("*") and am.group(2).startswith(m.group(2)[:-1]) and am.group(2) != m.group(2)
            if covered:
                add(
                    findings, "W", loc,
                    f"deny rule '{deny}' already covers allow rule '{allow}' -- deny is "
                    "evaluated first and wins regardless of specificity, so the allow rule "
                    "never fires. An exception has to be carved out of the deny pattern "
                    "itself. (Project-scope rules only; a deny in another settings scope "
                    "isn't visible here.)",
                    code="V02",
                )


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
                    "a component inventory -- the client already surfaces every component "
                    "to the session, so this list adds nothing on the day it is written "
                    "and misleads on the day someone renames one. Say when to reach for "
                    "a capability instead of naming what exists (lines with trigger "
                    "phrasing like '... use X when Y' are exempt)",
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
            add(
                findings, "W", ".claude/harness-spec.md",
                "missing -- a generated harness should carry a spec as its "
                "source of truth; without one audit_harness.py has nothing to "
                "compare against and reports no drift in either direction",
            )
        return

    text = hc.read_text(spec)
    backticked = set(re.findall(r"`([\w./\-]+)`", text))
    actual = set()
    for d in hc.iter_skill_dirs(root):
        actual.add(f".claude/skills/{d.name}/")
    for f in hc.iter_agent_files(root):
        actual.add(f".claude/agents/{f.relative_to(root / '.claude' / 'agents')}")
    for f in hc.iter_workflow_files(root):
        actual.add(f".claude/workflows/{f.name}")

    # Two distinct findings: the convention is a backticked repo-relative
    # path (the template says so), so a bare name is a nudge, not a defect,
    # and only a component absent from the spec entirely is real drift.
    _check_inventory_statuses(text, findings)
    for component in sorted(actual):
        bare = Path(component.rstrip("/")).name
        stem = Path(component.rstrip("/")).stem
        if any(component.rstrip("/") in ref for ref in backticked):
            continue
        if bare in text or stem in text or component in text:
            add(
                findings, "W", ".claude/harness-spec.md",
                f"{component} is referred to by bare name -- write it as a backticked "
                "repo-relative path so the spec reads the same way both scripts and a "
                "human resolve it",
            )
        else:
            add(
                findings, "W", ".claude/harness-spec.md",
                f"component exists on disk but isn't mentioned in the spec: {component}",
            )


def _check_inventory_statuses(spec_text, findings):
    """V01. A status outside the template's vocabulary is a row the drift
    check cannot read: `done` claims nothing and `Validated` (capitalised)
    is compared lowercase by the audit but not by anything else, so the row
    silently stops asserting that its file exists."""
    for row in hc.iter_inventory_rows(spec_text):
        if len(row) < len(hc.INVENTORY_COLUMNS):
            continue
        status = row[-1].strip().strip("`")
        if status in hc.SPEC_STATUSES or status.startswith("<"):
            continue
        add(
            findings, "E", ".claude/harness-spec.md",
            f"row {row[0]} has status '{status}', which is not one of "
            f"{'/'.join(hc.SPEC_STATUSES)} -- the drift check reads only those, so this row "
            "neither claims nor disclaims a file (status is case-sensitive; write it lowercase)",
            code="V01",
        )


# Over this, the report adds a warning. It is the documented per-file
# CLAUDE.md guideline applied to the whole always-loaded set, since that set
# is what the session actually pays for. Stated with its exception, because a
# number without one is the kind of rail this skill warns against generating.
ALWAYS_LOADED_LINE_BUDGET = 400

MAX_IMPORT_HOPS = 4


def always_loaded_report(root):
    """Measure what enters context on every session, before the first prompt.

    A measurement, not a judgement: it prints whether or not anything is
    wrong, because the number is the thing a harness author needs to see and
    almost never has. Project scope only -- see `uncounted` for why that
    matters."""
    root = Path(root)
    entries = []
    seen = set()

    def add_file(path, note, hops=0):
        try:
            resolved = path.resolve()
        except OSError:
            return
        if resolved in seen or not path.is_file():
            return
        seen.add(resolved)
        text = hc.read_text(path)
        try:
            shown = str(path.relative_to(root))
        except ValueError:
            shown = str(path)
        entries.append({
            "path": shown,
            "lines": len(text.splitlines()),
            "bytes": len(text.encode("utf-8")),
            "note": note,
        })
        if hops < MAX_IMPORT_HOPS:
            for target in hc.parse_at_imports(text):
                imported, external = hc.resolve_import(target, path)
                if not external:
                    add_file(imported, "import, expands at launch", hops + 1)

    for path in hc.claude_md_paths(root):
        add_file(path, "")

    for rule in hc.iter_rule_files(root):
        fm = hc.parse_frontmatter(hc.read_text(rule))
        if fm.ok and fm.data.get("paths"):
            continue  # loads on a matching file read, not at launch
        add_file(rule, "NO paths:, loads at launch")

    return {
        "entries": entries,
        "total_lines": sum(e["lines"] for e in entries),
        "total_bytes": sum(e["bytes"] for e in entries),
        "line_budget": ALWAYS_LOADED_LINE_BUDGET,
        "uncounted": [
            "user scope (~/.claude/CLAUDE.md, ~/.claude/rules/)",
            "CLAUDE.md files in ancestor directories above this repo",
            "auto memory (MEMORY.md, machine-local, first 200 lines or 25KB)",
            "managed-policy CLAUDE.md and any managed `claudeMd` setting",
        ],
    }


def print_always_loaded_report(report):
    print("\n== Always-loaded context, project scope ==")
    print("(enters every session before the first prompt)\n")
    if not report["entries"]:
        print("  (nothing -- no CLAUDE.md and no unscoped rules)")
    else:
        width = max(len(e["path"]) for e in report["entries"])
        width = max(width, 20)
        for e in report["entries"]:
            note = f"   {e['note']}" if e["note"] else ""
            print(f"  {e['path']:<{width}}  {e['lines']:>6,} lines  {e['bytes'] / 1024:>7.1f} KB{note}")
        print("  " + "-" * (width + 24))
        print(f"  {'TOTAL':<{width}}  {report['total_lines']:>6,} lines  {report['total_bytes'] / 1024:>7.1f} KB")
    print("\n  Not counted here: " + "; ".join(report["uncounted"]) + ".")


def run(root, strict):
    findings = []
    check_settings(root, findings)
    check_skills(root, findings)
    check_skill_scripts(root, findings)
    check_agents(root, findings)
    check_workflows(root, findings)
    check_rules(root, findings)
    check_claude_md(root, findings)
    check_harness_spec(root, findings)

    report = always_loaded_report(root)
    if report["total_lines"] > ALWAYS_LOADED_LINE_BUDGET:
        add(
            findings, "W", "always-loaded",
            f"{report['total_lines']:,} lines load on every session (CLAUDE.md + expanded "
            f"@imports + rules without paths:), over the {ALWAYS_LOADED_LINE_BUDGET}-line "
            "guideline -- adherence drops as this grows. The exception is a monorepo that "
            "still overflows after path-scoping what it can; if that's this repo, the number "
            "is the cost of the layout, not a defect",
        )

    has_error = any(f[0] == "E" for f in findings)
    has_warning = any(f[0] == "W" for f in findings)
    exit_code = hc.EXIT_LINT_FAILED if (has_error or (strict and has_warning)) else hc.EXIT_OK
    return findings, exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--path", required=True, help="path to the target repo root")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures (exit 1)")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: --path '{args.path}' is not a directory", file=sys.stderr)
        return hc.EXIT_USAGE_ERROR

    findings, exit_code = run(root, args.strict)

    if args.json:
        errors = sum(1 for f in findings if f[0] == "E")
        warnings = sum(1 for f in findings if f[0] == "W")
        print(json.dumps({
            "errors": errors, "warnings": warnings,
            "findings": hc.findings_to_json(findings),
            "always_loaded": always_loaded_report(root),
        }, indent=2))
    else:
        errors = [f for f in findings if f[0] == "E"]
        warnings = [f for f in findings if f[0] == "W"]
        hc.print_findings_text(errors, "Errors")
        hc.print_findings_text(warnings, "Warnings")
        print_always_loaded_report(always_loaded_report(root))
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")
        if exit_code == hc.EXIT_OK:
            print("PASS" + (" (strict: warnings would fail)" if warnings and not args.strict else ""))
        else:
            print("FAIL")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
