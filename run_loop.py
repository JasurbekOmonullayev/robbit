import os
import subprocess
import time
from datetime import datetime

SYNC_SOURCE = os.getenv("SYNC_SOURCE", "google")
SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "7200"))
RUN_ON_START = os.getenv("RUN_ON_START", "true").lower() == "true"


def run_sync() -> int:
    print(f"[{datetime.now().isoformat()}] Starting sync...", flush=True)
    cmd = ["python", "/app/sync_excel_to_clickup.py", "--source", SYNC_SOURCE]
    result = subprocess.run(cmd, check=False)
    print(f"[{datetime.now().isoformat()}] Sync finished with code={result.returncode}", flush=True)
    return result.returncode


def main() -> int:
    if RUN_ON_START:
        run_sync()

    while True:
        time.sleep(SYNC_INTERVAL_SECONDS)
        run_sync()


if __name__ == "__main__":
    raise SystemExit(main())
