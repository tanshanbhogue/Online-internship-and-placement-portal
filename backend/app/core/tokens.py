from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.core.config import settings
from app.core.errors import NotAuthenticated
from app.modules.auth.session_models import RevokedToken


ALGORITHM = "HS256"
COOKIE_NAME = "access_token"


def create_access_token(user_id: int, role: str) -> tuple[str, str, datetime]:
    """Create a signed access token and return (token, jti, expiry)."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid4())

    payload = {
        "sub": str(user_id),
        "role": str(role.value if hasattr(role, "value") else role),
        "jti": jti,
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, expires_at


def decode_access_token(token: str) -> dict:
    """Validate a JWT. Never accept an alternate signing algorithm."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "role", "jti", "iat", "exp"]},
        )

        # Reject malformed identity and session claims.
        if (
            not str(payload["sub"]).isdigit()
            or not isinstance(payload["role"], str)
            or not payload["role"]
            or not isinstance(payload["jti"], str)
            or not payload["jti"]
        ):
            raise NotAuthenticated()

        return payload
    except NotAuthenticated:
        raise
    except (jwt.PyJWTError, KeyError, TypeError, ValueError, OverflowError):
        raise NotAuthenticated() from None


def set_session_cookie(response: Response, token: str) -> None:
    """Set the access token only in a protected, HTTP-only cookie."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    """Remove the session cookie from the browser."""
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        secure=settings.COOKIE_SECURE,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
    )


def is_revoked(db: Session, jti: str) -> bool:
    """Return whether a token identifier has been revoked."""
    return (
        db.query(RevokedToken)
        .filter(RevokedToken.jti == jti)
        .first()
        is not None
    )


def revoke(db: Session, jti: str, expires_at: datetime) -> None:
    """Persist a token revocation until its expiry."""
    existing = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()

    if existing is None:
        db.add(RevokedToken(jti=jti, expires_at=expires_at))
        db.commit()
