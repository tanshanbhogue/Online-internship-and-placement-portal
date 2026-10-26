# ==============================================================================
# FILE   : backend/app/core/tokens.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Creation and verification of session tokens and the cookie helpers.
#
# EXPOSES
#   create_access_token(user_id: int, role: str) -> tuple[str, str, datetime]   # (jwt, jti, expires_at); claims sub, role, jti, iat, exp (+30 min)
#   decode_access_token(token: str) -> dict   # raises NotAuthenticated on bad signature/expired/malformed; algorithm pinned to HS256, secret from settings
#   set_session_cookie(response, token) -> None   # name "access_token", HttpOnly=True, Secure=settings.COOKIE_SECURE, SameSite=settings.COOKIE_SAMESITE, path="/", max_age 30 min
#   clear_session_cookie(response) -> None
#   is_revoked(db, jti) -> bool ; revoke(db, jti, expires_at) -> None
#
# SECURITY
#   SEC-05: unpredictable jti (uuid4), HttpOnly + Secure cookie, expiry after 30 minutes of inactivity (sliding: dependencies re-issue the cookie), invalidated on logout. Never log tokens.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import NotAuthenticated

ALGORITHM = "HS256"  # pinned: the token's own header can never choose the algorithm
COOKIE_NAME = "access_token"


def create_access_token(user_id: int, role: str, jti: str | None = None) -> tuple[str, str, datetime]:
    """Returns (jwt, jti, expires_at). Pass an existing `jti` to re-issue (sliding expiry) without changing identity."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = jti or str(uuid.uuid4())
    claims = {"sub": str(user_id), "role": role, "jti": jti, "iat": int(now.timestamp()), "exp": int(expires_at.timestamp())}
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=ALGORITHM), jti, expires_at


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "jti"]},
        )
    except jwt.PyJWTError:
        raise NotAuthenticated()


def set_session_cookie(response: Response, token: str) -> None:
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
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )


def is_revoked(db: Session, jti: str) -> bool:
    from app.modules.auth.session_models import RevokedToken

    return db.get(RevokedToken, jti) is not None


def revoke(db: Session, jti: str, expires_at: datetime) -> None:
    from app.modules.auth.session_models import RevokedToken

    if db.get(RevokedToken, jti) is None:
        db.add(RevokedToken(jti=jti, expires_at=expires_at))
        db.commit()
