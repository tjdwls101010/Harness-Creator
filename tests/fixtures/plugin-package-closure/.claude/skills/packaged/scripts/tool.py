#!/usr/bin/env python3
"""Fixture CLI whose module docstring leaks a path into --help.

    python tool.py --target <path>

Conventions come from docs/design/notes.md.
"""

import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", help="path to operate on")
    return parser.parse_args()


if __name__ == "__main__":
    main()
