from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError
from news_sentiment.collectors.sse import collect_sse_news, parse_sse_news_payload
from news_sentiment.config_loader import load_source_definition_map


def test_parse_sse_news_payload_extracts_bulletin_rows() -> None:
    payload = """
    jsonpCallbackNewsSentiment({
      "result": [[
        {
          "SECURITY_CODE": "603019",
          "SECURITY_NAME": "中科曙光",
          "TITLE": "中科曙光关于签署算力合作协议的公告",
          "URL": "/disclosure/listedinfo/announcement/c/new/2026-04-02/603019_20260402_A.pdf",
          "BULLETIN_TYPE_DESC": "临时公告",
          "SSEDATE": "2026-04-02"
        }
      ]]
    })
    """
    rows = parse_sse_news_payload(payload)
    assert len(rows) == 1
    assert rows[0].source == "sse"
    assert rows[0].source_type == "hard_event"
    assert rows[0].title == "中科曙光关于签署算力合作协议的公告"
    assert rows[0].url == "https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-04-02/603019_20260402_A.pdf"


def test_collect_sse_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """
    jsonpCallbackNewsSentiment({
      "result": [[
        {
          "SECURITY_CODE": "603019",
          "SECURITY_NAME": "中科曙光",
          "TITLE": "中科曙光关于签署算力合作协议的公告",
          "URL": "/disclosure/listedinfo/announcement/c/new/2026-04-02/603019_20260402_A.pdf",
          "BULLETIN_TYPE_DESC": "临时公告",
          "SSEDATE": "2026-04-02"
        }
      ]]
    })
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.sse.fetch_sse_news_payload",
        lambda: payload,
    )
    assert main(["collect", "--source", "sse"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_sse_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.sse.fetch_sse_news_payload",
        lambda: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_sse_news()
    except CollectorFetchError as exc:
        assert exc.source == "sse"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_sse_news_returns_empty_rows_on_empty_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.sse.fetch_sse_news_payload",
        lambda: "jsonpCallbackNewsSentiment({\"result\": []})",
    )

    rows = collect_sse_news()
    assert rows == []


def test_sse_source_definition_is_registered() -> None:
    source = load_source_definition_map()["sse"]
    assert source.source_type == "hard_event"
    assert source.enabled is True


def test_parse_sse_news_payload_accepts_current_nested_result_shape() -> None:
    payload = """
    jsonpCallbackNewsSentiment({
      "result": [
        [
          {
            "SECURITY_CODE": "600025",
            "SECURITY_NAME": "华能水电",
            "TITLE": "2026年一季度发电量完成情况公告",
            "URL": "/disclosure/listedinfo/announcement/c/new/2026-04-10/600025_20260410_717G.pdf",
            "SSEDATE": "2026-04-10"
          }
        ],
        [
          {
            "SECURITY_CODE": "600019",
            "SECURITY_NAME": "宝钢股份",
            "TITLE": "宝钢股份2026年第一次临时股东会会议资料",
            "URL": "/disclosure/listedinfo/announcement/c/new/2026-04-10/600019_20260410_YD3D.pdf",
            "SSEDATE": "2026-04-10"
          }
        ]
      ]
    })
    """

    rows = parse_sse_news_payload(payload)
    assert [row.title for row in rows] == [
        "2026年一季度发电量完成情况公告",
        "宝钢股份2026年第一次临时股东会会议资料",
    ]
