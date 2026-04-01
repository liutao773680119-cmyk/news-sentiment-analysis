from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from typing import Sequence

from news_sentiment.analysis import score_event
from news_sentiment.collectors import (
    CollectFailure,
    CollectorError,
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
    "live-smoke",
    "report",
    "run-once",
)


@dataclass(frozen=True)
class CollectResult:
    rows: list[RawNews]
    failed_sources: list[CollectFailure]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="news-sentiment")
    subparsers = parser.add_subparsers(dest="command")
    collect_parser = subparsers.add_parser("collect")
    collect_parser.add_argument("--source", default="fixture")
    subparsers.add_parser("normalize")
    subparsers.add_parser("merge-events")
    subparsers.add_parser("analyze-events")
    live_smoke_parser = subparsers.add_parser("live-smoke")
    live_smoke_parser.add_argument("--source", default="all")
    subparsers.add_parser("report")
    run_once_parser = subparsers.add_parser("run-once")
    run_once_parser.add_argument("--source", default="fixture")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = ProjectPaths.discover()

    if args.command == "collect":
        result = run_collect(paths, args.source)
        if result.failed_sources:
            print(
                f"warning: failed_sources={format_collect_failures(result.failed_sources)}",
                file=sys.stderr,
            )
        return 0
    if args.command == "normalize":
        return run_normalize(paths)
    if args.command == "merge-events":
        return run_merge_events(paths)
    if args.command == "analyze-events":
        return run_analyze_events(paths)
    if args.command == "live-smoke":
        return run_live_smoke(paths, args.source)
    if args.command == "report":
        return run_report(paths)
    if args.command == "run-once":
        run_collect(paths, args.source)
        run_normalize(paths)
        run_merge_events(paths)
        run_analyze_events(paths)
        return run_report(paths)
    return 0


def run_collect(paths: ProjectPaths, source: str) -> CollectResult:
    store = JsonlStore(paths.raw_news_path, RawNews)
    result = collect_from_source(source)
    store.write_many(result.rows)
    return result


def collect_from_source(source: str) -> CollectResult:
    if source != "all":
        return CollectResult(rows=_collect_rows(source), failed_sources=[])

    rows: list[RawNews] = []
    failed_sources: list[CollectFailure] = []
    for source_definition in load_source_definitions():
        if not source_definition.enabled:
            continue
        try:
            rows.extend(_collect_rows(source_definition.source_id))
        except CollectorError as exc:
            failed_sources.append(
                CollectFailure(
                    source=exc.source,
                    kind=exc.kind,
                    message=exc.message,
                )
            )
        except Exception as exc:
            failed_sources.append(
                CollectFailure(
                    source=source_definition.source_id,
                    kind="unexpected_error",
                    message=str(exc) or exc.__class__.__name__,
                )
            )
    return CollectResult(rows=rows, failed_sources=failed_sources)


def format_collect_failures(failures: list[CollectFailure]) -> str:
    if not failures:
        return "none"
    return ",".join(f"{failure.source}:{failure.kind}" for failure in failures)


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


def run_live_smoke(paths: ProjectPaths, source: str) -> int:
    collect_result = run_collect(paths, source)
    run_normalize(paths)
    run_merge_events(paths)
    run_analyze_events(paths)
    run_report(paths)

    raw_count = len(JsonlStore(paths.raw_news_path, RawNews).read_all())
    normalized_count = len(JsonlStore(paths.normalized_news_path, NormalizedNews).read_all())
    event_count = len(JsonlStore(paths.events_path, Event).read_all())
    analysis_count = len(JsonlStore(paths.analyses_path, EventAnalysis).read_all())
    print(
        " ".join(
            [
                f"raw_news={raw_count}",
                f"normalized_news={normalized_count}",
                f"events={event_count}",
                f"analyses={analysis_count}",
                f"failed_sources={format_collect_failures(collect_result.failed_sources)}",
                f"report={paths.latest_report_path}",
            ]
        )
    )
    return 0
