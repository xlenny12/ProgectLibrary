#!/usr/bin/env python3
"""
Restore users.dat, books.dat, and borrows.dat from the encrypted signed audit log.

Run only after verifying that .env points to the same FERNET_KEY and
AUDIT_HMAC_KEY that were used to create audit.dat.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.audit import verify_integrity
from app.services.recovery_service import RecoveryService


def main() -> None:
    ok, tampered = verify_integrity()
    if not ok:
        raise SystemExit(f"Audit integrity check failed: {len(tampered)} tampered line(s).")

    counts = RecoveryService().restore_from_audit(actor_id="system")
    print("Database restored from audit log:")
    print(f"  users:   {counts['users']}")
    print(f"  books:   {counts['books']}")
    print(f"  borrows: {counts['borrows']}")


if __name__ == "__main__":
    main()
