from __future__ import annotations

from datetime import datetime, timedelta

from news_sentiment.history.matcher import match_historical_events
from news_sentiment.mapping.stock_mapper import map_themes_to_stocks
from news_sentiment.models import Event, EventAnalysis
from news_sentiment.settings import ProjectPaths


REPORT_WINDOW_DAYS = 2
HARD_EVENT_CATALYST_KEYWORDS = (
    "受理",
    "签署",
    "合作",
    "获批",
    "中标",
    "订单",
    "合同",
    "回购",
    "增持",
    "减持",
    "定增",
    "重组",
    "收购",
    "激励",
)


def _parse_event_timestamp(event: Event) -> datetime | None:
    timestamp = event.published_at or event.first_seen_at or event.last_seen_at
    if not timestamp:
        return None
    return datetime.fromisoformat(timestamp)


def _is_market_relevant(event: Event, analysis: EventAnalysis) -> bool:
    if analysis.themes:
        return True
    if analysis.direction != "neutral":
        return True
    if event.event_type == "fast_news":
        return True
    if event.event_type == "hard_event":
        text = f"{event.canonical_title} {event.summary}"
        return any(keyword in text for keyword in HARD_EVENT_CATALYST_KEYWORDS)
    return False


def write_text_report(
    paths: ProjectPaths,
    events: list[Event],
    analyses: list[EventAnalysis],
) -> None:
    event_map = {event.event_id: event for event in events}
    lines: list[str] = []
    event_times = {
        event.event_id: parsed
        for event in events
        for parsed in [_parse_event_timestamp(event)]
        if parsed is not None
    }
    latest_batch_time = max(event_times.values(), default=None)
    cutoff_time = (
        latest_batch_time - timedelta(days=REPORT_WINDOW_DAYS)
        if latest_batch_time is not None
        else None
    )
    ranked_analyses = sorted(
        [
            analysis
            for analysis in analyses
            if analysis.triggered
            and analysis.event_id in event_map
            and _is_market_relevant(event_map[analysis.event_id], analysis)
            and (
                cutoff_time is None
                or analysis.event_id not in event_times
                or event_times[analysis.event_id] >= cutoff_time
            )
        ],
        key=lambda analysis: (
            1 if analysis.themes else 0,
            analysis.impact_score,
        ),
        reverse=True,
    )
    for analysis in ranked_analyses:
        event = event_map[analysis.event_id]
        theme_matches = map_themes_to_stocks(analysis.themes)
        historical = match_historical_events(analysis.themes)
        status = "关注"
        lines.extend(
            [
                f"[{status}] {event.canonical_title}",
                f"来源: {event.source or '未知'}",
                f"发布时间: {event.published_at or event.first_seen_at or '未知'}",
                f"URL: {event.url or '无'}",
                f"方向: {analysis.direction}",
                f"强度: {analysis.impact_score:.1f}",
                f"题材: {', '.join(analysis.themes) if analysis.themes else '无'}",
                f"个股: {', '.join(match.stock_code for match in theme_matches[:3]) if theme_matches else '无'}",
                f"历史: {historical[0]['historical_event_id'] if historical else '无'}",
                "",
            ]
        )

    paths.latest_report_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines).strip()
    paths.latest_report_path.write_text((content + "\n") if content else "", encoding="utf-8")
