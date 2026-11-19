# Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
# File: backend/tests/test_mock_tests.py
#
# Covers Test Plan UT_12, UT_13, IT_09 (attempt stored), IT_10, ST_08 and Security SEC-01, SEC-06, SEC-12, SEC-13, SEC-14.
# Needs story #24 (models, finalize) merged first.
import json
from datetime import datetime, timedelta, timezone

import pytest
from freezegun import freeze_time
from sqlalchemy import func, select

from app.modules.mock_test.models import AttemptStatus, MockAttempt, MockAttemptAnswer, MockTest, MockTestQuestion
from app.modules.question_bank.models import Category, Difficulty, Question, QuestionOption, QuestionType


def _now():
    return datetime.now(timezone.utc)


def _jump(seconds):
    return freeze_time(_now() + timedelta(seconds=seconds))


@pytest.fixture()
def bank(db):
    """Aptitude category with 5 MCQs (option index 1 is correct), a 30-minute test and a 1-minute test."""
    category = Category(name="Aptitude", slug="aptitude")
    db.add(category)
    db.commit()
    questions = []
    for n in range(5):
        q = Question(
            category_id=category.id, type=QuestionType.MCQ, prompt=f"Aptitude Q{n}", difficulty=Difficulty.EASY,
            explanation=f"Secret explanation {n}",
            options=[QuestionOption(text=f"opt{i}", is_correct=(i == 1), position=i) for i in range(3)],
        )
        db.add(q)
        questions.append(q)
    db.commit()

    def make_test(title, minutes, qs):
        test = MockTest(title=title, category_id=category.id, duration_minutes=minutes)
        test.test_questions = [MockTestQuestion(question_id=q.id, position=i) for i, q in enumerate(qs)]
        db.add(test)
        db.commit()
        return test

    return {
        "category": category,
        "questions": questions,
        "full": make_test("Full Aptitude Mock - 30 min", 30, questions),
        "quick": make_test("Quick Check - 1 min", 1, questions[:3]),
    }


def _correct(db, question_id):
    return db.scalar(select(QuestionOption.id).where(QuestionOption.question_id == question_id, QuestionOption.is_correct.is_(True)))


def _wrong(db, question_id):
    return db.scalar(select(QuestionOption.id).where(QuestionOption.question_id == question_id, QuestionOption.is_correct.is_(False)))


def _start(client, test):
    return client.post(f"/api/mock-tests/{test.id}/attempts")


def _answer(client, attempt_id, question_id, option_id):
    return client.put(f"/api/mock-attempts/{attempt_id}/answers", json={"question_id": question_id, "selected_option_id": option_id})


# ------------------------------------------------------------------ list
def test_list_shows_active_tests_with_counts(student_client, bank):
    items = student_client.get("/api/mock-tests").json()["items"]
    assert [(i["title"], i["duration_minutes"], i["question_count"], i["open_attempt_id"]) for i in items] == [
        ("Full Aptitude Mock - 30 min", 30, 5, None),
        ("Quick Check - 1 min", 1, 3, None),
    ]


def test_list_hides_inactive_tests_and_tests_without_usable_questions(student_client, db, bank):
    bank["quick"].is_active = False
    db.add(MockTest(title="Empty", category_id=bank["category"].id, duration_minutes=10))
    db.commit()
    assert [i["title"] for i in student_client.get("/api/mock-tests").json()["items"]] == ["Full Aptitude Mock - 30 min"]


def test_coding_and_inactive_questions_are_not_part_of_an_attempt(student_client, db, bank):
    coding = Question(category_id=bank["category"].id, type=QuestionType.CODING, prompt="Code", difficulty=Difficulty.EASY, test_cases=json.dumps([]))
    db.add(coding)
    db.commit()
    bank["full"].test_questions.append(MockTestQuestion(question_id=coding.id, position=9))
    bank["questions"][0].is_active = False
    db.commit()
    body = _start(student_client, bank["full"]).json()
    assert body["total_questions"] == 4 and {q["type"] for q in body["questions"]} == {"mcq"}


