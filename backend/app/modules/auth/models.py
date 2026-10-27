# ==============================================================================
# FILE   : backend/app/modules/auth/models.py
# STORY  : #14 Student Registration  [FR-001; SEC-02, SEC-08, SEC-09]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 2
# ==============================================================================
#
# PURPOSE
#   SQLAlchemy model for application users (students and admins). Every other module's foreign keys point at users.id.
#
# EXPOSES
#   class Role(str, enum.Enum): STUDENT = "student"; ADMIN = "admin"
#   class User(Base) __tablename__ = "users":
#     id int PK ; name str(100) not null ; email str(254) unique, indexed, stored LOWERCASE ; password_hash str(255) not null
#     role Role not null default STUDENT ; college str(100) null ; batch str(20) null ; is_active bool default True
#     created_at datetime(UTC) default now
#
# RULES
#   Email uniqueness enforced by a unique constraint (race-safe), not only by a pre-check. No plaintext password column, ever (SEC-02).
#
# USED BY
#   register_service (#14), login_service and dependencies (#19), application/practice models (FKs).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================


import enum
from datetime import datetime

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UTCDateTime, utcnow


class Role(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Stored lowercase. The unique index (not just a pre-check) makes duplicate registration race-safe.
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(Role, values_callable=lambda e: [m.value for m in e], native_enum=False, length=20, validate_strings=True),
        nullable=False,
        default=Role.STUDENT,
    )
    college: Mapped[str | None] = mapped_column(String(100), nullable=True)
    batch: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
