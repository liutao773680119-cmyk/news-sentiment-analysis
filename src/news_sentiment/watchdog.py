from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from news_sentiment.cli import (
    LiveSmokeStatus,
    SuspiciousCandidate,
    collect_from_source,
    collect_suspicious_candidates,
    execute_live_smoke,
    format_collect_failures,
    format_live_smoke_status,
)
from news_sentiment.collectors import CollectorError
from news_sentiment.settings import ProjectPaths


WATCHDOG_NOTIFICATION_TITLE = "news-sentiment-watchdog"


@dataclass(frozen=True)
class SourceProbeResult:
    source: str
    status: str
    rows: int


def run_watchdog_once(paths: ProjectPaths, source: str, limit: int) -> int:
    initial_status = execute_live_smoke(paths, source)
    initial_suspicious = collect_suspicious_candidates(paths)
    if not initial_status.failed_sources and not initial_suspicious:
        print("watchdog_status=clean")
        print(format_live_smoke_status(initial_status))
        print("suspicious_count=0")
        return 0

    probes = _probe_failed_sources(initial_status.failed_sources)
    rerun_attempted = bool(initial_status.failed_sources) and not initial_suspicious and all(
        probe.status == "ok" for probe in probes
    )
    rerun_status = None
    rerun_suspicious: list[SuspiciousCandidate] = []
    final_status = initial_status
    final_suspicious = initial_suspicious
    if rerun_attempted:
        rerun_status = execute_live_smoke(paths, source)
        rerun_suspicious = collect_suspicious_candidates(paths)
        final_status = rerun_status
        final_suspicious = rerun_suspicious

    watchdog_status = "alert"
    if rerun_attempted and not final_status.failed_sources and not final_suspicious:
        watchdog_status = "recovered"

    incident_path = _write_incident_snapshot(
        paths=paths,
        initial_status=initial_status,
        initial_suspicious=initial_suspicious,
        probes=probes,
        rerun_attempted=rerun_attempted,
        rerun_status=rerun_status,
        rerun_suspicious=rerun_suspicious,
        final_status=final_status,
        final_suspicious=final_suspicious,
        limit=limit,
    )
    send_desktop_notification(
        WATCHDOG_NOTIFICATION_TITLE,
        _build_notification_message(
            watchdog_status=watchdog_status,
            initial_status=initial_status,
            initial_suspicious=initial_suspicious,
            final_status=final_status,
            final_suspicious=final_suspicious,
        ),
    )

    print(f"watchdog_status={watchdog_status}")
    print(format_live_smoke_status(final_status))
    print(f"suspicious_count={len(final_suspicious)}")
    print(f"incident_path={incident_path}")
    print(f"initial_failed_sources={format_collect_failures(initial_status.failed_sources)}")
    print(f"initial_suspicious_count={len(initial_suspicious)}")
    if probes:
        print(f"probe_results={_format_probe_results(probes)}")
    print(f"rerun_attempted={_bool_token(rerun_attempted)}")
    if rerun_attempted:
        assert rerun_status is not None
        print(f"rerun_failed_sources={format_collect_failures(rerun_status.failed_sources)}")
        print(f"rerun_suspicious_count={len(rerun_suspicious)}")
    return 0


def send_desktop_notification(title: str, message: str) -> bool:
    script = f'display notification "{_escape_applescript(message)}" with title "{_escape_applescript(title)}"'
    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return False
    return True


def _probe_failed_sources(failures: list) -> list[SourceProbeResult]:
    probes = []
    for failure in failures:
        try:
            result = collect_from_source(failure.source)
        except CollectorError as exc:
            probes.append(SourceProbeResult(source=exc.source, status=exc.kind, rows=0))
            continue
        except Exception:
            probes.append(
                SourceProbeResult(source=failure.source, status="unexpected_error", rows=0)
            )
            continue
        probes.append(SourceProbeResult(source=failure.source, status="ok", rows=len(result.rows)))
    return probes


def _write_incident_snapshot(
    *,
    paths: ProjectPaths,
    initial_status: LiveSmokeStatus,
    initial_suspicious: list[SuspiciousCandidate],
    probes: list[SourceProbeResult],
    rerun_attempted: bool,
    rerun_status: LiveSmokeStatus | None,
    rerun_suspicious: list[SuspiciousCandidate],
    final_status: LiveSmokeStatus,
    final_suspicious: list[SuspiciousCandidate],
    limit: int,
) -> Path:
    incident_dir = paths.data_dir / "monitoring" / "incidents"
    incident_dir.mkdir(parents=True, exist_ok=True)
    incident_path = incident_dir / f"{_incident_timestamp()}-watchdog.json"
    incident_path.write_text(
        json.dumps(
            {
                "initial": _status_payload(initial_status, initial_suspicious, limit),
                "probes": [_probe_payload(probe) for probe in probes],
                "rerun": _rerun_payload(rerun_attempted, rerun_status, rerun_suspicious, limit),
                "final": _status_payload(final_status, final_suspicious, limit),
                "report_head": _read_report_head(paths.latest_report_path),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return incident_path


def _status_payload(
    status: LiveSmokeStatus,
    suspicious: list[SuspiciousCandidate],
    limit: int,
) -> dict[str, object]:
    return {
        "raw_news": status.raw_count,
        "normalized_news": status.normalized_count,
        "events": status.event_count,
        "analyses": status.analysis_count,
        "failed_sources": _failure_tokens(status.failed_sources),
        "suspicious_count": len(suspicious),
        "suspicious_titles": [candidate.event.canonical_title for candidate in suspicious[: max(limit, 0)]],
        "report_path": str(status.report_path),
    }


def _rerun_payload(
    rerun_attempted: bool,
    rerun_status: LiveSmokeStatus | None,
    rerun_suspicious: list[SuspiciousCandidate],
    limit: int,
) -> dict[str, object]:
    if not rerun_attempted or rerun_status is None:
        return {"attempted": False}
    payload = _status_payload(rerun_status, rerun_suspicious, limit)
    payload["attempted"] = True
    return payload


def _probe_payload(probe: SourceProbeResult) -> dict[str, object]:
    return {"source": probe.source, "status": probe.status, "rows": probe.rows}


def _failure_tokens(failures: list) -> list[str]:
    return [f"{failure.source}:{failure.kind}" for failure in failures]


def _format_probe_results(probes: list[SourceProbeResult]) -> str:
    return ",".join(f"{probe.source}:{probe.status}:{probe.rows}" for probe in probes)


def _read_report_head(report_path: Path, max_lines: int = 80) -> list[str]:
    if not report_path.exists():
        return []
    return report_path.read_text(encoding="utf-8").splitlines()[:max_lines]


def _build_notification_message(
    *,
    watchdog_status: str,
    initial_status: LiveSmokeStatus,
    initial_suspicious: list[SuspiciousCandidate],
    final_status: LiveSmokeStatus,
    final_suspicious: list[SuspiciousCandidate],
) -> str:
    if watchdog_status == "recovered":
        return (
            f"瞬时异常已自愈: {format_collect_failures(initial_status.failed_sources)} -> "
            f"{format_collect_failures(final_status.failed_sources)}"
        )
    parts = []
    if final_status.failed_sources:
        parts.append(f"failed_sources={format_collect_failures(final_status.failed_sources)}")
    if final_suspicious:
        parts.append(f"suspicious_count={len(final_suspicious)}")
    if not parts:
        parts.append(f"initial_suspicious_count={len(initial_suspicious)}")
    return " ".join(parts)


def _incident_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _bool_token(value: bool) -> str:
    return "true" if value else "false"


def _escape_applescript(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')
