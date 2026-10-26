# ==============================================================================
# FILE   : backend/app/modules/auth/session_models.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Tables that support sessions and login throttling.
#
# EXPOSES
#   RevokedToken: jti str(36) PK ; expires_at datetime ; revoked_at datetime default now  (logout / invalidation list, SEC-05)
#   LoginAttempt: id PK ; email str(254) indexed (lowercase) ; ip str(45) null ; success bool ; attempted_at datetime(UTC) indexed  (SEC-03)
#   Add a cleanup helper purge_expired(db) removing rows older than the throttle window / past expires_at.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from datetime import datetime, timedelta

from sqlalchemy import Boolean, String, delete
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.config import settings
from app.db.base import Base, UTCDateTime, utcnow


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(36), primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), index=True, nullable=False)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(UTCDateTime, index=True, nullable=False, default=utcnow)


def purge_expired(db: Session) -> None:
    """Remove revocations whose token has expired anyway, and attempts older than the throttle window."""
    now = utcnow()
    cutoff = now - timedelta(minutes=settings.LOGIN_WINDOW_MINUTES)
    db.execute(delete(RevokedToken).where(RevokedToken.expires_at < now))
    db.execute(delete(LoginAttempt).where(LoginAttempt.attempted_at < cutoff))
    db.commit()
