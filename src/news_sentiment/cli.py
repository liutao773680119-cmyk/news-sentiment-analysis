from __future__ import annotations

import argparse
from typing import Sequence


COMMANDS = (
    "collect",
    "normalize",
    "merge-events",
    "analyze-events",
    "report",
    "run-once",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="news-sentiment")
    subparsers = parser.add_subparsers(dest="command")
    for command in COMMANDS:
        subparsers.add_parser(command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0
