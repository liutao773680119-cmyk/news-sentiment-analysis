from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from io import StringIO
from urllib.error import HTTPError
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


def _parse_calendar_date(value: str) -> datetime:
    normalized = value.strip()
    for old, new in (("Sept.", "Sep."), ("Sept ", "Sep "), ("Sept,", "Sep,")):
        normalized = normalized.replace(old, new)
    for fmt in ("%b. %d, %Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue
    raise ValueError(f"unsupported EIA date: {value}")


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
    date_pattern = r"([A-Za-z]{3,9}\.?\s+\d{1,2},\s+\d{4})"
    week_match = re.search(rf"Data for week ending\s+{date_pattern}", html)
    release_match = re.search(rf"Release Date:</span>\s*<span class=\"date\">{date_pattern}", html)
    if not week_match or not release_match:
        raise CollectorParseError("eia_wpsr", "wpsr page metadata not found")

    week_ending = _parse_calendar_date(week_match.group(1)).date().isoformat()
    release_date = _parse_calendar_date(release_match.group(1)).replace(
        hour=10,
        minute=30,
        tzinfo=EASTERN_TZ,
    )
    return week_ending, release_date.replace(microsecond=0).isoformat()


def _parse_next_release_at(html: str) -> datetime | None:
    date_pattern = r"([A-Za-z]{3,9}\.?\s+\d{1,2},\s+\d{4})"
    release_match = re.search(rf"Next Release Date:</span>\s*<span class=\"date\">{date_pattern}", html)
    if not release_match:
        return None
    return _parse_calendar_date(release_match.group(1)).replace(
        hour=10,
        minute=30,
        tzinfo=EASTERN_TZ,
    )


def _is_pre_release_access_restricted(exc: Exception, page_html: str) -> bool:
    if not isinstance(exc, HTTPError) or exc.code != 403:
        return False
    next_release_at = _parse_next_release_at(page_html)
    if next_release_at is None:
        return False
    return datetime.now(EASTERN_TZ) < next_release_at


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
    except Exception as exc:
        raise CollectorFetchError("eia_wpsr", str(exc) or exc.__class__.__name__) from exc

    try:
        table1_csv = fetch_eia_wpsr_table1_csv()
    except Exception as exc:
        if _is_pre_release_access_restricted(exc, page_html):
            return []
        raise CollectorFetchError("eia_wpsr", str(exc) or exc.__class__.__name__) from exc

    if not page_html.strip() or not table1_csv.strip():
        raise CollectorEmptyResultError("eia_wpsr", "empty response body")

    rows = parse_eia_wpsr_release(page_html, table1_csv)
    if not rows:
        raise CollectorParseError("eia_wpsr", "no rows parsed from wpsr release")
    return rows
