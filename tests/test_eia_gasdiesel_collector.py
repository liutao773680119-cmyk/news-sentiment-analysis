from news_sentiment.cli import main
from news_sentiment.collectors.eia_gasdiesel import (
    collect_eia_gasdiesel_news,
    parse_eia_gasdiesel_feed,
)
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.config_loader import load_source_definition_map


def test_parse_eia_gasdiesel_feed_extracts_price_update_row() -> None:
    payload = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <rss version="2.0">
      <channel>
        <title>EIA: Gasoline and Diesel Fuel Update</title>
        <item>
          <title>Data For 04/13/26</title>
          <link>http://www.eia.gov/petroleum/gasdiesel/</link>
          <pubDate>Tue, 14 Apr 2026 09:07:55 EST</pubDate>
          <description><![CDATA[
            <br/>Summary Excerpt:<br/>
            Regular Gasoline Retail Price<br/>
            (Dollars per Gallon)<br/>
            4.123  .. U.S.<br/>
            On-Highway Diesel Fuel Retail Price<br/>
            (Dollars  per Gallon)<br/>
            5.608  .. U.S.<br/>
          ]]></description>
        </item>
      </channel>
    </rss>
    """

    rows = parse_eia_gasdiesel_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "eia_gasdiesel-20260414100755"
    assert rows[0].source == "eia_gasdiesel"
    assert rows[0].source_type == "fast_news"
    assert rows[0].published_at == "2026-04-14T10:07:55-04:00"
    assert rows[0].title == "EIA汽柴油零售价更新 美国汽油4.123美元/加仑 美国柴油5.608美元/加仑"
    assert rows[0].content == (
        "美国汽油零售价 4.123 美元/加仑；美国柴油零售价 5.608 美元/加仑。"
        "来源：EIA Gasoline and Diesel Fuel Update"
    )
    assert rows[0].url == "http://www.eia.gov/petroleum/gasdiesel/"


def test_collect_eia_gasdiesel_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="ISO-8859-1" ?>
    <rss version="2.0">
      <channel>
        <item>
          <title>Data For 04/13/26</title>
          <link>http://www.eia.gov/petroleum/gasdiesel/</link>
          <pubDate>Tue, 14 Apr 2026 09:07:55 EST</pubDate>
          <description><![CDATA[
            <br/>Regular Gasoline Retail Price<br/>4.123  .. U.S.<br/>
            On-Highway Diesel Fuel Retail Price<br/>5.608  .. U.S.<br/>
          ]]></description>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.eia_gasdiesel.fetch_eia_gasdiesel_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "eia_gasdiesel"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_eia_gasdiesel_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.eia_gasdiesel.fetch_eia_gasdiesel_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_eia_gasdiesel_news()
    except CollectorFetchError as exc:
        assert exc.source == "eia_gasdiesel"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_eia_gasdiesel_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.eia_gasdiesel.fetch_eia_gasdiesel_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_eia_gasdiesel_news()
    except CollectorParseError as exc:
        assert exc.source == "eia_gasdiesel"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_eia_gasdiesel_source_definition_is_registered() -> None:
    source = load_source_definition_map()["eia_gasdiesel"]
    assert source.source_type == "fast_news"
    assert source.enabled is True
    assert source.timeout_seconds == 20
