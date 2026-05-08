import json

from news_sentiment.cli import main
from news_sentiment.config_loader import SourceDefinition
from news_sentiment.collectors.errors import CollectorFetchError
from news_sentiment.models import RawNews


def _source_definition(source_id: str) -> SourceDefinition:
    return SourceDefinition(
        source_id=source_id,
        name=source_id,
        source_type="fast_news",
        enabled=True,
        priority=1,
        timeout_seconds=10,
        user_agent="test-agent",
        no_proxy_hosts=(),
        retry_count=0,
        backoff_seconds=0.0,
    )


def test_watchdog_once_recovers_transient_failed_source(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)
    source_calls = {"stcn": 0}

    def stcn_collector() -> list[RawNews]:
        source_calls["stcn"] += 1
        if source_calls["stcn"] == 1:
            raise CollectorFetchError("stcn", "timed out")
        return [
            RawNews(
                news_id=f"stcn-{source_calls['stcn']}",
                source="stcn",
                source_type="fast_news",
                published_at="2026-05-08T09:30:00+08:00",
                captured_at="2026-05-08T09:31:00+08:00",
                title="算力企业签署合作协议",
                content="证券时报快讯称算力企业签署合作协议。",
                url="https://example.com/stcn-1",
            )
        ]

    monkeypatch.setattr(
        "news_sentiment.cli.load_source_definitions",
        lambda: [_source_definition("cninfo"), _source_definition("stcn")],
    )
    monkeypatch.setattr(
        "news_sentiment.cli.get_registered_collectors",
        lambda: {
            "cninfo": lambda: [
                RawNews(
                    news_id="cninfo-1",
                    source="cninfo",
                    source_type="hard_event",
                    published_at="2026-05-08T09:31:00+08:00",
                    captured_at="2026-05-08T09:31:30+08:00",
                    title="中科曙光签署算力合作协议公告",
                    content="中科曙光签署算力合作协议公告。",
                    url="https://example.com/cninfo-1",
                )
            ],
            "stcn": stcn_collector,
        },
    )
    monkeypatch.setattr(
        "news_sentiment.watchdog._incident_timestamp",
        lambda: "20260508T010203Z",
    )
    notifications: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "news_sentiment.watchdog.send_desktop_notification",
        lambda title, message: notifications.append((title, message)) or True,
    )

    assert main(["watchdog-once", "--source", "all", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "watchdog_status=recovered" in output
    assert "failed_sources=none" in output
    assert "suspicious_count=0" in output
    assert "initial_failed_sources=stcn:fetch_error" in output
    assert "rerun_attempted=true" in output

    incident_path = (
        tmp_path
        / "data"
        / "monitoring"
        / "incidents"
        / "20260508T010203Z-watchdog.json"
    )
    payload = json.loads(incident_path.read_text(encoding="utf-8"))
    assert payload["initial"]["failed_sources"] == ["stcn:fetch_error"]
    assert payload["probes"] == [{"source": "stcn", "status": "ok", "rows": 1}]
    assert payload["rerun"]["attempted"] is True
    assert payload["rerun"]["failed_sources"] == []
    assert payload["final"]["failed_sources"] == []
    assert notifications


def test_watchdog_once_keeps_alert_when_failed_source_persists(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        "news_sentiment.cli.load_source_definitions",
        lambda: [_source_definition("cninfo"), _source_definition("stcn")],
    )
    monkeypatch.setattr(
        "news_sentiment.cli.get_registered_collectors",
        lambda: {
            "cninfo": lambda: [
                RawNews(
                    news_id="cninfo-1",
                    source="cninfo",
                    source_type="hard_event",
                    published_at="2026-05-08T09:31:00+08:00",
                    captured_at="2026-05-08T09:31:30+08:00",
                    title="中科曙光签署算力合作协议公告",
                    content="中科曙光签署算力合作协议公告。",
                    url="https://example.com/cninfo-1",
                )
            ],
            "stcn": lambda: (_ for _ in ()).throw(CollectorFetchError("stcn", "timed out")),
        },
    )
    monkeypatch.setattr(
        "news_sentiment.watchdog._incident_timestamp",
        lambda: "20260508T030405Z",
    )
    notifications: list[tuple[str, str]] = []
    monkeypatch.setattr(
        "news_sentiment.watchdog.send_desktop_notification",
        lambda title, message: notifications.append((title, message)) or True,
    )

    assert main(["watchdog-once", "--source", "all", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "watchdog_status=alert" in output
    assert "failed_sources=stcn:fetch_error" in output
    assert "suspicious_count=0" in output
    assert "rerun_attempted=false" in output

    incident_path = (
        tmp_path
        / "data"
        / "monitoring"
        / "incidents"
        / "20260508T030405Z-watchdog.json"
    )
    payload = json.loads(incident_path.read_text(encoding="utf-8"))
    assert payload["probes"] == [{"source": "stcn", "status": "fetch_error", "rows": 0}]
    assert payload["rerun"]["attempted"] is False
    assert payload["final"]["failed_sources"] == ["stcn:fetch_error"]
    assert notifications
