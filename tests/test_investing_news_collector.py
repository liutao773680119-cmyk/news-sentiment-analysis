from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.investing_news import (
    collect_investing_news,
    parse_investing_news_feed,
)
from news_sentiment.config_loader import load_source_definition_map


def test_parse_investing_news_feed_extracts_rows() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <title>Investing.com Stock Market News</title>
        <item>
          <title>Tesla expands robotaxi service to Dallas, Houston</title>
          <link>https://www.investing.com/news/stock-market-news/tesla-rolls-out-robotaxis-in-dallas-and-houston-4622171</link>
          <description>Tesla expands robotaxi service to Dallas and Houston.</description>
          <pubDate>Sun, 19 Apr 2026 00:05:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_investing_news_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "investing_news-20260419000500-1"
    assert rows[0].source == "investing_news"
    assert rows[0].source_type == "fast_news"
    assert rows[0].published_at == "2026-04-19T00:05:00+00:00"
    assert rows[0].title == "Tesla expands robotaxi service to Dallas, Houston"
    assert rows[0].content == "Summary: Tesla expands robotaxi service to Dallas and Houston."
    assert (
        rows[0].url
        == "https://www.investing.com/news/stock-market-news/tesla-rolls-out-robotaxis-in-dallas-and-houston-4622171"
    )


def test_parse_investing_news_feed_accepts_iso_like_pubdate() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Russia stocks lower at close of trade; MOEX Russia Index unchanged</title>
          <link>https://www.investing.com/news/stock-market-news/russia-stocks-lower-at-close-of-trade-moex-russia-index-unchanged-4622176</link>
          <pubDate>2026-04-18 21:20:03</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_investing_news_feed(payload)
    assert len(rows) == 1
    assert rows[0].published_at == "2026-04-18T21:20:03+00:00"


def test_collect_investing_news_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Merchant vessels report gunfire as they attempt to cross Hormuz, shipping sources say</title>
          <link>https://www.investing.com/news/stock-market-news/merchant-vessels-report-gunfire-4622148</link>
          <description>Shipping sources report gunfire near Hormuz.</description>
          <pubDate>Sun, 19 Apr 2026 00:10:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.investing_news.fetch_investing_news_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "investing_news"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_investing_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.investing_news.fetch_investing_news_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_investing_news()
    except CollectorFetchError as exc:
        assert exc.source == "investing_news"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_investing_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.investing_news.fetch_investing_news_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_investing_news()
    except CollectorParseError as exc:
        assert exc.source == "investing_news"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_investing_news_source_definition_is_registered() -> None:
    source = load_source_definition_map()["investing_news"]
    assert source.source_type == "fast_news"
    assert source.enabled is False
