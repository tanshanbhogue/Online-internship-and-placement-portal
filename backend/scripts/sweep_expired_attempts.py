# Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
# File: backend/scripts/sweep_expired_attempts.py
#
# Closes every mock-test attempt whose time ran out while nobody was looking (tab closed, connection lost).
# Run it from backend/ once a minute, for example:   * * * * *  cd /path/to/backend && python -m scripts.sweep_expired_attempts
# Safe to run repeatedly and from several machines at once: each attempt is closed exactly once (SEC-14).
import sys

from app.core.database import SessionLocal, init_db
from app.modules.mock_test.finalize import sweep_expired


def main() -> int:
    init_db()
    with SessionLocal() as db:
        closed = sweep_expired(db)
    print(f"Auto-submitted {closed} expired attempt(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
