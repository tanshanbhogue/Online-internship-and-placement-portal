# Story #25 Score and Answer Analysis - owner: Sinchana (sinchanaurs1104)
# File: backend/tests/test_mock_results.py
#
# Covers Test Plan UT_15, IT_09, ST_07 (analysis part), ST_08 and Security SEC-06, SEC-12.
# Attempts are built from the #24 models and closed with finalize_attempt, so #23's routes are not needed.
from datetime import datetime, timedelta, timezone

import pytest
from freezegun import freeze_time
from sqlalchemy import select

from app.modules.auth.models import User
from app.modules.mock_test import finalize
from app.modules.mock_test.models import (
    MockAttempt,
    MockAttemptAnswer,
    MockAttemptQuestion,
    MockTest,
    MockTestQuestion,
)
from app.modules.question_bank.models import Category, Difficulty, Question, QuestionOption, QuestionType

DIFFS = [Difficulty.EASY, Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]


def _now():
    return datetime.now(timezone.utc)


@pytest.fixture()
def bank(db):
    category = Category(name="Aptitude", slug="aptitude")
    db.add(category)
    db.commit()
    questions = []
    for n, difficulty in enumerate(DIFFS):
        q = Question(
            category_id=category.id, type=QuestionType.MCQ, prompt=f"Q{n}", difficulty=difficulty, explanation=f"Why {n}",
            options=[QuestionOption(text=f"o{i}", is_correct=(i == 1), position=i) for i in range(3)],
        )
        db.add(q)
        questions.append(q)
    db.commit()
    test = MockTest(title="Full Aptitude Mock", category_id=category.id, duration_minutes=30)
    test.test_questions = [MockTestQuestion(question_id=q.id, position=i) for i, q in enumerate(questions)]
    db.add(test)
    db.commit()
    return test, questions


def _opt(db, question, correct):
    return db.scalar(select(QuestionOption.id).where(QuestionOption.question_id == question.id, QuestionOption.is_correct.is_(correct)))


def closed_attempt(db, student, test, questions, picks, *, minutes_used=10, auto=False, test_obj=None):
    """picks = list of (question index, correct?). Returns the attempt, finalized as manual or auto."""
    started = _now() - timedelta(minutes=minutes_used + (31 if auto else 0))
    attempt = MockAttempt(student_id=student.id, test_id=test.id, started_at=started, ends_at=started + timedelta(minutes=30), total_questions=len(questions))
    attempt.attempt_questions = [MockAttemptQuestion(question_id=q.id, position=i) for i, q in enumerate(questions)]
    for index, correct in picks:
        attempt.answers.append(MockAttemptAnswer(question_id=questions[index].id, selected_option_id=_opt(db, questions[index], correct)))
    db.add(attempt)
    db.commit()
    if auto:
        finalize.auto_submit_if_expired(db, attempt.id, source="sweeper")
    else:
        with freeze_time(started + timedelta(minutes=minutes_used)):
            finalize.finalize_attempt(db, attempt.id, auto=False, source="manual")
    db.refresh(attempt)
    return attempt


@pytest.fixture()
def me(db, student_client):
    return db.scalar(select(User).where(User.email == "student@test.com"))


# ------------------------------------------------------------------ UT_15 / ST_07: score and breakdown
def test_ut15_summary_and_breakdown_mark_each_question(student_client, db, bank, me):
    test, qs = bank
    attempt = closed_attempt(db, me, test, qs, [(0, True), (1, False), (2, True)], minutes_used=12)  # Q3 skipped
    body = student_client.get(f"/api/mock-results/{attempt.id}").json()
    assert (body["total_questions"], body["answered_count"], body["correct_count"]) == (4, 3, 2)
    assert (body["incorrect_count"], body["skipped_count"]) == (1, 1)
    assert body["score_percent"] == 50.0 and body["accuracy_percent"] == 66.67
    assert body["time_taken_seconds"] == 12 * 60 and body["time_limit_seconds"] == 1800
    assert body["status"] == "submitted" and body["auto_submitted"] is False
    outcomes = [(i["position"], i["outcome"]) for i in body["breakdown"]]
    assert outcomes == [(1, "correct"), (2, "incorrect"), (3, "correct"), (4, "skipped")]
    first = body["breakdown"][0]
    assert first["correct_option_id"] == _opt(db, qs[0], True) and first["selected_option_id"] == _opt(db, qs[0], True)
    assert first["explanation"] == "Why 0" and len(first["options"]) == 3
    wrong = body["breakdown"][1]
    assert wrong["selected_option_id"] == _opt(db, qs[1], False) and wrong["correct_option_id"] == _opt(db, qs[1], True)
    assert body["breakdown"][3]["selected_option_id"] is None


def test_st07_auto_submitted_attempt_is_flagged_and_analysed(student_client, db, bank, me):
    test, qs = bank
    attempt = closed_attempt(db, me, test, qs, [(0, True)], auto=True)
    body = student_client.get(f"/api/mock-results/{attempt.id}").json()
    assert body["status"] == "auto_submitted" and body["auto_submitted"] is True
    assert body["correct_count"] == 1 and body["score_percent"] == 25.0
    assert body["time_taken_seconds"] == 30 * 60  # submitted_at is the configured end time


def test_all_unanswered_has_no_accuracy_but_a_zero_score(student_client, db, bank, me):
    test, qs = bank
    attempt = closed_attempt(db, me, test, qs, [])
    body = student_client.get(f"/api/mock-results/{attempt.id}").json()
    assert body["score_percent"] == 0.0 and body["accuracy_percent"] is None and body["skipped_count"] == 4


