from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError
from news_sentiment.models import Event, EventAnalysis
from news_sentiment.social_collectors import (
    _fetch_weibo_hot_search_payload,
    _match_weibo_topics_to_events,
)
from news_sentiment.storage import JsonlStore


def test_collect_social_fixture_writes_sidecar_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["run-once", "--source", "fixture"]) == 0
    assert main(["collect-social", "--platform", "fixture"]) == 0

    signals = JsonlStore(
        tmp_path / "data" / "social" / "social_signals.jsonl",
        model_cls=dict,
    ).read_all()
    assert len(signals) == 1
    assert signals[0]["platform"] == "fixture"
    assert signals[0]["event_id"] == "event-001"


def test_match_weibo_topics_to_events_returns_signal_for_matching_theme_and_title() -> None:
    payload = {
        "data": {
            "realtime": [
                {"word": "无关话题", "num": "1200"},
                {"word": "英伟达算力合作", "num": "42876"},
            ]
        }
    }
    events = [
        Event(
            event_id="event-001",
            first_seen_at="2026-04-01T09:30:00+08:00",
            last_seen_at="2026-04-01T09:30:00+08:00",
            canonical_title="中科曙光与英伟达签署算力合作协议",
            summary="summary",
            source="cninfo",
            published_at="2026-04-01T09:30:00+08:00",
            url="https://example.com/1",
            event_subtype="cooperation_agreement",
        )
    ]
    analyses = {
        "event-001": EventAnalysis(
            event_id="event-001",
            direction="bullish",
            impact_score=88.0,
            reasoning="rule",
            themes=["算力", "英伟达链"],
            triggered=True,
        )
    }

    signals = _match_weibo_topics_to_events(payload, events, analyses)

    assert len(signals) == 1
    assert signals[0].event_id == "event-001"
    assert signals[0].platform == "weibo"
    assert signals[0].heat_score == 42876.0
    assert signals[0].sample_posts == ["英伟达算力合作"]


def test_collect_social_weibo_reports_visitor_gate_failure(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.cli.collect_social_signals",
        lambda paths, platform: (_ for _ in ()).throw(
            CollectorFetchError("weibo", "visitor gate or html fallback")
        ),
    )

    assert main(["collect-social", "--platform", "weibo"]) == 0

    err = capsys.readouterr().err
    assert "warning: social_platform_failed=weibo:fetch_error" in err
    assert "visitor gate or html fallback" in err


def test_fetch_weibo_hot_search_payload_uses_cookie_and_referer_when_configured(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_fetch_html(url: str, **kwargs: object) -> str:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return '{"ok":1,"data":{"realtime":[]}}'

    monkeypatch.setenv("WEIBO_COOKIE", "SUB=abc; XSRF-TOKEN=xyz")

    payload = _fetch_weibo_hot_search_payload(fake_fetch_html)

    assert payload["ok"] == 1
    assert captured["kwargs"] == {
        "timeout_seconds": 10,
        "user_agent": "Mozilla/5.0",
        "extra_headers": {
            "Accept": "application/json",
            "Cookie": "SUB=abc; XSRF-TOKEN=xyz",
            "Referer": "https://weibo.com/",
        },
    }
