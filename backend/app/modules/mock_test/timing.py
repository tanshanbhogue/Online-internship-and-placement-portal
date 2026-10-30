# Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
# File: backend/app/modules/mock_test/timing.py
#
# Pure helpers (no database) for the one clock that matters: SERVER time (SEC-13). A page refresh or a
# changed browser clock cannot move `ends_at`, so these functions are the only place time is compared.
#
# Contract
#   remaining_seconds(attempt, now=None) -> int   whole seconds left, never negative (rounded UP so 0 means "over")
#   is_expired(attempt, now=None)        -> bool  now >= ends_at
#   accepts_late_input(attempt, now=None)-> bool  now <= ends_at + GRACE_SECONDS
# Tests: tests/test_mock_auto_submit.py
import math
from datetime import datetime, timedelta

from app.db.base import utcnow

# A final "Submit" that was sent at the buzzer may arrive a moment late (network). Answers inside this window
# are still kept; anything later is ignored and the attempt is closed with the answers saved so far.
GRACE_SECONDS = 5


def _now(now: datetime | None) -> datetime:
    return now if now is not None else utcnow()


def remaining_seconds(attempt, now: datetime | None = None) -> int:
    delta = (attempt.ends_at - _now(now)).total_seconds()
    return max(0, math.ceil(delta))


def is_expired(attempt, now: datetime | None = None) -> bool:
    return _now(now) >= attempt.ends_at


def accepts_late_input(attempt, now: datetime | None = None) -> bool:
    return _now(now) <= attempt.ends_at + timedelta(seconds=GRACE_SECONDS)
