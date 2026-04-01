from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urljoin
from urllib.request import urlopen

from news_sentiment.models import RawNews


CNINFO_DISCLOSURE_URL = "https://www.cninfo.com.cn/new/disclosure/stock"


def fetch_cninfo_news_html(url: str = CNINFO_DISCLOSURE_URL) -> str:
    with urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8", errors="ignore")


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


def collect_cninfo_news() -> list[RawNews]:
    return parse_cninfo_news_list(fetch_cninfo_news_html())
