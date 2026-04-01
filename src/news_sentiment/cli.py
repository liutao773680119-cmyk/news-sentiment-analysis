from __future__ import annotations

import argparse
from typing import Sequence

from news_sentiment.analysis import score_event
from news_sentiment.collectors import (
    collect_cninfo_news,
    collect_fixture_news,
    collect_miit_news,
    collect_stcn_news,
)
from news_sentiment.config_loader import load_scoring_config, load_source_definitions
from news_sentiment.event_merge import merge_news_items
from news_sentiment.models import Event, EventAnalysis, NormalizedNews, RawNews
from news_sentiment.normalize import normalize_news_items
from news_sentiment.reporting import write_text_report
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
    if args.command == "merge-events":
        return run_merge_events(paths)
    if args.command == "analyze-events":
        return run_analyze_events(paths)
    if args.command == "report":
        return run_report(paths)
    if args.command == "run-once":
        run_collect(paths, args.source)
        run_normalize(paths)
        run_merge_events(paths)
        run_analyze_events(paths)
        return run_report(paths)
    return 0


def run_collect(paths: ProjectPaths, source: str) -> int:
    store = JsonlStore(paths.raw_news_path, RawNews)
    if source == "all":
        rows = []
        for source_definition in load_source_definitions():
            if not source_definition.enabled:
                continue
            rows.extend(_collect_rows(source_definition.source_id))
    else:
        rows = _collect_rows(source)
    store.write_many(rows)
    return 0


def _collect_rows(source: str) -> list[RawNews]:
    if source == "fixture":
        return collect_fixture_news()
    if source == "cninfo":
        return collect_cninfo_news()
    if source == "miit":
        return collect_miit_news()
    if source == "stcn":
        return collect_stcn_news()
    raise ValueError(f"Unsupported source: {source}")


def run_normalize(paths: ProjectPaths) -> int:
    raw_store = JsonlStore(paths.raw_news_path, RawNews)
    normalized_store = JsonlStore(paths.normalized_news_path, NormalizedNews)
    normalized_store.write_many(normalize_news_items(raw_store.read_all()))
    return 0


def run_merge_events(paths: ProjectPaths) -> int:
    normalized_store = JsonlStore(paths.normalized_news_path, NormalizedNews)
    events_store = JsonlStore(paths.events_path, Event)
    events_store.write_many(merge_news_items(normalized_store.read_all()))
    return 0


def run_analyze_events(paths: ProjectPaths) -> int:
    events_store = JsonlStore(paths.events_path, Event)
    analyses_store = JsonlStore(paths.analyses_path, EventAnalysis)
    scoring_config = load_scoring_config()
    analyses_store.write_many(
        [score_event(event, scoring_config=scoring_config) for event in events_store.read_all()]
    )
    return 0


def run_report(paths: ProjectPaths) -> int:
    events_store = JsonlStore(paths.events_path, Event)
    analyses_store = JsonlStore(paths.analyses_path, EventAnalysis)
    write_text_report(paths, events_store.read_all(), analyses_store.read_all())
    return 0
