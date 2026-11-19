# The ONE place that reads a student's scored history. Story #27 builds trends and insights on collect_points().
# Everything is computed from the stored attempts at request time (nothing is cached or pre-aggregated), so the
# dashboard reflects a new attempt immediately and every number can be checked by hand.
#
# Contract
#   AttemptPoint(kind, id, at, category, title, score)         one finished, scored attempt
#   collect_points(db, student_id, filters) -> list[AttemptPoint]   oldest first; ONLY this student's rows 
#   summarize(points) -> SummaryResponse
#   recent_attempts(points, limit) -> AttemptList               newest first
# Counted: practice sessions with status completed and a score; mock attempts that are submitted/auto_submitted
# with a score. Open, partial-without-score and other students' attempts are never counted.
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.analytics.schemas import AnalyticsFilters, AttemptList, AttemptRow, SummaryResponse
from app.modules.mock_test.models import AttemptStatus, MockAttempt, MockTest
from app.modules.practice.models import PracticeSession, SessionStatus
from app.modules.question_bank.models import Category


@dataclass(frozen=True)
class AttemptPoint:
    kind: str  # "practice" | "mock"
    id: int
    at: datetime
    category: str
    title: str
    score: float


def _bounds(filters: AnalyticsFilters) -> tuple[datetime | None, datetime | None]:
    start = datetime.combine(filters.date_from, time.min, tzinfo=timezone.utc) if filters.date_from else None
    end = datetime.combine(filters.date_to + timedelta(days=1), time.min, tzinfo=timezone.utc) if filters.date_to else None
    return start, end  # [start, end): date_to is inclusive of the whole day


def collect_points(db: Session, student_id: int, filters: AnalyticsFilters) -> list[AttemptPoint]:
    start, end = _bounds(filters)
    points: list[AttemptPoint] = []

    if filters.source in ("all", "practice"):
        query = (
            select(PracticeSession.id, PracticeSession.completed_at, PracticeSession.score_percent, Category.name)
            .join(Category, Category.id == PracticeSession.category_id)
            .where(
                PracticeSession.student_id == student_id,
                PracticeSession.status == SessionStatus.COMPLETED,
                PracticeSession.score_percent.is_not(None),
                PracticeSession.completed_at.is_not(None),
            )
        )
        if start:
            query = query.where(PracticeSession.completed_at >= start)
        if end:
            query = query.where(PracticeSession.completed_at < end)
        for sid, at, score, category in db.execute(query).all():
            points.append(AttemptPoint("practice", sid, at, category, f"{category} practice", float(score)))

    if filters.source in ("all", "mock"):
        query = (
            select(MockAttempt.id, MockAttempt.submitted_at, MockAttempt.score_percent, MockTest.title, Category.name)
            .join(MockTest, MockTest.id == MockAttempt.test_id)
            .join(Category, Category.id == MockTest.category_id)
            .where(
                MockAttempt.student_id == student_id,
                MockAttempt.status != AttemptStatus.IN_PROGRESS,
                MockAttempt.score_percent.is_not(None),
                MockAttempt.submitted_at.is_not(None),
            )
        )
        if start:
            query = query.where(MockAttempt.submitted_at >= start)
        if end:
            query = query.where(MockAttempt.submitted_at < end)
        for aid, at, score, title, category in db.execute(query).all():
            points.append(AttemptPoint("mock", aid, at, category, title, float(score)))

    points.sort(key=lambda p: (p.at, p.kind, p.id))
    return points


def summarize(points: list[AttemptPoint]) -> SummaryResponse:
    if not points:
        return SummaryResponse(
            has_data=False, total_attempts=0, practice_attempts=0, mock_attempts=0,
            average_score=None, best_score=None, latest_score=None, last_attempt_at=None,
        )
    scores = [p.score for p in points]
    return SummaryResponse(
        has_data=True,
        total_attempts=len(points),
        practice_attempts=sum(1 for p in points if p.kind == "practice"),
        mock_attempts=sum(1 for p in points if p.kind == "mock"),
        average_score=round(sum(scores) / len(scores), 2),
        best_score=max(scores),
        latest_score=points[-1].score,
        last_attempt_at=points[-1].at,
    )


def recent_attempts(points: list[AttemptPoint], limit: int = 20) -> AttemptList:
    newest_first = list(reversed(points))
    return AttemptList(
        items=[
            AttemptRow(kind=p.kind, id=p.id, title=p.title, category=p.category, score_percent=p.score, completed_at=p.at)
            for p in newest_first[:limit]
        ],
        total=len(points),
    )
