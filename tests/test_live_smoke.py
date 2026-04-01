from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError
from news_sentiment.models import RawNews


def test_live_smoke_runs_pipeline_and_prints_summary(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.cli.collect_cninfo_news",
        lambda: [
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
    )
    monkeypatch.setattr("news_sentiment.cli.collect_miit_news", lambda: [])
    monkeypatch.setattr("news_sentiment.cli.collect_stcn_news", lambda: [])

    assert main(["live-smoke", "--source", "all"]) == 0
    output = capsys.readouterr().out
    assert "raw_news=1" in output
    assert "events=1" in output
    assert "report=" in output


def test_live_smoke_reports_failed_sources_and_keeps_running(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.cli.collect_cninfo_news",
        lambda: [
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
    )
    monkeypatch.setattr(
        "news_sentiment.cli.collect_stcn_news",
        lambda: (_ for _ in ()).throw(CollectorFetchError("stcn", "timed out")),
    )
    monkeypatch.setattr("news_sentiment.cli.collect_miit_news", lambda: [])

    assert main(["live-smoke", "--source", "all"]) == 0
    output = capsys.readouterr().out
    assert "raw_news=1" in output
    assert "failed_sources=stcn:fetch_error" in output
