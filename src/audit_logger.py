"""
audit_logger.py

Append-only audit log in JSON Lines format. Each entry stores the SHA-256 hash
of the previous entry, so any edit or deletion breaks the chain and is
detectable with verify_chain(). Supports 21 CFR Part 11.10(e) record integrity.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

GENESIS = "0" * 64


def _hash(entry: dict) -> str:
    return hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()


def _last_hash(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return GENESIS
    last = path.read_text(encoding="utf-8").strip().splitlines()[-1]
    return json.loads(last)["entry_hash"]


def log_event(path: str, event_type: str, sample_id: Optional[str], actor: str = "system", **details) -> dict:
    p = Path(path)
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "event_type": event_type,
        "sample_id": sample_id,
        "actor": actor,
        "details": details,
        "prev_hash": _last_hash(p),
    }
    entry["entry_hash"] = _hash(entry)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def verify_chain(path: str) -> bool:
    """Return True if no entry has been altered, removed, or reordered."""
    prev = GENESIS
    for line in Path(path).read_text(encoding="utf-8").strip().splitlines():
        entry = json.loads(line)
        stored = entry.pop("entry_hash")
        if entry["prev_hash"] != prev or _hash(entry) != stored:
            return False
        prev = stored
    return True
