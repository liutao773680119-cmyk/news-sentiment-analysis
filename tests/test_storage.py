from news_sentiment.models import RawNews
from news_sentiment.storage import JsonlStore


def test_jsonl_store_round_trip(tmp_path) -> None:
    store = JsonlStore(tmp_path / "raw.jsonl", RawNews)
    record = RawNews(
        news_id="n1",
        source="fixture",
        source_type="fast_news",
        published_at="2026-04-01T09:30:00+08:00",
        captured_at="2026-04-01T09:31:00+08:00",
        title="title",
        content="body",
        url="https://example.com/1",
    )
    store.write_many([record])
    loaded = store.read_all()
    assert loaded == [record]
