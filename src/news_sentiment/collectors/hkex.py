from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, urljoin

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


HKEX_JSON_URL_TEMPLATE = "https://www1.hkexnews.hk/ncms/json/eds/lcisehk1relsde_{page}.json"
HKEX_BASE_URL = "https://www1.hkexnews.hk"
HK_TZ = timezone(timedelta(hours=8))


def fetch_hkex_news_payload(page: int = 1) -> str:
    source_definition = load_source_definition_map()["hkex"]
    url = HKEX_JSON_URL_TEMPLATE.format(page=page)
    return fetch_html(
        url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def _parse_release_time(raw_value: str) -> str:
    parsed = datetime.strptime(raw_value.strip(), "%d/%m/%Y %H:%M")
    return parsed.replace(tzinfo=HK_TZ).isoformat()


def parse_hkex_news_payload(payload: str) -> tuple[list[RawNews], int]:
    parsed = json.loads(payload)
    captured_at = datetime.now(timezone.utc).isoformat()
    rows: list[RawNews] = []
    max_num_of_file = int(parsed.get("maxNumOfFile", 1) or 1)

    for item in parsed.get("newsInfoLst", []):
        title = str(item.get("title", "")).strip()
        web_path = str(item.get("webPath", "")).strip()
        release_time = str(item.get("relTime", "")).strip()
        news_id = str(item.get("newsId", "")).strip()
        stocks = item.get("stock", [])
        stock_code = ""
        if isinstance(stocks, list) and stocks:
            stock_code = str(stocks[0].get("sc", "")).strip()
        if not title or not web_path or not release_time:
            continue
        url = urljoin(HKEX_BASE_URL, web_path)
        if stock_code:
            url = f"{url}?{urlencode({'stockCode': stock_code})}"
        rows.append(
            RawNews(
                news_id=f"hkex-{news_id or stock_code or len(rows) + 1}",
                source="hkex",
                source_type="hard_event",
                published_at=_parse_release_time(release_time),
                captured_at=captured_at,
                title=title,
                content=title,
                url=url,
            )
        )
    return rows, max_num_of_file


def collect_hkex_news() -> list[RawNews]:
    try:
        first_payload = fetch_hkex_news_payload(1)
    except Exception as exc:
        raise CollectorFetchError("hkex", str(exc) or exc.__class__.__name__) from exc

    if not first_payload.strip():
        raise CollectorEmptyResultError("hkex", "empty response body")

    try:
        first_rows, max_num_of_file = parse_hkex_news_payload(first_payload)
    except Exception as exc:
        raise CollectorParseError("hkex", str(exc) or exc.__class__.__name__) from exc

    rows = list(first_rows)
    for page in range(2, max_num_of_file + 1):
        try:
            payload = fetch_hkex_news_payload(page)
        except Exception as exc:
            raise CollectorFetchError("hkex", str(exc) or exc.__class__.__name__) from exc
        if not payload.strip():
            continue
        try:
            page_rows, _ = parse_hkex_news_payload(payload)
        except Exception as exc:
            raise CollectorParseError("hkex", str(exc) or exc.__class__.__name__) from exc
        rows.extend(page_rows)

    if not rows:
        raise CollectorParseError("hkex", "no announcement rows matched response")
    return rows
