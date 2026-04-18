from news_sentiment.cli import main
from news_sentiment.collectors.boe import collect_boe_news, parse_boe_news_feed
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.config_loader import load_source_definition_map


def test_parse_boe_news_feed_extracts_news_rows_only() -> None:
    payload = """<rss version="2.0">
      <channel>
        <title>News</title>
        <item>
          <guid isPermaLink="false">{1}</guid>
          <link>https://www.bankofengland.co.uk/news/2026/april/boe-enhances-resolution-readiness-with-updated-operational-guides</link>
          <title>Bank of England enhances resolution readiness with updated operational guides</title>
          <description>The Bank of England has today published new and updated guidance on how the Bank might implement the UK’s resolution regime in the event of a bank failure.</description>
          <pubDate>Mon, 13 Apr 2026 11:00:00 +0100</pubDate>
        </item>
        <item>
          <guid isPermaLink="false">{2}</guid>
          <link>https://www.bankofengland.co.uk/minutes/2026/march/sonia-stakeholder-advisory-group-24-march-2026</link>
          <title>Minutes of the SONIA Stakeholder Advisory Group - 24 March 2026</title>
          <description>Minutes content.</description>
          <pubDate>Fri, 17 Apr 2026 16:20:02 +0100</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_boe_news_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "boe-20260413100000-1"
    assert rows[0].source == "boe"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-04-13T11:00:00+01:00"
    assert rows[0].title == "Bank of England enhances resolution readiness with updated operational guides"
    assert rows[0].content == (
        "The Bank of England has today published new and updated guidance on how the Bank might implement the UK’s resolution regime in the event of a bank failure."
    )
    assert rows[0].url == "https://www.bankofengland.co.uk/news/2026/april/boe-enhances-resolution-readiness-with-updated-operational-guides"


def test_collect_boe_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<rss version="2.0">
      <channel>
        <item>
          <guid isPermaLink="false">{1}</guid>
          <link>https://www.bankofengland.co.uk/news/2026/april/changes-to-publication-dates-of-the-decision-maker-panel-data-and-agents-summary</link>
          <title>Changes to publication dates of the Decision Maker Panel data and Agents’ summary of business conditions</title>
          <description>We are changing the publication dates of the Decision Maker Panel and Agents’ summary of business conditions.</description>
          <pubDate>Thu, 02 Apr 2026 09:30:00 +0100</pubDate>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.boe.fetch_boe_news_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "boe"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_boe_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.boe.fetch_boe_news_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_boe_news()
    except CollectorFetchError as exc:
        assert exc.source == "boe"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_boe_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.boe.fetch_boe_news_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_boe_news()
    except CollectorParseError as exc:
        assert exc.source == "boe"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_boe_source_definition_is_registered() -> None:
    source = load_source_definition_map()["boe"]
    assert source.source_type == "policy"
    assert source.enabled is False
