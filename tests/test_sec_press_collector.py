from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.sec_press import collect_sec_press_news, parse_sec_press_feed
from news_sentiment.config_loader import load_source_definition_map


def test_parse_sec_press_feed_extracts_rows() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
      <channel>
        <title>Press Releases</title>
        <item>
          <title>SEC Approves Exemptive Order and Proposed Rule Change to Permit Customer Cross-Margining in the U.S. Treasury Market</title>
          <link>https://www.sec.gov/newsroom/press-releases/2026-36-sec-approves-exemptive-order-proposed-rule-change-permit-customer-cross-margining-us-treasury-market</link>
          <description>The Securities and Exchange Commission today issued a conditional exemptive order.</description>
          <pubDate>Wed, 15 Apr 2026 15:45:51 -0400</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_sec_press_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "sec_press-20260415194551-1"
    assert rows[0].source == "sec_press"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-04-15T15:45:51-04:00"
    assert rows[0].title == "SEC Approves Exemptive Order and Proposed Rule Change to Permit Customer Cross-Margining in the U.S. Treasury Market"
    assert rows[0].content == "Summary: The Securities and Exchange Commission today issued a conditional exemptive order."
    assert rows[0].url == "https://www.sec.gov/newsroom/press-releases/2026-36-sec-approves-exemptive-order-proposed-rule-change-permit-customer-cross-margining-us-treasury-market"


def test_collect_sec_press_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <title>Press Releases</title>
        <item>
          <title>SEC Announces Enforcement Results for Fiscal Year 2025</title>
          <link>https://www.sec.gov/newsroom/press-releases/2026-34</link>
          <description>The Securities and Exchange Commission today announced enforcement results for the fiscal year.</description>
          <pubDate>Tue, 07 Apr 2026 15:48:30 -0400</pubDate>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.sec_press.fetch_sec_press_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "sec_press"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_sec_press_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.sec_press.fetch_sec_press_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_sec_press_news()
    except CollectorFetchError as exc:
        assert exc.source == "sec_press"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_sec_press_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.sec_press.fetch_sec_press_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_sec_press_news()
    except CollectorParseError as exc:
        assert exc.source == "sec_press"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_sec_press_source_definition_is_registered() -> None:
    source = load_source_definition_map()["sec_press"]
    assert source.source_type == "policy"
    assert source.enabled is False
