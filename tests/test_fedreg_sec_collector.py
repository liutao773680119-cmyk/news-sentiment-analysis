from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.fedreg_sec import collect_fedreg_sec_news, parse_fedreg_sec_payload
from news_sentiment.config_loader import load_source_definition_map


def test_parse_fedreg_sec_payload_extracts_rows() -> None:
    payload = {
        "results": [
            {
                "title": "Concept Release on Consolidated Audit Trail and Other Audit Trails and Data Sources",
                "type": "Proposed Rule",
                "abstract": "The Securities and Exchange Commission is publishing this concept release.",
                "document_number": "2026-07651",
                "html_url": "https://www.federalregister.gov/documents/2026/04/20/2026-07651/concept-release-on-consolidated-audit-trail-and-other-audit-trails-and-data-sources",
                "publication_date": "2026-04-20",
            }
        ]
    }

    rows = parse_fedreg_sec_payload(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "fedreg_sec-2026-07651"
    assert rows[0].source == "fedreg_sec"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-04-20T00:00:00+00:00"
    assert rows[0].title == "Concept Release on Consolidated Audit Trail and Other Audit Trails and Data Sources"
    assert rows[0].content == (
        "Type: Proposed Rule\n"
        "Abstract: The Securities and Exchange Commission is publishing this concept release."
    )
    assert rows[0].url == "https://www.federalregister.gov/documents/2026/04/20/2026-07651/concept-release-on-consolidated-audit-trail-and-other-audit-trails-and-data-sources"


def test_collect_fedreg_sec_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = {
        "results": [
            {
                "title": "Sunshine Act Meetings",
                "type": "Notice",
                "abstract": None,
                "document_number": "2026-07650",
                "html_url": "https://www.federalregister.gov/documents/2026/04/20/2026-07650/sunshine-act-meetings",
                "publication_date": "2026-04-20",
            }
        ]
    }

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.fedreg_sec.fetch_fedreg_sec_payload",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "fedreg_sec"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_fedreg_sec_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.fedreg_sec.fetch_fedreg_sec_payload",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_fedreg_sec_news()
    except CollectorFetchError as exc:
        assert exc.source == "fedreg_sec"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_fedreg_sec_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.fedreg_sec.fetch_fedreg_sec_payload",
        lambda url=None: {"results": []},
    )

    try:
        collect_fedreg_sec_news()
    except CollectorParseError as exc:
        assert exc.source == "fedreg_sec"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_fedreg_sec_source_definition_is_registered() -> None:
    source = load_source_definition_map()["fedreg_sec"]
    assert source.source_type == "policy"
    assert source.enabled is False
