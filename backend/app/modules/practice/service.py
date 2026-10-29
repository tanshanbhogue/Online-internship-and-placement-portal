from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.errors import Conflict, NotFound, ValidationFailed
from app.db.base import utcnow
from app.modules.auth.models import User
from app.modules.practice import scoring
from app.modules.practice.code_evaluator import get_code_evaluator
from app.modules.practice.models import (
    EvaluationStatus,
    PracticeAnswer,
    PracticeSession,
    PracticeSessionQuestion,
    SessionStatus,
)
from app.modules.practice.schemas import (
    AnswerFeedback,
    AnswerRequest,
    BreakdownItem,
    CategoryRef,
    SessionResult,
)
from app.modules.question_bank import service as question_bank
from app.modules.question_bank.models import Question, QuestionType


def _load_session(db: Session, student: User, session_id: int) -> PracticeSession:
    """Another student's session is indistinguishable from a missing one (SEC-06)."""
    session = db.scalar(
        select(PracticeSession)
        .where(PracticeSession.id == session_id, PracticeSession.student_id == student.id)
        .options(
            selectinload(PracticeSession.session_questions).selectinload(PracticeSessionQuestion.question).selectinload(Question.options),
            selectinload(PracticeSession.answers),
        )
        # Always re-read collections (answers change between requests, even if the Session object is reused).
        .execution_options(populate_existing=True)
    )
    if session is None:
        raise NotFound("Practice session not found")
    return session


def start_session(db: Session, student: User, category_id: int, count: int | None) -> PracticeSession:
    questions = question_bank.pick_questions_for_practice(
        db, category_id, count if count is not None else settings.PRACTICE_DEFAULT_QUESTION_COUNT
    )  # NotFound when the category does not exist
    if not questions:
        raise NotFound("No questions found", code="no_questions")

    session = PracticeSession(
        student_id=student.id,  # always from the authenticated user, never from the request
        category_id=category_id,
        status=SessionStatus.IN_PROGRESS,
        total_questions=len(questions),
    )
    session.session_questions = [PracticeSessionQuestion(question_id=q.id, position=i) for i, q in enumerate(questions)]
    db.add(session)
    db.commit()
    return _load_session(db, student, session.id)


def submit_answer(db: Session, student: User, session_id: int, payload: AnswerRequest) -> AnswerFeedback:
    session = _load_session(db, student, session_id)
    if session.status != SessionStatus.IN_PROGRESS:
        raise Conflict("Session already finished")

    entry = next((sq for sq in session.session_questions if sq.question_id == payload.question_id), None)
    if entry is None:
        raise NotFound("Question is not part of this session")
    if any(a.question_id == payload.question_id for a in session.answers):
        raise Conflict("Question already answered")

    question = entry.question
    keys = question_bank.get_answer_key(db, [question.id])
    key = keys[question.id]

    if question.type == QuestionType.MCQ:
        if payload.selected_option_id is None:
            raise ValidationFailed(fields={"selected_option_id": ["Select an option"]})
        if payload.selected_option_id not in {o.id for o in question.options}:
            raise ValidationFailed(fields={"selected_option_id": ["Not a valid option for this question"]})
        is_correct = payload.selected_option_id in key.correct_option_ids
        status = EvaluationStatus.EVALUATED
        answer = PracticeAnswer(
            session_id=session.id, question_id=question.id, selected_option_id=payload.selected_option_id,
            is_correct=is_correct, evaluation_status=status,
        )
    else:
        if payload.code is None:
            raise ValidationFailed(fields={"code": ["Enter your code"]})
        result = get_code_evaluator().evaluate(question, payload.code)  # stored, never executed
        is_correct, status = result.is_correct, result.status
        answer = PracticeAnswer(
            session_id=session.id, question_id=question.id, submitted_code=payload.code,
            is_correct=is_correct, evaluation_status=status,
        )

    db.add(answer)
    session.answered_count += 1
    if is_correct is True:
        session.correct_count += 1
    try:
        db.commit()  # persisted immediately so leaving mid-session keeps progress
    except IntegrityError:
        db.rollback()
        raise Conflict("Question already answered")

    correct_option_id = min(key.correct_option_ids) if question.type == QuestionType.MCQ and key.correct_option_ids else None
    return AnswerFeedback(
        question_id=question.id,
        is_correct=is_correct,
        evaluation_status=status.value,
        correct_option_id=correct_option_id,
        explanation=key.explanation,
    )


def _build_result(db: Session, session: PracticeSession) -> SessionResult:
    answers = {a.question_id: a for a in session.answers}
    keys = question_bank.get_answer_key(db, [sq.question_id for sq in session.session_questions])
    breakdown: list[BreakdownItem] = []
    for sq in session.session_questions:
        key, answer = keys.get(sq.question_id), answers.get(sq.question_id)
        correct_option = min(key.correct_option_ids) if key and key.correct_option_ids else None
        breakdown.append(
            BreakdownItem(
                question_id=sq.question_id,
                prompt=sq.question.prompt,
                selected_option_id=answer.selected_option_id if answer else None,
                correct_option_id=correct_option,
                is_correct=(answer.is_correct if answer else False),  # unanswered counts as not correct
                explanation=key.explanation if key else None,
            )
        )
    return SessionResult(
        session_id=session.id,
        category=CategoryRef(id=session.category.id, name=session.category.name),
        status=session.status.value,
        total_questions=session.total_questions,
        answered_count=session.answered_count,
        correct_count=session.correct_count,
        score_percent=session.score_percent,
        completed_at=session.completed_at,
        breakdown=breakdown,
    )


def finish_session(db: Session, student: User, session_id: int) -> SessionResult:
    session = _load_session(db, student, session_id)
    if session.status != SessionStatus.COMPLETED:  # idempotent: finishing twice returns the same result
        summary = scoring.score_session(
            session.total_questions,
            [scoring.AnswerResult(a.is_correct, a.evaluation_status) for a in session.answers],
        )
        session.answered_count = summary.answered
        session.correct_count = summary.correct
        session.score_percent = summary.percent
        session.status = SessionStatus.COMPLETED
        session.completed_at = utcnow()
        db.commit()
    return _build_result(db, session)


def get_result(db: Session, student: User, session_id: int) -> SessionResult:
    session = _load_session(db, student, session_id)
    if session.status != SessionStatus.COMPLETED:
        raise Conflict("Session not finished")
    return _build_result(db, session)


def list_history(db: Session, student: User) -> list[PracticeSession]:
    return list(
        db.scalars(
            select(PracticeSession)
            .where(PracticeSession.student_id == student.id, PracticeSession.status == SessionStatus.COMPLETED)
            .order_by(PracticeSession.completed_at.desc(), PracticeSession.id.desc())
        ).all()
    )
