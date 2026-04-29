from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError
from news_sentiment.models import RawNews


def _collector_map(**overrides):
    collectors = {
        "fixture": lambda: [],
        "bis": lambda: [],
        "boj": lambda: [],
        "boc_press": lambda: [],
        "boe": lambda: [],
        "cftc_press": lambda: [],
        "cls": lambda: [],
        "csrc": lambda: [],
        "cninfo": lambda: [],
        "ecb": lambda: [],
        "eia_gasdiesel": lambda: [],
        "eia_wpsr": lambda: [],
        "fed": lambda: [],
        "fedreg_ofac": lambda: [],
        "fedreg_sec": lambda: [],
        "hkex": lambda: [],
        "investing_economic": lambda: [],
        "investing_forex": lambda: [],
        "irm_cninfo": lambda: [],
        "investing_news": lambda: [],
        "miit": lambda: [],
        "occ_news": lambda: [],
        "sec_press": lambda: [],
        "sse": lambda: [],
        "sse_einteractive": lambda: [],
        "stcn": lambda: [],
        "szse": lambda: [],
    }
    collectors.update(overrides)
    return collectors


def test_live_smoke_runs_pipeline_and_prints_summary(tmp_path, monkeypatch, capsys) -> None:
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
            ]
        ),
    )

    assert main(["live-smoke", "--source", "all"]) == 0
    output = capsys.readouterr().out
    assert "raw_news=1" in output
    assert "events=1" in output
    assert "report=" in output


def test_live_smoke_reports_failed_sources_and_keeps_running(tmp_path, monkeypatch, capsys) -> None:
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
            stcn=lambda: (_ for _ in ()).throw(CollectorFetchError("stcn", "timed out")),
        ),
    )

    assert main(["live-smoke", "--source", "all"]) == 0
    output = capsys.readouterr().out
    assert "raw_news=1" in output
    assert "failed_sources=stcn:fetch_error" in output
