from datetime import datetime, timedelta, timezone

from fastapi import Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import Forbidden, NotAuthenticated
from app.core.tokens import (
    COOKIE_NAME,
    clear_session_cookie,
    decode_access_token,
    is_revoked,
    set_session_cookie,
)
from app.modules.auth.models import Role, User


def get_client_ip(request: Request) -> str | None:
    """Return the direct client IP without trusting spoofable forwarded headers."""
    if request.client is None:
        return None
    return request.client.host


def get_current_user(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> User:
    """Authenticate the session cookie and renew its expiry on activity."""
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise NotAuthenticated()

    try:
        payload = decode_access_token(token)
        jti = payload["jti"]
        user_id = int(payload["sub"])
    except (NotAuthenticated, KeyError, TypeError, ValueError):
        clear_session_cookie(response)
        raise NotAuthenticated() from None

    if is_revoked(db, jti):
        clear_session_cookie(response)
        raise NotAuthenticated()

    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        clear_session_cookie(response)
        raise NotAuthenticated()

    # Extend the existing token's expiry while retaining its jti,
    # so the same session can still be revoked on logout.
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=30)
    refreshed_payload = dict(payload)
    refreshed_payload["iat"] = now
    refreshed_payload["exp"] = expires_at

    import jwt
    from app.core.config import settings

    refreshed_token = jwt.encode(
        refreshed_payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    set_session_cookie(response, refreshed_token)

    return user


def get_current_student(
    user: User = Depends(get_current_user),
) -> User:
    """Require an authenticated student."""
    if user.role != Role.STUDENT:
        raise Forbidden()
    return user


def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Require an authenticated administrator."""
    if user.role != Role.ADMIN:
        raise Forbidden()
    return user
