# ==============================================================================
# FILE   : backend/app/modules/question_bank/router.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Student-facing read endpoints for categories and questions.
#
# ROUTES
#   router = APIRouter(prefix="/api/question-bank", tags=["question-bank"])
#   GET /api/question-bank/categories                                  Depends(get_current_user) -> list[CategoryOut]
#   GET /api/question-bank/categories/{category_id}/questions?count=&difficulty=   Depends(get_current_user) -> PublicQuestionList of QuestionPublic
#         unknown category -> 404 ; category with zero questions -> 200 with items [] (UI shows 'No questions found', IT_07)
#
# RULES
#   Response models MUST be QuestionPublic so correct options, explanations and test cases cannot leak (SEC-12). Inspect the JSON in tests.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.question_bank import service
from app.modules.question_bank.models import Difficulty
from app.modules.question_bank.schemas import CategoryOut, PublicQuestionList, QuestionPublic

router = APIRouter(prefix="/api/question-bank", tags=["question-bank"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [
        CategoryOut(id=c.id, name=c.name, slug=c.slug, question_count=count)
        for c, count in service.list_categories(db)
    ]


@router.get("/categories/{category_id}/questions", response_model=PublicQuestionList)
def list_questions(
    category_id: int,
    count: int | None = Query(default=None, ge=1, le=50),
    difficulty: Difficulty | None = None,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    questions, total = service.list_public_questions(db, category_id, count, difficulty)
    return PublicQuestionList(items=[QuestionPublic.model_validate(q) for q in questions], total=total)
