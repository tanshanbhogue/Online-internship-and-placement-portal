
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import TooManyAttempts
from app.db.base import utcnow
from app.modules.auth.session_models import LoginAttempt


def ensure_not_throttled(db: Session, email: str, ip: str | None) -> None:
    """Reject login attempts after the configured number of recent failures."""
    normalized_email = email.strip().lower()
    cutoff = utcnow() - timedelta(minutes=settings.LOGIN_WINDOW_MINUTES)

    failures = (
        db.query(LoginAttempt)
        .filter(
            LoginAttempt.email == normalized_email,
            LoginAttempt.success.is_(False),
            LoginAttempt.attempted_at >= cutoff,
        )
        .count()
    )

    if failures >= settings.LOGIN_MAX_FAILURES:
        raise TooManyAttempts()


def record_attempt(
    db: Session,
    email: str,
    ip: str | None,
    success: bool,
) -> None:
    """Record a login result without storing credentials."""
    attempt = LoginAttempt(
        email=email.strip().lower(),
        ip=ip,
        success=success,
        attempted_at=utcnow(),
    )
    db.add(attempt)
    db.commit()


def clear_failures(db: Session, email: str) -> None:
    """Clear previous failed attempts after a successful login."""
    normalized_email = email.strip().lower()

    (
        db.query(LoginAttempt)
        .filter(
            LoginAttempt.email == normalized_email,
            LoginAttempt.success.is_(False),
        )
        .delete(synchronize_session=False)
    )
    db.commit()
