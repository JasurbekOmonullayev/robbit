#!/bin/sh
set -eu

: "${SYNC_INTERVAL_SECONDS:=7200}"
: "${SYNC_SOURCE:=google}"
: "${RUN_ON_START:=true}"

run_sync() {
  echo "[$(date -Iseconds)] Starting sync..."
  python /app/sync_excel_to_clickup.py --source "$SYNC_SOURCE"
  echo "[$(date -Iseconds)] Sync finished."
}

if [ "$RUN_ON_START" = "true" ]; then
  run_sync
fi

while true; do
  sleep "$SYNC_INTERVAL_SECONDS"
  run_sync
done
