#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_PATH="${NEWS_SENTIMENT_WATCH_LOG:-/tmp/news-sentiment-watch.log}"
INTERVAL_SECONDS="${NEWS_SENTIMENT_WATCH_INTERVAL_SECONDS:-600}"
LIMIT="${NEWS_SENTIMENT_WATCH_LIMIT:-10}"
LOCK_DIR="${NEWS_SENTIMENT_WATCH_LOCK_DIR:-$ROOT_DIR/data/monitoring/news-sentiment-watch.lock}"
HEARTBEAT_PATH="${NEWS_SENTIMENT_WATCH_HEARTBEAT_PATH:-$ROOT_DIR/data/monitoring/watchdog_heartbeat.json}"
INCIDENT_DIR="${NEWS_SENTIMENT_WATCH_INCIDENT_DIR:-$ROOT_DIR/data/monitoring/incidents}"
INCIDENT_RETENTION="${NEWS_SENTIMENT_WATCH_INCIDENT_RETENTION:-200}"
REPORT_HEAD_LINES="${NEWS_SENTIMENT_WATCH_REPORT_HEAD_LINES:-80}"
RUN_ONCE="${NEWS_SENTIMENT_WATCH_RUN_ONCE:-0}"
WATCH_COMMAND="${NEWS_SENTIMENT_WATCH_COMMAND:-}"
SUMMARY_ENABLED="${NEWS_SENTIMENT_SUMMARY_ENABLED:-1}"
SUMMARY_INTERVAL_SECONDS="${NEWS_SENTIMENT_SUMMARY_INTERVAL_SECONDS:-21600}"
SUMMARY_HOURS="${NEWS_SENTIMENT_SUMMARY_HOURS:-6}"
SUMMARY_COMMAND="${NEWS_SENTIMENT_SUMMARY_COMMAND:-}"
LAST_SUMMARY_EPOCH="$(date +%s)"

cd "$ROOT_DIR"
export PYTHONPATH=src

write_heartbeat() {
  local status="$1"
  local exit_code="${2:-0}"
  mkdir -p "$(dirname "$HEARTBEAT_PATH")"
  printf '{\n  "updated_at": "%s",\n  "pid": %s,\n  "status": "%s",\n  "last_exit_code": %s,\n  "log_path": "%s"\n}\n' \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    "$$" \
    "$status" \
    "$exit_code" \
    "$LOG_PATH" > "$HEARTBEAT_PATH"
}

prune_incidents() {
  if [[ "$INCIDENT_RETENTION" -le 0 || ! -d "$INCIDENT_DIR" ]]; then
    return 0
  fi
  local count
  local remove_count
  count="$(find "$INCIDENT_DIR" -maxdepth 1 -type f -name '*-watchdog.json' | wc -l | tr -d ' ')"
  remove_count=$((count - INCIDENT_RETENTION))
  if [[ "$remove_count" -le 0 ]]; then
    return 0
  fi
  find "$INCIDENT_DIR" -maxdepth 1 -type f -name '*-watchdog.json' \
    | sort \
    | head -n "$remove_count" \
    | while IFS= read -r incident_path; do
        rm -f "$incident_path"
      done
}

run_watchdog_command() {
  if [[ -n "$WATCH_COMMAND" ]]; then
    bash -c "$WATCH_COMMAND"
  else
    ./.venv/bin/python -m news_sentiment watchdog-once --source all --limit "$LIMIT"
  fi
}

run_summary_command() {
  if [[ -n "$SUMMARY_COMMAND" ]]; then
    bash -c "$SUMMARY_COMMAND"
  else
    ./.venv/bin/python -m news_sentiment watchdog-summary --hours "$SUMMARY_HOURS" --log-path "$LOG_PATH"
  fi
}

run_summary_if_due() {
  if [[ "$SUMMARY_ENABLED" != "1" ]]; then
    return 0
  fi
  local now_epoch
  local summary_exit_code=0
  now_epoch="$(date +%s)"
  if [[ "$SUMMARY_INTERVAL_SECONDS" -gt 0 && $((now_epoch - LAST_SUMMARY_EPOCH)) -lt "$SUMMARY_INTERVAL_SECONDS" ]]; then
    return 0
  fi
  printf '===== summary %s =====\n' "$(date '+%Y-%m-%d_%H:%M:%S')" >> "$LOG_PATH"
  if run_summary_command >> "$LOG_PATH" 2>&1; then
    summary_exit_code=0
  else
    summary_exit_code=$?
    printf 'summary_command_failed=%s\n' "$summary_exit_code" >> "$LOG_PATH"
  fi
  LAST_SUMMARY_EPOCH="$now_epoch"
  return 0
}

run_iteration() {
  local exit_code=0
  write_heartbeat "running" 0
  printf '===== %s =====\n' "$(date '+%Y-%m-%d_%H:%M:%S')" >> "$LOG_PATH"
  if run_watchdog_command >> "$LOG_PATH" 2>&1; then
    exit_code=0
  else
    exit_code=$?
    printf 'watchdog_command_failed=%s\n' "$exit_code" >> "$LOG_PATH"
  fi
  if [[ "$REPORT_HEAD_LINES" -gt 0 && -f data/reports/latest_report.txt ]]; then
    sed -n "1,${REPORT_HEAD_LINES}p" data/reports/latest_report.txt >> "$LOG_PATH"
  fi
  prune_incidents
  run_summary_if_due
  printf '\n' >> "$LOG_PATH"
  if [[ "$exit_code" -eq 0 ]]; then
    write_heartbeat "completed" "$exit_code"
  else
    write_heartbeat "command_failed" "$exit_code"
  fi
  return "$exit_code"
}

mkdir -p "$(dirname "$LOG_PATH")"
mkdir -p "$(dirname "$LOCK_DIR")"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf 'watchdog_status=already_running lock_dir=%s\n' "$LOCK_DIR" >> "$LOG_PATH"
  write_heartbeat "already_running" 2
  exit 2
fi
cleanup() {
  rm -rf "$LOCK_DIR"
}
trap cleanup EXIT

if [[ "$RUN_ONCE" == "1" ]]; then
  run_iteration
  exit $?
fi

while true; do
  run_iteration || true
  write_heartbeat "sleeping" 0
  sleep "$INTERVAL_SECONDS"
done
