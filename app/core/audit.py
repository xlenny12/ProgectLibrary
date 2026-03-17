#REVIEW LATER
"""
Audit logger.
Every line is: ISO_TIMESTAMP|USER_ID|ACTION|DETAIL
The file is Fernet-encrypted at rest.
An HMAC-SHA256 tag is appended per-line (base64) after a second pipe so
replaying the log to reconstruct the DB is verifiable.

Format on disk (encrypted):
  <fernet blob of newline-joined lines>

Each plaintext line:
  2024-01-15T10:23:44Z|admin-uuid|USER_CREATED|{"username":"alice"}|hmac_b64
"""
import hashlib
import hmac
import json
import base64
from datetime import datetime, timezone
from pathlib import Path
from app.core.config import get_settings
from app.core.crypto import encrypt, decrypt


def _log_path() -> Path:
    p = get_settings().data_dir / "audit.dat"
    return p


def _sign_line(line: str) -> str:
    key = get_settings().audit_hmac_key.encode()
    if not key or key == b"":
        raise RuntimeError("AUDIT_HMAC_KEY is not configured. Set it in .env")
    sig = hmac.new(key, line.encode(), hashlib.sha256).digest()
    return base64.b64encode(sig).decode()


def _read_lines() -> list[str]:
    path = _log_path()
    if not path.exists():
        return []
    return decrypt(path.read_bytes()).splitlines()


def _write_lines(lines: list[str]) -> None:
    _log_path().write_bytes(encrypt("\n".join(lines)))


def log(user_id: str, action: str, detail: dict | None = None) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    detail_str = json.dumps(detail or {}, ensure_ascii=False)
    line_body = f"{ts}|{user_id}|{action}|{detail_str}"
    sig = _sign_line(line_body)
    full_line = f"{line_body}|{sig}"
    lines = _read_lines()
    lines.append(full_line)
    _write_lines(lines)


def verify_integrity() -> tuple[bool, list[str]]:
    """Returns (all_ok, list_of_tampered_lines)."""
    key = get_settings().audit_hmac_key.encode()
    if not key or key == b"":
        raise RuntimeError("AUDIT_HMAC_KEY is not configured.")
    tampered = []
    for raw in _read_lines():
        parts = raw.rsplit("|", 1)
        if len(parts) != 2:
            tampered.append(raw)
            continue
        body, sig_b64 = parts
        expected = base64.b64encode(
            hmac.new(key, body.encode(), hashlib.sha256).digest()
        ).decode()
        if not hmac.compare_digest(sig_b64, expected):
            tampered.append(raw)
    return (len(tampered) == 0, tampered)


def replay_events() -> list[dict]:
    """Parse all audit lines into dicts (for DB recovery)."""
    events = []
    for raw in _read_lines():
        parts = raw.split("|")
        if len(parts) >= 4:
            events.append({
                "timestamp": parts[0],
                "user_id": parts[1],
                "action": parts[2],
                "detail": json.loads(parts[3]),
            })
    return events
