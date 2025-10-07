# app/utils/helpers.py
import hashlib

def compute_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()