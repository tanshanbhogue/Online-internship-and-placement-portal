from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.modules.analytics import insights, service, trends
from app.modules.analytics.insights_schemas import (
    CategoryInsightOut,
    FocusAreaOut,
    InsightsResponse,
    TrendFilters,
    TrendPoint,
    TrendResponse,
)
from app.modules.analytics.schemas import AnalyticsFilters
from app.modules.auth.models import User

router = APIRouter(prefix="/api/analytics", tags=["analytics-insights"], dependencies=[Depends(get_current_student)])


@router.get("/trends", response_model=TrendResponse)
def trend(
    filters: Annotated[TrendFilters, Query()],
    response: Response,
    student: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    points = service.collect_points(db, student.id, filters)
    scores = [p.score for p in points]
    averages = trends.moving_average(scores, filters.window)
    return TrendResponse(
        has_data=bool(points),
        window=filters.window,
        direction=trends.trend_direction(scores),
        points=[
            TrendPoint(index=i, kind=p.kind, id=p.id, at=p.at, category=p.category, title=p.title, score=p.score, moving_average=averages[i - 1])
            for i, p in enumerate(points, start=1)
        ],
    )


@router.get("/strengths-weaknesses", response_model=InsightsResponse)
def strengths_weaknesses(
    filters: Annotated[AnalyticsFilters, Query()],
    response: Response,
    student: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    points = service.collect_points(db, student.id, filters)
    by_category: dict[str, list[float]] = {}
    for p in points:  # points are oldest first, so each list is oldest -> newest
        by_category.setdefault(p.category, []).append(p.score)
    results = sorted((insights.classify(name, scores) for name, scores in by_category.items()), key=lambda i: i.category)
    return InsightsResponse(
        has_data=bool(points),
        categories=[CategoryInsightOut(**vars(i)) for i in results],
        strengths=[i.category for i in results if i.status in ("strong", "improved")],
        weaknesses=[i.category for i in results if i.status == "weak"],
        focus_areas=[FocusAreaOut(**vars(f)) for f in insights.focus_areas(results)],
    )
