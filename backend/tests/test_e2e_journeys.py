# Story #30 End-to-End Integration Testing - owner: Tanmayi (tanshanbhogue)
# File: backend/tests/test_e2e_journeys.py
#
# Whole-product journeys through the real HTTP API with the real services and a real database (no mocks of our own code).
# Needs every Sprint 2 story merged. Test Plan: ST_01..ST_11, IT_xx chains; see docs/e2e-traceability.md.
# Gap: Sprint 1 has no admin API to POST an internship, so listings are inserted into the database (as the seed script does).
import io
from datetime import date, datetime, timedelta, timezone

import pytest
from freezegun import freeze_time
from sqlalchemy import select

from app.core.config import settings
from app.modules.internship.models import Internship
from app.modules.mock_test.models import MockTest, MockTestQuestion
from app.modules.question_bank.models import Category, Difficulty, Question, QuestionOption, QuestionType

PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"


@pytest.fixture(autouse=True)
def storage_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "RESUME_STORAGE_DIR", str(tmp_path / "resumes"))


@pytest.fixture()
def world(db):
    """One category with 6 MCQs (practice + mock use them) and one internship, 2 mock tests."""
    category = Category(name="Aptitude", slug="aptitude")
    db.add(category)
    db.commit()
    questions = []
    for n in range(6):
        q = Question(category_id=category.id, type=QuestionType.MCQ, prompt=f"Q{n}", difficulty=Difficulty.EASY, explanation=f"Secret why {n}",
                     options=[QuestionOption(text=f"o{i}", is_correct=(i == 1), position=i) for i in range(3)])
        db.add(q)
        questions.append(q)
    internship = Internship(title="Backend Intern - Acme", company="Acme", description="d", deadline=date.today() + timedelta(days=30))
    db.add(internship)
    db.commit()
    tests = {}
    for key, minutes, qs in (("full", 30, questions), ("quick", 1, questions[:3])):
        test = MockTest(title=f"{key} test", category_id=category.id, duration_minutes=minutes)
        test.test_questions = [MockTestQuestion(question_id=q.id, position=i) for i, q in enumerate(qs)]
        db.add(test)
        tests[key] = test
    db.commit()
    return {"category": category, "questions": questions, "internship": internship, "tests": tests}


def option(db, question_id, correct):
    return db.scalar(select(QuestionOption.id).where(QuestionOption.question_id == question_id, QuestionOption.is_correct.is_(correct)))


def take_mock(client, db, test, right):
    """Start, answer `right` questions correctly (the rest wrongly) and submit. Returns the attempt id."""
    started = client.post(f"/api/mock-tests/{test.id}/attempts").json()
    for index, question in enumerate(started["questions"]):
        client.put(f"/api/mock-attempts/{started['attempt_id']}/answers", json={"question_id": question["id"], "selected_option_id": option(db, question["id"], index < right)})
    assert client.post(f"/api/mock-attempts/{started['attempt_id']}/submit").status_code == 200
    return started["attempt_id"]


def practise(client, db, category, right):
    started = client.post("/api/practice/sessions", json={"category_id": category.id, "count": 5}).json()
    for index, question in enumerate(started["questions"]):
        client.post(f"/api/practice/sessions/{started['session_id']}/answers", json={"question_id": question["id"], "selected_option_id": option(db, question["id"], index < right)})
    assert client.post(f"/api/practice/sessions/{started['session_id']}/finish").status_code == 200