def test_by_difficulty_totals(student_client, db, bank, me):
    test, qs = bank
    attempt = closed_attempt(db, me, test, qs, [(0, True), (1, False), (3, True)])
    stats = {s["difficulty"]: (s["total"], s["correct"]) for s in student_client.get(f"/api/mock-results/{attempt.id}").json()["by_difficulty"]}
    assert stats == {"easy": (2, 1), "medium": (1, 0), "hard": (1, 1)}


def test_breakdown_filters_by_difficulty_and_outcome(student_client, db, bank, me):
    test, qs = bank
    attempt = closed_attempt(db, me, test, qs, [(0, True), (1, False), (2, False)])
    url = f"/api/mock-results/{attempt.id}"
    easy = student_client.get(url, params={"difficulty": "easy"}).json()
    assert [i["position"] for i in easy["breakdown"]] == [1, 2] and easy["filtered_count"] == 2
    assert easy["total_questions"] == 4  # the summary is not affected by the filter
    wrong = student_client.get(url, params={"outcome": "incorrect"}).json()
    assert [i["position"] for i in wrong["breakdown"]] == [2, 3]
    both = student_client.get(url, params={"outcome": "skipped", "difficulty": "hard"}).json()
    assert [i["position"] for i in both["breakdown"]] == [4]
    assert student_client.get(url, params={"difficulty": "extreme"}).status_code == 422


# ------------------------------------------------------------------ IT_09 / ST_08: history
def test_it09_result_is_retrievable_later_from_history(student_client, db, bank, me):
    test, qs = bank
    attempt = closed_attempt(db, me, test, qs, [(0, True), (1, True)])
    history = student_client.get("/api/mock-results").json()["items"]
    assert [h["attempt_id"] for h in history] == [attempt.id]
    assert history[0]["score_percent"] == 50.0 and history[0]["test_title"] == "Full Aptitude Mock"
    detail = student_client.get(f"/api/mock-results/{history[0]['attempt_id']}").json()
    assert detail["score_percent"] == history[0]["score_percent"]  # same numbers both ways


def test_st08_back_to_back_attempts_are_listed_separately_newest_first(student_client, db, bank, me):
    test, qs = bank
    first = closed_attempt(db, me, test, qs, [(0, True)], minutes_used=40)
    second = closed_attempt(db, me, test, qs, [(0, True), (1, True), (2, True)], minutes_used=5)
    items = student_client.get("/api/mock-results").json()["items"]
    assert [(i["attempt_id"], i["score_percent"]) for i in items] == [(second.id, 75.0), (first.id, 25.0)]


def test_history_excludes_open_attempts_and_other_students(student_client, db, bank, me, make_user):
    test, qs = bank
    other = make_user("other@test.com")
    closed_attempt(db, other, test, qs, [(0, True)])
    started = _now()
    db.add(MockAttempt(student_id=me.id, test_id=test.id, started_at=started, ends_at=started + timedelta(minutes=30), total_questions=4))
    db.commit()
    assert student_client.get("/api/mock-results").json()["items"] == []


# ------------------------------------------------------------------ SEC-12 / SEC-06
def test_sec12_open_attempt_has_no_result_and_leaks_nothing(student_client, db, bank, me):
    test, qs = bank
    started = _now()
    attempt = MockAttempt(student_id=me.id, test_id=test.id, started_at=started, ends_at=started + timedelta(minutes=30), total_questions=4)
    attempt.attempt_questions = [MockAttemptQuestion(question_id=q.id, position=i) for i, q in enumerate(qs)]
    db.add(attempt)
    db.commit()
    response = student_client.get(f"/api/mock-results/{attempt.id}")
    assert response.status_code == 409 and response.json()["code"] == "attempt_in_progress"
    assert "Why 0" not in response.text and "correct_option_id" not in response.text


def test_open_attempt_whose_time_is_up_is_closed_then_shown(student_client, db, bank, me):
    test, qs = bank
    started = _now() - timedelta(minutes=45)
    attempt = MockAttempt(student_id=me.id, test_id=test.id, started_at=started, ends_at=started + timedelta(minutes=30), total_questions=4)
    attempt.attempt_questions = [MockAttemptQuestion(question_id=q.id, position=i) for i, q in enumerate(qs)]
    db.add(attempt)
    db.commit()
    body = student_client.get(f"/api/mock-results/{attempt.id}").json()
    assert body["status"] == "auto_submitted" and body["score_percent"] == 0.0


def test_sec06_other_students_results_are_invisible(student_client, db, bank, make_user):
    test, qs = bank
    other = make_user("other@test.com")
    attempt = closed_attempt(db, other, test, qs, [(0, True)])
    assert student_client.get(f"/api/mock-results/{attempt.id}").status_code == 404
    assert student_client.get("/api/mock-results/99999").status_code == 404


def test_guests_and_admins_are_refused(client, admin_client, bank):
    assert client.get("/api/mock-results").status_code == 401
    assert client.get("/api/mock-results/1").status_code == 401
    assert admin_client.get("/api/mock-results").status_code == 403


# ------------------------------------------------------------------ percentile
def test_percentile_needs_five_other_attempts_then_ranks_among_them(student_client, db, bank, me, make_user):
    test, qs = bank
    mine = closed_attempt(db, me, test, qs, [(0, True), (1, True), (2, True)])  # 75 %
    assert student_client.get(f"/api/mock-results/{mine.id}").json()["percentile"] is None
    for n, picks in enumerate([[], [(0, True)], [(0, True), (1, True)], [(0, True), (1, True), (2, True)], [(0, True), (1, True), (2, True), (3, True)]]):
        closed_attempt(db, make_user(f"p{n}@test.com"), test, qs, picks)  # 0, 25, 50, 75, 100 %
    assert student_client.get(f"/api/mock-results/{mine.id}").json()["percentile"] == 60  # beats 3 of 5 others
