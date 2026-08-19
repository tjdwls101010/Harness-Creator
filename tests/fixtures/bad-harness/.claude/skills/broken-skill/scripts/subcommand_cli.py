#!/usr/bin/env python3
"""Subcommand CLI whose subparsers carry no help."""

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")
    run = subparsers.add_parser("run")
    run.add_argument("--target", help="name of the target")
    args = parser.parse_args()
    print(args.command)
