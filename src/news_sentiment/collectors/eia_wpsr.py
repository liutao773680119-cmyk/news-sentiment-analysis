from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from io import StringIO
from zoneinfo import ZoneInfo

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


EIA_WPSR_PAGE_URL = "https://www.eia.gov/petroleum/supply/weekly/index.php"
EIA_WPSR_TABLE1_URL = "https://ir.eia.gov/wpsr/table1.csv"
EASTERN_TZ = ZoneInfo("America/New_York")


def fetch_eia_wpsr_page(url: str | None = None) -> str:
    source_definition = load_source_definition_map()["eia_wpsr"]
    return fetch_html(
        url or EIA_WPSR_PAGE_URL,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def fetch_eia_wpsr_table1_csv(url: str | None = None) -> str:
    source_definition = load_source_definition_map()["eia_wpsr"]
    return fetch_html(
        url or EIA_WPSR_TABLE1_URL,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def _parse_page_metadata(html: str) -> tuple[str, str]:
    week_match = re.search(r"Data for week ending\s+([A-Za-z]{3}\.\s+\d{1,2},\s+\d{4})", html)
    release_match = re.search(r"Release Date:</span>\s*<span class=\"date\">([A-Za-z]{3}\.\s+\d{1,2},\s+\d{4})", html)
    if not week_match or not release_match:
        raise CollectorParseError("eia_wpsr", "wpsr page metadata not found")

    week_ending = datetime.strptime(week_match.group(1), "%b. %d, %Y").date().isoformat()
    release_date = datetime.strptime(release_match.group(1), "%b. %d, %Y").replace(
        hour=10,
        minute=30,
        tzinfo=EASTERN_TZ,
    )
    return week_ending, release_date.replace(microsecond=0).isoformat()


def _parse_table1_metrics(payload: str) -> dict[str, tuple[str, str]]:
    reader = csv.reader(StringIO(payload))
    rows = list(reader)
    if len(rows) < 2:
        raise CollectorParseError("eia_wpsr", "wpsr table1 payload too short")

    metrics: dict[str, tuple[str, str]] = {}
    wanted = {
        "Commercial (Excluding SPR)": "美国商业原油库存",
        "Total Motor Gasoline": "汽油库存",
        "Distillate Fuel Oil": "馏分油库存",
    }
    for row in rows[1:]:
        if len(row) < 4:
            continue
        stub = row[0].strip()
        if stub not in wanted:
            continue
        metrics[wanted[stub]] = (row[1].strip(), row[3].strip())

    if len(metrics) != len(wanted):
        raise CollectorParseError("eia_wpsr", "wpsr table1 core metrics missing")
    return metrics


def _format_diff_phrase(metric_name: str, diff: str) -> str:
    direction = "增加"
    amount = diff
    if diff.startswith("-"):
        direction = "减少"
        amount = diff[1:]
    return f"{metric_name}{direction}{amount}百万桶"


def parse_eia_wpsr_release(page_html: str, table1_csv: str) -> list[RawNews]:
    week_ending, published_at = _parse_page_metadata(page_html)
    metrics = _parse_table1_metrics(table1_csv)
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    crude_value, crude_diff = metrics["美国商业原油库存"]
    gasoline_value, gasoline_diff = metrics["汽油库存"]
    distillate_value, distillate_diff = metrics["馏分油库存"]

    title = (
        "EIA周报 "
        f"{_format_diff_phrase('美国商业原油库存', crude_diff)} "
        f"{_format_diff_phrase('汽油库存', gasoline_diff)} "
        f"{_format_diff_phrase('馏分油库存', distillate_diff)}"
    )
    content = (
        f"数据截至 {week_ending}；报告日期 {published_at[:10]}。"
        f"美国商业原油库存 {crude_value} 百万桶，较前周 {crude_diff}；"
        f"汽油库存 {gasoline_value} 百万桶，较前周 {gasoline_diff}；"
        f"馏分油库存 {distillate_value} 百万桶，较前周 {distillate_diff}。"
        "来源：EIA Weekly Petroleum Status Report"
    )
    return [
        RawNews(
            news_id=f"eia_wpsr-{published_at[:10].replace('-', '')}",
            source="eia_wpsr",
            source_type="fast_news",
            published_at=published_at,
            captured_at=captured_at,
            title=title,
            content=content,
            url=EIA_WPSR_PAGE_URL,
        )
    ]


def collect_eia_wpsr_news() -> list[RawNews]:
    try:
        page_html = fetch_eia_wpsr_page()
        table1_csv = fetch_eia_wpsr_table1_csv()
    except Exception as exc:
        raise CollectorFetchError("eia_wpsr", str(exc) or exc.__class__.__name__) from exc

    if not page_html.strip() or not table1_csv.strip():
        raise CollectorEmptyResultError("eia_wpsr", "empty response body")

    rows = parse_eia_wpsr_release(page_html, table1_csv)
    if not rows:
        raise CollectorParseError("eia_wpsr", "no rows parsed from wpsr release")
    return rows
