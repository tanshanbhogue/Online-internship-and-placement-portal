# ==============================================================================
# FILE   : backend/app/modules/practice/schemas.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Pydantic models for practice endpoints.
#
# EXPOSES
#   StartSessionRequest: category_id, count (optional 1..50)
#   SessionStartResponse: session_id, category {id,name}, total_questions, questions: list[QuestionPublic] (from question_bank.schemas; NO answers)
#   AnswerRequest: question_id, selected_option_id (mcq) OR code (coding, <= 20000 chars); exactly one of the two
#   AnswerFeedback: question_id, is_correct (bool | null when pending), evaluation_status, correct_option_id (mcq only), explanation   <- allowed ONLY after that question is answered (use case step 7)
#   BreakdownItem: question_id, prompt, selected_option_id, correct_option_id, is_correct, explanation
#   SessionResult: session_id, category, status, total_questions, answered_count, correct_count, score_percent, completed_at, breakdown
#   HistoryItem: session_id, category_name, correct_count, total_questions, score_percent, completed_at ; HistoryResponse: items
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.modules.question_bank.schemas import QuestionPublic


class CategoryRef(BaseModel):
    id: int
    name: str


class StartSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category_id: int
    count: int | None = Field(default=None, ge=1, le=50)


class SessionStartResponse(BaseModel):
    session_id: int
    category: CategoryRef
    total_questions: int
    questions: list[QuestionPublic]  # no answers (SEC-12)


class AnswerRequest(BaseModel):
    """Exactly one of selected_option_id (mcq) or code (coding)."""

    model_config = ConfigDict(extra="forbid")

    question_id: int
    selected_option_id: int | None = None
    code: Annotated[str, StringConstraints(max_length=20000)] | None = None

    @model_validator(mode="after")
    def _exactly_one_answer(self):
        if (self.selected_option_id is None) == (self.code is None):
            raise ValueError("Provide exactly one of selected_option_id or code")
        return self


class AnswerFeedback(BaseModel):
    """Allowed ONLY after that question has been answered."""

    question_id: int
    is_correct: bool | None
    evaluation_status: str
    correct_option_id: int | None = None
    explanation: str | None = None


class BreakdownItem(BaseModel):
    question_id: int
    prompt: str
    selected_option_id: int | None = None
    correct_option_id: int | None = None
    is_correct: bool | None = None
    explanation: str | None = None


class SessionResult(BaseModel):
    session_id: int
    category: CategoryRef
    status: str
    total_questions: int
    answered_count: int
    correct_count: int
    score_percent: float | None
    completed_at: datetime | None
    breakdown: list[BreakdownItem]


class HistoryItem(BaseModel):
    session_id: int
    category_name: str
    correct_count: int
    total_questions: int
    score_percent: float | None
    completed_at: datetime | None


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
