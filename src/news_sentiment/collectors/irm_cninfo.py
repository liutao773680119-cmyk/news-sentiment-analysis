from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from html import unescape
from urllib.parse import urljoin

import requests

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


IRM_CNINFO_HOME_URL = "https://irm.cninfo.com.cn/newircs/"
IRM_CNINFO_DETAIL_URL = "https://irm.cninfo.com.cn/newircs/question/getQuestionDetail?questionId={question_id}"
IRM_CNINFO_BASE_URL = "https://irm.cninfo.com.cn"
IRM_CNINFO_HOME_TIMEOUT_SECONDS = 5
IRM_CNINFO_DETAIL_TIMEOUT_SECONDS = 3
IRM_CNINFO_MAX_DETAIL_ENRICHMENT = 10
CHINA_TZ = timezone(timedelta(hours=8))


def current_china_time() -> datetime:
    return datetime.now(timezone.utc).astimezone(CHINA_TZ)


def fetch_irm_cninfo_homepage(url: str = IRM_CNINFO_HOME_URL) -> str:
    source_definition = load_source_definition_map()["irm_cninfo"]
    return _fetch_irm_cninfo_html(
        url,
        timeout_seconds=min(source_definition.timeout_seconds, IRM_CNINFO_HOME_TIMEOUT_SECONDS),
        user_agent=source_definition.user_agent,
    )


def fetch_irm_cninfo_question_detail(question_id: str) -> str:
    source_definition = load_source_definition_map()["irm_cninfo"]
    return _fetch_irm_cninfo_html(
        IRM_CNINFO_DETAIL_URL.format(question_id=question_id),
        timeout_seconds=min(source_definition.timeout_seconds, IRM_CNINFO_DETAIL_TIMEOUT_SECONDS),
        user_agent=source_definition.user_agent,
    )


def _fetch_irm_cninfo_html(url: str, *, timeout_seconds: int, user_agent: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": user_agent},
        timeout=(timeout_seconds, timeout_seconds),
    )
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"
    return response.text


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(_strip_tags(value)).replace("\xa0", " ")).strip()


def _parse_time(raw_value: str, *, now: datetime | None = None) -> str:
    reference = now or current_china_time()
    value = raw_value.strip()
    if not value:
        return reference.replace(microsecond=0).isoformat()

    hour_match = re.search(r"(\d+)\s*小时前", value)
    if hour_match:
        return (reference - timedelta(hours=int(hour_match.group(1)))).replace(microsecond=0).isoformat()

    minute_match = re.search(r"(\d+)\s*分钟前", value)
    if minute_match:
        return (reference - timedelta(minutes=int(minute_match.group(1)))).replace(microsecond=0).isoformat()

    yesterday_match = re.search(r"昨天(?:\s*(\d{1,2}:\d{2}))?", value)
    if yesterday_match:
        clock = yesterday_match.group(1) or "00:00"
        hour, minute = (int(part) for part in clock.split(":"))
        return (
            (reference - timedelta(days=1))
            .replace(hour=hour, minute=minute, second=0, microsecond=0)
            .isoformat()
        )

    for pattern, format_string in (
        (r"\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?", "%Y-%m-%d %H:%M"),
        (r"\d{4}年\d{2}月\d{2}日(?:\s+\d{2}:\d{2})?", "%Y年%m月%d日 %H:%M"),
    ):
        absolute_match = re.search(pattern, value)
        if absolute_match:
            normalized = absolute_match.group(0)
            if len(normalized) == 10 or len(normalized) == 11:
                normalized = f"{normalized} 00:00"
            return datetime.strptime(normalized, format_string).replace(tzinfo=CHINA_TZ).isoformat()

    return reference.replace(microsecond=0).isoformat()


def _parse_timestamp_ms(value: object) -> str:
    try:
        timestamp_ms = int(value or 0)
    except (TypeError, ValueError):
        timestamp_ms = 0
    if timestamp_ms <= 0:
        return ""
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=CHINA_TZ).replace(microsecond=0).isoformat()


