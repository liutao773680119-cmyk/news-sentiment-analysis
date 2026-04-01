from __future__ import annotations

from typing import Protocol

from news_sentiment.models import RawNews


class Collector(Protocol):
    def collect(self) -> list[RawNews]:
        ...
