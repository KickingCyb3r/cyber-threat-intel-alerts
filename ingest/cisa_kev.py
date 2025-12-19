import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict

import requests

CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def setup_logger(log_path: str = "logs/kev_ingest.log") -> logging.Logger:
    """Configure logging to console + file."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger("cisa_kev_ingest")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if executed multiple times in the same interpreter
    if logger.handlers:
        return logger

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    # Console handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # File handler
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


def fetch_json_with_retries(
    url: str,
    logger: logging.Logger,
    retries: int = 3,
    timeout_sec: int = 15,
) -> Dict[str, Any]:
    """Fetch JSON from a URL with retries and exponential backoff."""
    last_err: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Fetching CISA KEV (attempt {attempt}/{retries}) | timeout={timeout_sec}s")
            resp = requests.get(url, timeout=timeout_sec)

            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

            return resp.json()

        except Exception as e:
            last_err = e
            logger.warning(f"Fetch failed: {e}")

            if attempt < retries:
                backoff = 2 ** attempt
                logger.info(f"Retrying in {backoff}s...")
                time.sleep(backoff)

    raise RuntimeError(f"Unable to fetch CISA KEV after {retries} attempts: {last_err}")


def validate_payload(payload: Dict[str, Any]) -> int:
    """Basic validation of expected structure; returns vulnerability count."""
    vulns = payload.get("vulnerabilities")
    if not isinstance(vulns, list):
        raise ValueError("Invalid payload: 'vulnerabilities' missing or not a list")
    return len(vulns)


def write_artifacts(payload: Dict[str, Any], logger: logging.Logger) -> None:
    """Write output/kev_latest.json and a timestamped snapshot."""
    os.makedirs("output", exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    snapshot_path = f"output/kev_{ts}.json"
    latest_path = "output/kev_latest.json"

    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    logger.info(f"Saved snapshot: {snapshot_path}")
    logger.info(f"Updated latest: {latest_path}")


def main() -> None:
    logger = setup_logger()
    start = time.time()

    logger.info("=== CISA KEV Ingestion: START ===")
    logger.info(f"Source URL: {CISA_KEV_URL}")

    payload = fetch_json_with_retries(CISA_KEV_URL, logger, retries=3, timeout_sec=15)
    count = validate_payload(payload)

    write_artifacts(payload, logger)

    elapsed = round(time.time() - start, 2)
    logger.info(f"Records in feed: {count}")
    logger.info(f"=== CISA KEV Ingestion: SUCCESS in {elapsed}s ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.getLogger("cisa_kev_ingest").exception(f"=== CISA KEV Ingestion: FAILED | {e} ===")
        raise
