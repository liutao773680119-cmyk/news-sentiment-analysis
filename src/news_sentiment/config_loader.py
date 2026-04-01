from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml


@dataclass(frozen=True)
class ThemeDefinition:
    name: str
    aliases: List[str]
    status: str


@dataclass(frozen=True)
class ThemeRegistry:
    themes: List[ThemeDefinition]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_theme_registry() -> ThemeRegistry:
    path = _project_root() / "data" / "reference" / "theme_registry.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    themes = [
        ThemeDefinition(
            name=item["name"],
            aliases=list(item.get("aliases", [])),
            status=item.get("status", "active"),
        )
        for item in payload.get("themes", [])
    ]
    return ThemeRegistry(themes=themes)
