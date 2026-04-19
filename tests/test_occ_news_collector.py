from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.occ_news import collect_occ_news, parse_occ_news_feed
from news_sentiment.config_loader import load_source_definition_map


def test_parse_occ_news_feed_extracts_rows() -> None:
    payload = """<?xml version="1.0" encoding="Windows-1252" ?>
    <rss version="2.0">
      <channel>
        <title>OCC News</title>
        <item>
          <title>OCC Announces Enforcement Actions for April 2026</title>
          <description>The Office of the Comptroller of the Currency (OCC) today released enforcement actions for April 2026.</description>
          <pubDate>16 Apr 2026 11:00:00 -0400</pubDate>
          <link>https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-28.html</link>
        </item>
      </channel>
    </rss>
    """

    rows = parse_occ_news_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "occ_news-20260416150000-1"
    assert rows[0].source == "occ_news"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-04-16T11:00:00-04:00"
    assert rows[0].title == "OCC Announces Enforcement Actions for April 2026"
    assert rows[0].content == "Summary: The Office of the Comptroller of the Currency (OCC) today released enforcement actions for April 2026."
    assert rows[0].url == "https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-28.html"


def test_collect_occ_news_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="Windows-1252" ?>
    <rss version="2.0">
      <channel>
        <title>OCC News</title>
        <item>
          <title>OCC Issues Final Rule to Rescind Recovery Planning Guidelines</title>
          <description>The Office of the Comptroller of the Currency (OCC) today announced a final rule to rescind its recovery planning guidelines.</description>
          <pubDate>31 Mar 2026 11:00:00 -0400</pubDate>
          <link>https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-21.html</link>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.occ_news.fetch_occ_news_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "occ_news"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_occ_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.occ_news.fetch_occ_news_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_occ_news()
    except CollectorFetchError as exc:
        assert exc.source == "occ_news"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_occ_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.occ_news.fetch_occ_news_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_occ_news()
    except CollectorParseError as exc:
        assert exc.source == "occ_news"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_occ_news_source_definition_is_registered() -> None:
    source = load_source_definition_map()["occ_news"]
    assert source.source_type == "policy"
    assert source.enabled is False
