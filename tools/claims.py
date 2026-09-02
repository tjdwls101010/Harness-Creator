#!/usr/bin/env python3
"""Claim-loss audit for a rewrite: freeze what a document asserts, then check
that every frozen claim survived the rewrite or was dropped on purpose.

    claims.py extract <file>                      -> JSON claim list on stdout
    claims.py check <claims.json> <file> --dispositions <file> [--json]

`extract` finds claim candidates -- headings, bold spans, table rows, and
any sentence carrying a negation, a number, or a backticked identifier --
and gives each a stable ID (C1, C2, ...) in document order with the exact
text as its anchor. Save that output before rewriting: the IDs are the
contract the rewrite is checked against.

`check` requires every frozen ID to be accounted for: its anchor is still in
the target file (whitespace and bold markers ignored), or the dispositions
file names it with a verb --

    C3 DROP <reason>                  deliberately removed; a reason is required
    C7 REWORDED <new anchor>          the new wording, which must be in the target
    C8 MOVED <path> :: <anchor>       lives in another file now, checked there
    C9 TOOL <where>                   became a script check or message; say which
    C2 KEEP                           explicit: the anchor must still be present

Exit 1 if any ID is unaccounted for, a DROP has no reason, or a disposition
names an ID that is not in the claim list.

What this cannot see: a paraphrase that keeps the words and loses the point,
a claim that lost part of itself while its anchor survived, and a claim the
extractor never found because it carried none of the markers above. Those
are the reviewer's job. This tool is a floor under a rewrite, not a proof.

Development-only; not shipped with the skill. Python 3.10+, stdlib only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2

_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|(?<=[.!?]\*\*)\s+")
_NEGATION_RE = re.compile(
    r"\b(never|not|cannot|can't|don't|doesn't|won't|isn't|aren't|no|none|"
    r"nothing|nobody|without|only)\b",
    re.IGNORECASE,
)
_DIGIT_RE = re.compile(r"\d")
_BACKTICK_RE = re.compile(r"`[^`\n]+`")


def _strip_comments_and_fences(text):
    """Blank out fenced code and HTML comments, keeping line structure so
    line numbers still point at the source."""
    text = _HTML_COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    out = []
    fence = None
    for line in text.split("\n"):
        m = _FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[0]
                out.append("")
                continue
            out.append(line)
        else:
            out.append("")
            if m and m.group(1)[0] == fence:
                fence = None
    return out


def _is_separator_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return bool(cells) and set("".join(cells)) <= set("-: ")


def _sentence_is_claim(sentence):
    return bool(
        _NEGATION_RE.search(sentence)
        or _DIGIT_RE.search(sentence)
        or _BACKTICK_RE.search(sentence)
    )


def _paragraphs(lines):
    """Yield (start_line, text) for each paragraph, with every list item
    and table row as its own paragraph. Line numbers are 1-based."""
    buf = []
    start = None
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        boundary = (
            not stripped
            or _HEADING_RE.match(line)
            or _TABLE_ROW_RE.match(line)
            or _BULLET_RE.match(line)
        )
        if boundary and buf:
            yield start, " ".join(buf)
            buf, start = [], None
        if not stripped:
            continue
        if _HEADING_RE.match(line) or _TABLE_ROW_RE.match(line):
            yield i, stripped
            continue
        if not buf:
            start = i
        buf.append(stripped)
    if buf:
        yield start, " ".join(buf)


def extract(text):
    """Return the claim list for a markdown document."""
    lines = _strip_comments_and_fences(text)
    claims = []

    def add(kind, anchor, line):
        anchor = anchor.strip()
        if anchor:
            claims.append({"id": f"C{len(claims) + 1}", "kind": kind, "anchor": anchor, "line": line})

    for line_no, para in _paragraphs(lines):
        heading = _HEADING_RE.match(para)
        if heading:
            add("heading", heading.group(2), line_no)
            continue
        if _TABLE_ROW_RE.match(para):
            if not _is_separator_row(para):
                add("table-row", para, line_no)
            continue
        body = _BULLET_RE.sub("", para, count=1)
        for sentence in _SENTENCE_SPLIT_RE.split(body):
            sentence = sentence.strip()
            if not sentence:
                continue
            bold = _BOLD_RE.fullmatch(sentence)
            if bold:
                add("bold", bold.group(1), line_no)
                continue
            for m in _BOLD_RE.finditer(sentence):
                add("bold", m.group(1), line_no)
            if _sentence_is_claim(sentence):
                add("sentence", sentence, line_no)
    return claims


def normalize(text):
    """Whitespace-insensitive, bold-marker-insensitive form used for matching."""
    return " ".join(text.replace("**", "").split())


def anchor_present(anchor, text):
    return normalize(anchor) in normalize(text)


_VERBS = ("DROP", "REWORDED", "MOVED", "TOOL", "KEEP")


def parse_dispositions(text):
    """Return ({id: (verb, rest)}, [errors])."""
    table = {}
    errors = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 2)
        if len(parts) < 2 or parts[1] not in _VERBS:
            errors.append(f"dispositions line {n}: expected '<ID> <{'|'.join(_VERBS)}> [rest]', got {raw!r}")
            continue
        cid, verb = parts[0], parts[1]
        rest = parts[2].strip() if len(parts) == 3 else ""
        if cid in table:
            errors.append(f"dispositions line {n}: {cid} is listed twice")
            continue
        table[cid] = (verb, rest)
    return table, errors


def check(claims, target_text, dispositions, base_dir):
    """Return (verdicts, failures). verdicts maps id -> one-line verdict."""
    verdicts = {}
    failures = []
    known = {c["id"] for c in claims}
    for cid in dispositions:
        if cid not in known:
            failures.append(f"{cid}: disposition names an ID that is not in the claim list")

    for claim in claims:
        cid, anchor = claim["id"], claim["anchor"]
        verb, rest = dispositions.get(cid, ("", ""))
        if verb == "DROP":
            if not rest:
                verdicts[cid] = "DROP without a reason"
                failures.append(f"{cid}: DROP needs a reason -- a drop nobody can justify is a loss")
            else:
                verdicts[cid] = f"DROP: {rest}"
        elif verb == "TOOL":
            if not rest:
                verdicts[cid] = "TOOL without a destination"
                failures.append(f"{cid}: TOOL needs to say which script or check now carries it")
            else:
                verdicts[cid] = f"TOOL: {rest}"
        elif verb == "REWORDED":
            if rest and anchor_present(rest, target_text):
                verdicts[cid] = f"REWORDED: {rest}"
            else:
                verdicts[cid] = "REWORDED but the new anchor is not in the target"
                failures.append(f"{cid}: new wording {rest!r} not found in the target")
        elif verb == "MOVED":
            path_part, sep, new_anchor = rest.partition("::")
            path = Path(path_part.strip())
            if not path.is_absolute():
                path = base_dir / path
            new_anchor = new_anchor.strip() or anchor
            if sep and path.is_file() and anchor_present(new_anchor, path.read_text(encoding="utf-8")):
                verdicts[cid] = f"MOVED: {path_part.strip()}"
            else:
                verdicts[cid] = "MOVED but not found at the named path"
                failures.append(f"{cid}: {new_anchor!r} not found in {path_part.strip() or '(no path)'}")
        else:
            if anchor_present(anchor, target_text):
                verdicts[cid] = "SURVIVED"
            else:
                verdicts[cid] = "MISSING"
                failures.append(
                    f"{cid} (line {claim['line']}): anchor not in the target and no disposition -- "
                    f"{anchor[:80]!r}"
                )
    return verdicts, failures


def cmd_extract(args):
    path = Path(args.file)
    if not path.is_file():
        print(f"error: {args.file} is not a file", file=sys.stderr)
        return EXIT_USAGE
    print(json.dumps(extract(path.read_text(encoding="utf-8")), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_check(args):
    claims_path, target_path, disp_path = Path(args.claims), Path(args.file), Path(args.dispositions)
    for p in (claims_path, target_path, disp_path):
        if not p.is_file():
            print(f"error: {p} is not a file", file=sys.stderr)
            return EXIT_USAGE
    claims = json.loads(claims_path.read_text(encoding="utf-8"))
    dispositions, errors = parse_dispositions(disp_path.read_text(encoding="utf-8"))
    verdicts, failures = check(
        claims, target_path.read_text(encoding="utf-8"), dispositions, disp_path.resolve().parent
    )
    failures = errors + failures
    if args.json:
        print(json.dumps({"claims": verdicts, "failures": failures, "ok": not failures}, indent=2, ensure_ascii=False))
    else:
        for cid in (c["id"] for c in claims):
            print(f"{cid:>5}  {verdicts.get(cid, '?')}")
        print()
        if failures:
            print(f"FAIL -- {len(failures)} unaccounted for:")
            for f in failures:
                print(f"  - {f}")
        else:
            print(f"PASS -- every one of {len(claims)} frozen IDs is accounted for")
    return EXIT_FAILED if failures else EXIT_OK


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_extract = sub.add_parser("extract", help="list a document's claim candidates as JSON with stable IDs")
    p_extract.add_argument("file", help="markdown document to extract claims from")
    p_extract.set_defaults(func=cmd_extract)

    p_check = sub.add_parser("check", help="verify every frozen claim ID survived the rewrite or has a disposition")
    p_check.add_argument("claims", help="the JSON list `extract` printed before the rewrite")
    p_check.add_argument("file", help="the rewritten document")
    p_check.add_argument("--dispositions", required=True, help="text file of '<ID> <VERB> [rest]' lines; relative MOVED paths resolve against its directory")
    p_check.add_argument("--json", action="store_true", help="machine-readable output: per-ID verdicts and the failure list")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
