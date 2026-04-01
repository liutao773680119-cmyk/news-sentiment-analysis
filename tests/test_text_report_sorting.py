from news_sentiment.models import Event, EventAnalysis
from news_sentiment.reporting.text_report import write_text_report
from news_sentiment.settings import ProjectPaths


def test_write_text_report_filters_non_triggered_and_sorts_by_score(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-1",
            first_seen_at="2026-04-01T09:30:00+08:00",
            last_seen_at="2026-04-01T09:30:00+08:00",
            canonical_title="低分事件",
            summary="summary",
            source="fixture",
            published_at="2026-04-01T09:30:00+08:00",
            url="https://example.com/1",
        ),
        Event(
            event_id="event-2",
            first_seen_at="2026-04-01T09:31:00+08:00",
            last_seen_at="2026-04-01T09:31:00+08:00",
            canonical_title="高分事件",
            summary="summary",
            source="fixture",
            published_at="2026-04-01T09:31:00+08:00",
            url="https://example.com/2",
        ),
        Event(
            event_id="event-3",
            first_seen_at="2026-04-01T09:32:00+08:00",
            last_seen_at="2026-04-01T09:32:00+08:00",
            canonical_title="未触发事件",
            summary="summary",
            source="fixture",
            published_at="2026-04-01T09:32:00+08:00",
            url="https://example.com/3",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-1",
            direction="bullish",
            impact_score=71.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-2",
            direction="bullish",
            impact_score=95.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-3",
            direction="neutral",
            impact_score=40.0,
            reasoning="rule",
            themes=[],
            triggered=False,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "未触发事件" not in content
    assert content.index("高分事件") < content.index("低分事件")
