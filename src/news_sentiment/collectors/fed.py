from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


FED_PRESS_FEED_URL = "https://www.federalreserve.gov/feeds/press_monetary.xml"


def fetch_fed_press_feed(url: str | None = None) -> str:
    source_definition = load_source_definition_map()["fed"]
    return fetch_html(
        url or FED_PRESS_FEED_URL,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def _normalize_text(value: str | None) -> str:
    return " ".join(unescape(value or "").replace("\xa0", " ").split())


def _parse_pub_date(value: str) -> datetime:
    parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def parse_fed_press_feed(payload: str) -> list[RawNews]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise CollectorParseError("fed", f"invalid rss payload: {exc}") from exc

    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows: list[RawNews] = []
    seen_urls: set[str] = set()
    for index, item in enumerate(root.findall("./channel/item"), start=1):
        title = _normalize_text(item.findtext("title"))
        link = _normalize_text(item.findtext("link"))
        description = _normalize_text(item.findtext("description"))
        category = _normalize_text(item.findtext("category"))
        pub_date = _normalize_text(item.findtext("pubDate"))
        if not title or not link or not pub_date or link in seen_urls:
            continue
        seen_urls.add(link)
        published_at = _parse_pub_date(pub_date).replace(microsecond=0).isoformat()
        content_lines = []
        if category:
            content_lines.append(f"Category: {category}")
        if description:
            content_lines.append(f"Summary: {description}")
        rows.append(
            RawNews(
                news_id=f"fed-{_parse_pub_date(pub_date).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')}-{index}",
                source="fed",
                source_type="policy",
                published_at=published_at,
                captured_at=captured_at,
                title=title,
                content="\n".join(content_lines) or title,
                url=link,
            )
        )
    return rows


def collect_fed_news() -> list[RawNews]:
    try:
        payload = fetch_fed_press_feed()
    except Exception as exc:
        raise CollectorFetchError("fed", str(exc) or exc.__class__.__name__) from exc

    if not payload.strip():
        raise CollectorEmptyResultError("fed", "empty response body")

    rows = parse_fed_press_feed(payload)
    if not rows:
        raise CollectorParseError("fed", "no feed items matched rss")
    return rows
