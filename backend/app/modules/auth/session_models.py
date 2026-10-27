from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.core.config import settings
from app.db.base import Base, UTCDateTime, utcnow


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti: Mapped[str] = mapped_column(String(36), primary_key=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utcnow, nullable=False
    )


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utcnow, nullable=False, index=True
    )


def purge_expired(db: Session) -> None:
    """Delete expired tokens and login attempts outside the throttle window."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=settings.LOGIN_WINDOW_MINUTES)

    db.query(RevokedToken).filter(
        RevokedToken.expires_at <= now
    ).delete(synchronize_session=False)

    db.query(LoginAttempt).filter(
        LoginAttempt.attempted_at < cutoff
    ).delete(synchronize_session=False)

    db.commit()
