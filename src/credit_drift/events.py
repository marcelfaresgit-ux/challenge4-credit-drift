from __future__ import annotations

import json
from datetime import UTC, datetime

from credit_drift.config import LOGS_DIR


def record_event(event: str, **details: object) -> None:
    """Acrescenta um evento operacional sem incluir linhas do dataset."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "event": event,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        **details,
    }
    with (LOGS_DIR / "pipeline_events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
