from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CollectFailure:
    source: str
    kind: str
    message: str


class CollectorError(RuntimeError):
    kind = "collector_error"

    def __init__(self, source: str, message: str) -> None:
        super().__init__(message)
        self.source = source
        self.message = message
        self.kind = self.__class__.kind


class CollectorFetchError(CollectorError):
    kind = "fetch_error"


class CollectorParseError(CollectorError):
    kind = "parse_error"


class CollectorEmptyResultError(CollectorError):
    kind = "empty_result"
