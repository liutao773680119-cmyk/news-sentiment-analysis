from __future__ import annotations

import ast
import json
import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urlencode, urljoin

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


MIIT_NEWS_URL = "https://www.miit.gov.cn/xwfb/gxdt/index.html"


def fetch_miit_news_html(url: str = MIIT_NEWS_URL) -> str:
    source_definition = load_source_definition_map()["miit"]
    shell_html = fetch_html(
        url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )
    build_url, params = extract_miit_build_request(shell_html)
    payload = fetch_html(
        f"{build_url}?{urlencode(params)}",
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )
    return parse_miit_build_response_html(payload)


def extract_miit_build_request(html: str) -> tuple[str, dict[str, str]]:
    match = re.search(
        r'url="(?P<url>/api-gateway/[^"]+)"[^>]+queryData="(?P<query>\{[^"]+\})"',
        html,
        re.S,
    )
    if not match:
        raise CollectorParseError("miit", "miit build-unit request metadata not found")

    build_url = urljoin(MIIT_NEWS_URL, match.group("url"))
    params = ast.literal_eval(match.group("query"))
    return build_url, {str(key): str(value) for key, value in params.items()}


def parse_miit_build_response_html(payload: str) -> str:
    parsed = json.loads(payload)
    return str(parsed.get("data", {}).get("html", ""))


def parse_miit_news_list(html: str) -> list[RawNews]:
    rows: list[RawNews] = []
    pattern = re.compile(
        r'<a[^>]+href="(?P<href>[^"]+)"[^>]+title="(?P<title>[^"]+)"[^>]*>.*?</a>\s*<span[^>]*>(?P<date>\d{4}-\d{2}-\d{2})</span>',
        re.S,
    )
    captured_at = datetime.now(timezone.utc).isoformat()
    for match in pattern.finditer(html):
        title = unescape(match.group("title")).strip()
        href = urljoin(MIIT_NEWS_URL, match.group("href").strip())
        published_at = f"{match.group('date')}T00:00:00+08:00"
        slug = href.rstrip("/").split("/")[-1]
        rows.append(
            RawNews(
                news_id=f"miit-{slug}",
                source="miit",
                source_type="policy",
                published_at=published_at,
                captured_at=captured_at,
                title=title,
                content=title,
                url=href,
            )
        )
    return rows


def collect_miit_news() -> list[RawNews]:
    try:
        html = fetch_miit_news_html()
    except Exception as exc:
        raise CollectorFetchError("miit", str(exc) or exc.__class__.__name__) from exc

    if not html.strip():
        raise CollectorEmptyResultError("miit", "empty response body")

    rows = parse_miit_news_list(html)
    if not rows:
        raise CollectorParseError("miit", "no news rows matched response")
    return rows
