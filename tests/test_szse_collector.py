from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.szse import collect_szse_news, parse_szse_news_payload
from news_sentiment.config_loader import load_source_definition_map


def test_parse_szse_news_payload_extracts_announcement_rows() -> None:
    payload = """
    {
      "recordCount": 2,
      "data": [
        {
          "secCode": "000977",
          "secName": "浪潮信息",
          "announList": [
            {
              "title": "浪潮信息：关于授权董事会制定中期分红方案的公告",
              "attachPath": "/disc/disk03/finalpage/2026-04-11/f3993889-863c-495f-8178-a479d773adad.PDF",
              "bigCategoryId": "0113",
              "publishTime": "2026-04-11 00:00:00.0"
            },
            {
              "title": "浪潮信息：2025年年度报告摘要",
              "attachPath": "/disc/disk03/finalpage/2026-04-11/3836e036-1b38-46d9-abd6-11fddb109e9d.PDF",
              "bigCategoryId": "010301",
              "publishTime": "2026-04-11 00:00:00.0"
            }
          ]
        }
      ]
    }
    """

    rows = parse_szse_news_payload(payload)
    assert len(rows) == 2
    assert rows[0].source == "szse"
    assert rows[0].source_type == "hard_event"
    assert rows[0].title == "浪潮信息：关于授权董事会制定中期分红方案的公告"
    assert rows[0].published_at == "2026-04-11T00:00:00+08:00"
    assert (
        rows[0].url
        == "https://www.szse.cn/disc/disk03/finalpage/2026-04-11/f3993889-863c-495f-8178-a479d773adad.PDF"
    )


def test_collect_szse_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """
    {
      "recordCount": 1,
      "data": [
        {
          "secCode": "000977",
          "secName": "浪潮信息",
          "announList": [
            {
              "title": "浪潮信息：关于授权董事会制定中期分红方案的公告",
              "attachPath": "/disc/disk03/finalpage/2026-04-11/f3993889-863c-495f-8178-a479d773adad.PDF",
              "publishTime": "2026-04-11 00:00:00.0"
            }
          ]
        }
      ]
    }
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.szse.fetch_szse_news_payload",
        lambda: payload,
    )
    assert main(["collect", "--source", "szse"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_szse_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.szse.fetch_szse_news_payload",
        lambda: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_szse_news()
    except CollectorFetchError as exc:
        assert exc.source == "szse"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_szse_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.szse.fetch_szse_news_payload",
        lambda: "{\"data\":[]}",
    )

    try:
        collect_szse_news()
    except CollectorParseError as exc:
        assert exc.source == "szse"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_szse_source_definition_is_registered() -> None:
    source = load_source_definition_map()["szse"]
    assert source.source_type == "hard_event"
    assert source.enabled is True
