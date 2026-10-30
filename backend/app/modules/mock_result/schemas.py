# Story #25 Score and Answer Analysis - owner: Sinchana (sinchanaurs1104)
# File: backend/app/modules/mock_result/schemas.py
#
# Contract (UC-7). Shapes exist ONLY for a CLOSED attempt, so answer keys and explanations never reach the
# browser while a test is running (SEC-12).
#   ResultSummary  score, accuracy, correct/incorrect/skipped, time taken, status, percentile (when enough data)
#   ResultDetail   ResultSummary + the question-by-question breakdown (optionally filtered)
#   HistoryItem    one row of "My Test History"
from datetime import datetime

from pydantic import BaseModel


class OptionView(BaseModel):
    id: int
    text: str


class BreakdownItem(BaseModel):
    position: int
    question_id: int
    prompt: str
    difficulty: str
    category_name: str
    options: list[OptionView]
    selected_option_id: int | None
    correct_option_id: int | None
    outcome: str  # correct | incorrect | skipped
    explanation: str | None


class DifficultyStat(BaseModel):
    difficulty: str
    total: int
    correct: int


class TestRef(BaseModel):
    __test__ = False

    id: int
    title: str


class ResultSummary(BaseModel):
    attempt_id: int
    test: TestRef
    category_name: str
    status: str  # submitted | auto_submitted
    auto_submitted: bool
    started_at: datetime
    submitted_at: datetime | None
    time_taken_seconds: int
    time_limit_seconds: int
    total_questions: int
    answered_count: int
    correct_count: int
    incorrect_count: int
    skipped_count: int
    score_percent: float | None
    accuracy_percent: float | None  # correct / answered
    percentile: int | None  # % of other students' attempts of this test that scored lower; None below 5 others
    by_difficulty: list[DifficultyStat]


class ResultDetail(ResultSummary):
    breakdown: list[BreakdownItem]
    filtered_count: int


class HistoryItem(BaseModel):
    attempt_id: int
    test_title: str
    category_name: str
    status: str
    score_percent: float | None
    correct_count: int
    total_questions: int
    submitted_at: datetime | None
    time_taken_seconds: int


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
