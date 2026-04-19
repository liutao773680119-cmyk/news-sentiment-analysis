from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.investing_economic import (
    collect_investing_economic_news,
    parse_investing_economic_feed,
)
from news_sentiment.config_loader import load_source_definition_map


def test_parse_investing_economic_feed_extracts_rows() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <title>Economic Indicators News</title>
        <item>
          <title>Canadian housing starts decrease 6% in March</title>
          <link>https://www.investing.com/news/economic-indicators/canadian-housing-starts-decrease-6-in-march-4630001</link>
          <description>Canadian housing starts decrease 6% in March.</description>
          <pubDate>Sun, 19 Apr 2026 04:20:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_investing_economic_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "investing_economic-20260419042000-1"
    assert rows[0].source == "investing_economic"
    assert rows[0].source_type == "fast_news"
    assert rows[0].published_at == "2026-04-19T04:20:00+00:00"
    assert rows[0].title == "Canadian housing starts decrease 6% in March"
    assert rows[0].content == "Summary: Canadian housing starts decrease 6% in March."
    assert rows[0].url == "https://www.investing.com/news/economic-indicators/canadian-housing-starts-decrease-6-in-march-4630001"


def test_parse_investing_economic_feed_accepts_iso_like_pubdate() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Italy saw modest growth in Q1, central bank estimates</title>
          <link>https://www.investing.com/news/economic-indicators/italy-growth-q1-4630002</link>
          <pubDate>2026-04-19 04:30:00</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_investing_economic_feed(payload)
    assert len(rows) == 1
    assert rows[0].published_at == "2026-04-19T04:30:00+00:00"


def test_collect_investing_economic_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>US tariffs drive steep drop in EU exports for second month</title>
          <link>https://www.investing.com/news/economic-indicators/eu-exports-fall-4630003</link>
          <description>US tariffs drive steep drop in EU exports for second month.</description>
          <pubDate>Sun, 19 Apr 2026 04:35:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.investing_economic.fetch_investing_economic_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "investing_economic"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_investing_economic_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.investing_economic.fetch_investing_economic_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_investing_economic_news()
    except CollectorFetchError as exc:
        assert exc.source == "investing_economic"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_investing_economic_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.investing_economic.fetch_investing_economic_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_investing_economic_news()
    except CollectorParseError as exc:
        assert exc.source == "investing_economic"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_investing_economic_source_definition_is_registered() -> None:
    source = load_source_definition_map()["investing_economic"]
    assert source.source_type == "fast_news"
    assert source.enabled is True
