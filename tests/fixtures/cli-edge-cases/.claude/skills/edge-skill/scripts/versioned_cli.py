#!/usr/bin/env python3
"""Documented CLI that also carries --version.

`action="version"` supplies its own help text from argparse's _VersionAction,
so omitting `help=` there is correct, not an oversight.
"""

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="name of the target to run against")
    parser.add_argument("--version", action="version", version="1.0")
    args = parser.parse_args()
    print(args.target)
