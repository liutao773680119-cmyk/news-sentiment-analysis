from news_sentiment.cli import main
from news_sentiment.models import RawNews, SocialSignal
from news_sentiment.storage import JsonlStore


def _collector_map(**overrides):
    collectors = {
        "fixture": lambda: [],
        "csrc": lambda: [],
        "cninfo": lambda: [],
        "miit": lambda: [],
        "sse": lambda: [],
        "stcn": lambda: [],
    }
    collectors.update(overrides)
    return collectors


def test_run_once_generates_text_report(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["run-once", "--source", "fixture"]) == 0
    report_path = tmp_path / "data" / "reports" / "latest_report.txt"
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "关注" in content
    assert "事件类型:" in content
    assert "来源:" in content
    assert "发布时间:" in content
    assert "URL:" in content


def test_run_once_all_merges_sources_and_prefers_authoritative_source(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        "news_sentiment.cli.get_registered_collectors",
        lambda: _collector_map(
            cninfo=lambda: [
                RawNews(
                    news_id="cninfo-1",
                    source="cninfo",
                    source_type="hard_event",
                    published_at="2026-04-01T09:31:00+08:00",
                    captured_at="2026-04-01T09:31:30+08:00",
                    title="中科曙光签署算力合作协议公告",
                    content="中科曙光签署算力合作协议公告。",
                    url="https://www.cninfo.com.cn/notice/1",
                )
            ],
            stcn=lambda: [
                RawNews(
                    news_id="stcn-1",
                    source="stcn",
                    source_type="fast_news",
                    published_at="2026-04-01T09:29:00+08:00",
                    captured_at="2026-04-01T09:29:30+08:00",
                    title="中科曙光签署算力合作协议",
                    content="证券时报快讯称中科曙光签署算力合作协议。",
                    url="https://www.stcn.com/article/1.html",
                )
            ],
        ),
    )

    assert main(["run-once", "--source", "all"]) == 0
    content = (tmp_path / "data" / "reports" / "latest_report.txt").read_text(encoding="utf-8")
    assert content.count("[关注]") == 1
    assert "事件类型: 合作协议" in content
    assert "来源: cninfo" in content


def test_run_once_all_continues_when_one_source_fails(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        "news_sentiment.cli.get_registered_collectors",
        lambda: _collector_map(
            cninfo=lambda: [
                RawNews(
                    news_id="cninfo-1",
                    source="cninfo",
                    source_type="hard_event",
                    published_at="2026-04-01T09:31:00+08:00",
                    captured_at="2026-04-01T09:31:30+08:00",
                    title="中科曙光签署算力合作协议公告",
                    content="中科曙光签署算力合作协议公告。",
                    url="https://www.cninfo.com.cn/notice/1",
                )
            ],
            stcn=lambda: (_ for _ in ()).throw(RuntimeError("stcn unavailable")),
        ),
    )

    assert main(["run-once", "--source", "all"]) == 0
    content = (tmp_path / "data" / "reports" / "latest_report.txt").read_text(encoding="utf-8")
    assert "中科曙光签署算力合作协议公告" in content


def test_report_reads_social_signals_sidecar_when_present(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["run-once", "--source", "fixture"]) == 0

    social_store = JsonlStore(tmp_path / "data" / "social" / "social_signals.jsonl", SocialSignal)
    social_store.write_many(
        [
            SocialSignal(
                event_id="event-001",
                platform="weibo",
                captured_at="2026-04-01T09:35:00+08:00",
                heat_score=82.0,
                heat_delta=18.0,
                co_mentioned_themes=["算力"],
                sample_posts=["算力热度升温"],
            )
        ]
    )

    assert main(["report"]) == 0
    content = (tmp_path / "data" / "reports" / "latest_report.txt").read_text(encoding="utf-8")
    assert "[社交热度观察]" in content
    assert "平台: weibo" in content
