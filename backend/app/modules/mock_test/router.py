# Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
# File: backend/app/modules/mock_test/router.py
#
# Contract (all student-only; guests get 401, admins 403)
#   GET  /api/mock-tests                           list active tests (UC-5 step 1-2)
#   POST /api/mock-tests/{test_id}/attempts        start (201) or resume the open attempt (200)
#   GET  /api/mock-attempts/{attempt_id}           running state; closes the attempt first if time is up
#   PUT  /api/mock-attempts/{attempt_id}/answers   save / change / clear one answer
#   POST /api/mock-attempts/{attempt_id}/submit    manual submit (optional final answers); repeat calls are harmless
# Errors: 404 not found or not yours; 409 time_expired | already_submitted | no_questions(404)
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.modules.auth.models import User
from app.modules.mock_test import service
from app.modules.mock_test.models import AttemptStatus
from app.modules.mock_test.schemas import (
    AttemptState,
    CategoryRef,
    MockTestList,
    MockTestSummary,
    SaveAnswerRequest,
    SaveAnswerResponse,
    StartAttemptResponse,
    SubmitRequest,
    SubmitResponse,
)

router = APIRouter(prefix="/api", tags=["mock-tests"], dependencies=[Depends(get_current_student)])


@router.get("/mock-tests", response_model=MockTestList)
def list_tests(student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return MockTestList(
        items=[
            MockTestSummary(
                id=test.id,
                title=test.title,
                description=test.description,
                category=CategoryRef(id=test.category.id, name=test.category.name),
                duration_minutes=test.duration_minutes,
                question_count=count,
                open_attempt_id=open_attempt_id,
            )
            for test, count, open_attempt_id in service.list_tests(db, student)
        ]
    )


@router.post("/mock-tests/{test_id}/attempts", response_model=StartAttemptResponse, status_code=201)
def start_attempt(test_id: int, response: Response, student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    attempt, resumed = service.start_attempt(db, student, test_id)
    if resumed:
        response.status_code = 200
    return service.build_state(db, attempt, resumed=resumed)


@router.get("/mock-attempts/{attempt_id}", response_model=AttemptState)
def get_attempt(attempt_id: int, response: Response, student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    response.headers["Cache-Control"] = "no-store"  # the countdown must never come from a cache
    return service.build_state(db, service.get_attempt(db, student, attempt_id))


@router.put("/mock-attempts/{attempt_id}/answers", response_model=SaveAnswerResponse)
def save_answer(
    attempt_id: int,
    payload: SaveAnswerRequest,
    response: Response,
    student: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    remaining = service.save_answer(db, student, attempt_id, payload)
    return SaveAnswerResponse(question_id=payload.question_id, selected_option_id=payload.selected_option_id, remaining_seconds=remaining)


@router.post("/mock-attempts/{attempt_id}/submit", response_model=SubmitResponse)
def submit_attempt(
    attempt_id: int,
    payload: SubmitRequest | None = None,
    student: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    attempt, _ = service.submit_attempt(db, student, attempt_id, payload.answers if payload else None)
    return SubmitResponse(
        attempt_id=attempt.id,
        status=attempt.status.value,
        auto_submitted=attempt.status == AttemptStatus.AUTO_SUBMITTED,
        submitted_at=attempt.submitted_at,
    )
