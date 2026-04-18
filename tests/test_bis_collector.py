from news_sentiment.cli import main
from news_sentiment.collectors.bis import collect_bis_news, parse_bis_press_feed
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.config_loader import load_source_definition_map


def test_parse_bis_press_feed_extracts_rows() -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns="http://purl.org/rss/1.0/"
             xmlns:dc="http://purl.org/dc/elements/1.1/">
      <channel rdf:about="https://www.bis.org/doclist/all_pressrels.rss">
        <title>Press releases</title>
      </channel>
      <item rdf:about="https://www.bis.org/press/p260416.htm">
        <title>CPMI-IOSCO assesses that the United Kingdom has implemented the Principles for financial market infrastructures for two FMI types, but recommends some improvements</title>
        <link>https://www.bis.org/press/p260416.htm</link>
        <description>The UK's framework is complete and consistent with the PFMI in most aspects.</description>
        <dc:date>2026-04-16T12:47:00Z</dc:date>
      </item>
    </rdf:RDF>
    """

    rows = parse_bis_press_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "bis-20260416124700-1"
    assert rows[0].source == "bis"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-04-16T12:47:00+00:00"
    assert rows[0].title.startswith("CPMI-IOSCO assesses")
    assert rows[0].content == "The UK's framework is complete and consistent with the PFMI in most aspects."
    assert rows[0].url == "https://www.bis.org/press/p260416.htm"


def test_collect_bis_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns="http://purl.org/rss/1.0/"
             xmlns:dc="http://purl.org/dc/elements/1.1/">
      <channel rdf:about="https://www.bis.org/doclist/all_pressrels.rss">
        <title>Press releases</title>
      </channel>
      <item rdf:about="https://www.bis.org/press/p260327.htm">
        <title>BIS extends term for John Williams as Chair of the Markets Committee</title>
        <link>https://www.bis.org/press/p260327.htm</link>
        <description>John C. Williams is to continue as Chair of the Markets Committee.</description>
        <dc:date>2026-03-27T09:03:00Z</dc:date>
      </item>
    </rdf:RDF>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.bis.fetch_bis_press_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "bis"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_bis_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.bis.fetch_bis_press_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_bis_news()
    except CollectorFetchError as exc:
        assert exc.source == "bis"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_bis_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.bis.fetch_bis_press_feed",
        lambda url=None: "<?xml version='1.0'?><rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'></rdf:RDF>",
    )

    try:
        collect_bis_news()
    except CollectorParseError as exc:
        assert exc.source == "bis"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_bis_source_definition_is_registered() -> None:
    source = load_source_definition_map()["bis"]
    assert source.source_type == "policy"
    assert source.enabled is True
