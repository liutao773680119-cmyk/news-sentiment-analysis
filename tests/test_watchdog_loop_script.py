import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_news_sentiment_watchdog_loop.sh"


def test_watchdog_loop_run_once_writes_heartbeat_and_prunes_incidents(tmp_path) -> None:
    log_path = tmp_path / "watch.log"
    lock_dir = tmp_path / "watch.lock"
    heartbeat_path = tmp_path / "heartbeat.json"
    incident_dir = tmp_path / "incidents"
    incident_dir.mkdir()
    for timestamp in ("20260509T010000Z", "20260509T020000Z", "20260509T030000Z"):
        (incident_dir / f"{timestamp}-watchdog.json").write_text("{}", encoding="utf-8")

    env = {
        **os.environ,
        "NEWS_SENTIMENT_WATCH_RUN_ONCE": "1",
        "NEWS_SENTIMENT_WATCH_LOG": str(log_path),
        "NEWS_SENTIMENT_WATCH_LOCK_DIR": str(lock_dir),
        "NEWS_SENTIMENT_WATCH_HEARTBEAT_PATH": str(heartbeat_path),
        "NEWS_SENTIMENT_WATCH_INCIDENT_DIR": str(incident_dir),
        "NEWS_SENTIMENT_WATCH_INCIDENT_RETENTION": "2",
        "NEWS_SENTIMENT_WATCH_REPORT_HEAD_LINES": "0",
        "NEWS_SENTIMENT_WATCH_COMMAND": "printf 'watchdog_status=clean\\nsuspicious_count=0\\n'",
    }

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "watchdog_status=clean" in log_path.read_text(encoding="utf-8")
    heartbeat = json.loads(heartbeat_path.read_text(encoding="utf-8"))
    assert heartbeat["status"] == "completed"
    assert heartbeat["last_exit_code"] == 0
    assert not lock_dir.exists()
    assert sorted(path.name for path in incident_dir.glob("*-watchdog.json")) == [
        "20260509T020000Z-watchdog.json",
        "20260509T030000Z-watchdog.json",
    ]


def test_watchdog_loop_run_once_can_trigger_summary(tmp_path) -> None:
    log_path = tmp_path / "watch.log"
    lock_dir = tmp_path / "watch.lock"
    heartbeat_path = tmp_path / "heartbeat.json"
    summary_marker = tmp_path / "summary.marker"

    env = {
        **os.environ,
        "NEWS_SENTIMENT_WATCH_RUN_ONCE": "1",
        "NEWS_SENTIMENT_WATCH_LOG": str(log_path),
        "NEWS_SENTIMENT_WATCH_LOCK_DIR": str(lock_dir),
        "NEWS_SENTIMENT_WATCH_HEARTBEAT_PATH": str(heartbeat_path),
        "NEWS_SENTIMENT_WATCH_REPORT_HEAD_LINES": "0",
        "NEWS_SENTIMENT_WATCH_COMMAND": "printf 'watchdog_status=clean\\nsuspicious_count=0\\n'",
        "NEWS_SENTIMENT_SUMMARY_INTERVAL_SECONDS": "0",
        "NEWS_SENTIMENT_SUMMARY_COMMAND": f"printf summary_ran > '{summary_marker}'",
    }

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert summary_marker.read_text(encoding="utf-8") == "summary_ran"


def test_watchdog_loop_refuses_second_runner_when_lock_exists(tmp_path) -> None:
    log_path = tmp_path / "watch.log"
    lock_dir = tmp_path / "watch.lock"
    heartbeat_path = tmp_path / "heartbeat.json"
    lock_dir.mkdir()

    env = {
        **os.environ,
        "NEWS_SENTIMENT_WATCH_RUN_ONCE": "1",
        "NEWS_SENTIMENT_WATCH_LOG": str(log_path),
        "NEWS_SENTIMENT_WATCH_LOCK_DIR": str(lock_dir),
        "NEWS_SENTIMENT_WATCH_HEARTBEAT_PATH": str(heartbeat_path),
        "NEWS_SENTIMENT_WATCH_COMMAND": "printf 'should_not_run\\n'",
    }

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 2
    assert "watchdog_status=already_running" in log_path.read_text(encoding="utf-8")
    heartbeat = json.loads(heartbeat_path.read_text(encoding="utf-8"))
    assert heartbeat["status"] == "already_running"
    assert lock_dir.exists()
