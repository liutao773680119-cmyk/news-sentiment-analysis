from __future__ import annotations

from news_sentiment.config_loader import load_source_priority_map
from news_sentiment.models import Event, NormalizedNews


def merge_news_items(items: list[NormalizedNews]) -> list[Event]:
    if not items:
        return []

    source_priorities = load_source_priority_map()
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
        authoritative = max(
            group,
            key=lambda item: (
                source_priorities.get(item.source, 0),
                item.published_at,
            ),
        )
        authority_priority = source_priorities.get(authoritative.source, 0)
        events.append(
            Event(
                event_id=f"event-{index:03d}",
                first_seen_at=first.published_at,
                last_seen_at=last.published_at,
                canonical_title=authoritative.title,
                summary=authoritative.content,
                source=authoritative.source,
                published_at=authoritative.published_at,
                url=authoritative.url,
                member_news_ids=[item.news_id for item in group],
                event_type=authoritative.source_type,
                primary_entities=[],
                source_authority_score=authority_priority / 100.0,
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
