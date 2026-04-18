from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from html import unescape

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


SSE_EINTERACTIVE_FEED_URL = "https://sns.sseinfo.com/ajax/feeds.do?type=11&pageSize=20&lastid=-1&show=1&page=1"
SSE_EINTERACTIVE_DETAIL_URL = "https://sns.sseinfo.com/qadetail.do?weiboId={weibo_id}"
CHINA_TZ = timezone(timedelta(hours=8))


def current_china_time() -> datetime:
    return datetime.now(timezone.utc).astimezone(CHINA_TZ)


def fetch_sse_einteractive_feed(url: str = SSE_EINTERACTIVE_FEED_URL) -> str:
    source_definition = load_source_definition_map()["sse_einteractive"]
    return fetch_html(
        url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
        extra_headers={"X-Requested-With": "XMLHttpRequest", "Referer": "https://sns.sseinfo.com/qa.do"},
    )


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(_strip_tags(value)).replace("\xa0", " ")).strip()


def _extract_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        return ""
    start += len(start_marker)
    end = text.find(end_marker, start)
    if end == -1:
        return text[start:]
    return text[start:end]


def _parse_timestamp(raw_value: str, *, now: datetime | None = None) -> str:
    value = raw_value.strip()
    reference = now or current_china_time()
    if not value:
        return reference.replace(microsecond=0).isoformat()

    if re.fullmatch(r"\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}", value):
        return datetime.strptime(value, "%Y年%m月%d日 %H:%M").replace(tzinfo=CHINA_TZ).isoformat()

    yesterday_match = re.fullmatch(r"昨天 (\d{2}:\d{2})", value)
    if yesterday_match:
        hour, minute = (int(part) for part in yesterday_match.group(1).split(":"))
        return (
            (reference - timedelta(days=1))
            .replace(hour=hour, minute=minute, second=0, microsecond=0)
            .isoformat()
        )

    return reference.replace(microsecond=0).isoformat()


def parse_sse_einteractive_feed(html: str, *, now: datetime | None = None) -> list[RawNews]:
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows: list[RawNews] = []
    parts = html.split('<div class="m_feed_item" id="item-')

    for part in parts[1:]:
        id_match = re.match(r"(?P<id>\d+)", part)
        if id_match is None:
            continue
        weibo_id = id_match.group("id")
        block = part

        question_section = _extract_between(
            block,
            '<div class="m_feed_detail m_qa_detail">',
            '<div class="m_feed_detail m_qa">',
        )
        answer_section = _extract_between(
            block,
            '<div class="m_feed_detail m_qa">',
            '</div>\n\t\t\t</div>',
        )
        if not question_section or not answer_section:
            continue

        question_html_match = re.search(r'<div class="m_feed_txt" id="m_feed_txt-\d+">(?P<content>.*?)</div>', question_section, re.S)
        answer_html_match = re.search(r'<div class="m_feed_txt" id="m_feed_txt-\d+">(?P<content>.*?)</div>', answer_section, re.S)
        time_matches = re.findall(
            r"<span>(昨天 \d{2}:\d{2}|\d{4}年\d{2}月\d{2}日 \d{2}:\d{2})</span>\s*<em>来自</em>",
            block,
        )
        company_match = re.search(r":(?P<name>[^<(]+)\((?P<code>\d{6})\)", question_section)

        if question_html_match is None or answer_html_match is None or company_match is None:
            continue

        question_text = _normalize_text(question_html_match.group("content"))
        answer_text = _normalize_text(answer_html_match.group("content"))
        company_name = _normalize_text(company_match.group("name"))
        question_prefix = f":{company_name}({company_match.group('code')})"
        if question_text.startswith(question_prefix):
            question_text = question_text[len(question_prefix) :].strip()

        if not question_text or not answer_text:
            continue

        answer_time = time_matches[-1].strip() if time_matches else ""
        rows.append(
            RawNews(
                news_id=f"sse_einteractive-{weibo_id}",
                source="sse_einteractive",
                source_type="fast_news",
                published_at=_parse_timestamp(answer_time, now=now),
                captured_at=captured_at,
                title=f"{company_name}：{question_text}",
                content=f"问题：{question_text}\n回复：{answer_text}",
                url=SSE_EINTERACTIVE_DETAIL_URL.format(weibo_id=weibo_id),
            )
        )

    return rows


def collect_sse_einteractive_news() -> list[RawNews]:
    try:
        html = fetch_sse_einteractive_feed()
    except Exception as exc:
        raise CollectorFetchError("sse_einteractive", str(exc) or exc.__class__.__name__) from exc

    if not html.strip():
        raise CollectorEmptyResultError("sse_einteractive", "empty response body")

    rows = parse_sse_einteractive_feed(html)
    if not rows:
        raise CollectorParseError("sse_einteractive", "no latest reply rows matched response")
    return rows
