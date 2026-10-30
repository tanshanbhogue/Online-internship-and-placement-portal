# Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
# File: backend/tests/test_mock_auto_submit.py
#
# Covers Test Plan UT_14, ST_07 (server side) and Security SEC-06, SEC-07, SEC-13, SEC-14, SEC-20.
# Attempts are built directly from the models, so this file does not depend on story #23.
from datetime import datetime, timedelta, timezone

import pytest
from freezegun import freeze_time
from sqlalchemy import func, select

from app.modules.mock_test import finalize
from app.modules.mock_test.models import (
    AttemptStatus,
    AutoSubmitEvent,
    MockAttempt,
    MockAttemptAnswer,
    MockAttemptQuestion,
    MockTest,
    MockTestQuestion,
)
from app.modules.mock_test.timing import GRACE_SECONDS, accepts_late_input, is_expired, remaining_seconds
from app.modules.question_bank.models import Category, Difficulty, Question, QuestionOption, QuestionType


# ------------------------------------------------------------------ helpers
def _now():
    return datetime.now(timezone.utc)


@pytest.fixture()
def bank(db):
    """One category, one 1-minute test with 4 MCQs (option index 1 is always the correct one)."""
    category = Category(name="Aptitude", slug="aptitude")
    db.add(category)
    db.commit()
    questions = []
    for n in range(4):
        q = Question(
            category_id=category.id, type=QuestionType.MCQ, prompt=f"Q{n}", difficulty=Difficulty.EASY,
            options=[QuestionOption(text=f"o{i}", is_correct=(i == 1), position=i) for i in range(3)],
        )
        db.add(q)
        questions.append(q)
    db.commit()
    test = MockTest(title="Full Aptitude Mock", category_id=category.id, duration_minutes=1)
    test.test_questions = [MockTestQuestion(question_id=q.id, position=i) for i, q in enumerate(questions)]
    db.add(test)
    db.commit()
    return test, questions


def _option(db, question, correct: bool) -> int:
    return db.scalar(select(QuestionOption.id).where(QuestionOption.question_id == question.id, QuestionOption.is_correct.is_(correct)))


def make_attempt(db, student, test, questions, *, started_at=None, answers=()):
    """`answers` = list of (question_index, correct?)."""
    started = started_at or _now()
    attempt = MockAttempt(
        student_id=student.id, test_id=test.id, started_at=started,
        ends_at=started + timedelta(minutes=test.duration_minutes), total_questions=len(questions),
    )
    attempt.attempt_questions = [MockAttemptQuestion(question_id=q.id, position=i) for i, q in enumerate(questions)]
    for index, correct in answers:
        attempt.answers.append(MockAttemptAnswer(question_id=questions[index].id, selected_option_id=_option(db, questions[index], correct)))
    db.add(attempt)
    db.commit()
    return attempt


def _jump(seconds):
    """Freeze the SERVER clock `seconds` from now (kept small: the login cookie lasts 30 minutes)."""
    return freeze_time(_now() + timedelta(seconds=seconds))


@pytest.fixture()
def student(make_user):
    return make_user("student@test.com", role="student")


# ------------------------------------------------------------------ pure timing helpers (SEC-13)
def test_timing_helpers_use_the_given_clock(db, bank, student):
    test, questions = bank
    attempt = make_attempt(db, student, test, questions)
    assert remaining_seconds(attempt, attempt.started_at) == 60
    assert remaining_seconds(attempt, attempt.started_at + timedelta(seconds=59, milliseconds=100)) == 1  # rounded up
    assert remaining_seconds(attempt, attempt.ends_at + timedelta(minutes=5)) == 0  # never negative
    assert not is_expired(attempt, attempt.ends_at - timedelta(milliseconds=1))
    assert is_expired(attempt, attempt.ends_at)
    assert accepts_late_input(attempt, attempt.ends_at + timedelta(seconds=GRACE_SECONDS))
    assert not accepts_late_input(attempt, attempt.ends_at + timedelta(seconds=GRACE_SECONDS, milliseconds=1))


# ------------------------------------------------------------------ finalize / scoring (UT_14, ST_07)
def test_ut14_expired_attempt_is_auto_submitted_and_scored(db, bank, student):
    test, questions = bank
    attempt = make_attempt(db, student, test, questions, answers=[(0, True), (1, True), (2, False)])  # 4th unanswered
    with _jump(61):
        closed, transitioned = finalize.auto_submit_if_expired(db, attempt.id, source="lazy")
    assert transitioned and closed.status == AttemptStatus.AUTO_SUBMITTED
    assert closed.submitted_at == attempt.ends_at  # UC-6 step 6: the configured end time, not "now"
    assert (closed.answered_count, closed.correct_count, closed.score_percent) == (3, 2, 50.0)  # 2 of 4 questions
    assert db.scalar(select(func.count(AutoSubmitEvent.id))) == 1


