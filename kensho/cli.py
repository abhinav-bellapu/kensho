"""Kensho Bench CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from kensho import __version__
from kensho.runner import run_task_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kensho",
        description="Kensho Bench — evaluation harness for coding agents",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a benchmark task from YAML")
    run_parser.add_argument("task_yaml", type=Path, help="Path to task YAML file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        print(run_task_json(args.task_yaml))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
