# Story #30 End-to-End Integration Testing - owner: Tanmayi (tanshanbhogue)
# File: backend/tests/test_e2e_security_sweep.py
#
# One sweep over EVERY Sprint 2 endpoint: guests get 401, admins get 403 on student endpoints, a student never sees
# another student's data (404), and no endpoint leaks answer keys before submission. Security Requirements SEC-06/07/12/13/14.
import re
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.main import app
from app.modules.auth.models import User
from app.modules.mock_test.models import MockAttempt, MockTest, MockTestQuestion
from app.modules.question_bank.models import Category, Difficulty, Question, QuestionOption, QuestionType

STUDENT_GETS = ["/api/mock-tests", "/api/mock-results", "/api/analytics/summary", "/api/analytics/attempts", "/api/analytics/trends", "/api/analytics/strengths-weaknesses"]
STUDENT_ATTEMPT_PATHS = [("GET", "/api/mock-attempts/{id}"), ("PUT", "/api/mock-attempts/{id}/answers"), ("POST", "/api/mock-attempts/{id}/submit"),
                         ("POST", "/api/mock-attempts/{id}/auto-submit"), ("GET", "/api/mock-results/{id}")]
ADMIN_ONLY = [("POST", "/api/admin/mock-attempts/sweep"), ("GET", "/api/admin/performance")]


@pytest.fixture()
def attempt_of_other_student(db, make_user):
    category = Category(name="Aptitude", slug="aptitude")
    db.add(category)
    db.commit()
    q = Question(category_id=category.id, type=QuestionType.MCQ, prompt="Q", difficulty=Difficulty.EASY, explanation="Secret why",
                 options=[QuestionOption(text=f"o{i}", is_correct=(i == 1), position=i) for i in range(3)])
    db.add(q)
    db.commit()
    test = MockTest(title="t", category_id=category.id, duration_minutes=30)
    test.test_questions = [MockTestQuestion(question_id=q.id, position=0)]
    db.add(test)
    db.commit()
    other = make_user("other@test.com")
    now = datetime.now(timezone.utc)
    attempt = MockAttempt(student_id=other.id, test_id=test.id, started_at=now, ends_at=now + timedelta(minutes=30), total_questions=1)
    db.add(attempt)
    db.commit()
    return attempt, test


def test_every_sprint2_route_is_covered_by_this_sweep():
    """Fails when a story adds a route that the sweep does not know, so nobody forgets to secure and test it."""
    known = {p for p in STUDENT_GETS} | {p for _, p in STUDENT_ATTEMPT_PATHS} | {p for _, p in ADMIN_ONLY}
    known |= {"/api/mock-tests/{test_id}/attempts"}
    sprint2 = [r.path for r in app.routes if getattr(r, "path", "").startswith(("/api/mock", "/api/analytics", "/api/admin/mock", "/api/admin/performance"))]
    normalise = lambda p: re.sub(r"\{[^}]+\}", "{id}", p)  # noqa: E731
    known_n = {normalise(p) for p in known}
    missing = sorted({normalise(p) for p in sprint2} - known_n)
    assert missing == [], f"routes not in the security sweep: {missing}"


def test_guests_get_401_everywhere(client, attempt_of_other_student):
    attempt, test = attempt_of_other_student
    for path in STUDENT_GETS:
        assert client.get(path).status_code == 401, path
    for method, path in STUDENT_ATTEMPT_PATHS + ADMIN_ONLY:
        response = client.request(method, path.replace("{id}", str(attempt.id)), json={"question_id": 1, "selected_option_id": 1} if method == "PUT" else None)
        assert response.status_code == 401, (method, path)
    assert client.post(f"/api/mock-tests/{test.id}/attempts").status_code == 401


def test_admins_cannot_use_student_endpoints_and_students_cannot_use_admin_ones(student_client, admin_client, attempt_of_other_student):
    attempt, test = attempt_of_other_student
    for path in STUDENT_GETS:
        assert admin_client.get(path).status_code == 403, path
    assert admin_client.post(f"/api/mock-tests/{test.id}/attempts").status_code == 403
    for method, path in ADMIN_ONLY:
        assert student_client.request(method, path).status_code == 403, (method, path)


def test_students_cannot_touch_someone_elses_attempt(student_client, attempt_of_other_student):  # SEC-06: 404, never 403, so ids are not confirmable
    attempt, _ = attempt_of_other_student
    for method, path in STUDENT_ATTEMPT_PATHS:
        response = student_client.request(method, path.replace("{id}", str(attempt.id)), json={"question_id": 1, "selected_option_id": 1} if method == "PUT" else None)
        assert response.status_code == 404, (method, path, response.status_code)
        assert "Secret why" not in response.text


def test_no_answer_keys_before_submission_anywhere(student_client, db, attempt_of_other_student):  # SEC-12
    _, test = attempt_of_other_student
    started = student_client.post(f"/api/mock-tests/{test.id}/attempts")
    attempt_id = started.json()["attempt_id"]
    for text in (started.text, student_client.get(f"/api/mock-attempts/{attempt_id}").text, student_client.get("/api/mock-tests").text):
        assert "is_correct" not in text and "Secret why" not in text and "correct_option" not in text
    assert student_client.get(f"/api/mock-results/{attempt_id}").status_code == 409  # no result while the attempt is open


def test_a_closed_attempt_cannot_be_submitted_twice_or_edited(student_client, db, attempt_of_other_student):  # SEC-13 / SEC-14
    _, test = attempt_of_other_student
    attempt_id = student_client.post(f"/api/mock-tests/{test.id}/attempts").json()["attempt_id"]
    assert student_client.post(f"/api/mock-attempts/{attempt_id}/submit").status_code == 200
    again = student_client.post(f"/api/mock-attempts/{attempt_id}/submit")  # harmless repeat: same result, no second scoring
    assert again.status_code == 200 and again.json()["status"] == "submitted"
    locked = student_client.put(f"/api/mock-attempts/{attempt_id}/answers", json={"question_id": 1, "selected_option_id": 1})
    assert locked.status_code == 409 and locked.json()["code"] == "already_submitted"
    assert student_client.post(f"/api/mock-attempts/{attempt_id}/auto-submit").status_code == 200  # idempotent: already final
    me = db.scalar(select(User).where(User.email == "student@test.com"))
    rows = db.scalars(select(MockAttempt).where(MockAttempt.student_id == me.id)).all()
    assert len(rows) == 1 and rows[0].status.value == "submitted"


def test_dashboard_and_attempt_data_is_never_cached(student_client, attempt_of_other_student):
    _, test = attempt_of_other_student
    attempt_id = student_client.post(f"/api/mock-tests/{test.id}/attempts").json()["attempt_id"]
    for path in ("/api/analytics/summary", "/api/analytics/trends", f"/api/mock-attempts/{attempt_id}"):
        assert student_client.get(path).headers["cache-control"] == "no-store", path
