from __future__ import annotations

import json
from pathlib import Path


def _reference_path(name: str) -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "reference" / name


def match_historical_events(themes: list[str]) -> list[dict]:
    matches: list[dict] = []
    with _reference_path("historical_events.jsonl").open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            if set(payload.get("themes", [])) & set(themes):
                matches.append(payload)
    return matches
