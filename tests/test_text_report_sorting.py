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


def test_write_text_report_filters_stale_events_relative_to_latest_batch_time(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-old",
            first_seen_at="2026-03-20T09:30:00+08:00",
            last_seen_at="2026-03-20T09:30:00+08:00",
            canonical_title="过旧事件",
            summary="summary",
            source="miit",
            published_at="2026-03-20T09:30:00+08:00",
            url="https://example.com/old",
        ),
        Event(
            event_id="event-new",
            first_seen_at="2026-04-02T09:30:00+08:00",
            last_seen_at="2026-04-02T09:30:00+08:00",
            canonical_title="近期事件",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T09:30:00+08:00",
            url="https://example.com/new",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-old",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-new",
            direction="bullish",
            impact_score=75.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "近期事件" in content
    assert "过旧事件" not in content


def test_write_text_report_prioritizes_themed_events_when_scores_tie(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-no-theme",
            first_seen_at="2026-04-02T09:30:00+08:00",
            last_seen_at="2026-04-02T09:30:00+08:00",
            canonical_title="无题材事件",
            summary="summary",
            source="miit",
            published_at="2026-04-02T09:30:00+08:00",
            url="https://example.com/1",
        ),
        Event(
            event_id="event-theme",
            first_seen_at="2026-04-02T09:31:00+08:00",
            last_seen_at="2026-04-02T09:31:00+08:00",
            canonical_title="有题材事件",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T09:31:00+08:00",
            url="https://example.com/2",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-no-theme",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-theme",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert content.index("有题材事件") < content.index("无题材事件")
