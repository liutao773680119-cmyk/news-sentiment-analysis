from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def raw_news_path(self) -> Path:
        return self.data_dir / "raw" / "raw_news.jsonl"

    @property
    def normalized_news_path(self) -> Path:
        return self.data_dir / "normalized" / "normalized_news.jsonl"

    @property
    def events_path(self) -> Path:
        return self.data_dir / "events" / "events.jsonl"

    @classmethod
    def discover(cls, cwd: Path | None = None) -> "ProjectPaths":
        return cls(root=(cwd or Path.cwd()))
