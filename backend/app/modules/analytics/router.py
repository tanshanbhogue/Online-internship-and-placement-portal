# Contract (student-only: guests 401, admins 403; every row belongs to the logged-in student)
#   GET /api/analytics/summary    ?date_from ?date_to ?source=all|practice|mock   totals, average, best, latest
#   GET /api/analytics/attempts   same filters + ?limit=1..100 (default 20)       newest first, for drill-down 
# Responses carry Cache-Control: no-store, so the dashboard never shows stale numbers.
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.modules.analytics import service
from app.modules.analytics.schemas import AnalyticsFilters, AttemptList, AttemptsFilters, SummaryResponse
from app.modules.auth.models import User

router = APIRouter(prefix="/api/analytics", tags=["analytics"], dependencies=[Depends(get_current_student)])


@router.get("/summary", response_model=SummaryResponse)
def summary(
    filters: Annotated[AnalyticsFilters, Query()],
    response: Response,
    student: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    return service.summarize(service.collect_points(db, student.id, filters))


@router.get("/attempts", response_model=AttemptList)
def attempts(
    filters: Annotated[AttemptsFilters, Query()],
    response: Response,
    student: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    return service.recent_attempts(service.collect_points(db, student.id, filters), filters.limit)