# ------------------------------------------------------------------ UT_12 start with a visible countdown
def test_ut12_start_returns_server_time_countdown_and_questions(student_client, bank):
    response = _start(student_client, bank["quick"])
    body = response.json()
    assert response.status_code == 201 and body["resumed"] is False
    assert body["remaining_seconds"] == 60 and body["status"] == "in_progress"
    assert body["total_questions"] == 3 and len(body["questions"]) == 3 and body["answers"] == {}
    assert body["test"]["title"] == "Quick Check - 1 min"


def test_sec12_no_answer_keys_or_explanations_before_submission(student_client, db, bank):
    start = _start(student_client, bank["quick"])
    attempt_id = start.json()["attempt_id"]
    _answer(student_client, attempt_id, bank["questions"][0].id, _correct(db, bank["questions"][0].id))
    for payload in (start.text, student_client.get(f"/api/mock-attempts/{attempt_id}").text):
        assert "is_correct" not in payload and "correct_option" not in payload
        assert "explanation" not in payload and "Secret explanation" not in payload


# ------------------------------------------------------------------ IT_10 refresh does not reset the timer
def test_it10_start_again_resumes_the_same_attempt_with_less_time(student_client, bank):
    first = _start(student_client, bank["full"]).json()
    with _jump(20 * 60):
        again = _start(student_client, bank["full"])
    body = again.json()
    assert again.status_code == 200 and body["resumed"] is True
    assert body["attempt_id"] == first["attempt_id"]
    assert body["ends_at"] == first["ends_at"]
    assert body["remaining_seconds"] == 10 * 60  # 30 min - 20 min, not a fresh 30