# ------------------------------------------------------------------ the whole student journey (ST_01..ST_11 chained)
def test_register_login_browse_apply_practise_mock_and_see_analytics(client, login, db, world):
    # ST_01/ST_02 register then log in
    registered = client.post("/api/auth/register", json={"name": "Journey Student", "email": "journey@test.com", "password": "Journey@123"})
    assert registered.status_code in (200, 201), registered.text
    assert login(client, "journey@test.com", "Journey@123").status_code == 200
    # ST_03/ST_04 browse and apply
    listing = client.get("/api/internships").json()
    assert any(i["id"] == world["internship"].id for i in listing["items"])
    applied = client.post("/api/applications", data={"internship_id": str(world["internship"].id)}, files={"resume": ("cv.pdf", io.BytesIO(PDF), "application/pdf")})
    assert applied.status_code == 201
    assert [a["id"] for a in client.get("/api/applications/mine").json()["items"]] == [applied.json()["id"]]
    # a brand-new student: analytics are empty but valid (ST_09)
    assert client.get("/api/analytics/summary").json()["has_data"] is False
    # ST_05 practice, ST_07 mock test
    practise(client, db, world["category"], right=3)  # 60 %
    attempt_id = take_mock(client, db, world["tests"]["quick"], right=3)  # 100 %
    result = client.get(f"/api/mock-results/{attempt_id}").json()
    assert result["score_percent"] == 100.0 and len(result["breakdown"]) == 3
    # ST_10 / IT_11: the very next analytics call includes both attempts
    summary = client.get("/api/analytics/summary").json()
    assert (summary["total_attempts"], summary["practice_attempts"], summary["mock_attempts"]) == (2, 1, 1)
    assert summary["average_score"] == 80.0
    assert [p["kind"] for p in client.get("/api/analytics/trends").json()["points"]] == ["practice", "mock"]
    assert client.get("/api/mock-results").json()["items"][0]["attempt_id"] == attempt_id


def test_weak_category_improves_after_more_good_attempts(student_client, db, world):
    for right in (0, 1, 0):
        practise(student_client, db, world["category"], right)
    assert student_client.get("/api/analytics/strengths-weaknesses").json()["weaknesses"] == ["Aptitude"]
    for _ in range(3):
        take_mock(student_client, db, world["tests"]["quick"], right=3)
    body = student_client.get("/api/analytics/strengths-weaknesses").json()
    assert body["categories"][0]["status"] == "improved" and body["weaknesses"] == []  # ST_11


# ------------------------------------------------------------------ timed test: walk away, time runs out
def test_time_runs_out_while_the_student_is_away_and_everything_still_adds_up(student_client, db, world):
    with freeze_time(datetime.now(timezone.utc)) as clock:  # frozen "now", so the login cookie stays valid
        started = student_client.post(f"/api/mock-tests/{world['tests']['quick'].id}/attempts").json()
        first = started["questions"][0]
        student_client.put(f"/api/mock-attempts/{started['attempt_id']}/answers", json={"question_id": first["id"], "selected_option_id": option(db, first["id"], True)})
        clock.tick(timedelta(minutes=5))  # the 1-minute test is long over; nobody pressed anything
        result = student_client.get(f"/api/mock-results/{started['attempt_id']}")  # lazy auto-submit happens here
        assert result.status_code == 200
        body = result.json()
        assert body["status"] == "auto_submitted" and body["correct_count"] == 1 and body["score_percent"] == 33.33
        # late input is refused and the score never changes
        late = student_client.put(f"/api/mock-attempts/{started['attempt_id']}/answers", json={"question_id": first["id"], "selected_option_id": option(db, first["id"], False)})
        assert late.status_code == 409 and late.json()["code"] in ("already_submitted", "time_expired")
        again = student_client.post(f"/api/mock-attempts/{started['attempt_id']}/submit")  # idempotent: same final result
        assert again.status_code == 200 and again.json()["status"] == "auto_submitted"
        assert student_client.get(f"/api/mock-results/{started['attempt_id']}").json()["score_percent"] == 33.33
        summary = student_client.get("/api/analytics/summary").json()
    assert summary["mock_attempts"] == 1 and summary["latest_score"] == 33.33


def test_a_second_attempt_can_start_after_the_first_is_closed(student_client, db, world):
    first = take_mock(student_client, db, world["tests"]["quick"], right=1)
    second = student_client.post(f"/api/mock-tests/{world['tests']['quick'].id}/attempts")
    assert second.status_code == 201 and second.json()["attempt_id"] != first and second.json()["resumed"] is False
