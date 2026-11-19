# Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
# File: backend/app/modules/mock_test/service.py
#
# Contract
#   list_tests(db, student)                    -> list of (MockTest, question_count, open_attempt_id | None)
#   start_attempt(db, student, test_id)        -> (MockAttempt, resumed: bool)   resumes an open attempt, else creates one
#   get_attempt(db, student, attempt_id)       -> MockAttempt                    owner-only (SEC-06); closes it first if time is up
#   build_state(attempt, *, resumed=None)      -> AttemptState                   no answer keys (SEC-12), server-time remaining
#   save_answer(db, student, attempt_id, ...)  -> remaining_seconds              409 time_expired / already_submitted
#   submit_attempt(db, student, attempt_id, answers) -> (MockAttempt, transitioned)
# All time decisions use the server clock (SEC-13); closing goes through story #24's finalize_attempt (SEC-14).
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import Conflict, NotFound, ValidationFailed
from app.db.base import utcnow
from app.modules.auth.models import User
from app.modules.mock_test import finalize
from app.modules.mock_test.models import (
    AttemptStatus,
    MockAttempt,
    MockAttemptAnswer,
    MockAttemptQuestion,
    MockTest,
    MockTestQuestion,
)
from app.modules.mock_test.schemas import (
    AttemptState,
    CategoryRef,
    SaveAnswerRequest,
    StartAttemptResponse,
    TestRef,
)
from app.modules.mock_test.timing import accepts_late_input, is_expired, remaining_seconds
from app.modules.question_bank.models import QuestionType
from app.modules.question_bank.schemas import QuestionPublic


# ----------------------------------------------------------------------------- tests
def _usable_questions(test: MockTest) -> list[MockTestQuestion]:
    """Only active multiple-choice questions can be taken (coding answers are never executed, SEC-17)."""
    return [tq for tq in test.test_questions if tq.question.is_active and tq.question.type == QuestionType.MCQ]


def list_tests(db: Session, student: User) -> list[tuple[MockTest, int, int | None]]:
    tests = db.scalars(select(MockTest).where(MockTest.is_active.is_(True)).order_by(MockTest.id)).unique().all()
    open_attempts = {
        test_id: attempt_id
        for attempt_id, test_id in db.execute(
            select(MockAttempt.id, MockAttempt.test_id).where(
                MockAttempt.student_id == student.id, MockAttempt.status == AttemptStatus.IN_PROGRESS
            )
        ).all()
    }
    rows = []
    for test in tests:
        count = len(_usable_questions(test))
        if count == 0:
            continue  # nothing to take yet
        rows.append((test, count, open_attempts.get(test.id)))
    return rows


def _get_test(db: Session, test_id: int) -> MockTest:
    test = db.get(MockTest, test_id)
    if test is None or not test.is_active:
        raise NotFound("Mock test not found")
    return test


# ----------------------------------------------------------------------------- attempts
def _open_attempt(db: Session, student_id: int, test_id: int) -> MockAttempt | None:
    return db.scalar(
        select(MockAttempt)
        .where(MockAttempt.student_id == student_id, MockAttempt.test_id == test_id, MockAttempt.status == AttemptStatus.IN_PROGRESS)
        .execution_options(populate_existing=True)
    )


def start_attempt(db: Session, student: User, test_id: int) -> tuple[MockAttempt, bool]:
    test = _get_test(db, test_id)

    existing = _open_attempt(db, student.id, test.id)
    if existing is not None:
        if not is_expired(existing):
            return existing, True  # refresh / reconnect: same attempt, same deadline (IT_10, UC-5 alt flow)
        finalize.auto_submit_if_expired(db, existing.id, source="lazy")  # the old try ran out: close it, then start fresh

    questions = _usable_questions(test)
    if not questions:
        raise NotFound("No questions found", code="no_questions")

    started = utcnow()
    attempt = MockAttempt(
        student_id=student.id,  # always the authenticated user, never taken from the request
        test_id=test.id,
        status=AttemptStatus.IN_PROGRESS,
        started_at=started,
        ends_at=started + timedelta(minutes=test.duration_minutes),
        total_questions=len(questions),
    )
    attempt.attempt_questions = [MockAttemptQuestion(question_id=tq.question_id, position=i) for i, tq in enumerate(questions)]
    db.add(attempt)
    try:
        db.commit()
    except IntegrityError:  # two tabs pressed Start together: the unique index let only one through
        db.rollback()
        winner = _open_attempt(db, student.id, test.id)
        if winner is None:
            raise
        return winner, True
    return _open_attempt(db, student.id, test.id), False


