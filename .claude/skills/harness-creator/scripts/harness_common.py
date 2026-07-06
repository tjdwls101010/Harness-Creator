"""Shared helpers for harness-creator's validation/audit/test scripts.

Not a CLI itself -- imported by validate_harness.py, audit_harness.py, and
test_hook.py. A single conservative frontmatter parser and a single canonical
fact table (tool names, hook events, matcher support) live here so every
script agrees on what's valid, instead of each one re-implementing (and
silently disagreeing with) the same parsing and the same fact list. That
divergence is exactly the mistake skill-creator made (a hand-rolled parser in
utils.py that disagreed with a real-YAML expectation in validate.py) -- see
docs/plan/04-scripts-and-validation.md's common conventions.
"""

import json
import re
from pathlib import Path

EXIT_OK = 0
EXIT_LINT_FAILED = 1
EXIT_USAGE_ERROR = 2

# Verified against .tmp/docs_claude/05-reference/04-tools-reference.md via
# docs/plan/research/research-gap-report.md §2.
CANONICAL_TOOLS = frozenset({
    "Agent", "Artifact", "AskUserQuestion", "Bash", "CronCreate", "CronDelete",
    "CronList", "Edit", "EnterPlanMode", "EnterWorktree", "ExitPlanMode",
    "ExitWorktree", "Glob", "Grep", "ListMcpResourcesTool", "LSP", "Monitor",
    "NotebookEdit", "PowerShell", "PushNotification", "Read",
    "ReadMcpResourceTool", "RemoteTrigger", "ReportFindings", "ScheduleWakeup",
    "SendMessage", "SendUserFile", "ShareOnboardingGuide", "Skill",
    "TaskCreate", "TaskGet", "TaskList", "TaskOutput", "TaskStop", "TaskUpdate",
    "TodoWrite", "ToolSearch", "WaitForMcpServers", "WebFetch", "WebSearch",
    "Workflow", "Write",
})

# A tool name written in a matcher or an `mcp__server__tool` pattern is not a
# literal tool name -- don't flag these as unknown tools.
_MCP_TOOL_PREFIX = "mcp__"

# All 30 hook events, verified against references/hooks-events.md (itself
# verified against .tmp/docs_claude/05-reference/07-hooks-reference.md).
HOOK_EVENTS = frozenset({
    "SessionStart", "Setup", "InstructionsLoaded", "UserPromptSubmit",
    "UserPromptExpansion", "MessageDisplay", "PreToolUse", "PermissionRequest",
    "PermissionDenied", "PostToolUse", "PostToolUseFailure", "PostToolBatch",
    "Notification", "SubagentStart", "SubagentStop", "TaskCreated",
    "TaskCompleted", "Stop", "StopFailure", "TeammateIdle", "ConfigChange",
    "CwdChanged", "FileChanged", "WorktreeCreate", "WorktreeRemove",
    "PreCompact", "PostCompact", "Elicitation", "ElicitationResult",
    "SessionEnd",
})

# Events that do NOT support a `matcher` field at all (from
# references/hooks-events.md's per-event Matcher column). Every other event
# in HOOK_EVENTS supports some form of matcher (a tool name, a categorical
# value like "manual"/"auto", or a name pattern) -- only these ten fire
# unconditionally with no filtering axis.
NON_MATCHER_EVENTS = frozenset({
    "UserPromptSubmit", "MessageDisplay", "PostToolBatch", "TaskCreated",
    "TaskCompleted", "Stop", "TeammateIdle", "CwdChanged", "WorktreeCreate",
    "WorktreeRemove",
})

# Events where the `if` field (tool-input-based filtering) is meaningful at
# all -- it only makes sense on events that carry a tool_input to filter on.
TOOL_CONTEXT_EVENTS = frozenset({
    "PreToolUse", "PostToolUse", "PostToolUseFailure", "PermissionRequest",
    "PermissionDenied",
})

