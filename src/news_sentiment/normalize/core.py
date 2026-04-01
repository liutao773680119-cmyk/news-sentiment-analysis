from __future__ import annotations

from news_sentiment.models import NormalizedNews, RawNews


def normalize_news_items(items: list[RawNews]) -> list[NormalizedNews]:
    normalized = []
    for item in items:
        normalized.append(
            NormalizedNews(
                news_id=item.news_id,
                source=item.source,
                source_type=item.source_type,
                published_at=item.published_at,
                captured_at=item.captured_at,
                title=" ".join(item.title.split()),
                content=" ".join(item.content.split()),
                url=item.url,
            )
        )
    return normalized
