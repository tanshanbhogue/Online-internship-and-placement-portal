

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
