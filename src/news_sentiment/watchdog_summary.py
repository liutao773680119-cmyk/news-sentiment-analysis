from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from news_sentiment.settings import ProjectPaths


@dataclass(frozen=True)
class LogIteration:
    started_at: datetime
    status: str


@dataclass(frozen=True)
class ReportHighlight:
    title: str
    event_type: str = ""
    source: str = ""
    direction: str = ""
    impact_score: str = ""
    themes: str = ""
    stock_codes: str = ""


def run_watchdog_summary(
    paths: ProjectPaths,
    *,
    hours: int,
    now: str | None = None,
    log_path: Path | None = None,
    log_timezone: str = "local",
) -> int:
    now_at = _parse_now(now)
    window_start = now_at - timedelta(hours=hours)
    watch_log_path = log_path or Path("/tmp/news-sentiment-watch.log")
    iterations = _read_log_iterations(watch_log_path, window_start, now_at, log_timezone)
    incidents = _read_incidents(paths.data_dir / "monitoring" / "incidents", window_start, now_at)
    report_highlights = _read_report_highlights(paths.latest_report_path)
    summary_path = _write_summary(paths, window_start, now_at, iterations, incidents, report_highlights)
    print(f"summary_path={summary_path}")
    return 0


def _parse_now(now: str | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc).replace(microsecond=0)
    normalized = now.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _read_log_iterations(
    log_path: Path,
    window_start: datetime,
    window_end: datetime,
    log_timezone: str,
) -> list[LogIteration]:
    if not log_path.exists():
        return []

    iterations: list[LogIteration] = []
    current_started_at: datetime | None = None
    current_status: str | None = None
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("===== ") and line.endswith(" ====="):
            if current_started_at is not None and current_status is not None:
                _append_iteration(iterations, current_started_at, current_status, window_start, window_end)
            current_started_at = _parse_log_timestamp(line, log_timezone)
            current_status = None
            continue
        if line.startswith("watchdog_status="):
            current_status = line.split("=", 1)[1].split(" ", 1)[0]
    if current_started_at is not None and current_status is not None:
        _append_iteration(iterations, current_started_at, current_status, window_start, window_end)
    return iterations


def _append_iteration(
    iterations: list[LogIteration],
    started_at: datetime,
    status: str,
    window_start: datetime,
    window_end: datetime,
) -> None:
    if window_start <= started_at <= window_end:
        iterations.append(LogIteration(started_at=started_at, status=status))


def _parse_log_timestamp(line: str, log_timezone: str) -> datetime:
    token = line.removeprefix("===== ").removesuffix(" =====")
    parsed = datetime.strptime(token, "%Y-%m-%d_%H:%M:%S")
    if log_timezone == "utc":
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.replace(tzinfo=datetime.now().astimezone().tzinfo).astimezone(timezone.utc)


