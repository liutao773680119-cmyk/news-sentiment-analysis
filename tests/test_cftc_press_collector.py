from news_sentiment.cli import main
from news_sentiment.collectors.cftc_press import collect_cftc_press_news, parse_cftc_press_feed
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.config_loader import load_source_definition_map


def test_parse_cftc_press_feed_extracts_rows() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
      <channel>
        <title>Press Releases</title>
        <item>
          <title>CFTC Approves Order to Further Strengthen U.S. Treasury Market Liquidity</title>
          <link>https://www.cftc.gov/PressRoom/PressReleases/9214-26</link>
          <description/>
          <pubDate>Wed, 15 Apr 2026 18:42:19 +0000</pubDate>
        </item>
      </channel>
    </rss>
    """

    rows = parse_cftc_press_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "cftc_press-20260415184219-1"
    assert rows[0].source == "cftc_press"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-04-15T18:42:19+00:00"
    assert rows[0].title == "CFTC Approves Order to Further Strengthen U.S. Treasury Market Liquidity"
    assert rows[0].content == rows[0].title
    assert rows[0].url == "https://www.cftc.gov/PressRoom/PressReleases/9214-26"


def test_collect_cftc_press_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0">
      <channel>
        <title>Press Releases</title>
        <item>
          <title>CFTC Announces Innovation Task Force Staff</title>
          <link>https://www.cftc.gov/PressRoom/PressReleases/9210-26</link>
          <description/>
          <pubDate>Fri, 10 Apr 2026 15:25:20 +0000</pubDate>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.cftc_press.fetch_cftc_press_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "cftc_press"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_cftc_press_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.cftc_press.fetch_cftc_press_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_cftc_press_news()
    except CollectorFetchError as exc:
        assert exc.source == "cftc_press"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_cftc_press_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.cftc_press.fetch_cftc_press_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_cftc_press_news()
    except CollectorParseError as exc:
        assert exc.source == "cftc_press"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_cftc_press_source_definition_is_registered() -> None:
    source = load_source_definition_map()["cftc_press"]
    assert source.source_type == "policy"
    assert source.enabled is False
