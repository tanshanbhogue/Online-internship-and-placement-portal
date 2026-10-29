import enum
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UTCDateTime, utcnow
from app.modules.auth.models import User  # noqa: F401  (FK target must be registered)
from app.modules.internship.models import Internship


class ApplicationStatus(str, enum.Enum):
    APPLIED = "Applied"
    SHORTLISTED = "Shortlisted"
    REJECTED = "Rejected"
    SELECTED = "Selected"


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        # The database-level backstop for SEC-15: two simultaneous requests can never both insert.
        UniqueConstraint("student_id", "internship_id", name="uq_application_student_internship"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    internship_id: Mapped[int] = mapped_column(ForeignKey("internships.id", ondelete="RESTRICT"), index=True, nullable=False)
    cover_note: Mapped[str | None] = mapped_column(Text, nullable=True)  # <= 2000 chars, enforced in the service
    # Only the generated name is stored: never a filesystem path.
    resume_stored_name: Mapped[str] = mapped_column(String(80), nullable=False)
    resume_original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resume_size_bytes: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, values_callable=lambda e: [m.value for m in e], native_enum=False, length=20, validate_strings=True),
        nullable=False,
        default=ApplicationStatus.APPLIED,
    )
    applied_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow)

    internship: Mapped[Internship] = relationship(lazy="joined")