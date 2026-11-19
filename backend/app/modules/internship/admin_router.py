import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.errors import NotFound
from app.modules.application.models import Application
from app.modules.auth.models import User
from app.modules.internship.admin_schemas import InternshipAdminOut, InternshipAdminPage, InternshipWrite
from app.modules.internship.models import Internship

router = APIRouter(
    prefix="/api/admin/internships",
    tags=["admin-internships"],
    dependencies=[Depends(get_current_admin)],
)
audit = logging.getLogger("app.audit")  # SEC-20: who changed what, never any secret


def _out(db: Session, listing: Internship) -> InternshipAdminOut:
    count = db.scalar(select(func.count(Application.id)).where(Application.internship_id == listing.id)) or 0
    out = InternshipAdminOut.model_validate(listing)
    out.application_count = count
    return out


def _get(db: Session, internship_id: int) -> Internship:
    listing = db.get(Internship, internship_id)
    if listing is None:
        raise NotFound("Internship not found")
    return listing


@router.get("", response_model=InternshipAdminPage)
def list_all(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Every listing, including draft and inactive ones (students only ever see active)."""
    total = db.scalar(select(func.count(Internship.id))) or 0
    rows = db.scalars(
        select(Internship).order_by(Internship.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return InternshipAdminPage(items=[_out(db, r) for r in rows], total=total, page=page, page_size=page_size)


@router.get("/{internship_id}", response_model=InternshipAdminOut)
def get_one(internship_id: int, db: Session = Depends(get_db)):
    return _out(db, _get(db, internship_id))


@router.post("", response_model=InternshipAdminOut, status_code=201)
def create(payload: InternshipWrite, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    listing = Internship(**payload.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    audit.info("admin %s created internship %s", admin.id, listing.id)
    return _out(db, listing)


@router.put("/{internship_id}", response_model=InternshipAdminOut)
def update(internship_id: int, payload: InternshipWrite, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    listing = _get(db, internship_id)
    for name, value in payload.model_dump().items():
        setattr(listing, name, value)
    db.commit()
    db.refresh(listing)
    audit.info("admin %s updated internship %s", admin.id, listing.id)
    return _out(db, listing)