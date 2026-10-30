# Story #25 Score and Answer Analysis - owner: Sinchana (sinchanaurs1104)
# File: backend/app/modules/mock_result/router.py
#
# Contract (student-only; responses are never cached so a new attempt shows up at once)
#   GET /api/mock-results                         "My Test History": closed attempts, newest first
#   GET /api/mock-results/{attempt_id}            score summary + breakdown; ?difficulty=easy|medium|hard  ?outcome=correct|incorrect|skipped
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.modules.auth.models import User
from app.modules.mock_result import service
from app.modules.mock_result.schemas import HistoryResponse, ResultDetail

router = APIRouter(prefix="/api/mock-results", tags=["mock-results"], dependencies=[Depends(get_current_student)])


@router.get("", response_model=HistoryResponse)
def history(response: Response, student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    response.headers["Cache-Control"] = "no-store"
    return service.list_history(db, student)


@router.get("/{attempt_id}", response_model=ResultDetail)
def result(
    attempt_id: int,
    response: Response,
    difficulty: Literal["easy", "medium", "hard"] | None = Query(default=None),
    outcome: Literal["correct", "incorrect", "skipped"] | None = Query(default=None),
    student: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    return service.get_result(db, student, attempt_id, difficulty, outcome)
