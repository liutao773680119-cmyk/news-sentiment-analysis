from news_sentiment.cli import main
from news_sentiment.collectors.boj import collect_boj_news, parse_boj_policy_feed
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.config_loader import load_source_definition_map


def test_parse_boj_policy_feed_extracts_policy_rows_only() -> None:
    payload = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <title>日本銀行：RSS</title>
        <item>
          <title>金融政策決定会合における主な意見（3月18、19日開催分）</title>
          <description></description>
          <pubDate>Mon, 30 Mar 2026 08:50:00 +0900</pubDate>
          <link>http://www.boj.or.jp/mopo/mpmsche_minu/opinion_2026/opi260319.pdf</link>
          <guid>http://www.boj.or.jp/mopo/mpmsche_minu/opinion_2026/opi260319.pdf</guid>
        </item>
        <item>
          <title>金融政策手段における新規選定先の公表</title>
          <description></description>
          <pubDate>Tue, 01 Apr 2026 12:00:00 +0900</pubDate>
          <link>http://www.boj.or.jp/mopo/measures/select/s_release/srel260401a.pdf</link>
          <guid>http://www.boj.or.jp/mopo/measures/select/s_release/srel260401a.pdf</guid>
        </item>
      </channel>
    </rss>
    """

    rows = parse_boj_policy_feed(payload)
    assert len(rows) == 1
    assert rows[0].news_id == "boj-20260329235000-1"
    assert rows[0].source == "boj"
    assert rows[0].source_type == "policy"
    assert rows[0].published_at == "2026-03-30T08:50:00+09:00"
    assert rows[0].title == "金融政策決定会合における主な意見（3月18、19日開催分）"
    assert rows[0].content == "金融政策決定会合における主な意見（3月18、19日開催分）"
    assert rows[0].url == "http://www.boj.or.jp/mopo/mpmsche_minu/opinion_2026/opi260319.pdf"


def test_collect_boj_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>金融政策決定会合議事要旨（1月22、23日開催分）</title>
          <description></description>
          <pubDate>Wed, 25 Mar 2026 08:50:00 +0900</pubDate>
          <link>http://www.boj.or.jp/mopo/mpmsche_minu/minu_2026/g260123.pdf</link>
          <guid>http://www.boj.or.jp/mopo/mpmsche_minu/minu_2026/g260123.pdf</guid>
        </item>
      </channel>
    </rss>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.boj.fetch_boj_policy_feed",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "boj"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_boj_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.boj.fetch_boj_policy_feed",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_boj_news()
    except CollectorFetchError as exc:
        assert exc.source == "boj"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_boj_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.boj.fetch_boj_policy_feed",
        lambda url=None: "<?xml version='1.0'?><rss><channel></channel></rss>",
    )

    try:
        collect_boj_news()
    except CollectorParseError as exc:
        assert exc.source == "boj"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_boj_source_definition_is_registered() -> None:
    source = load_source_definition_map()["boj"]
    assert source.source_type == "policy"
    assert source.enabled is True