def test_answers_are_marked_only_after_finalization(db, bank, student):
    test, questions = bank
    attempt = make_attempt(db, student, test, questions, answers=[(0, True), (1, False)])
    assert [a.is_correct for a in attempt.answers] == [None, None]  # SEC-12: nothing is evaluated while the test runs
    with _jump(61):
        finalize.auto_submit_if_expired(db, attempt.id, source="lazy")
    rows = {a.question_id: a.is_correct for a in db.scalars(select(MockAttemptAnswer)).all()}
    assert rows == {questions[0].id: True, questions[1].id: False}


def test_manual_submit_before_expiry_is_a_normal_submission(db, bank, student):
    test, questions = bank
    attempt = make_attempt(db, student, test, questions, answers=[(0, True)])
    closed, transitioned = finalize.finalize_attempt(db, attempt.id, auto=False, source="manual")
    assert transitioned and closed.status == AttemptStatus.SUBMITTED
    assert closed.submitted_at < closed.ends_at
    assert db.scalar(select(func.count(AutoSubmitEvent.id))) == 0  # only the timer creates audit rows


def test_manual_submit_after_expiry_is_recorded_as_auto_submitted(db, bank, student):
    test, questions = bank
    attempt = make_attempt(db, student, test, questions, answers=[(0, True)])
    with _jump(90):
        closed, _ = finalize.finalize_attempt(db, attempt.id, auto=False, source="manual")
    assert closed.status == AttemptStatus.AUTO_SUBMITTED and closed.submitted_at == attempt.ends_at


def test_auto_finalize_refuses_while_time_remains(db, bank, student):
    from app.core.errors import Conflict

    test, questions = bank
    attempt = make_attempt(db, student, test, questions)
    with pytest.raises(Conflict) as exc:
        finalize.finalize_attempt(db, attempt.id, auto=True, source="client")
    assert exc.value.code == "not_expired"
    db.refresh(attempt)
    assert attempt.status == AttemptStatus.IN_PROGRESS


def test_sec14_finalizing_twice_changes_nothing_the_second_time(db, bank, student):
    test, questions = bank
    attempt = make_attempt(db, student, test, questions, answers=[(0, True)])
    with _jump(61):
        _, first = finalize.auto_submit_if_expired(db, attempt.id, source="client")
        again, second = finalize.auto_submit_if_expired(db, attempt.id, source="sweeper")
    assert (first, second) == (True, False)
    assert again.status == AttemptStatus.AUTO_SUBMITTED
    assert db.scalar(select(func.count(AutoSubmitEvent.id))) == 1  # one audit row, one scoring pass


def test_sec14_lost_race_after_manual_submit_creates_no_second_record(db, bank, student):
    test, questions = bank
    attempt = make_attempt(db, student, test, questions)
    finalize.finalize_attempt(db, attempt.id, auto=False, source="manual")  # the student was a moment faster
    with _jump(61):
        after, transitioned = finalize.auto_submit_if_expired(db, attempt.id, source="sweeper")
    assert not transitioned and after.status == AttemptStatus.SUBMITTED  # stays a normal submission
    assert db.scalar(select(func.count(AutoSubmitEvent.id))) == 0


def test_one_open_attempt_per_student_and_test_is_enforced_by_the_database(db, bank, student):
    from sqlalchemy.exc import IntegrityError

    test, questions = bank
    make_attempt(db, student, test, questions)
    with pytest.raises(IntegrityError):
        make_attempt(db, student, test, questions)
    db.rollback()


# ------------------------------------------------------------------ sweeper
def test_sweeper_closes_only_expired_attempts(db, bank, make_user):
    test, questions = bank
    old, fresh = make_user("old@test.com"), make_user("fresh@test.com")
    expired = make_attempt(db, old, test, questions, started_at=_now() - timedelta(minutes=5))
    running = make_attempt(db, fresh, test, questions)
    assert finalize.sweep_expired(db) == 1
    db.refresh(expired)
    db.refresh(running)
    assert expired.status == AttemptStatus.AUTO_SUBMITTED and running.status == AttemptStatus.IN_PROGRESS
    assert finalize.sweep_expired(db) == 0  # running it again is harmless
    event = db.scalar(select(AutoSubmitEvent))
    assert event.source == "sweeper" and event.attempt_id == expired.id