def test_it10_get_attempt_reports_remaining_time_from_the_server_clock(student_client, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    with _jump(5 * 60 + 30):
        response = student_client.get(f"/api/mock-attempts/{attempt_id}")
    assert response.json()["remaining_seconds"] == 24 * 60 + 30
    assert response.headers["cache-control"] == "no-store"  # the countdown must never come from a cache


def test_list_marks_the_open_attempt_so_the_student_can_resume(student_client, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    items = {i["id"]: i for i in student_client.get("/api/mock-tests").json()["items"]}
    assert items[bank["full"].id]["open_attempt_id"] == attempt_id and items[bank["quick"].id]["open_attempt_id"] is None


def test_starting_after_the_old_attempt_expired_closes_it_and_starts_fresh(student_client, db, bank):
    old = _start(student_client, bank["quick"]).json()
    with _jump(90):
        fresh = _start(student_client, bank["quick"])
    assert fresh.status_code == 201 and fresh.json()["attempt_id"] != old["attempt_id"]
    assert fresh.json()["remaining_seconds"] == 60
    assert db.get(MockAttempt, old["attempt_id"]).status == AttemptStatus.AUTO_SUBMITTED


# ------------------------------------------------------------------ saving answers
def test_answers_can_be_saved_changed_and_cleared(student_client, db, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    q = bank["questions"][0]
    assert _answer(student_client, attempt_id, q.id, _wrong(db, q.id)).status_code == 200
    assert _answer(student_client, attempt_id, q.id, _correct(db, q.id)).status_code == 200  # changed mind
    state = student_client.get(f"/api/mock-attempts/{attempt_id}").json()
    assert state["answers"] == {str(q.id): _correct(db, q.id)}
    assert db.scalar(select(func.count(MockAttemptAnswer.id))) == 1  # updated, not duplicated
    assert _answer(student_client, attempt_id, q.id, None).status_code == 200  # cleared
    assert student_client.get(f"/api/mock-attempts/{attempt_id}").json()["answers"] == {}


def test_saved_answers_survive_a_refresh(student_client, db, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    q = bank["questions"][2]
    _answer(student_client, attempt_id, q.id, _correct(db, q.id))
    resumed = _start(student_client, bank["full"]).json()
    assert resumed["answers"] == {str(q.id): _correct(db, q.id)}


def test_invalid_choices_are_rejected(student_client, db, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    q0, q1 = bank["questions"][0], bank["questions"][1]
    assert _answer(student_client, attempt_id, q0.id, _correct(db, q1.id)).status_code == 422  # option of another question
    assert _answer(student_client, attempt_id, 99999, 1).status_code == 404  # not in this attempt
    assert student_client.put(f"/api/mock-attempts/{attempt_id}/answers", json={"question_id": q0.id, "selected_option_id": 1, "x": 1}).status_code == 422


def test_sec13_saving_after_the_time_limit_is_refused_and_the_attempt_is_closed(student_client, db, bank):
    attempt_id = _start(student_client, bank["quick"]).json()["attempt_id"]
    q = bank["questions"][0]
    with _jump(61):
        response = _answer(student_client, attempt_id, q.id, _correct(db, q.id))
    assert response.status_code == 409 and response.json()["code"] == "time_expired"
    assert db.get(MockAttempt, attempt_id).status == AttemptStatus.AUTO_SUBMITTED
    assert db.scalar(select(func.count(MockAttemptAnswer.id))) == 0


def test_sec13_reading_an_expired_attempt_closes_it(student_client, bank):
    attempt_id = _start(student_client, bank["quick"]).json()["attempt_id"]
    with _jump(61):
        body = student_client.get(f"/api/mock-attempts/{attempt_id}").json()
    assert body["status"] == "auto_submitted" and body["remaining_seconds"] == 0 and body["questions"] == []


# ------------------------------------------------------------------ UT_13 manual submit
def test_ut13_manual_submit_before_the_limit_scores_the_attempt(student_client, db, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    qs = bank["questions"]
    _answer(student_client, attempt_id, qs[0].id, _correct(db, qs[0].id))
    _answer(student_client, attempt_id, qs[1].id, _correct(db, qs[1].id))
    _answer(student_client, attempt_id, qs[2].id, _wrong(db, qs[2].id))
    response = student_client.post(f"/api/mock-attempts/{attempt_id}/submit")
    assert response.status_code == 200
    assert response.json()["status"] == "submitted" and response.json()["auto_submitted"] is False
    attempt = db.get(MockAttempt, attempt_id)
    assert (attempt.answered_count, attempt.correct_count, attempt.score_percent) == (3, 2, 40.0)  # 2 of 5


def test_submit_with_final_answers_keeps_them(student_client, db, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    q = bank["questions"][0]
    body = {"answers": [{"question_id": q.id, "selected_option_id": _correct(db, q.id)}]}
    assert student_client.post(f"/api/mock-attempts/{attempt_id}/submit", json=body).status_code == 200
    assert db.get(MockAttempt, attempt_id).correct_count == 1


def test_submit_with_a_bad_answer_changes_nothing(student_client, db, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    q = bank["questions"][0]
    body = {"answers": [{"question_id": q.id, "selected_option_id": 999999}]}
    assert student_client.post(f"/api/mock-attempts/{attempt_id}/submit", json=body).status_code == 422
    assert db.get(MockAttempt, attempt_id).status == AttemptStatus.IN_PROGRESS


def test_submit_at_the_buzzer_inside_the_grace_window_keeps_late_answers_but_counts_as_auto(student_client, db, bank):
    attempt_id = _start(student_client, bank["quick"]).json()["attempt_id"]
    q = bank["questions"][0]
    body = {"answers": [{"question_id": q.id, "selected_option_id": _correct(db, q.id)}]}
    with _jump(62):  # 2 s after the limit, inside the 5 s grace
        response = student_client.post(f"/api/mock-attempts/{attempt_id}/submit", json=body)
    assert response.json()["status"] == "auto_submitted" and db.get(MockAttempt, attempt_id).correct_count == 1


def test_submit_long_after_the_limit_ignores_the_late_answers(student_client, db, bank):
    attempt_id = _start(student_client, bank["quick"]).json()["attempt_id"]
    q = bank["questions"][0]
    body = {"answers": [{"question_id": q.id, "selected_option_id": _correct(db, q.id)}]}
    with _jump(120):
        response = student_client.post(f"/api/mock-attempts/{attempt_id}/submit", json=body)
    assert response.json()["status"] == "auto_submitted"
    assert db.get(MockAttempt, attempt_id).answered_count == 0  # SEC-13: nothing counts after the limit


def test_sec14_submitting_twice_is_harmless_and_input_is_locked_afterwards(student_client, db, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    q = bank["questions"][0]
    first = student_client.post(f"/api/mock-attempts/{attempt_id}/submit").json()
    second = student_client.post(f"/api/mock-attempts/{attempt_id}/submit").json()
    assert first == second and first["status"] == "submitted"
    late = _answer(student_client, attempt_id, q.id, _correct(db, q.id))
    assert late.status_code == 409 and late.json()["code"] == "already_submitted"


# ------------------------------------------------------------------ ST_08 back-to-back tests stay separate
def test_st08_two_tests_back_to_back_are_recorded_separately(student_client, db, bank):
    qs = bank["questions"]
    a = _start(student_client, bank["full"]).json()["attempt_id"]
    _answer(student_client, a, qs[0].id, _correct(db, qs[0].id))
    student_client.post(f"/api/mock-attempts/{a}/submit")
    b = _start(student_client, bank["quick"]).json()["attempt_id"]
    _answer(student_client, b, qs[0].id, _wrong(db, qs[0].id))
    student_client.post(f"/api/mock-attempts/{b}/submit")
    first, second = db.get(MockAttempt, a), db.get(MockAttempt, b)
    assert a != b and (first.correct_count, first.total_questions) == (1, 5) and (second.correct_count, second.total_questions) == (0, 3)


def test_the_same_test_can_be_retaken_after_submitting(student_client, bank):
    a = _start(student_client, bank["quick"]).json()["attempt_id"]
    student_client.post(f"/api/mock-attempts/{a}/submit")
    again = _start(student_client, bank["quick"])
    assert again.status_code == 201 and again.json()["attempt_id"] != a


# ------------------------------------------------------------------ access control
def test_sec01_guests_get_401_on_every_route(client, bank):
    assert client.get("/api/mock-tests").status_code == 401
    assert client.post(f"/api/mock-tests/{bank['full'].id}/attempts").status_code == 401
    assert client.get("/api/mock-attempts/1").status_code == 401
    assert client.put("/api/mock-attempts/1/answers", json={"question_id": 1}).status_code == 401
    assert client.post("/api/mock-attempts/1/submit").status_code == 401


def test_admins_cannot_take_tests(admin_client, bank):
    assert admin_client.get("/api/mock-tests").status_code == 403
    assert admin_client.post(f"/api/mock-tests/{bank['full'].id}/attempts").status_code == 403


def test_sec06_another_students_attempt_is_invisible_in_every_route(client_factory, make_user, login, student_client, db, bank):
    attempt_id = _start(student_client, bank["full"]).json()["attempt_id"]
    q = bank["questions"][0]
    make_user("intruder@test.com")
    intruder = client_factory()
    assert login(intruder, "intruder@test.com").status_code == 200
    assert intruder.get(f"/api/mock-attempts/{attempt_id}").status_code == 404
    assert _answer(intruder, attempt_id, q.id, _correct(db, q.id)).status_code == 404
    assert intruder.post(f"/api/mock-attempts/{attempt_id}/submit").status_code == 404
    assert db.get(MockAttempt, attempt_id).status == AttemptStatus.IN_PROGRESS


def test_unknown_or_inactive_test_is_404(student_client, db, bank):
    bank["quick"].is_active = False
    db.commit()
    assert student_client.post("/api/mock-tests/99999/attempts").status_code == 404
    assert student_client.post(f"/api/mock-tests/{bank['quick'].id}/attempts").status_code == 404
