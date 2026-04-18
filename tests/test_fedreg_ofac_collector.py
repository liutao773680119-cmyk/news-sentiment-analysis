from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.fedreg_ofac import collect_fedreg_ofac_news, parse_fedreg_ofac_payload
from news_sentiment.config_loader import load_source_definition_map


def test_parse_fedreg_ofac_payload_extracts_rows() -> None:
    payload = {
        "results": [
            {
                "title": "Notice of OFAC Sanctions Action",
                "type": "Notice",
                "abstract": "The Office of Foreign Assets Control is publishing the names of one or more persons that have been placed on the SDN List.",
                "document_number": "2026-07425",
                "html_url": "https://www.federalregister.gov/documents/2026/04/16/2026-07425/notice-of-ofac-sanctions-action",
                "publication_date": "2026-04-16",
            }
        ]
    }

    rows = parse_fedreg_ofac_payload(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "fedreg_ofac-2026-07425"
    assert rows[0].source == "fedreg_ofac"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-04-16T00:00:00+00:00"
    assert rows[0].title == "Notice of OFAC Sanctions Action"
    assert rows[0].content == (
        "Type: Notice\n"
        "Abstract: The Office of Foreign Assets Control is publishing the names of one or more persons that have been placed on the SDN List."
    )
    assert rows[0].url == "https://www.federalregister.gov/documents/2026/04/16/2026-07425/notice-of-ofac-sanctions-action"


def test_collect_fedreg_ofac_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = {
        "results": [
            {
                "title": "Notice of OFAC Sanctions Actions",
                "type": "Notice",
                "abstract": "The Office of Foreign Assets Control is publishing updates to persons currently included on the SDN List.",
                "document_number": "2026-06723",
                "html_url": "https://www.federalregister.gov/documents/2026/04/07/2026-06723/notice-of-ofac-sanctions-actions",
                "publication_date": "2026-04-07",
            }
        ]
    }

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.fedreg_ofac.fetch_fedreg_ofac_payload",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "fedreg_ofac"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_fedreg_ofac_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.fedreg_ofac.fetch_fedreg_ofac_payload",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_fedreg_ofac_news()
    except CollectorFetchError as exc:
        assert exc.source == "fedreg_ofac"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_fedreg_ofac_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.fedreg_ofac.fetch_fedreg_ofac_payload",
        lambda url=None: {"results": []},
    )

    try:
        collect_fedreg_ofac_news()
    except CollectorParseError as exc:
        assert exc.source == "fedreg_ofac"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_fedreg_ofac_source_definition_is_registered() -> None:
    source = load_source_definition_map()["fedreg_ofac"]
    assert source.source_type == "policy"
    assert source.enabled is True
