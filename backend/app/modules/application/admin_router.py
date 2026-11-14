import logging

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.errors import NotFound
from app.modules.application.models import Application, ApplicationStatus
from app.modules.auth.models import User

router = APIRouter(
    prefix="/api/admin/applications",
    tags=["admin-applications"],
    dependencies=[Depends(get_current_admin)],
)
audit = logging.getLogger("app.audit")


class AdminApplicationOut(BaseModel):
    id: int
    internship_id: int
    internship_title: str
    company: str
    student_name: str
    student_email: str
    status: str
    cover_note: str | None = None
    resume_original_name: str
    applied_at: str


class AdminApplicationPage(BaseModel):
    items: list[AdminApplicationOut]
    total: int
    page: int
    page_size: int


class StatusUpdate(BaseModel):
    status: ApplicationStatus


def _row(app: Application, student: User) -> AdminApplicationOut:
    return AdminApplicationOut(
        id=app.id,
        internship_id=app.internship_id,
        internship_title=app.internship.title,
        company=app.internship.company,
        student_name=student.name,
        student_email=student.email,
        status=app.status.value,
        cover_note=app.cover_note,
        resume_original_name=app.resume_original_name,
        applied_at=app.applied_at.isoformat(),
    )


@router.get("", response_model=AdminApplicationPage)
def list_applications(
    internship_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    base = select(Application, User).join(User, User.id == Application.student_id)
    count = select(func.count(Application.id))
    if internship_id is not None:
        base = base.where(Application.internship_id == internship_id)
        count = count.where(Application.internship_id == internship_id)
    total = db.scalar(count) or 0
    rows = db.execute(base.order_by(Application.applied_at.desc(), Application.id.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return AdminApplicationPage(items=[_row(a, s) for a, s in rows], total=total, page=page, page_size=page_size)


@router.patch("/{application_id}/status", response_model=AdminApplicationOut)
def update_status(application_id: int, payload: StatusUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    application = db.get(Application, application_id)
    if application is None:
        raise NotFound("Application not found")
    application.status = payload.status
    db.commit()
    db.refresh(application)
    audit.info("admin %s set application %s to %s", admin.id, application.id, payload.status.value)  # SEC-20
    return _row(application, db.get(User, application.student_id))