from __future__ import annotations

from news_sentiment.history.matcher import match_historical_events
from news_sentiment.mapping.stock_mapper import map_themes_to_stocks
from news_sentiment.models import Event, EventAnalysis
from news_sentiment.settings import ProjectPaths


def write_text_report(
    paths: ProjectPaths,
    events: list[Event],
    analyses: list[EventAnalysis],
) -> None:
    event_map = {event.event_id: event for event in events}
    lines: list[str] = []
    for analysis in analyses:
        event = event_map[analysis.event_id]
        theme_matches = map_themes_to_stocks(analysis.themes)
        historical = match_historical_events(analysis.themes)
        status = "关注" if analysis.triggered else "观察"
        lines.extend(
            [
                f"[{status}] {event.canonical_title}",
                f"方向: {analysis.direction}",
                f"强度: {analysis.impact_score:.1f}",
                f"题材: {', '.join(analysis.themes) if analysis.themes else '无'}",
                f"个股: {', '.join(match.stock_code for match in theme_matches[:3]) if theme_matches else '无'}",
                f"历史: {historical[0]['historical_event_id'] if historical else '无'}",
                "",
            ]
        )

    paths.latest_report_path.parent.mkdir(parents=True, exist_ok=True)
    paths.latest_report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
