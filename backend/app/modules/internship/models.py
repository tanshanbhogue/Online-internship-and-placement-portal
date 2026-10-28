# ==============================================================================
# FILE   : backend/app/modules/internship/models.py
# STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   SQLAlchemy model for internship listings (data posted by admin, read by students). Corresponds to the Internship Service component.
#
# EXPOSES
#   class ListingStatus(str, enum.Enum): DRAFT="draft", ACTIVE="active", INACTIVE="inactive"   ("expired" is NOT stored; it is derived from deadline)
#   class Internship(Base) __tablename__ = "internships":
#     id int PK ; title str(150) ; company str(100) ; description text ; eligibility text null ; location str(100) null ; domain str(60) null (indexed)
#     stipend_per_month int null ; duration_months int null ; deadline date not null ; status ListingStatus default ACTIVE
#     created_at, updated_at datetime(UTC)
#
# USED BY
#   application/models.py (#18) has a FK to internships.id; application/service.py (#17) reads listings through internship/service.py.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

import enum
from datetime import date, datetime

from sqlalchemy import Date, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UTCDateTime, utcnow


class ListingStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"  # "expired" is derived from the deadline, never stored


class Internship(Base):
    __tablename__ = "internships"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    company: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    eligibility: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    stipend_per_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, values_callable=lambda e: [m.value for m in e], native_enum=False, length=20, validate_strings=True),
        nullable=False,
        default=ListingStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow)
