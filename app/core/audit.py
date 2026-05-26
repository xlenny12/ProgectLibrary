import base64
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.crypto import decrypt, encrypt

ACTION_RE = re.compile(r"^[A-Z0-9_]{3,80}$")


def _log_path() -> Path:
    return get_settings().data_dir / "audit.dat"


def _hmac_key() -> bytes:
    key = get_settings().audit_hmac_key.encode()
    if not key:
        raise RuntimeError("AUDIT_HMAC_KEY is not configured. Set it in .env")
    return key


def subject_ref(subject: str) -> str:
    """Stable pseudonymous reference for logs where raw identifiers are not needed."""
    digest = hmac.new(_hmac_key(), subject.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest[:24]


def _detail_to_token(detail: dict[str, Any]) -> str:
    payload = json.dumps(detail, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii")


def _detail_from_token(token: str) -> dict[str, Any]:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        return json.loads(decoded)
    except Exception:
        # Backward compatibility for old plaintext JSON audit entries.
        return json.loads(token)


def _sign_line(line: str) -> str:
    sig = hmac.new(_hmac_key(), line.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(sig).decode("ascii")


def _read_lines() -> list[str]:
    path = _log_path()
    if not path.exists() or path.stat().st_size == 0:
        return []
    return decrypt(path.read_bytes()).splitlines()


def _write_lines(lines: list[str]) -> None:
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encrypt("\n".join(lines)))


def _append_line(user_id: str, action: str, detail: dict[str, Any] | None = None) -> None:
    if not ACTION_RE.fullmatch(action):
        raise ValueError("Audit action has invalid format.")
    if any(ch in user_id for ch in ("|", "\n", "\r")):
        raise ValueError("Audit user_id contains unsupported control characters.")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    detail_token = _detail_to_token(detail or {})
    line_body = f"{ts}|{user_id}|{action}|{detail_token}"
    lines = _read_lines()
    lines.append(f"{line_body}|{_sign_line(line_body)}")
    _write_lines(lines)


def log(user_id: str, action: str, detail: dict[str, Any] | None = None) -> None:
    _append_line(user_id, action, detail)


def _parse_line(raw: str) -> dict[str, Any] | None:
    parts = raw.rsplit("|", 1)
    if len(parts) != 2:
        return None
    body, sig_b64 = parts
    body_parts = body.split("|", 3)
    if len(body_parts) != 4:
        return None
    try:
        detail = _detail_from_token(body_parts[3])
    except Exception:
        return None
    return {
        "timestamp": body_parts[0],
        "user_id": body_parts[1],
        "action": body_parts[2],
        "detail": detail,
        "signature": sig_b64,
        "_body": body,
    }


def verify_integrity() -> tuple[bool, list[str]]:
    tampered = []
    for raw in _read_lines():
        parsed = _parse_line(raw)
        if not parsed:
            tampered.append(raw)
            continue
        expected = _sign_line(parsed["_body"])
        if not hmac.compare_digest(parsed["signature"], expected):
            tampered.append(raw)
    return (len(tampered) == 0, tampered)


def replay_events() -> list[dict[str, Any]]:
    events = []
    for raw in _read_lines():
        parsed = _parse_line(raw)
        if parsed:
            parsed.pop("signature", None)
            parsed.pop("_body", None)
            events.append(parsed)
    return events


def replay_database() -> dict[str, list[dict[str, Any]]]:
    """Reconstruct the current database state from signed audit events."""
    users: dict[str, dict[str, Any]] = {}
    books: dict[str, dict[str, Any]] = {}
    borrows: dict[str, dict[str, Any]] = {}

    for event in replay_events():
        action = event["action"]
        detail = event["detail"]

        if action in {"USER_CREATED", "USER_UPDATED"} and "user" in detail:
            user = detail["user"]
            users[user["id"]] = user
        elif action in {"USER_DELETED_ADMIN", "USER_DELETED_GDPR"} and "user_id" in detail:
            user_id = detail["user_id"]
            users.pop(user_id, None)
            borrows = {borrow_id: b for borrow_id, b in borrows.items() if b.get("user_id") != user_id}
        elif action == "BORROWS_DELETED_GDPR" and "user_id" in detail:
            user_id = detail["user_id"]
            borrows = {borrow_id: b for borrow_id, b in borrows.items() if b.get("user_id") != user_id}

        elif action in {"BOOK_CREATED", "BOOK_UPDATED"} and "book" in detail:
            book = detail["book"]
            books[book["id"]] = book
        elif action == "BOOK_DELETED" and "book_id" in detail:
            books.pop(detail["book_id"], None)

        elif action in {"BOOK_BORROWED", "BOOK_RETURNED"} and "borrow" in detail:
            borrow = detail["borrow"]
            borrows[borrow["id"]] = borrow

    return {
        "users": list(users.values()),
        "books": list(books.values()),
        "borrows": list(borrows.values()),
    }


def _event_mentions_subject(event: dict[str, Any], subject_id: str) -> bool:
    if event.get("user_id") == subject_id:
        return True
    detail = event.get("detail", {})
    if detail.get("user_id") == subject_id:
        return True
    user = detail.get("user")
    if isinstance(user, dict) and user.get("id") == subject_id:
        return True
    borrow = detail.get("borrow")
    if isinstance(borrow, dict) and borrow.get("user_id") == subject_id:
        return True
    return False


def redact_subject(subject_id: str, actor_id: str, reason: str) -> int:
    """Remove prior audit entries for one subject, then log the authorized redaction."""
    kept: list[str] = []
    removed = 0
    for raw in _read_lines():
        parsed = _parse_line(raw)
        if parsed and _event_mentions_subject(parsed, subject_id):
            removed += 1
            continue
        kept.append(raw)

    _write_lines(kept)
    _append_line(
        "system",
        "SUBJECT_REDACTED",
        {"subject_ref": subject_ref(subject_id), "actor_ref": subject_ref(actor_id), "reason": reason, "removed": removed},
    )
    return removed