HOOK_HANDLER_TYPES = frozenset({"command", "http", "mcp_tool", "prompt", "agent"})

# Characters that keep a matcher in exact-string/list mode. Any other
# character flips it to an unanchored regex (references/hooks.md gotcha #3).
_EXACT_MATCHER_CHARS = re.compile(r"^[A-Za-z0-9_\-,\| \t]*$")


def is_exact_matcher(matcher):
    """True if `matcher` stays in exact-string/list mode; False if any
    character outside [A-Za-z0-9_-,| \\t] flips it to an unanchored regex."""
    return bool(_EXACT_MATCHER_CHARS.match(matcher))


def is_known_tool_token(token):
    """True if `token` is a canonical tool name or an mcp__ pattern -- used
    to avoid false-positive "unknown tool" warnings on MCP matchers."""
    token = token.strip()
    if token in CANONICAL_TOOLS:
        return True
    if token.startswith(_MCP_TOOL_PREFIX):
        return True
    return False


class Frontmatter:
    """Result of parsing a markdown file's YAML-ish frontmatter block.

    `data` is None when parsing was too uncertain to trust (see
    parse_frontmatter's docstring) -- callers must treat that as "could not
    verify", never as "frontmatter is empty".
    """

    def __init__(self, data, body, warnings):
        self.data = data
        self.body = body
        self.warnings = warnings

    @property
    def ok(self):
        return self.data is not None


_FRONTMATTER_FENCE = re.compile(r"^---\s*$")
_KEY_VALUE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")
_LIST_ITEM = re.compile(r"^-\s+(.*)$")


def parse_frontmatter(text):
    """Conservative frontmatter parser: stdlib has no real YAML parser, and
    a mis-parse that silently produces wrong data is worse than admitting
    defeat, so this only trusts a deliberately small subset of YAML --
    flat `key: value` pairs, `key:` followed by an indented `- item` list,
    and `key: >` / `key: |` followed by indented continuation lines folded
    or joined verbatim. Anything else (nested maps, flow-style `[..]`/`{..}`,
    anchors/aliases, multi-document markers) makes this function give up and
    return a Frontmatter with data=None plus a warning explaining why --
    never a best-effort guess that could be wrong. Callers must treat
    data=None as "could not verify this file's frontmatter", which for a
    skill kills auto-triggering silently (see references/skills.md), so a
    lint pass should warn loudly rather than pass or fail confidently on
    unparseable input.

    Returns a Frontmatter. `body` is the text after the closing `---` line
    regardless of whether the frontmatter itself parsed (a skill/agent still
    loads its body even with broken frontmatter -- only auto-triggering
    dies, which is exactly the gotcha this parser exists to help catch).
    """
    lines = text.splitlines()
    warnings = []

    if not lines or not _FRONTMATTER_FENCE.match(lines[0]):
        return Frontmatter(None, text, ["no frontmatter fence ('---') at top of file"])

    end_idx = None
    for i in range(1, len(lines)):
        if _FRONTMATTER_FENCE.match(lines[i]):
            end_idx = i
            break

    if end_idx is None:
        return Frontmatter(None, text, ["frontmatter opened with '---' but never closed"])

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:])

    data = {}
    i = 0
    n = len(fm_lines)
    while i < n:
        raw = fm_lines[i]
        if raw.strip() == "":
            i += 1
            continue
        if raw != raw.lstrip():
            # Top-level frontmatter keys should not be indented. An
            # indented top-level line means either a structure this parser
            # doesn't understand, or a continuation this loop mis-tracked --
            # either way, don't guess.
            warnings.append(
                f"line {i + 2}: unexpected indentation at top level, "
                "structure too complex for the conservative parser"
            )
            return Frontmatter(None, body, warnings)

        m = _KEY_VALUE.match(raw)
        if not m:
            warnings.append(f"line {i + 2}: expected 'key: value', got: {raw!r}")
            return Frontmatter(None, body, warnings)

        key, rest = m.group(1), m.group(2).strip()
        i += 1

        if rest in (">", "|", ">-", "|-"):
            block_lines = []
            while i < n and (fm_lines[i].strip() == "" or fm_lines[i].startswith((" ", "\t"))):
                if fm_lines[i].strip() != "":
                    block_lines.append(fm_lines[i].strip())
                i += 1
            joined = " ".join(block_lines) if rest.startswith(">") else "\n".join(block_lines)
            data[key] = joined
            continue

        if rest == "":
            # Either an indented list or an indented nested block follows.
            list_items = []
            saw_list = False
            while i < n and fm_lines[i].startswith((" ", "\t")):
                item_line = fm_lines[i].strip()
                lm = _LIST_ITEM.match(item_line)
                if lm:
                    saw_list = True
                    list_items.append(_unquote(lm.group(1)))
                    i += 1
                    continue
                # Indented but not a list item -> a nested map. Out of scope.
                warnings.append(
                    f"line {i + 2}: nested mapping under '{key}:' is not "
                    "supported by the conservative parser"
                )
                return Frontmatter(None, body, warnings)
            data[key] = list_items if saw_list else None
            continue

        if rest.startswith("[") or rest.startswith("{"):
            warnings.append(
                f"line {i + 1}: flow-style YAML ('{rest[:1]}...') under "
                f"'{key}:' is not supported by the conservative parser"
            )
            return Frontmatter(None, body, warnings)

        data[key] = _unquote(rest)

    return Frontmatter(data, body, warnings)


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def load_json_lenient(path):
    """Parse a JSON file, returning (data, error_message). error_message is
    None on success. Never raises -- callers report parse failure as a lint
    E and move on, since one broken JSON file shouldn't crash the whole
    lint run and hide every other finding."""
    try:
        return json.loads(read_text(path)), None
    except FileNotFoundError:
        return None, f"{path}: file not found"
    except json.JSONDecodeError as e:
        return None, f"{path}: JSON parse error at line {e.lineno}: {e.msg}"