def _read_incidents(
    incident_dir: Path,
    window_start: datetime,
    window_end: datetime,
) -> list[dict[str, object]]:
    if not incident_dir.exists():
        return []

    incidents = []
    for incident_path in sorted(incident_dir.glob("*-watchdog.json")):
        incident_at = _parse_incident_timestamp(incident_path.name)
        if incident_at is None or not (window_start <= incident_at <= window_end):
            continue
        try:
            payload = json.loads(incident_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        payload["_path"] = str(incident_path)
        incidents.append(payload)
    return incidents


def _parse_incident_timestamp(name: str) -> datetime | None:
    timestamp = name.split("-", 1)[0]
    try:
        return datetime.strptime(timestamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _write_summary(
    paths: ProjectPaths,
    window_start: datetime,
    window_end: datetime,
    iterations: list[LogIteration],
    incidents: list[dict[str, object]],
    report_highlights: list[ReportHighlight],
) -> Path:
    summary_dir = paths.data_dir / "monitoring" / "summaries"
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_path = summary_dir / f"{window_end.strftime('%Y%m%dT%H%M%SZ')}-summary.md"
    summary_path.write_text(
        _format_summary(window_start, window_end, iterations, incidents, report_highlights),
        encoding="utf-8",
    )
    return summary_path


def _format_summary(
    window_start: datetime,
    window_end: datetime,
    iterations: list[LogIteration],
    incidents: list[dict[str, object]],
    report_highlights: list[ReportHighlight],
) -> str:
    status_counts = Counter(iteration.status for iteration in iterations)
    failed_source_counts: Counter[str] = Counter()
    suspicious_title_counts: Counter[str] = Counter()
    latest_report_head: list[str] = []
    for incident in incidents:
        final = incident.get("final", {})
        if isinstance(final, dict):
            failed_source_counts.update(_as_strings(final.get("failed_sources", [])))
            suspicious_title_counts.update(_as_strings(final.get("suspicious_titles", [])))
        report_head = incident.get("report_head", [])
        if isinstance(report_head, list) and report_head:
            latest_report_head = _as_strings(report_head)[:12]

    lines = [
        "# Watchdog Summary",
        "",
        f"Window: {_iso(window_start)} -> {_iso(window_end)}",
        "",
        "## Status",
        f"- Iterations: {len(iterations)}",
        f"- clean: {status_counts.get('clean', 0)}",
        f"- alert: {status_counts.get('alert', 0)}",
        f"- recovered: {status_counts.get('recovered', 0)}",
        "",
        "## Failed Sources",
    ]
    lines.extend(_counter_lines(failed_source_counts))
    lines.extend(["", "## Suspicious Titles"])
    lines.extend(_counter_lines(suspicious_title_counts))
    lines.extend(["", "## Report Highlights"])
    lines.extend(_report_highlight_lines(report_highlights))
    lines.extend(["", "## Latest Report Head"])
    lines.extend(f"- {line}" for line in latest_report_head if line)
    lines.extend(["", "## Next Step", _next_step(failed_source_counts, suspicious_title_counts), ""])
    return "\n".join(lines)


def _read_report_highlights(report_path: Path, *, limit: int = 10) -> list[ReportHighlight]:
    if not report_path.exists():
        return []

    highlights: list[ReportHighlight] = []
    current: dict[str, str] | None = None
    for line in report_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(("[关注] ", "[温度] ")):
            if current is not None:
                highlights.append(_build_report_highlight(current))
                if len(highlights) >= limit:
                    return highlights
            current = {"title": line}
            continue
        if current is None or ": " not in line:
            continue
        key, value = line.split(": ", 1)
        current[key] = value
    if current is not None and len(highlights) < limit:
        highlights.append(_build_report_highlight(current))
    return highlights


def _build_report_highlight(payload: dict[str, str]) -> ReportHighlight:
    return ReportHighlight(
        title=payload.get("title", ""),
        event_type=payload.get("事件类型", ""),
        source=payload.get("来源", ""),
        direction=payload.get("方向", ""),
        impact_score=payload.get("强度", ""),
        themes=payload.get("题材", ""),
        stock_codes=payload.get("个股", ""),
    )


def _report_highlight_lines(highlights: list[ReportHighlight]) -> list[str]:
    if not highlights:
        return ["- none"]

    lines: list[str] = []
    for item in highlights:
        lines.append(f"- {item.title}")
        lines.extend(
            [
                f"  - 类型: {item.event_type or '未知'}",
                f"  - 来源: {item.source or '未知'}",
                f"  - 方向: {item.direction or '未知'}",
                f"  - 强度: {item.impact_score or '未知'}",
                f"  - 题材: {item.themes or '无'}",
                f"  - 个股: {item.stock_codes or '无'}",
            ]
        )
    return lines


def _counter_lines(counter: Counter[str]) -> list[str]:
    if not counter:
        return ["- none"]
    return [f"- `{item}`: {count}" for item, count in counter.most_common()]


def _next_step(
    failed_source_counts: Counter[str],
    suspicious_title_counts: Counter[str],
) -> str:
    if suspicious_title_counts:
        return "- Review suspicious titles before changing rules."
    if failed_source_counts:
        return "- Check source stability before changing content rules."
    return "- No action required."


def _as_strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
