#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_PATH="${NEWS_SENTIMENT_WATCH_LOG:-/tmp/news-sentiment-watch.log}"
INTERVAL_SECONDS="${NEWS_SENTIMENT_WATCH_INTERVAL_SECONDS:-1800}"
LIMIT="${NEWS_SENTIMENT_WATCH_LIMIT:-10}"

cd "$ROOT_DIR"
export PYTHONPATH=src

while true; do
  printf '===== %s =====\n' "$(date '+%Y-%m-%d_%H:%M:%S')" >> "$LOG_PATH"
  ./.venv/bin/python -m news_sentiment watchdog-once --source all --limit "$LIMIT" >> "$LOG_PATH" 2>&1
  if [[ -f data/reports/latest_report.txt ]]; then
    sed -n '1,80p' data/reports/latest_report.txt >> "$LOG_PATH"
  fi
  printf '\n' >> "$LOG_PATH"
  sleep "$INTERVAL_SECONDS"
done
