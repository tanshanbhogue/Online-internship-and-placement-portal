# ==============================================================================
# FILE   : backend/app/modules/question_bank/admin_router.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Admin-only endpoints to manage categories and questions (use case 'Manage Categorized Question Bank').
#
# ROUTES
#   router = APIRouter(prefix="/api/admin/question-bank", tags=["admin-question-bank"]) ; every route Depends(get_current_admin) (SEC-07)
#   GET    /categories -> list[CategoryOut]          POST /categories (CategoryCreate) -> 201 CategoryOut (duplicate name -> 409 conflict)
#   GET    /questions?category_id=&page=&page_size= -> paginated list[QuestionAdminOut]
#   POST   /questions (QuestionCreate) -> 201 QuestionAdminOut          GET /questions/{id} -> QuestionAdminOut
#   PUT    /questions/{id} (QuestionUpdate) -> QuestionAdminOut         DELETE /questions/{id} -> 204 (soft delete)
#   Incomplete data (e.g. no correct option) -> 422 with field errors (use case A1).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.modules.auth.models import User
from app.modules.question_bank import service
from app.modules.question_bank.schemas import (
    AdminQuestionPage,
    CategoryCreate,
    CategoryOut,
    QuestionAdminOut,
    QuestionCreate,
    QuestionUpdate,
)

# Every route is admin-only (SEC-07): students get 403, guests 401.
router = APIRouter(
    prefix="/api/admin/question-bank",
    tags=["admin-question-bank"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return [
        CategoryOut(id=c.id, name=c.name, slug=c.slug, question_count=count)
        for c, count in service.list_categories(db)
    ]


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    category = service.create_category(db, admin.id, payload)
    return CategoryOut(id=category.id, name=category.name, slug=category.slug, question_count=0)


@router.get("/questions", response_model=AdminQuestionPage)
def list_questions(
    category_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = service.list_admin_questions(db, category_id, page, page_size)
    return AdminQuestionPage(
        items=[QuestionAdminOut.model_validate(q) for q in items], total=total, page=page, page_size=page_size
    )


@router.post("/questions", response_model=QuestionAdminOut, status_code=201)
def create_question(payload: QuestionCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return service.create_question(db, admin.id, payload)


@router.get("/questions/{question_id}", response_model=QuestionAdminOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    return service.get_admin_question(db, question_id)


@router.put("/questions/{question_id}", response_model=QuestionAdminOut)
def update_question(
    question_id: int, payload: QuestionUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    return service.update_question(db, admin.id, question_id, payload)


@router.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> Response:
    service.soft_delete_question(db, admin.id, question_id)
    return Response(status_code=204)
