from __future__ import annotations

from news_sentiment.models import Event, NormalizedNews


def merge_news_items(items: list[NormalizedNews]) -> list[Event]:
    if not items:
        return []

    groups: list[list[NormalizedNews]] = []
    for item in items:
        target_group = None
        for group in groups:
            if _is_similar(item.title, group[0].title):
                target_group = group
                break
        if target_group is None:
            groups.append([item])
        else:
            target_group.append(item)

    events: list[Event] = []
    for index, group in enumerate(groups, start=1):
        first = min(group, key=lambda item: item.published_at)
        last = max(group, key=lambda item: item.published_at)
        events.append(
            Event(
                event_id=f"event-{index:03d}",
                first_seen_at=first.published_at,
                last_seen_at=last.published_at,
                canonical_title=first.title,
                summary=first.content,
                member_news_ids=[item.news_id for item in group],
                event_type=first.source_type,
                primary_entities=[],
                source_authority_score=0.0,
            )
        )
    return events


def _is_similar(left: str, right: str) -> bool:
    left_chars = {char for char in left if not char.isspace()}
    right_chars = {char for char in right if not char.isspace()}
    if not left_chars or not right_chars:
        return False
    overlap = len(left_chars & right_chars)
    base = min(len(left_chars), len(right_chars))
    return overlap / base >= 0.7
