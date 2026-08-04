#!/usr/bin/env python3
"""Look up one hook event's schema instead of reading all thirty.

    hook_event.py --event PreToolUse
    hook_event.py --list

references/hooks-events.md is a lookup table: pick your event in
hooks.md's router, then read that event's row. But markdown's unit of
access is the whole file, so reading it at all costs ~3,800 words to get
the ~300 that apply. This makes the access pattern match the content.

The markdown stays the source of truth rather than moving to a queryable
store. Every fact in it is a product mechanic where being wrong is worse
than being absent, and this repo's method for keeping those right is
adversarial reading of diffs -- the cross-file audit that caught two
factually wrong router rows would not have been possible against a
binary. So: text on disk, a query in front of it.

The --event choices are generated from the file, so this script's own
signature is also the authoritative event list. That matters beyond
ergonomics: several of these events postdate common training data, and a
model that cannot see them listed will refuse to author one as
nonexistent rather than look it up.

Python 3.10+, stdlib only.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_common as hc

EVENTS_MD = Path(__file__).resolve().parent.parent / "references" / "hooks-events.md"

# A markdown table cell may contain an escaped pipe (`\|`), which is how
# this file writes alternatives like `change`\|`add`. Splitting on a bare
# pipe tears those rows apart and makes well-formed rows look ragged.
_CELL = re.compile(r"(?<!\\)\|")


def _rows(text):
    """Yield (event_name, {column: cell}) for the dense reference table."""
    header = None
    for line in text.split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in _CELL.split(line)[1:-1]]
        if header is None:
            if cells and cells[0] == "Event":
                header = cells
            continue
        if not cells or set("".join(cells)) <= set("-: "):
            continue
        if len(cells) != len(header):
            continue
        yield cells[0].strip("`"), dict(zip(header, cells))


def _sections(text):
    """Yield (event_name, section_text) for the expanded events."""
    for m in re.finditer(r"^### `?(\w+)`?.*?(?=^### |^## |\Z)", text, re.M | re.S):
        yield m.group(1), m.group(0).rstrip()


def _preamble(text):
    """The shared input fields every event carries, which the per-event
    rows deliberately omit. A single-event reader still needs them."""
    m = re.search(r"^(.*?)(?=^## )", text, re.M | re.S)
    if not m:
        return ""
    keep = [p for p in m.group(1).split("\n\n")
            if "session_id" in p or "common" in p.lower()]
    return "\n\n".join(keep).strip()


def load(path=EVENTS_MD):
    text = hc.read_text(path)
    expanded = dict(_sections(text))
    tabled = dict(_rows(text))
    return text, expanded, tabled


def event_names(path=EVENTS_MD):
    """In lifecycle order, not alphabetical.

    The file enumerates the events in the order they can fire, and that
    order is itself information -- it is how a reader sees that Setup sits
    outside normal startup, or that SessionEnd is last. The enumeration in
    the preamble is the authority; anything defined further down but not
    listed there is appended so a new event cannot go missing here."""
    try:
        text, expanded, tabled = load(path)
    except OSError:
        return []
    defined = set(expanded) | set(tabled)
    m = re.search(r"in lifecycle order:(.*?)(?:\.\s|\n\n)", text, re.S)
    ordered = [n for n in re.findall(r"`(\w+)`", m.group(1))] if m else []
    seen = set()
    names = [n for n in ordered if n in defined and not (n in seen or seen.add(n))]
    names += sorted(defined - set(names))
    return names


def render(name, text, expanded, tabled):
    if name in expanded:
        body = expanded[name]
    elif name in tabled:
        row = tabled[name]
        body = f"### `{name}`\n\n" + "\n".join(
            f"**{col}.** {val}" for col, val in row.items() if col != "Event" and val
        )
    else:
        return None
    pre = _preamble(text)
    return f"{body}\n\n---\n{pre}\n" if pre else body + "\n"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    names = event_names()
    parser.add_argument("--event", choices=names or None, metavar="EVENT",
                        help="hook event to describe; one of: " + ", ".join(names))
    parser.add_argument("--list", action="store_true",
                        help="print every event name, one per line")
    args = parser.parse_args()

    if not args.list and not args.event:
        parser.error("one of --event or --list is required")

    if args.list:
        for n in names:
            print(n)
        return hc.EXIT_OK

    text, expanded, tabled = load()
    out = render(args.event, text, expanded, tabled)
    if out is None:
        print(f"no such event: {args.event}", file=sys.stderr)
        return hc.EXIT_USAGE_ERROR
    print(out)
    return hc.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
