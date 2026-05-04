"""
keep_alive.py
─────────────
Pings your Streamlit app every 10 minutes so it never goes to sleep.

Usage:
  1. Set your app URL below (or pass as env var STREAMLIT_URL)
  2. Run locally:       python keep_alive.py
  3. Or run on a cron / background process on any always-on machine.

To run in the background on Mac/Linux:
  nohup python keep_alive.py &

To run as a cron job (every 10 min):
  */10 * * * * /usr/bin/python3 /path/to/keep_alive.py >> /tmp/keep_alive.log 2>&1
"""

import os
import time
import logging
import urllib.request
import urllib.error
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
APP_URL      = os.environ.get("STREAMLIT_URL", "https://your-app-name.streamlit.app")
INTERVAL_SEC = 10 * 60   # ping every 10 minutes
TIMEOUT_SEC  = 30        # request timeout

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("keep_alive")


def ping():
    try:
        req = urllib.request.Request(APP_URL, headers={"User-Agent": "keep-alive-bot/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            log.info(f"OK  {resp.status}  {APP_URL}")
    except urllib.error.HTTPError as e:
        log.warning(f"HTTP {e.code}  {APP_URL}")
    except urllib.error.URLError as e:
        log.error(f"FAIL  {e.reason}  {APP_URL}")
    except Exception as e:
        log.error(f"ERROR  {e}")


def main():
    log.info(f"Keep-alive started — pinging {APP_URL} every {INTERVAL_SEC // 60} minutes")
    if "your-app-name" in APP_URL:
        log.warning("APP_URL is still the placeholder. Update it with your real Streamlit URL.")
    while True:
        ping()
        time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    main()
