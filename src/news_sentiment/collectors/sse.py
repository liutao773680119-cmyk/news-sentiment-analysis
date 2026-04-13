from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from time import sleep
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


SSE_BULLETIN_QUERY_URL = "https://query.sse.com.cn/security/stock/queryCompanyBulletinNew.do"
SSE_BULLETIN_REFERER = "https://www.sse.com.cn/disclosure/listedinfo/announcement/"
SSE_STATIC_BULLETIN_URL = "https://static.sse.com.cn"
CHINA_TZ = timezone(timedelta(hours=8))
SSE_LOOKBACK_DAYS = 3


def _jsonp_payload_to_json(payload: str) -> str:
    body = payload.strip()
    if not body:
        return body
    if "(" not in body or not body.endswith(")"):
        return body
    return body[body.find("(") + 1 : -1]


def fetch_sse_news_payload(url: str = SSE_BULLETIN_QUERY_URL) -> str:
    source_definition = load_source_definition_map()["sse"]
    today = datetime.now(CHINA_TZ).date()
    begin_date = (today - timedelta(days=SSE_LOOKBACK_DAYS - 1)).isoformat()
    end_date = today.isoformat()
    query = urlencode(
        {
            "jsonCallBack": "jsonpCallbackNewsSentiment",
            "isPagination": "true",
            "pageHelp.pageSize": 50,
            "pageHelp.pageNo": 1,
            "pageHelp.beginPage": 1,
            "pageHelp.endPage": 1,
            "pageHelp.cacheSize": 1,
            "START_DATE": begin_date,
            "END_DATE": end_date,
            "SECURITY_CODE": "",
            "TITLE": "",
            "BULLETIN_TYPE": "",
            "stockType": "",
        }
    )
    headers = {
        "User-Agent": source_definition.user_agent,
        "Referer": SSE_BULLETIN_REFERER,
        "Accept": "*/*",
    }
    request = Request(f"{url}?{query}", headers=headers, method="GET")

    for attempt in range(source_definition.retry_count + 1):
        try:
            with urlopen(request, timeout=source_definition.timeout_seconds) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception:
            if attempt >= source_definition.retry_count:
                raise
            delay = source_definition.backoff_seconds * (attempt + 1)
            if delay > 0:
                sleep(delay)
    raise RuntimeError("unreachable")


def parse_sse_news_payload(payload: str) -> list[RawNews]:
    parsed = json.loads(_jsonp_payload_to_json(payload))
    captured_at = datetime.now(timezone.utc).isoformat()
    rows: list[RawNews] = []
    raw_result = parsed.get("result", [])
    flattened_items = []
    for item in raw_result:
        if isinstance(item, list):
            flattened_items.extend(item)
        else:
            flattened_items.append(item)

    for item in flattened_items:
        security_code = str(item.get("SECURITY_CODE", "")).strip()
        title = str(item.get("TITLE", "")).strip()
        url = str(item.get("URL", "")).strip()
        published_date = str(item.get("SSEDATE", "")).strip()[:10]
        if not title or not url or not published_date:
            continue
        rows.append(
            RawNews(
                news_id=f"sse-{security_code}-{published_date}-{len(rows) + 1}",
                source="sse",
                source_type="hard_event",
                published_at=f"{published_date}T00:00:00+08:00",
                captured_at=captured_at,
                title=title,
                content=title,
                url=urljoin(SSE_STATIC_BULLETIN_URL, url),
            )
        )
    return rows


def collect_sse_news() -> list[RawNews]:
    try:
        payload = fetch_sse_news_payload()
    except Exception as exc:
        raise CollectorFetchError("sse", str(exc) or exc.__class__.__name__) from exc

    if not payload.strip():
        raise CollectorEmptyResultError("sse", "empty response body")

    rows = parse_sse_news_payload(payload)
    if not rows:
        raise CollectorParseError("sse", "no announcement rows matched response")
    return rows
