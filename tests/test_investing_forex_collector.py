from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.investing_forex import (
    collect_investing_forex_news,
    parse_investing_forex_feed,
)
from news_sentiment.config_loader import load_source_definition_map


def test_parse_investing_forex_feed_extracts_rows() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <title>Forex News</title>
        <item>
          <title>Goldman Sachs lowers EUR/HUF forecast on deeper rate cut bets</title>
          <link>https://www.investing.com/news/forex-news/goldman-sachs-lowers-eurhuf-forecast-4629001</link>
          <description>Goldman Sachs lowers EUR/HUF forecast on deeper rate cut bets.</description>
          <pubDate>Sun, 19 Apr 2026 03:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_investing_forex_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "investing_forex-20260419030000-1"
    assert rows[0].source == "investing_forex"
    assert rows[0].source_type == "fast_news"
    assert rows[0].published_at == "2026-04-19T03:00:00+00:00"
    assert rows[0].title == "Goldman Sachs lowers EUR/HUF forecast on deeper rate cut bets"
    assert rows[0].content == "Summary: Goldman Sachs lowers EUR/HUF forecast on deeper rate cut bets."
    assert rows[0].url == "https://www.investing.com/news/forex-news/goldman-sachs-lowers-eurhuf-forecast-4629001"


def test_parse_investing_forex_feed_accepts_iso_like_pubdate() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Dollar steadies after volatile session</title>
          <link>https://www.investing.com/news/forex-news/dollar-steadies-4629002</link>
          <pubDate>2026-04-19 03:10:00</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_investing_forex_feed(payload)
    assert len(rows) == 1
    assert rows[0].published_at == "2026-04-19T03:10:00+00:00"


def test_collect_investing_forex_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Yen firms as traders reassess rate path</title>
          <link>https://www.investing.com/news/forex-news/yen-firms-4629003</link>
          <description>Yen firms as traders reassess rate path.</description>
          <pubDate>Sun, 19 Apr 2026 03:15:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.investing_forex.fetch_investing_forex_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "investing_forex"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_investing_forex_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.investing_forex.fetch_investing_forex_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_investing_forex_news()
    except CollectorFetchError as exc:
        assert exc.source == "investing_forex"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_investing_forex_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.investing_forex.fetch_investing_forex_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_investing_forex_news()
    except CollectorParseError as exc:
        assert exc.source == "investing_forex"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_investing_forex_source_definition_is_registered() -> None:
    source = load_source_definition_map()["investing_forex"]
    assert source.source_type == "fast_news"
    assert source.enabled is True
