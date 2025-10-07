# app/core/logger.py
import json, os, datetime
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