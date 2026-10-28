

from datetime import date, datetime, timezone

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import ApplicationWindowClosed, NotFound
from app.modules.internship.models import Internship, ListingStatus
from app.modules.internship.schemas import InternshipFilters


def _today() -> date:
    return datetime.now(timezone.utc).date()


def is_open(listing: Internship, today: date | None = None) -> bool:
    today = today or _today()
    return listing.status == ListingStatus.ACTIVE and listing.deadline >= today


def ensure_open(listing: Internship) -> None:
    """Server-side deadline enforcement (SEC-15): the UI being bypassed does not matter."""
    if not is_open(listing):
        raise ApplicationWindowClosed()


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_listings(db: Session, filters: InternshipFilters) -> tuple[list[Internship], int]:
    """ACTIVE listings only. Past-deadline ones are included (shown as Closed) but sorted after open ones."""
    today = _today()
    conditions = [Internship.status == ListingStatus.ACTIVE]

    if filters.q and filters.q.strip():
        pattern = f"%{_escape_like(filters.q.strip())}%"
        conditions.append(
            or_(Internship.title.ilike(pattern, escape="\\"), Internship.company.ilike(pattern, escape="\\"))
        )
    if filters.location:
        conditions.append(func.lower(Internship.location) == filters.location.strip().lower())
    if filters.domain:
        conditions.append(func.lower(Internship.domain) == filters.domain.strip().lower())
    if filters.min_stipend is not None:
        conditions.append(Internship.stipend_per_month >= filters.min_stipend)
    if filters.max_duration_months is not None:
        conditions.append(Internship.duration_months <= filters.max_duration_months)
    if filters.open_only:
        conditions.append(Internship.deadline >= today)

    where = and_(*conditions)
    total = db.scalar(select(func.count(Internship.id)).where(where)) or 0
    open_first = case((Internship.deadline >= today, 0), else_=1)
    rows = db.scalars(
        select(Internship)
        .where(where)
        .order_by(open_first, Internship.deadline.asc(), Internship.id.asc())
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
    ).all()
    return list(rows), total


def get_listing(db: Session, internship_id: int) -> Internship:
    listing = db.get(Internship, internship_id)
    if listing is None or listing.status != ListingStatus.ACTIVE:
        raise NotFound("Internship not found")
    return listing
