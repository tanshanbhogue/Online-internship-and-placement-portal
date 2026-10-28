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
