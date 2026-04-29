from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml


@dataclass(frozen=True)
class ThemeDefinition:
    name: str
    aliases: List[str]
    match_name: bool
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
    market_event_boost_weight: float
    theme_expansion_weight: float


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    name: str
    source_type: str
    enabled: bool
    priority: int
    timeout_seconds: int
    user_agent: str
    no_proxy_hosts: tuple[str, ...]
    retry_count: int
    backoff_seconds: float


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_theme_registry() -> ThemeRegistry:
    path = _project_root() / "data" / "reference" / "theme_registry.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    themes = [
        ThemeDefinition(
            name=item["name"],
            aliases=list(item.get("aliases", [])),
            match_name=bool(item.get("match_name", True)),
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
        market_event_boost_weight=float(weights.get("market_event_boost", 30)),
        theme_expansion_weight=float(weights.get("theme_expansion", 25)),
    )


def load_source_definitions() -> list[SourceDefinition]:
    path = _project_root() / "configs" / "sources.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [
        SourceDefinition(
            source_id=item["id"],
            name=item["name"],
            source_type=item["type"],
            enabled=bool(item.get("enabled", True)),
            priority=int(item.get("priority", 0)),
            timeout_seconds=int(item.get("timeout_seconds", 10)),
            user_agent=str(item.get("user_agent", "news-sentiment-mvp/0.1")),
            no_proxy_hosts=tuple(str(host) for host in item.get("no_proxy_hosts", [])),
            retry_count=int(item.get("retry_count", 0)),
            backoff_seconds=float(item.get("backoff_seconds", 0.0)),
        )
        for item in payload.get("sources", [])
    ]


def load_source_priority_map() -> dict[str, int]:
    return {item.source_id: item.priority for item in load_source_definitions()}


def load_source_definition_map() -> dict[str, SourceDefinition]:
    return {item.source_id: item for item in load_source_definitions()}
