# Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
# File: backend/app/modules/mock_test/finalize.py
#
# The ONE place an attempt is closed, scored and (when the timer did it) audited. Manual submit (#23), the
# auto-submit endpoint, a late read and the sweeper all call finalize_attempt(), so every path behaves the same.
#
# Contract
#   finalize_attempt(db, attempt_id, *, auto, source) -> (MockAttempt, transitioned: bool)
#       Compare-and-set on status, so two racing callers (manual submit vs timeout) close the attempt ONCE
#       (SEC-14): the loser gets (attempt, False) and nothing is written twice.
#       auto=True raises Conflict(code="not_expired") if the server clock says time is not up (SEC-13).
#       A manual call that arrives after ends_at is recorded as auto_submitted, never as a normal submit.
#   auto_submit_if_expired(db, attempt_id, source) -> (MockAttempt, transitioned)   no-op unless expired
#   sweep_expired(db, limit=500) -> int                                              closes every expired attempt
#   Scoring reuses practice.scoring.score_session so a mock test and a practice set are scored by one rule.
# Tests: tests/test_mock_auto_submit.py (UT_14, ST_07, SEC-13, SEC-14)
import logging
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.errors import Conflict, NotFound
from app.db.base import utcnow
from app.modules.mock_test.models import AttemptStatus, AutoSubmitEvent, MockAttempt, MockAttemptAnswer
from app.modules.mock_test.timing import is_expired
from app.modules.practice import scoring
from app.modules.practice.models import EvaluationStatus
from app.modules.question_bank import service as question_bank

audit = logging.getLogger("security.audit")  # never log answers, tokens or personal data here (SEC-20)


def _load(db: Session, attempt_id: int) -> MockAttempt:
    attempt = db.scalar(
        select(MockAttempt).where(MockAttempt.id == attempt_id).execution_options(populate_existing=True)
    )
    if attempt is None:
        raise NotFound("Attempt not found")
    return attempt


def _score(db: Session, attempt: MockAttempt) -> None:
    """Mark every saved answer correct/incorrect against the SERVER-side key and store the totals."""
    answers = db.scalars(select(MockAttemptAnswer).where(MockAttemptAnswer.attempt_id == attempt.id)).all()
    keys = question_bank.get_answer_key(db, [aq.question_id for aq in attempt.attempt_questions])
    results = []
    for answer in answers:
        key = keys.get(answer.question_id)
        answer.is_correct = bool(key and answer.selected_option_id in key.correct_option_ids)
        results.append(scoring.AnswerResult(answer.is_correct, EvaluationStatus.EVALUATED))
    summary = scoring.score_session(attempt.total_questions, results)
    attempt.answered_count = summary.answered
    attempt.correct_count = summary.correct
    attempt.score_percent = summary.percent  # unanswered questions stay in the denominator, so they count as wrong


def finalize_attempt(
    db: Session,
    attempt_id: int,
    *,
    auto: bool,
    source: str,
    now: datetime | None = None,
) -> tuple[MockAttempt, bool]:
    attempt = _load(db, attempt_id)
    if attempt.status != AttemptStatus.IN_PROGRESS:
        return attempt, False  # already closed: skip, never create a duplicate record

    moment = now or utcnow()
    expired = is_expired(attempt, moment)
    if auto and not expired:
        raise Conflict("The time limit has not expired yet", code="not_expired")

    target = AttemptStatus.AUTO_SUBMITTED if (auto or expired) else AttemptStatus.SUBMITTED
    submitted_at = attempt.ends_at if target == AttemptStatus.AUTO_SUBMITTED else moment

    claimed = db.execute(
        update(MockAttempt)
        .where(MockAttempt.id == attempt_id, MockAttempt.status == AttemptStatus.IN_PROGRESS)
        .values(status=target, submitted_at=submitted_at)
        .execution_options(synchronize_session=False)
    )
    if claimed.rowcount != 1:  # somebody else closed it between our read and our write
        db.rollback()
        return _load(db, attempt_id), False

    try:
        attempt = _load(db, attempt_id)  # re-read inside the same transaction: now holds the new status
        _score(db, attempt)
        if target == AttemptStatus.AUTO_SUBMITTED:
            db.add(AutoSubmitEvent(attempt_id=attempt.id, student_id=attempt.student_id, source=source, ended_at=attempt.ends_at))
        db.commit()
    except Exception:
        db.rollback()  # status goes back to in_progress, so the next caller can retry
        raise

    if target == AttemptStatus.AUTO_SUBMITTED:
        audit.info("mock_attempt.auto_submitted attempt_id=%s student_id=%s source=%s", attempt.id, attempt.student_id, source)
    return attempt, True


def auto_submit_if_expired(db: Session, attempt_id: int, source: str, now: datetime | None = None) -> tuple[MockAttempt, bool]:
    attempt = _load(db, attempt_id)
    if attempt.status == AttemptStatus.IN_PROGRESS and is_expired(attempt, now):
        return finalize_attempt(db, attempt_id, auto=True, source=source, now=now)
    return attempt, False


def sweep_expired(db: Session, limit: int = 500, now: datetime | None = None) -> int:
    """Close every attempt whose time is up. Safe to run often (cron) and from several workers at once."""
    moment = now or utcnow()
    ids = db.scalars(
        select(MockAttempt.id)
        .where(MockAttempt.status == AttemptStatus.IN_PROGRESS, MockAttempt.ends_at <= moment)
        .order_by(MockAttempt.ends_at)
        .limit(limit)
    ).all()
    closed = 0
    for attempt_id in ids:
        try:
            _, transitioned = auto_submit_if_expired(db, attempt_id, source="sweeper", now=moment)
        except Exception:  # one bad row must not stop the others
            db.rollback()
            audit.exception("mock_attempt.sweep_failed attempt_id=%s", attempt_id)
            continue
        closed += 1 if transitioned else 0
    return closed
