# ==============================================================================
# FILE   : backend/app/modules/practice/router.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   HTTP endpoints for practice sessions.
#
# ROUTES
#   router = APIRouter(prefix="/api/practice", tags=["practice"]) ; every route Depends(get_current_student)
#   POST /api/practice/sessions                      StartSessionRequest -> 201 SessionStartResponse ; 404 no_questions
#   POST /api/practice/sessions/{id}/answers         AnswerRequest -> 200 AnswerFeedback ; 404 other student's session ; 409 already answered / finished
#   POST /api/practice/sessions/{id}/finish          -> 200 SessionResult (partial sessions allowed, unanswered count as not correct)
#   GET  /api/practice/sessions/{id}                 -> 200 SessionResult (completed only)
#   GET  /api/practice/history                       -> 200 HistoryResponse
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.modules.auth.models import User
from app.modules.practice import service
from app.modules.practice.schemas import (
    AnswerFeedback,
    AnswerRequest,
    CategoryRef,
    HistoryItem,
    HistoryResponse,
    SessionResult,
    SessionStartResponse,
    StartSessionRequest,
)
from app.modules.question_bank.schemas import QuestionPublic

router = APIRouter(prefix="/api/practice", tags=["practice"], dependencies=[Depends(get_current_student)])


@router.post("/sessions", response_model=SessionStartResponse, status_code=201)
def start_session(payload: StartSessionRequest, student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    session = service.start_session(db, student, payload.category_id, payload.count)
    return SessionStartResponse(
        session_id=session.id,
        category=CategoryRef(id=session.category.id, name=session.category.name),
        total_questions=session.total_questions,
        questions=[QuestionPublic.model_validate(sq.question) for sq in session.session_questions],
    )


@router.post("/sessions/{session_id}/answers", response_model=AnswerFeedback)
def submit_answer(session_id: int, payload: AnswerRequest, student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return service.submit_answer(db, student, session_id, payload)


@router.post("/sessions/{session_id}/finish", response_model=SessionResult)
def finish_session(session_id: int, student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return service.finish_session(db, student, session_id)


@router.get("/history", response_model=HistoryResponse)
def history(student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return HistoryResponse(
        items=[
            HistoryItem(
                session_id=s.id,
                category_name=s.category.name,
                correct_count=s.correct_count,
                total_questions=s.total_questions,
                score_percent=s.score_percent,
                completed_at=s.completed_at,
            )
            for s in service.list_history(db, student)
        ]
    )


# Declared after /history so the literal path is matched first.
@router.get("/sessions/{session_id}", response_model=SessionResult)
def get_session(session_id: int, student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return service.get_result(db, student, session_id)
