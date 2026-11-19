# Contract
#   AnalyticsFilters   shared by #26 and #27 (AttemptsFilters adds ?limit=1..100): ?date_from=YYYY-MM-DD &date_to=YYYY-MM-DD &source=all|practice|mock
#   SummaryResponse    totals and averages across practice sessions + mock attempts of the LOGGED-IN student
#   AttemptRow         one scored attempt for the drill-down list (kind + id lead to /practice/result/:id or /mock-tests/result/:id)
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AnalyticsFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date_from: date | None = None
    date_to: date | None = None
    source: Literal["all", "practice", "mock"] = "all"

    @model_validator(mode="after")
    def _order(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must not be after date_to")
        return self


class AttemptsFilters(AnalyticsFilters):
    limit: int = Field(default=20, ge=1, le=100)


class SummaryResponse(BaseModel):
    has_data: bool
    total_attempts: int
    practice_attempts: int
    mock_attempts: int
    average_score: float | None
    best_score: float | None
    latest_score: float | None
    last_attempt_at: datetime | None


class AttemptRow(BaseModel):
    kind: Literal["practice", "mock"]
    id: int
    title: str
    category: str
    score_percent: float
    completed_at: datetime


class AttemptList(BaseModel):
    items: list[AttemptRow]
    total: int
