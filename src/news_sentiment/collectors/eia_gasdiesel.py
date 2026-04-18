from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
from zoneinfo import ZoneInfo

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


EIA_GASDIESEL_FEED_URL = "https://www.eia.gov/petroleum/gasdiesel/includes/gas_diesel_rss.xml"
EASTERN_TZ = ZoneInfo("America/New_York")


def fetch_eia_gasdiesel_feed(url: str | None = None) -> str:
    source_definition = load_source_definition_map()["eia_gasdiesel"]
    return fetch_html(
        url or EIA_GASDIESEL_FEED_URL,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def _normalize_text(value: str | None) -> str:
    return " ".join(unescape(value or "").replace("\xa0", " ").split())


def _extract_us_price(text: str, label: str) -> str:
    pattern = rf"{re.escape(label)}.*?(\d+\.\d+)\s*\.\.\s*U\.S\."
    match = re.search(pattern, text, re.S)
    return match.group(1) if match else ""


def _parse_pub_date(value: str) -> str:
    normalized = value.replace(" EST", " -0500").replace(" EDT", " -0400")
    parsed = parsedate_to_datetime(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=EASTERN_TZ)
    return parsed.astimezone(EASTERN_TZ).replace(microsecond=0).isoformat()


def parse_eia_gasdiesel_feed(payload: str) -> list[RawNews]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise CollectorParseError("eia_gasdiesel", f"invalid rss payload: {exc}") from exc

    rows: list[RawNews] = []
    captured_at = datetime.now(ZoneInfo("UTC")).replace(microsecond=0).isoformat()
    for item in root.findall("./channel/item"):
        title = _normalize_text(item.findtext("title"))
        link = _normalize_text(item.findtext("link"))
        pub_date = _normalize_text(item.findtext("pubDate"))
        description = item.findtext("description") or ""
        normalized_description = _normalize_text(re.sub(r"<br\s*/?>", "\n", description, flags=re.I))
        gasoline_us = _extract_us_price(normalized_description, "Regular Gasoline Retail Price")
        diesel_us = _extract_us_price(normalized_description, "On-Highway Diesel Fuel Retail Price")
        if not title or not link or not pub_date or not gasoline_us or not diesel_us:
            continue
        published_at = _parse_pub_date(pub_date)
        rows.append(
            RawNews(
                news_id=f"eia_gasdiesel-{datetime.fromisoformat(published_at).astimezone(EASTERN_TZ).strftime('%Y%m%d%H%M%S')}",
                source="eia_gasdiesel",
                source_type="fast_news",
                published_at=published_at,
                captured_at=captured_at,
                title=f"EIA汽柴油零售价更新 美国汽油{gasoline_us}美元/加仑 美国柴油{diesel_us}美元/加仑",
                content=(
                    f"美国汽油零售价 {gasoline_us} 美元/加仑；"
                    f"美国柴油零售价 {diesel_us} 美元/加仑。"
                    "来源：EIA Gasoline and Diesel Fuel Update"
                ),
                url=link,
            )
        )
    return rows


def collect_eia_gasdiesel_news() -> list[RawNews]:
    try:
        payload = fetch_eia_gasdiesel_feed()
    except Exception as exc:
        raise CollectorFetchError("eia_gasdiesel", str(exc) or exc.__class__.__name__) from exc

    if not payload.strip():
        raise CollectorEmptyResultError("eia_gasdiesel", "empty response body")

    rows = parse_eia_gasdiesel_feed(payload)
    if not rows:
        raise CollectorParseError("eia_gasdiesel", "no feed items matched rss")
    return rows
