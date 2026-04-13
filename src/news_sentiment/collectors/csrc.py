from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urljoin

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


CSRC_NEWS_URL = "https://www.csrc.gov.cn/"
CSRC_BASE_URL = "https://www.csrc.gov.cn"


def fetch_csrc_news_html(url: str = CSRC_NEWS_URL) -> str:
    source_definition = load_source_definition_map()["csrc"]
    return fetch_html(
        url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def parse_csrc_news_list(html: str) -> list[RawNews]:
    year_match = re.search(r"页面生成时间\s*(\d{4})-\d{2}-\d{2}", html)
    page_year = int(year_match.group(1)) if year_match else datetime.now().year
    section_match = re.search(
        r"<li class=\"xwfb\">.*?<div class=\"tab-content\">\s*<div class=\"tab-list\" style=\"display: block;\">(?P<section>.*?)</div>\s*<div class=\"tab-list\">",
        html,
        re.S,
    )
    if not section_match:
        return []

    section = section_match.group("section")
    pattern = re.compile(
        r"<a href=\"(?P<href>[^\"]+)\"[^>]*>\s*(?P<title>.*?)\s*</a>.*?<span class=\"time(?:_first)?\">\s*(?P<date>\d{4}-\d{2}-\d{2}|\d{2}-\d{2})\s*</span>",
        re.S,
    )
    captured_at = datetime.now(timezone.utc).isoformat()
    rows: list[RawNews] = []
    seen_urls: set[str] = set()
    for match in pattern.finditer(section):
        title = re.sub(r"\s+", " ", unescape(match.group("title"))).strip()
        href = urljoin(CSRC_BASE_URL, match.group("href").strip())
        raw_date = match.group("date")
        published_date = raw_date if len(raw_date) == 10 else f"{page_year}-{raw_date}"
        if href in seen_urls:
            continue
        seen_urls.add(href)
        rows.append(
            RawNews(
                news_id=f"csrc-{published_date}-{len(rows) + 1}",
                source="csrc",
                source_type="policy",
                published_at=f"{published_date}T00:00:00+08:00",
                captured_at=captured_at,
                title=title,
                content=title,
                url=href,
            )
        )
    return rows


def collect_csrc_news() -> list[RawNews]:
    try:
        html = fetch_csrc_news_html()
    except Exception as exc:
        raise CollectorFetchError("csrc", str(exc) or exc.__class__.__name__) from exc

    if not html.strip():
        raise CollectorEmptyResultError("csrc", "empty response body")

    rows = parse_csrc_news_list(html)
    if not rows:
        raise CollectorParseError("csrc", "no news rows matched html")
    return rows
