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


@dataclass(frozen=True)
class ScoringConfig:
    trigger_score: float
    source_authority_weight: float
    freshness_weight: float
    policy_boost_weight: float
    theme_expansion_weight: float


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


def load_scoring_config() -> ScoringConfig:
    path = _project_root() / "configs" / "scoring.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    thresholds = payload.get("thresholds", {})
    weights = payload.get("weights", {})
    return ScoringConfig(
        trigger_score=float(thresholds.get("trigger_score", 70)),
        source_authority_weight=float(weights.get("source_authority", 30)),
        freshness_weight=float(weights.get("freshness", 20)),
        policy_boost_weight=float(weights.get("policy_boost", 25)),
        theme_expansion_weight=float(weights.get("theme_expansion", 25)),
    )
