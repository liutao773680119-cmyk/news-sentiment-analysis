from __future__ import annotations

import csv
from pathlib import Path

from news_sentiment.models import ThemeMatch


def _reference_path(name: str) -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "reference" / name


def map_themes_to_stocks(themes: list[str]) -> list[ThemeMatch]:
    matches: list[ThemeMatch] = []
    with _reference_path("theme_stock_map.csv").open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["theme_name"] in themes:
                matches.append(
                    ThemeMatch(
                        theme_name=row["theme_name"],
                        stock_code=row["stock_code"],
                        stock_name=row["stock_name"],
                        relation_type=row["relation_type"],
                        weight=float(row["weight"]),
                    )
                )
    return sorted(matches, key=lambda item: item.weight, reverse=True)
