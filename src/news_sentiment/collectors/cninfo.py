from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from html import unescape
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


CNINFO_DISCLOSURE_URL = "https://www.cninfo.com.cn/new/disclosure/stock"
CNINFO_QUERY_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
CHINA_TZ = timezone(timedelta(hours=8))


def fetch_cninfo_news_html(url: str = CNINFO_DISCLOSURE_URL) -> str:
    return fetch_cninfo_news_payload()


def fetch_cninfo_news_payload(url: str = CNINFO_QUERY_URL) -> str:
    source_definition = load_source_definition_map()["cninfo"]
    data = urlencode(
        {
            "pageNum": 1,
            "pageSize": 30,
            "column": "szse",
            "tabName": "fulltext",
            "plate": "",
            "stock": "",
            "searchkey": "",
            "secid": "",
            "category": "",
            "trade": "",
            "seDate": "",
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        }
    ).encode("utf-8")
    headers = {
        "User-Agent": source_definition.user_agent,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    request = Request(url, data=data, headers=headers, method="POST")

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


def parse_cninfo_news_list(html: str) -> list[RawNews]:
    rows: list[RawNews] = []
    pattern = re.compile(
        r"<tr>\s*<td>(?P<code>\d{6})</td>\s*<td>(?P<name>[^<]+)</td>\s*<td>\s*<a href=\"(?P<href>[^\"]+)\">\s*(?P<title>[^<]+)\s*</a>\s*</td>\s*<td>(?P<date>\d{4}-\d{2}-\d{2})</td>",
        re.S,
    )
    captured_at = datetime.now(timezone.utc).isoformat()
    for match in pattern.finditer(html):
        title = unescape(match.group("title")).strip()
        href = urljoin("https://www.cninfo.com.cn", match.group("href").strip())
        published_at = f"{match.group('date')}T00:00:00+08:00"
        announcement_id = href.split("announcementId=")[-1] if "announcementId=" in href else match.group("code")
        rows.append(
            RawNews(
                news_id=f"cninfo-{announcement_id}",
                source="cninfo",
                source_type="hard_event",
                published_at=published_at,
                captured_at=captured_at,
                title=title,
                content=title,
                url=href,
            )
        )
    return rows


def parse_cninfo_news_payload(payload: str) -> list[RawNews]:
    parsed = json.loads(payload)
    captured_at = datetime.now(timezone.utc).isoformat()
    rows: list[RawNews] = []
    for item in parsed.get("announcements", []):
        sec_code = str(item.get("secCode", "")).strip()
        org_id = str(item.get("orgId", "")).strip()
        announcement_id = str(item.get("announcementId", "")).strip()
        title = unescape(str(item.get("announcementTitle", "")).strip())
        timestamp_ms = int(item.get("announcementTime", 0))
        published_at = (
            datetime.fromtimestamp(timestamp_ms / 1000, tz=CHINA_TZ).isoformat()
            if timestamp_ms
            else f"{datetime.now(CHINA_TZ).date().isoformat()}T00:00:00+08:00"
        )
        announcement_date = published_at[:10]
        href = (
            "https://www.cninfo.com.cn/new/disclosure/detail"
            f"?stockCode={sec_code}&announcementId={announcement_id}"
            f"&orgId={org_id}&announcementTime={announcement_date}"
        )
        rows.append(
            RawNews(
                news_id=f"cninfo-{announcement_id}",
                source="cninfo",
                source_type="hard_event",
                published_at=published_at,
                captured_at=captured_at,
                title=title,
                content=title,
                url=href,
            )
        )
    return rows


def collect_cninfo_news() -> list[RawNews]:
    try:
        payload = fetch_cninfo_news_payload()
    except Exception as exc:
        raise CollectorFetchError("cninfo", str(exc) or exc.__class__.__name__) from exc

    if not payload.strip():
        raise CollectorEmptyResultError("cninfo", "empty response body")

    rows = parse_cninfo_news_payload(payload)
    if not rows:
        raise CollectorParseError("cninfo", "no announcement rows matched response")
    return rows
