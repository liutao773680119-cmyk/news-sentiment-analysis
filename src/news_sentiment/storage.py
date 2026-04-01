from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Generic, List, Type, TypeVar


T = TypeVar("T")


class JsonlStore(Generic[T]):
    def __init__(self, path: Path, model_cls: Type[T]) -> None:
        self.path = path
        self.model_cls = model_cls

    def write_many(self, records: List[T]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(asdict(record), ensure_ascii=False))
                handle.write("\n")

    def read_all(self) -> List[T]:
        if not self.path.exists():
            return []
        rows: List[T] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                payload = json.loads(line)
                rows.append(self.model_cls(**payload))
        return rows
