

import logging

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ValidationFailed
from app.modules.application import duplicate_check, resume_storage
from app.modules.application.models import Application, ApplicationStatus
from app.modules.auth.models import User
from app.modules.internship import service as internship_service

audit = logging.getLogger("security.audit")

MAX_COVER_NOTE_LENGTH = 2000


def apply(db: Session, student: User, internship_id: int, cover_note: str | None, resume: UploadFile | None) -> Application:
    listing = internship_service.get_listing(db, internship_id)  # 404
    internship_service.ensure_open(listing)  # 409 window closed, enforced server-side (SEC-15)
    duplicate_check.ensure_not_already_applied(db, student.id, listing.id)  # 409 already applied

    note = (cover_note or "").strip() or None
    if note and len(note) > MAX_COVER_NOTE_LENGTH:
        raise ValidationFailed(fields={"cover_note": [f"Cover note must be at most {MAX_COVER_NOTE_LENGTH} characters"]})
    if resume is None or not (resume.filename or "").strip():
        raise ValidationFailed(fields={"resume": ["Please upload your resume"]})

    stored = resume_storage.save_resume(resume)  # InvalidFile (422) on a bad file
    application = Application(
        student_id=student.id,  # from the authenticated user, never the request (SEC-06)
        internship_id=listing.id,
        cover_note=note,  # kept as plain text; React escapes it on display (SEC-10)
        resume_stored_name=stored.stored_name,
        resume_original_name=stored.original_name,
        resume_content_type=stored.content_type,
        resume_size_bytes=stored.size_bytes,
        status=ApplicationStatus.APPLIED,
    )
    db.add(application)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        resume_storage.delete_resume(stored.stored_name)  # no orphaned file
        raise duplicate_check.translate_integrity_error(exc)

    audit.info("application_created student_id=%s application_id=%s", student.id, application.id)
    return application


def list_for_student(db: Session, student_id: int) -> list[Application]:
    return list(
        db.scalars(
            select(Application)
            .where(Application.student_id == student_id)
            .order_by(Application.applied_at.desc(), Application.id.desc())
        ).all()
    )
