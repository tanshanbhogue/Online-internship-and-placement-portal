

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.internship import service
from app.modules.internship.models import Internship
from app.modules.internship.schemas import (
    SHORT_DESCRIPTION_LENGTH,
    InternshipDetail,
    InternshipFilters,
    InternshipListResponse,
    InternshipSummary,
)

router = APIRouter(prefix="/api/internships", tags=["internships"])


def _summary_fields(listing: Internship) -> dict:
    description = listing.description or ""
    short = description if len(description) <= SHORT_DESCRIPTION_LENGTH else description[:SHORT_DESCRIPTION_LENGTH].rstrip() + "…"
    return {
        "id": listing.id,
        "title": listing.title,
        "company": listing.company,
        "short_description": short,
        "location": listing.location,
        "domain": listing.domain,
        "stipend_per_month": listing.stipend_per_month,
        "duration_months": listing.duration_months,
        "deadline": listing.deadline,
        "is_open": service.is_open(listing),
    }


@router.get("", response_model=InternshipListResponse)
def list_internships(
    filters: Annotated[InternshipFilters, Query()],
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = service.list_listings(db, filters)
    return InternshipListResponse(
        items=[InternshipSummary(**_summary_fields(i)) for i in items],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


@router.get("/{internship_id}", response_model=InternshipDetail)
def get_internship(internship_id: int, _user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = service.get_listing(db, internship_id)
    return InternshipDetail(**_summary_fields(listing), description=listing.description, eligibility=listing.eligibility)
