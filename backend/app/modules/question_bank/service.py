# ==============================================================================
# FILE   : backend/app/modules/question_bank/service.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Business logic for reading and administering questions. Also exposes the internal answer-key lookup used by practice scoring (#22).
#
# EXPOSES (names used by #22, do not rename)
#   list_categories(db) -> list[tuple[Category, int]]          # with count of active questions
#   list_public_questions(db, category_id, count: int, difficulty: Difficulty | None) -> tuple[list[Question], int]
#       random sample of active questions (limit count, default settings.PRACTICE_DEFAULT_QUESTION_COUNT, max 50); NotFound if category missing; EMPTY list if none (IT_07)
#   pick_questions_for_practice(db, category_id, count) -> list[Question]     # same selection used when a practice session starts
#   get_answer_key(db, question_ids: list[int]) -> dict[int, AnswerKey]
#       AnswerKey = dataclass(question_id, type, correct_option_ids: set[int], explanation) ; INTERNAL ONLY, never returned by an HTTP route
#   Admin: create_category, create_question, update_question, soft_delete_question, list_admin_questions(db, category_id, page, page_size), get_admin_question
#
# RULES
#   Validation failures raise ValidationFailed with field messages. Every admin mutation writes a security.audit log line with admin id, action and question id (SEC-20). Parameterised ORM queries only.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

import logging
import re
from dataclasses import dataclass

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.errors import Conflict, NotFound, ValidationFailed, fields_from_pydantic
from app.modules.question_bank.models import Category, Difficulty, Question, QuestionOption, QuestionType
from app.modules.question_bank.schemas import CategoryCreate, QuestionCreate, QuestionUpdate

audit = logging.getLogger("security.audit")

MAX_PRACTICE_QUESTIONS = 50


@dataclass(frozen=True)
class AnswerKey:
    """INTERNAL ONLY. Never returned by an HTTP route (SEC-12)."""

    question_id: int
    type: QuestionType
    correct_option_ids: set[int]
    explanation: str | None


# ----------------------------------------------------------------------------- student side
def list_categories(db: Session) -> list[tuple[Category, int]]:
    active_count = func.count(Question.id)
    rows = db.execute(
        select(Category, active_count)
        .outerjoin(Question, (Question.category_id == Category.id) & (Question.is_active.is_(True)))
        .group_by(Category.id)
        .order_by(Category.id)
    ).all()
    return [(category, int(count)) for category, count in rows]


def _get_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise NotFound("Category not found")
    return category


def _clamp_count(count: int | None) -> int:
    value = settings.PRACTICE_DEFAULT_QUESTION_COUNT if count is None else count
    return max(1, min(int(value), MAX_PRACTICE_QUESTIONS))


def list_public_questions(
    db: Session, category_id: int, count: int | None, difficulty: Difficulty | None
) -> tuple[list[Question], int]:
    """Random sample of ACTIVE questions of that category. Empty list (not an error) when there are none."""
    _get_category(db, category_id)
    conditions = [Question.category_id == category_id, Question.is_active.is_(True)]
    if difficulty is not None:
        conditions.append(Question.difficulty == difficulty)
    available = db.scalar(select(func.count(Question.id)).where(*conditions)) or 0
    items = db.scalars(
        select(Question)
        .where(*conditions)
        .options(selectinload(Question.options))
        .order_by(func.random())
        .limit(_clamp_count(count))
    ).all()
    return list(items), int(available)


def pick_questions_for_practice(db: Session, category_id: int, count: int | None) -> list[Question]:
    questions, _ = list_public_questions(db, category_id, count, None)
    return questions


def get_answer_key(db: Session, question_ids: list[int]) -> dict[int, AnswerKey]:
    if not question_ids:
        return {}
    questions = db.scalars(
        select(Question).where(Question.id.in_(question_ids)).options(selectinload(Question.options))
    ).all()
    return {
        q.id: AnswerKey(
            question_id=q.id,
            type=q.type,
            correct_option_ids={o.id for o in q.options if o.is_correct},
            explanation=q.explanation,
        )
        for q in questions
    }


