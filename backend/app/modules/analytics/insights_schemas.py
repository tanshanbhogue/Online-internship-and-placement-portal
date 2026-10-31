from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.modules.analytics.schemas import AnalyticsFilters


class TrendFilters(AnalyticsFilters):
    window: int = Field(default=3, ge=2, le=10)


class TrendPoint(BaseModel):
    index: int  # 1-based position in the (filtered) history
    kind: Literal["practice", "mock"]
    id: int
    at: datetime
    category: str
    title: str
    score: float
    moving_average: float


class TrendResponse(BaseModel):
    has_data: bool
    window: int
    direction: Literal["improving", "declining", "steady", "not_enough_data"]
    points: list[TrendPoint]


class CategoryInsightOut(BaseModel):
    category: str
    attempts: int
    average: float
    recent_average: float
    earlier_average: float | None
    status: Literal["strong", "average", "weak", "improved", "not_enough_data"]


class FocusAreaOut(BaseModel):
    category: str
    priority: int
    message: str


class InsightsResponse(BaseModel):
    has_data: bool
    categories: list[CategoryInsightOut]
    strengths: list[str]  # status strong or improved
    weaknesses: list[str]  # status weak
    focus_areas: list[FocusAreaOut]