def parse_irm_cninfo_question_detail_payload(payload: str) -> dict[str, str]:
    parsed = json.loads(payload)
    data = parsed.get("data") or {}
    question_content = _normalize_text(str(data.get("questionContent", "")))
    reply_content = _normalize_text(str(data.get("replyContent", "")))
    return {
        "company_name": _normalize_text(str(data.get("shortName", ""))),
        "stock_code": _normalize_text(str(data.get("stockCode", ""))),
        "question_content": question_content,
        "reply_content": reply_content,
        "published_at": _parse_timestamp_ms(data.get("replyDate") or data.get("questionDate")),
    }


def parse_irm_cninfo_homepage(html: str, *, now: datetime | None = None) -> list[RawNews]:
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows: list[RawNews] = []
    block_pattern = re.compile(
        r'<div class="left-content table-list"[^>]*>(?P<block>.*?)<div class="el-loading-mask cover">',
        re.S,
    )

    for match in block_pattern.finditer(html):
        block = match.group("block")
        detail_match = re.search(
            r'href="(?P<href>//irm\.cninfo\.com\.cn/ircs/question/questionDetail\?questionId=(?P<id>\d+))"',
            block,
        )
        question_id_match = re.search(
            r"clickEventPraise\(\$event,'[^']+','S','(?P<id>\d+)','Q'\)",
            block,
        ) or re.search(r"clickEventFavorite\(\$event,'(?P<id>\d+)','que'\)", block)
        question_match = re.search(
            r'<div class="question-content"[^>]*>(?P<content>.*?)</div>',
            block,
            re.S,
        )
        company_name_match = re.search(r'<span class="compnay-name">(?P<name>.*?)&nbsp;', block, re.S)
        company_code_match = re.search(r'<span class="company-code hidden-xs-only">\[(?P<code>\d{6})\]</span>', block)
        time_matches = re.findall(r'<span class="question-time(?: [^"]+)?">(?P<time>[^<]+)</span>', block)

        if question_match is None or company_name_match is None:
            continue

        question_text = _normalize_text(question_match.group("content"))
        company_name = _normalize_text(company_name_match.group("name"))
        company_code = company_code_match.group("code") if company_code_match else ""
        question_id = (
            detail_match.group("id")
            if detail_match is not None
            else question_id_match.group("id") if question_id_match is not None else ""
        )
        relative_time = next((item.strip() for item in time_matches if item.strip()), "")

        if not question_text or not question_id:
            continue

        title_prefix = company_name or company_code or "互动易"
        rows.append(
            RawNews(
                news_id=f"irm_cninfo-{question_id}",
                source="irm_cninfo",
                source_type="fast_news",
                published_at=_parse_time(relative_time, now=now),
                captured_at=captured_at,
                title=f"{title_prefix}：{question_text}",
                content=question_text,
                url=f"{IRM_CNINFO_BASE_URL}/ircs/question/questionDetail?questionId={question_id}",
            )
        )

    return rows


def collect_irm_cninfo_news() -> list[RawNews]:
    try:
        html = fetch_irm_cninfo_homepage()
    except Exception as exc:
        raise CollectorFetchError("irm_cninfo", str(exc) or exc.__class__.__name__) from exc

    if not html.strip():
        raise CollectorEmptyResultError("irm_cninfo", "empty response body")

    rows = parse_irm_cninfo_homepage(html)
    if not rows:
        raise CollectorParseError("irm_cninfo", "no question rows matched homepage")

    enriched_rows: list[RawNews] = []
    for index, row in enumerate(rows):
        if index >= IRM_CNINFO_MAX_DETAIL_ENRICHMENT:
            enriched_rows.append(row)
            continue

        question_id = row.news_id.replace("irm_cninfo-", "", 1)
        try:
            detail_payload = fetch_irm_cninfo_question_detail(question_id)
            detail = parse_irm_cninfo_question_detail_payload(detail_payload)
        except Exception:
            enriched_rows.append(row)
            continue

        question_content = detail.get("question_content", "") or row.content
        reply_content = detail.get("reply_content", "")
        if not reply_content:
            continue

        company_name = detail.get("company_name", "") or row.title.split("：", 1)[0]
        enriched_rows.append(
            RawNews(
                news_id=row.news_id,
                source=row.source,
                source_type=row.source_type,
                published_at=detail.get("published_at", "") or row.published_at,
                captured_at=row.captured_at,
                title=f"{company_name}：{question_content}",
                content=f"问题：{question_content}\n回复：{reply_content}",
                url=row.url,
            )
        )

    if enriched_rows:
        return enriched_rows
    return rows
