# ==============================================================================
# FILE   : backend/app/modules/application/duplicate_check.py
# STORY  : #18 Prevent Duplicate Internship Applications  [FR-002; SEC-15]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Server-side duplicate-application guard (FR-002 fail condition 'duplicate applications are blocked', SEC-15). Story #17's service calls this.
#
# EXPOSES (exact names)
#   has_applied(db, student_id: int, internship_id: int) -> bool
#   get_existing(db, student_id, internship_id) -> Application | None
#   ensure_not_already_applied(db, student_id, internship_id) -> None     # raises AlreadyApplied ("You have already applied to this internship", 409)
#   translate_integrity_error(exc: IntegrityError) -> AppError          # maps a violation of uq_application_student_internship to AlreadyApplied; re-raises other IntegrityErrors
#
# RULES
#   The check by itself is not enough: #17 must also wrap the insert and call translate_integrity_error so two simultaneous requests yield exactly one row (test below).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

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
