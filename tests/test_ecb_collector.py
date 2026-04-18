from news_sentiment.cli import main
from news_sentiment.collectors.ecb import collect_ecb_news, parse_ecb_press_feed
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.config_loader import load_source_definition_map


def test_parse_ecb_press_feed_extracts_press_release_rows_only() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <title>ECB - European Central Bank</title>
        <item>
          <title>ECB Governing Council urges Single Market boost to strengthen bank competitiveness</title>
          <link>https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260414~ad43db8bb6.en.html</link>
          <description>ECB press release body summary.</description>
          <pubDate>Tue, 14 Apr 2026 11:00:00 +0200</pubDate>
        </item>
        <item>
          <title>Christine Lagarde: IMFC Statement</title>
          <link>https://www.ecb.europa.eu/press/key/date/2026/html/ecb.sp260417~033a4546f5.en.html</link>
          <description>Speech content.</description>
          <pubDate>Fri, 17 Apr 2026 15:00:00 +0200</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_ecb_press_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "ecb-20260414090000-1"
    assert rows[0].source == "ecb"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-04-14T11:00:00+02:00"
    assert rows[0].title == "ECB Governing Council urges Single Market boost to strengthen bank competitiveness"
    assert rows[0].content == "ECB press release body summary."
    assert rows[0].url == "https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260414~ad43db8bb6.en.html"


def test_collect_ecb_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Eurosystem sets out comprehensive strategy for future of European payments</title>
          <link>https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260331~04561d8476.en.html</link>
          <description>ECB launches a press release on European payments.</description>
          <pubDate>Tue, 31 Mar 2026 10:00:00 +0200</pubDate>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.ecb.fetch_ecb_press_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "ecb"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_ecb_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.ecb.fetch_ecb_press_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_ecb_news()
    except CollectorFetchError as exc:
        assert exc.source == "ecb"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_ecb_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.ecb.fetch_ecb_press_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_ecb_news()
    except CollectorParseError as exc:
        assert exc.source == "ecb"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_ecb_source_definition_is_registered() -> None:
    source = load_source_definition_map()["ecb"]
    assert source.source_type == "policy"
    assert source.enabled is False