# ----------------------------------------------------------------------------- admin side
def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return (slug or "category")[:60]


def create_category(db: Session, admin_id: int, data: CategoryCreate) -> Category:
    name = data.name.strip()
    slug = _slugify(name)
    clash = db.scalar(select(Category.id).where(func.lower(Category.name) == name.lower()))
    if clash is not None or db.scalar(select(Category.id).where(Category.slug == slug)) is not None:
        raise Conflict("A category with this name already exists")
    category = Category(name=name, slug=slug)
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise Conflict("A category with this name already exists")
    audit.info("category_created admin_id=%s category_id=%s", admin_id, category.id)
    return category


def _apply_fields(question: Question, data: QuestionCreate) -> None:
    question.category_id = data.category_id
    question.type = data.type
    question.prompt = data.prompt
    question.difficulty = data.difficulty
    question.explanation = (data.explanation or "").strip() or None
    question.starter_code = data.starter_code if data.type == QuestionType.CODING else None
    question.test_cases = data.test_cases if data.type == QuestionType.CODING else None
    question.options = [
        QuestionOption(text=o.text, is_correct=o.is_correct, position=i) for i, o in enumerate(data.options)
    ]


def _require_category(db: Session, category_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise ValidationFailed(fields={"category_id": ["Category does not exist"]})


def create_question(db: Session, admin_id: int, data: QuestionCreate) -> Question:
    _require_category(db, data.category_id)
    question = Question()
    _apply_fields(question, data)
    db.add(question)
    db.commit()
    audit.info("question_created admin_id=%s question_id=%s", admin_id, question.id)
    return question


def get_admin_question(db: Session, question_id: int) -> Question:
    question = db.scalar(select(Question).where(Question.id == question_id).options(selectinload(Question.options)))
    if question is None:
        raise NotFound("Question not found")
    return question


def update_question(db: Session, admin_id: int, question_id: int, data: QuestionUpdate) -> Question:
    question = get_admin_question(db, question_id)
    merged = {
        "category_id": question.category_id,
        "type": question.type,
        "prompt": question.prompt,
        "difficulty": question.difficulty,
        "explanation": question.explanation,
        "starter_code": question.starter_code,
        "test_cases": question.test_cases,
        "options": [{"text": o.text, "is_correct": o.is_correct} for o in question.options],
    }
    for name in data.model_fields_set:
        value = getattr(data, name)
        if name == "options" and value is not None:
            value = [{"text": o.text, "is_correct": o.is_correct} for o in value]
        merged[name] = value
    if merged["type"] == QuestionType.CODING and "options" not in data.model_fields_set:
        merged["options"] = []  # switching to coding drops the old options
    try:
        validated = QuestionCreate.model_validate(merged)
    except ValidationError as exc:
        raise ValidationFailed(fields=fields_from_pydantic(exc.errors()))
    _require_category(db, validated.category_id)
    _apply_fields(question, validated)
    db.commit()
    audit.info("question_updated admin_id=%s question_id=%s", admin_id, question.id)
    return question


def soft_delete_question(db: Session, admin_id: int, question_id: int) -> None:
    question = get_admin_question(db, question_id)
    question.is_active = False  # kept so practice history still resolves
    db.commit()
    audit.info("question_deleted admin_id=%s question_id=%s", admin_id, question.id)


def list_admin_questions(
    db: Session, category_id: int | None, page: int, page_size: int
) -> tuple[list[Question], int]:
    conditions = []
    if category_id is not None:
        conditions.append(Question.category_id == category_id)
    total = db.scalar(select(func.count(Question.id)).where(*conditions)) or 0
    items = db.scalars(
        select(Question)
        .where(*conditions)
        .options(selectinload(Question.options))
        .order_by(Question.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(items), int(total)
