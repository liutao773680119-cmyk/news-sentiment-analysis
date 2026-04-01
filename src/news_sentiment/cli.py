from __future__ import annotations

import argparse
from typing import Sequence

from news_sentiment.collectors import collect_fixture_news
from news_sentiment.models import NormalizedNews, RawNews
from news_sentiment.normalize import normalize_news_items
from news_sentiment.settings import ProjectPaths
from news_sentiment.storage import JsonlStore


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
    collect_parser = subparsers.add_parser("collect")
    collect_parser.add_argument("--source", default="fixture")
    subparsers.add_parser("normalize")
    subparsers.add_parser("merge-events")
    subparsers.add_parser("analyze-events")
    subparsers.add_parser("report")
    run_once_parser = subparsers.add_parser("run-once")
    run_once_parser.add_argument("--source", default="fixture")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = ProjectPaths.discover()

    if args.command == "collect":
        return run_collect(paths, args.source)
    if args.command == "normalize":
        return run_normalize(paths)
    if args.command == "run-once":
        run_collect(paths, args.source)
        return run_normalize(paths)
    return 0


def run_collect(paths: ProjectPaths, source: str) -> int:
    if source != "fixture":
        raise ValueError(f"Unsupported source: {source}")
    store = JsonlStore(paths.raw_news_path, RawNews)
    store.write_many(collect_fixture_news())
    return 0


def run_normalize(paths: ProjectPaths) -> int:
    raw_store = JsonlStore(paths.raw_news_path, RawNews)
    normalized_store = JsonlStore(paths.normalized_news_path, NormalizedNews)
    normalized_store.write_many(normalize_news_items(raw_store.read_all()))
    return 0
