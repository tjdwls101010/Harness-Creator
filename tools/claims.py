#!/usr/bin/env python3
"""Claim-loss audit for a rewrite: freeze what a document asserts, then check
that every frozen claim survived the rewrite or was dropped on purpose.

    claims.py extract <file>                      -> JSON claim list on stdout
    claims.py check <claims.json> <file> --dispositions <file> [--json]

`extract` finds claim candidates -- `#` headings, bold spans, pipe-delimited
table rows, and any sentence carrying a negation, a number, or a backticked
identifier; with --all-sentences, every sentence -- and gives each a stable
ID (C1, C2, ...) in document order with the exact text as its anchor. Fenced
code and HTML comments are never claims. Prune the list by hand, then save
it: the IDs are the contract the rewrite is checked against.

`check` requires every frozen ID to be accounted for: its anchor is still in
the target's visible text (whitespace and `**` ignored; fenced code and HTML
comments do not count, and N identical anchors need N occurrences), or the
dispositions file names it with a verb --

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

Python 3.10+, stdlib only.
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
_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)(?:\s+#+)?\s*$")
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
                fence = m.group(1)
                out.append("")
                continue
            out.append(line)
        else:
            out.append("")
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
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
    """Yield paragraphs as lists of (line_no, text) pieces, one piece per
    source line, with every heading, list item and table row as its own
    paragraph. Line numbers are 1-based."""
    buf = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        boundary = (
            not stripped
            or _HEADING_RE.match(line)
            or _TABLE_ROW_RE.match(line)
            or _BULLET_RE.match(line)
        )
        if boundary and buf:
            yield buf
            buf = []
        if not stripped:
            continue
        if _HEADING_RE.match(line) or _TABLE_ROW_RE.match(line):
            yield [(i, stripped)]
            continue
        buf.append((i, stripped))
    if buf:
        yield buf


def _sentences_with_lines(pieces):
    """Split a paragraph into sentences, each tagged with the source line it
    starts on."""
    text = " ".join(t for _, t in pieces)
    starts = []
    offset = 0
    for line_no, piece in pieces:
        starts.append((offset, line_no))
        offset += len(piece) + 1
    pos = 0
    for sentence in _SENTENCE_SPLIT_RE.split(text):
        idx = text.find(sentence, pos)
        pos = idx + len(sentence)
        line_no = next(l for o, l in reversed(starts) if o <= idx)
        yield line_no, sentence.strip()


def extract(text, all_sentences=False):
    """Return the claim list for a markdown document."""
    lines = _strip_comments_and_fences(text)
    claims = []

    def add(kind, anchor, line):
        anchor = anchor.strip()
        if anchor:
            claims.append({"id": f"C{len(claims) + 1}", "kind": kind, "anchor": anchor, "line": line})

    for pieces in _paragraphs(lines):
        line_no, para = pieces[0]
        heading = _HEADING_RE.match(para)
        if len(pieces) == 1 and heading:
            add("heading", heading.group(2), line_no)
            continue
        if len(pieces) == 1 and _TABLE_ROW_RE.match(para):
            if not _is_separator_row(para):
                add("table-row", para, line_no)
            continue
        pieces = [(pieces[0][0], _BULLET_RE.sub("", pieces[0][1], count=1))] + pieces[1:]
        for line_no, sentence in _sentences_with_lines(pieces):
            if not sentence:
                continue
            bold = _BOLD_RE.fullmatch(sentence)
            if bold:
                add("bold", bold.group(1), line_no)
                continue
            for m in _BOLD_RE.finditer(sentence):
                add("bold", m.group(1), line_no)
            if all_sentences or _sentence_is_claim(sentence):
                add("sentence", sentence, line_no)
    return claims


def normalize(text):
    """Whitespace-insensitive, bold-marker-insensitive form used for matching."""
    return " ".join(text.replace("**", "").split())


def visible_text(text):
    """The target as a reader sees it: fenced code and HTML comments removed,
    so a claim that survives only inside a code block or a comment is a loss."""
    return "\n".join(_strip_comments_and_fences(text))


def anchor_count(anchor, text):
    return normalize(visible_text(text)).count(normalize(anchor))


def anchor_present(anchor, text):
    return anchor_count(anchor, text) > 0


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

    # N frozen IDs sharing one anchor need N occurrences in the target, or
    # one surviving copy would vouch for every deleted context.
    needed = {}
    for claim in claims:
        if dispositions.get(claim["id"], ("", ""))[0] in ("", "KEEP"):
            key = normalize(claim["anchor"])
            needed[key] = needed.get(key, 0) + 1
    available = {key: anchor_count(key, target_text) for key in needed}

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
            key = normalize(anchor)
            if available.get(key, 0) > 0:
                available[key] -= 1
                verdicts[cid] = "SURVIVED"
            else:
                verdicts[cid] = "MISSING"
                short = "fewer copies than frozen IDs" if needed.get(key, 0) > 1 else "not in the target"
                failures.append(
                    f"{cid} (line {claim['line']}): anchor {short} and no disposition -- "
                    f"{anchor[:80]!r}"
                )
    return verdicts, failures


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}")


def _load_claims(path):
    try:
        claims = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON: {exc}")
    if not isinstance(claims, list) or not all(
        isinstance(c, dict) and isinstance(c.get("id"), str) and isinstance(c.get("anchor"), str)
        for c in claims
    ):
        raise SystemExit(f"error: {path} is not a claim list (a JSON array of objects with 'id' and 'anchor')")
    ids = [c["id"] for c in claims]
    if len(set(ids)) != len(ids):
        raise SystemExit(f"error: {path} has duplicate IDs")
    for c in claims:
        c.setdefault("line", 0)
    return claims


def cmd_extract(args):
    print(json.dumps(extract(_read(args.file), all_sentences=args.all_sentences), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_check(args):
    claims = _load_claims(args.claims)
    target_text = _read(args.file)
    dispositions, errors = parse_dispositions(_read(args.dispositions))
    verdicts, failures = check(claims, target_text, dispositions, Path(args.dispositions).resolve().parent)
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

    p_extract = sub.add_parser(
        "extract", help="list a document's claim candidates as JSON with stable IDs",
        description="Print a JSON array of {id, kind, anchor, line} in document order. kind is one of "
                    "heading, bold, table-row, sentence. Prune by hand, then save the file for `check`.",
    )
    p_extract.add_argument("file", help="markdown document to extract claims from")
    p_extract.add_argument("--all-sentences", action="store_true",
                           help="take every sentence as a candidate, not only those with a negation, number or backtick; use for a full rewrite, then prune")
    p_extract.set_defaults(func=cmd_extract)

    p_check = sub.add_parser(
        "check", help="verify every frozen claim ID survived the rewrite or has a disposition",
        description="Exit 0 when every ID in the claim list is accounted for, 1 otherwise, 2 on unreadable input. "
                    "Disposition lines: '<ID> DROP <reason>', '<ID> REWORDED <new anchor in the target>', "
                    "'<ID> MOVED <path> :: <anchor in that file>', '<ID> TOOL <script or check that now carries it>', "
                    "'<ID> KEEP'. An ID with no line must have its anchor in the target's visible text.",
    )
    p_check.add_argument("claims", help="the JSON list `extract` printed before the rewrite")
    p_check.add_argument("file", help="the rewritten document")
    p_check.add_argument("--dispositions", required=True, help="text file of '<ID> <VERB> [rest]' lines; relative MOVED paths resolve against its directory")
    p_check.add_argument("--json", action="store_true", help="machine-readable output: per-ID verdicts and the failure list")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    try:
        return args.func(args)
    except SystemExit as exc:
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
            return EXIT_USAGE
        raise


if __name__ == "__main__":
    sys.exit(main())