def _owned_attempt(db: Session, student: User, attempt_id: int, *, lock: bool = False) -> MockAttempt:
    """Another student's attempt is indistinguishable from a missing one (SEC-06)."""
    query = select(MockAttempt).where(MockAttempt.id == attempt_id, MockAttempt.student_id == student.id)
    if lock:
        query = query.with_for_update(of=MockAttempt)  # no-op on SQLite; row lock on PostgreSQL
    attempt = db.scalar(query.execution_options(populate_existing=True))
    if attempt is None:
        raise NotFound("Attempt not found")
    return attempt


def get_attempt(db: Session, student: User, attempt_id: int) -> MockAttempt:
    attempt = _owned_attempt(db, student, attempt_id)
    if attempt.status == AttemptStatus.IN_PROGRESS and is_expired(attempt):
        attempt, _ = finalize.auto_submit_if_expired(db, attempt.id, source="lazy")
    return attempt


def build_state(db: Session, attempt: MockAttempt, *, resumed: bool | None = None) -> AttemptState | StartAttemptResponse:
    open_ = attempt.status == AttemptStatus.IN_PROGRESS
    questions: list[QuestionPublic] = []
    answers: dict[int, int] = {}
    if open_:
        questions = [QuestionPublic.model_validate(aq.question) for aq in attempt.attempt_questions]
        answers = {
            qid: oid
            for qid, oid in db.execute(
                select(MockAttemptAnswer.question_id, MockAttemptAnswer.selected_option_id).where(MockAttemptAnswer.attempt_id == attempt.id)
            ).all()
        }
    now = utcnow()
    data = dict(
        attempt_id=attempt.id,
        test=TestRef(
            id=attempt.test.id,
            title=attempt.test.title,
            category=CategoryRef(id=attempt.test.category.id, name=attempt.test.category.name),
            duration_minutes=attempt.test.duration_minutes,
        ),
        status=attempt.status.value,
        started_at=attempt.started_at,
        ends_at=attempt.ends_at,
        server_time=now,
        remaining_seconds=remaining_seconds(attempt, now) if open_ else 0,
        total_questions=attempt.total_questions,
        questions=questions,
        answers=answers,
    )
    return StartAttemptResponse(**data, resumed=resumed) if resumed is not None else AttemptState(**data)


# ----------------------------------------------------------------------------- answers
def _validated_choice(attempt: MockAttempt, question_id: int, option_id: int | None) -> MockAttemptQuestion:
    entry = next((aq for aq in attempt.attempt_questions if aq.question_id == question_id), None)
    if entry is None:
        raise NotFound("Question is not part of this attempt")
    if option_id is not None and option_id not in {o.id for o in entry.question.options}:
        raise ValidationFailed(fields={"selected_option_id": ["Not a valid option for this question"]})
    return entry


def _store_choice(db: Session, attempt_id: int, question_id: int, option_id: int | None) -> None:
    existing = db.scalar(select(MockAttemptAnswer).where(MockAttemptAnswer.attempt_id == attempt_id, MockAttemptAnswer.question_id == question_id))
    if option_id is None:
        if existing is not None:
            db.delete(existing)  # "clear my answer"
        return
    if existing is not None:
        existing.selected_option_id = option_id
    else:
        db.add(MockAttemptAnswer(attempt_id=attempt_id, question_id=question_id, selected_option_id=option_id))


def save_answer(db: Session, student: User, attempt_id: int, payload: SaveAnswerRequest) -> int:
    attempt = _owned_attempt(db, student, attempt_id, lock=True)
    if attempt.status != AttemptStatus.IN_PROGRESS:
        raise Conflict("This test has already been submitted", code="already_submitted")
    if is_expired(attempt):
        finalize.auto_submit_if_expired(db, attempt.id, source="lazy")
        raise Conflict("The time limit has expired", code="time_expired")

    _validated_choice(attempt, payload.question_id, payload.selected_option_id)
    _store_choice(db, attempt.id, payload.question_id, payload.selected_option_id)
    try:
        db.commit()
    except IntegrityError:  # two requests created the same row at once: the second one just updates it
        db.rollback()
        _store_choice(db, attempt.id, payload.question_id, payload.selected_option_id)
        db.commit()
    return remaining_seconds(attempt)


def submit_attempt(db: Session, student: User, attempt_id: int, answers: list[SaveAnswerRequest] | None) -> tuple[MockAttempt, bool]:
    attempt = _owned_attempt(db, student, attempt_id, lock=True)
    if attempt.status != AttemptStatus.IN_PROGRESS:
        return attempt, False  # a second click / retry: same answer, nothing written (SEC-14)

    if answers and accepts_late_input(attempt):
        for item in answers:  # validate everything first, so a bad payload changes nothing
            _validated_choice(attempt, item.question_id, item.selected_option_id)
        for item in answers:
            _store_choice(db, attempt.id, item.question_id, item.selected_option_id)
        db.commit()

    return finalize.finalize_attempt(db, attempt.id, auto=False, source="manual")
