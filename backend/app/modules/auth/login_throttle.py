# ==============================================================================
# FILE   : backend/app/modules/auth/login_throttle.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Brute-force protection (SEC-03).
#
# EXPOSES
#   ensure_not_throttled(db, email, ip) -> None   # raise TooManyAttempts if >= settings.LOGIN_MAX_FAILURES (5) failed attempts for that email within LOGIN_WINDOW_MINUTES (15)
#   record_attempt(db, email, ip, success: bool) -> None
#   clear_failures(db, email) -> None             # called after a successful login
#
# RULES
#   Apply throttling to unknown emails too (otherwise it reveals which accounts exist, SEC-04). While throttled even the correct password is refused until the window passes. Use UTC time so tests can freeze it with freezegun.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from datetime import timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import TooManyAttempts
from app.db.base import utcnow
from app.modules.auth.session_models import LoginAttempt


def _normalise(email: str) -> str:
    return (email or "").strip().lower()[:254]


def ensure_not_throttled(db: Session, email: str, ip: str | None) -> None:
    """Applies to unknown emails too, so throttling never reveals which accounts exist (SEC-04)."""
    cutoff = utcnow() - timedelta(minutes=settings.LOGIN_WINDOW_MINUTES)
    failures = db.scalar(
        select(func.count(LoginAttempt.id)).where(
            LoginAttempt.email == _normalise(email),
            LoginAttempt.success.is_(False),
            LoginAttempt.attempted_at >= cutoff,
        )
    )
    if (failures or 0) >= settings.LOGIN_MAX_FAILURES:
        raise TooManyAttempts()


def record_attempt(db: Session, email: str, ip: str | None, success: bool) -> None:
    db.add(LoginAttempt(email=_normalise(email), ip=(ip or None), success=success, attempted_at=utcnow()))
    db.commit()


def clear_failures(db: Session, email: str) -> None:
    db.execute(
        delete(LoginAttempt).where(LoginAttempt.email == _normalise(email), LoginAttempt.success.is_(False))
    )
    db.commit()
