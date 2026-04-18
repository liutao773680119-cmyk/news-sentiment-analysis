from news_sentiment.cli import main
from news_sentiment.collectors.boc_press import collect_boc_press_news, parse_boc_press_feed
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.config_loader import load_source_definition_map


def test_parse_boc_press_feed_extracts_press_release_rows() -> None:
    payload = """<?xml version="1.0"?>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns="http://purl.org/rss/1.0/"
             xmlns:dc="http://purl.org/dc/elements/1.1/">
      <channel rdf:about="https://www.bankofcanada.ca/content_type/press-releases/feed/">
        <title>Press Releases - Bank of Canada</title>
      </channel>
      <item rdf:about="https://www.bankofcanada.ca/2026/03/fad-press-release-2026-03-18/">
        <title>Bank of Canada maintains policy rate at 2 1/4%</title>
        <link>https://www.bankofcanada.ca/2026/03/fad-press-release-2026-03-18/</link>
        <description>The Bank of Canada today held its target for the overnight rate at 2.25%.</description>
        <dc:date>2026-03-18T09:47:23+00:00</dc:date>
        <dc:language>en</dc:language>
      </item>
    </rdf:RDF>
    """

    rows = parse_boc_press_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "boc_press-20260318094723-1"
    assert rows[0].source == "boc_press"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-03-18T09:47:23+00:00"
    assert rows[0].title == "Bank of Canada maintains policy rate at 2 1/4%"
    assert rows[0].content == "The Bank of Canada today held its target for the overnight rate at 2.25%."
    assert rows[0].url == "https://www.bankofcanada.ca/2026/03/fad-press-release-2026-03-18/"


def test_collect_boc_press_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0"?>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns="http://purl.org/rss/1.0/"
             xmlns:dc="http://purl.org/dc/elements/1.1/">
      <channel rdf:about="https://www.bankofcanada.ca/content_type/press-releases/feed/">
        <title>Press Releases - Bank of Canada</title>
      </channel>
      <item rdf:about="https://www.bankofcanada.ca/2026/03/changes-bank-of-canada-governing-council/">
        <title>Changes to Bank of Canada Governing Council</title>
        <link>https://www.bankofcanada.ca/2026/03/changes-bank-of-canada-governing-council/</link>
        <description>The Bank of Canada announced today the departure of Deputy Governor Rhys Mendes.</description>
        <dc:date>2026-03-23T13:00:55+00:00</dc:date>
        <dc:language>en</dc:language>
      </item>
    </rdf:RDF>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.boc_press.fetch_boc_press_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "boc_press"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_boc_press_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.boc_press.fetch_boc_press_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_boc_press_news()
    except CollectorFetchError as exc:
        assert exc.source == "boc_press"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_boc_press_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.boc_press.fetch_boc_press_feed",
        lambda url=None: "<?xml version='1.0'?><rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'></rdf:RDF>",
    )

    try:
        collect_boc_press_news()
    except CollectorParseError as exc:
        assert exc.source == "boc_press"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_boc_press_source_definition_is_registered() -> None:
    source = load_source_definition_map()["boc_press"]
    assert source.source_type == "policy"
    assert source.enabled is True
