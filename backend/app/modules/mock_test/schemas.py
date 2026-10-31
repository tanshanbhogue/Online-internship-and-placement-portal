# Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
# File: backend/app/modules/mock_test/schemas.py
#
# Contract (what the browser receives and may send)
#   MockTestSummary   one test in the list: title, category, duration, question count, open attempt id (resume)
#   AttemptState      everything needed to render a running attempt: SERVER-time remaining_seconds, the
#                     questions WITHOUT answers (SEC-12) and the choices saved so far
#   SaveAnswerRequest one choice (selected_option_id null clears it)
#   SubmitRequest     optional final snapshot of the choices, accepted until the grace window ends
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.question_bank.schemas import QuestionPublic


class CategoryRef(BaseModel):
    id: int
    name: str


class MockTestSummary(BaseModel):
    id: int
    title: str
    description: str | None
    category: CategoryRef
    duration_minutes: int
    question_count: int
    open_attempt_id: int | None  # set when the student already has this test running (Resume)


class MockTestList(BaseModel):
    items: list[MockTestSummary]


class TestRef(BaseModel):
    __test__ = False  # not a pytest class

    id: int
    title: str
    category: CategoryRef
    duration_minutes: int


class AttemptState(BaseModel):
    attempt_id: int
    test: TestRef
    status: str  # in_progress | submitted | auto_submitted
    started_at: datetime
    ends_at: datetime
    server_time: datetime  # changes on every response, so the browser can re-anchor its countdown
    remaining_seconds: int
    total_questions: int
    questions: list[QuestionPublic]  # empty once the attempt is closed
    answers: dict[int, int]  # question id -> selected option id


class StartAttemptResponse(AttemptState):
    resumed: bool  # true when an open attempt was returned instead of a new one (refresh / reconnect, UC-5 alt flow)


class SaveAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: int
    selected_option_id: int | None = None


class SaveAnswerResponse(BaseModel):
    question_id: int
    selected_option_id: int | None
    remaining_seconds: int


class SubmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answers: list[SaveAnswerRequest] | None = Field(default=None, max_length=200)


class SubmitResponse(BaseModel):
    attempt_id: int
    status: str
    auto_submitted: bool
    submitted_at: datetime | None
