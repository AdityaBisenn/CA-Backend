# app/core/logger.py
import json
import os
import datetime
from app.core.config import settings


def log_error(module: str, error_type: str, message: str, sample_row: str = None):
    log_path = os.path.join(settings.LOG_DIR, "error_log.jsonl")
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "module": module,
        "error_type": error_type,
        "message": message,
        "sample_row": sample_row,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: int,
    client: str | None = None,
    user_agent: str | None = None,
    auth_present: bool = False,
    extra: dict | None = None,
):
    """Append a JSONL entry for each API request.

    Keeps entries minimal to avoid logging sensitive tokens. `auth_present` is a
    boolean indicating whether an Authorization header was present; we do NOT
    record the token itself.
    """
    log_path = os.path.join(settings.LOG_DIR, "request_log.jsonl")
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "client": client,
        "user_agent": user_agent,
        "auth_present": auth_present,
    }
    if extra:
        entry["extra"] = extra

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        # Best-effort logging; never raise from logging helper
        pass