def iter_skill_dirs(root):
    """Yield each `.claude/skills/<name>/` directory that exists under root."""
    skills_root = Path(root) / ".claude" / "skills"
    if not skills_root.is_dir():
        return
    for child in sorted(skills_root.iterdir()):
        if child.is_dir():
            yield child


def iter_agent_files(root):
    """Yield each `.claude/agents/*.md` file under root."""
    agents_root = Path(root) / ".claude" / "agents"
    if not agents_root.is_dir():
        return
    for child in sorted(agents_root.glob("*.md")):
        yield child


def iter_workflow_files(root):
    """Yield each `.claude/workflows/*.js` file under root."""
    workflows_root = Path(root) / ".claude" / "workflows"
    if not workflows_root.is_dir():
        return
    for child in sorted(workflows_root.glob("*.js")):
        yield child


def iter_rule_files(root):
    """Yield each `.claude/rules/*.md` file under root."""
    rules_root = Path(root) / ".claude" / "rules"
    if not rules_root.is_dir():
        return
    for child in sorted(rules_root.glob("*.md")):
        yield child


def settings_paths(root):
    """Return the settings.json paths that exist under root, in the order
    they're conventionally layered (project, then local)."""
    root = Path(root)
    candidates = [
        root / ".claude" / "settings.json",
        root / ".claude" / "settings.local.json",
    ]
    return [p for p in candidates if p.is_file()]


def print_findings_text(findings, title):
    """findings: list of (level, location, message) where level is 'E' or
    'W'. Human-readable text output -- the default, per D9's convention that
    text is the default and --json is the machine-readable opt-in."""
    print(f"== {title} ==")
    if not findings:
        print("  (no findings)")
        return
    for level, location, message in findings:
        print(f"  [{level}] {location}: {message}")


def findings_to_json(findings):
    return [{"level": level, "location": location, "message": message} for level, location, message in findings]
