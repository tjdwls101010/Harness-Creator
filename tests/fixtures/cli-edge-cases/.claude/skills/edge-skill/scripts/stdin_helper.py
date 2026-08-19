#!/usr/bin/env python3
"""Reads a JSON event on stdin. Not a CLI -- no argparse, nothing to describe.

Regression pin, not a slice: this is silent because the check keys on
`.add_argument` calls, so click/typer/stdin-only scripts never reach it.
"""

import json
import sys

if __name__ == "__main__":
    print(json.load(sys.stdin).get("tool_name", ""))
