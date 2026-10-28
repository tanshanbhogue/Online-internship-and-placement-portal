
import hashlib
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.errors import InvalidCredentials
from app.core.security import verify_dummy, verify_password
from app.core.tokens import create_access_token, revoke
from app.modules.auth.login_throttle import (
    clear_failures,
    ensure_not_throttled,
    record_attempt,
)
from app.modules.auth.models import User
from app.modules.auth.session_models import purge_expired


audit_logger = logging.getLogger("security.audit")


def authenticate(
    db: Session,
    email: str,
    password: str,
    ip: str | None,
) -> tuple[User, str, datetime]:
    """Authenticate credentials and create a session token."""
    normalized_email = email.strip().lower()

    # Clean expired records and enforce the throttle before checking credentials.
    purge_expired(db)
    ensure_not_throttled(db, normalized_email, ip)

    user = db.query(User).filter(User.email == normalized_email).first()

    if user is None:
        verify_dummy(password)
        password_ok = False
    else:
        password_ok = verify_password(password, user.password_hash)

    # Do not disclose whether an account exists, has a wrong password,
    # or is inactive.
    if user is None or not password_ok or not user.is_active:
        record_attempt(db, normalized_email, ip, success=False)

        email_hash = hashlib.sha256(
            normalized_email.encode("utf-8")
        ).hexdigest()
        audit_logger.warning(
            "login_failed email_hash=%s",
            email_hash,
        )
        raise InvalidCredentials()

    clear_failures(db, normalized_email)
    record_attempt(db, normalized_email, ip, success=True)

    token, _jti, expires_at = create_access_token(
        user_id=user.id,
        role=user.role.value,
    )
    return user, token, expires_at


def logout(db: Session, token_payload: dict) -> None:
    """Revoke a previously validated session token."""
    jti = token_payload.get("jti")
    exp = token_payload.get("exp")

    if not isinstance(jti, str) or not jti or exp is None:
        return

    try:
        expires_at = datetime.fromtimestamp(float(exp), tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return

    revoke(db, jti, expires_at)
