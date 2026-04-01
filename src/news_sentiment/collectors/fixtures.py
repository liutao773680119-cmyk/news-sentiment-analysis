from __future__ import annotations

from news_sentiment.models import RawNews


def collect_fixture_news() -> list[RawNews]:
    return [
        RawNews(
            news_id="fixture-001",
            source="fixture",
            source_type="policy",
            published_at="2026-04-01T09:30:00+08:00",
            captured_at="2026-04-01T09:31:00+08:00",
            title="工信部发布算力基础设施支持政策",
            content="工信部发布文件，支持算力基础设施建设和智算中心发展。",
            url="https://example.com/fixture-001",
        )
    ]