# ------------------------------------------------------------------ HTTP: student endpoint
def test_endpoint_rejects_early_request_and_keeps_the_attempt_open(student_client, db, bank):
    from app.modules.auth.models import User

    test, questions = bank
    logged_in = db.scalar(select(User).where(User.email == "student@test.com"))
    attempt = make_attempt(db, logged_in, test, questions)
    response = student_client.post(f"/api/mock-attempts/{attempt.id}/auto-submit")
    assert response.status_code == 409 and response.json()["code"] == "not_expired"
    db.refresh(attempt)
    assert attempt.status == AttemptStatus.IN_PROGRESS  # a tampered client timer cannot end the test early (SEC-13)


def test_st07_endpoint_after_expiry_auto_submits_and_reports_it(student_client, db, bank):
    from app.modules.auth.models import User

    test, questions = bank
    logged_in = db.scalar(select(User).where(User.email == "student@test.com"))
    attempt = make_attempt(db, logged_in, test, questions, answers=[(0, True), (1, True)])
    with _jump(61):
        response = student_client.post(f"/api/mock-attempts/{attempt.id}/auto-submit")
    body = response.json()
    assert response.status_code == 200
    assert (body["status"], body["auto_submitted"], body["already_final"]) == ("auto_submitted", True, False)
    # calling it again (browser retry) is harmless
    with _jump(65):
        again = student_client.post(f"/api/mock-attempts/{attempt.id}/auto-submit").json()
    assert (again["status"], again["already_final"]) == ("auto_submitted", True)
    assert db.scalar(select(func.count(AutoSubmitEvent.id))) == 1


def test_endpoint_after_manual_submit_reports_already_final(student_client, db, bank):
    from app.modules.auth.models import User

    test, questions = bank
    logged_in = db.scalar(select(User).where(User.email == "student@test.com"))
    attempt = make_attempt(db, logged_in, test, questions)
    finalize.finalize_attempt(db, attempt.id, auto=False, source="manual")
    with _jump(61):
        body = student_client.post(f"/api/mock-attempts/{attempt.id}/auto-submit").json()
    assert (body["status"], body["auto_submitted"], body["already_final"]) == ("submitted", False, True)


def test_sec06_another_students_attempt_looks_missing(student_client, db, bank, make_user):
    test, questions = bank
    other = make_user("other@test.com")
    attempt = make_attempt(db, other, test, questions, started_at=_now() - timedelta(minutes=5))
    assert student_client.post(f"/api/mock-attempts/{attempt.id}/auto-submit").status_code == 404
    db.refresh(attempt)
    assert attempt.status == AttemptStatus.IN_PROGRESS  # and it was not closed by the stranger's call


def test_endpoint_requires_a_session(client, db, bank, student):
    test, questions = bank
    attempt = make_attempt(db, student, test, questions)
    assert client.post(f"/api/mock-attempts/{attempt.id}/auto-submit").status_code == 401


# ------------------------------------------------------------------ HTTP: admin sweep (SEC-07)
def test_sec07_admin_sweep_is_admin_only(client, student_client, admin_client, db, bank, make_user):
    test, questions = bank
    other = make_user("late@test.com")
    make_attempt(db, other, test, questions, started_at=_now() - timedelta(minutes=5))
    assert client.post("/api/admin/mock-attempts/sweep").status_code == 401  # guest
    assert student_client.post("/api/admin/mock-attempts/sweep").status_code == 403  # student
    response = admin_client.post("/api/admin/mock-attempts/sweep")
    assert response.status_code == 200 and response.json() == {"auto_submitted": 1}


# ------------------------------------------------------------------ audit log (SEC-20)
def test_sec20_auto_submit_is_logged_without_answers(db, bank, student, caplog):
    test, questions = bank
    attempt = make_attempt(db, student, test, questions, answers=[(0, True)])
    with caplog.at_level("INFO", logger="security.audit"), _jump(61):
        finalize.auto_submit_if_expired(db, attempt.id, source="client")
    line = next(r.getMessage() for r in caplog.records if "auto_submitted" in r.getMessage())
    assert f"attempt_id={attempt.id}" in line and "source=client" in line
    assert "selected_option" not in line and "password" not in line.lower()
