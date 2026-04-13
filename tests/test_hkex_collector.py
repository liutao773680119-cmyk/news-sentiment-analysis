from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.hkex import collect_hkex_news, parse_hkex_news_payload
from news_sentiment.config_loader import load_source_definition_map


def test_parse_hkex_news_payload_extracts_rows_and_page_count() -> None:
    payload = """
    {
      "genDate":"1775836800475",
      "maxNumOfFile":2,
      "newsInfoLst":[
        {
          "newsId":12102478,
          "lTxt":"Announcements and Notices - [Very Substantial Disposal / Connected Transaction]",
          "sTxt":"Announcements and Notices - [Very Substantial Disposal / Connected Transaction]",
          "title":"(1) Very Substantial Disposal and Connected Transaction - Disposal of a Subsidiary",
          "ext":"pdf",
          "size":"374KB",
          "webPath":"/listedco/listconews/sehk/2026/0410/2026041001769.pdf",
          "market":"SEHK",
          "multi":0,
          "stock":[{"sc":"01906","sn":"BONNY HLDG"}],
          "relTime":"10/04/2026 22:55",
          "t1Code":"10000",
          "t2Code":"11200,11300"
        }
      ]
    }
    """

    rows, max_num_of_file = parse_hkex_news_payload(payload)
    assert max_num_of_file == 2
    assert len(rows) == 1
    assert rows[0].source == "hkex"
    assert rows[0].source_type == "hard_event"
    assert rows[0].title == "(1) Very Substantial Disposal and Connected Transaction - Disposal of a Subsidiary"
    assert rows[0].published_at == "2026-04-10T22:55:00+08:00"
    assert rows[0].url == "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0410/2026041001769.pdf"


def test_collect_hkex_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload_page_1 = """
    {
      "genDate":"1775836800475",
      "maxNumOfFile":1,
      "newsInfoLst":[
        {
          "newsId":12102472,
          "title":"SUPPLEMENTAL ANNOUNCEMENT CHANGE OF AUDITOR",
          "webPath":"/listedco/listconews/sehk/2026/0410/2026041001763.pdf",
          "stock":[{"sc":"09982","sn":"CENTRALCHINA MT"}],
          "relTime":"10/04/2026 22:49"
        }
      ]
    }
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.hkex.fetch_hkex_news_payload",
        lambda page=1: payload_page_1,
    )
    assert main(["collect", "--source", "hkex"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_hkex_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.hkex.fetch_hkex_news_payload",
        lambda page=1: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_hkex_news()
    except CollectorFetchError as exc:
        assert exc.source == "hkex"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_hkex_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.hkex.fetch_hkex_news_payload",
        lambda page=1: "{\"newsInfoLst\":[]}",
    )

    try:
        collect_hkex_news()
    except CollectorParseError as exc:
        assert exc.source == "hkex"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_hkex_source_definition_is_registered() -> None:
    source = load_source_definition_map()["hkex"]
    assert source.source_type == "hard_event"
    assert source.enabled is False
