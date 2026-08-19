#!/usr/bin/env python3
"""Run the example task against one target.

    python3 run.py --target <name>
"""

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="name of the target to run against")
    args = parser.parse_args()
    print(f"running example task against {args.target}")
