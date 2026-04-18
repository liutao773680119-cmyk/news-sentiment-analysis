from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.fed import collect_fed_news, parse_fed_press_feed
from news_sentiment.config_loader import load_source_definition_map


def test_parse_fed_press_feed_extracts_rows() -> None:
    payload = """<?xml version="1.0" encoding="utf-8" ?>
    <rss version="2.0">
      <channel>
        <title>FRB: Press Release - All Releases</title>
        <item>
          <title>Federal Reserve Board issues enforcement action with Community Bankshares, Inc.</title>
          <link>https://www.federalreserve.gov/newsevents/pressreleases/enforcement20260416a.htm</link>
          <description>Federal Reserve Board issues enforcement action with Community Bankshares, Inc.</description>
          <pubDate>Thu, 16 Apr 2026 15:00:00 GMT</pubDate>
          <category>Enforcement Actions</category>
        </item>
      </channel>
    </rss>
    """

    rows = parse_fed_press_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "fed-20260416150000-1"
    assert rows[0].source == "fed"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-04-16T15:00:00+00:00"
    assert rows[0].title == "Federal Reserve Board issues enforcement action with Community Bankshares, Inc."
    assert rows[0].content == (
        "Category: Enforcement Actions\n"
        "Summary: Federal Reserve Board issues enforcement action with Community Bankshares, Inc."
    )
    assert rows[0].url == "https://www.federalreserve.gov/newsevents/pressreleases/enforcement20260416a.htm"


def test_collect_fed_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="utf-8" ?>
    <rss version="2.0">
      <channel>
        <title>FRB: Press Release - All Releases</title>
        <item>
          <title>Federal Reserve Board announces approval of application by Burke &amp; Herbert Financial Services Corp.</title>
          <link>https://www.federalreserve.gov/newsevents/pressreleases/orders20260410a.htm</link>
          <description>Federal Reserve Board announces approval of application by Burke &amp; Herbert Financial Services Corp.</description>
          <pubDate>Fri, 10 Apr 2026 20:15:00 GMT</pubDate>
          <category>Orders on Banking Applications</category>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.fed.fetch_fed_press_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "fed"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_fed_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.fed.fetch_fed_press_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_fed_news()
    except CollectorFetchError as exc:
        assert exc.source == "fed"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_fed_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.fed.fetch_fed_press_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_fed_news()
    except CollectorParseError as exc:
        assert exc.source == "fed"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_fed_source_definition_is_registered() -> None:
    source = load_source_definition_map()["fed"]
    assert source.source_type == "policy"
    assert source.enabled is True
