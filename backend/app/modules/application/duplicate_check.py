from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AlreadyApplied, AppError
from app.modules.application.models import Application

CONSTRAINT_NAME = "uq_application_student_internship"


def get_existing(db: Session, student_id: int, internship_id: int) -> Application | None:
    return db.scalar(
        select(Application).where(Application.student_id == student_id, Application.internship_id == internship_id)
    )


def has_applied(db: Session, student_id: int, internship_id: int) -> bool:
    return get_existing(db, student_id, internship_id) is not None


def ensure_not_already_applied(db: Session, student_id: int, internship_id: int) -> None:
    if has_applied(db, student_id, internship_id):
        raise AlreadyApplied()


def translate_integrity_error(exc: IntegrityError) -> AppError:
    """Map a violation of the unique constraint to AlreadyApplied; any other IntegrityError is re-raised.

    Postgres names the constraint; SQLite reports the columns instead, so both spellings are recognised.
    """
    detail = str(getattr(exc, "orig", exc))
    if CONSTRAINT_NAME in detail or (
        "UNIQUE constraint failed" in detail
        and "applications.student_id" in detail
        and "applications.internship_id" in detail
    ):
        return AlreadyApplied()
    raise exc