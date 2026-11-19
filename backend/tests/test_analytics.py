# Covers Test Plan(data behind the dashboard).
# Practice sessions and mock attempts are inserted directly, so this file needs only the models of #22 and #24.
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.modules.auth.models import User
from app.modules.mock_test.models import AttemptStatus, MockAttempt, MockTest
from app.modules.practice.models import PracticeSession, SessionStatus
from app.modules.question_bank.models import Category

NOW = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)


@pytest.fixture()
def cats(db):
    rows = {name: Category(name=name, slug=name.lower()) for name in ("Aptitude", "Coding")}
    db.add_all(rows.values())
    db.commit()
    return rows


@pytest.fixture()
def test_apt(db, cats):
    test = MockTest(title="Full Aptitude Mock", category_id=cats["Aptitude"].id, duration_minutes=30)
    db.add(test)
    db.commit()
    return test


@pytest.fixture()
def me(db, student_client):
    return db.scalar(select(User).where(User.email == "student@test.com"))


def practice(db, student, category, score, days_ago=0, status=SessionStatus.COMPLETED):
    at = NOW - timedelta(days=days_ago)
    row = PracticeSession(
        student_id=student.id, category_id=category.id, status=status, total_questions=10,
        correct_count=0, answered_count=0, score_percent=score, started_at=at - timedelta(minutes=5),
        completed_at=at if status == SessionStatus.COMPLETED else None,
    )
    db.add(row)
    db.commit()
    return row


def mock(db, student, test, score, days_ago=0, status=AttemptStatus.SUBMITTED):
    at = NOW - timedelta(days=days_ago)
    row = MockAttempt(
        student_id=student.id, test_id=test.id, status=status, started_at=at - timedelta(minutes=20),
        ends_at=at + timedelta(minutes=10), submitted_at=None if status == AttemptStatus.IN_PROGRESS else at,
        total_questions=10, score_percent=None if status == AttemptStatus.IN_PROGRESS else score,
    )
    db.add(row)
    db.commit()
    return row


def get(client, path="/api/analytics/summary", **params):
    return client.get(path, params=params)


# ------------------------------------------------------------------ ST_09 empty state
def test_st09_new_student_gets_an_empty_but_valid_summary(student_client):
    body = get(student_client).json()
    assert body == {
        "has_data": False, "total_attempts": 0, "practice_attempts": 0, "mock_attempts": 0,
        "average_score": None, "best_score": None, "latest_score": None, "last_attempt_at": None,
    }
    assert get(student_client, "/api/analytics/attempts").json() == {"items": [], "total": 0}


# ------------------------------------------------------------------ IT_12 / UT_16 numbers
def test_it12_average_of_60_75_90_is_75_and_other_totals_match(student_client, db, me, cats, test_apt):
    practice(db, me, cats["Aptitude"], 60, days_ago=3)
    mock(db, me, test_apt, 75, days_ago=2)
    practice(db, me, cats["Coding"], 90, days_ago=1)
    body = get(student_client).json()
    assert body["has_data"] is True
    assert (body["total_attempts"], body["practice_attempts"], body["mock_attempts"]) == (3, 2, 1)
    assert (body["average_score"], body["best_score"], body["latest_score"]) == (75.0, 90.0, 90.0)
    assert body["last_attempt_at"].startswith("2026-10-19")


def test_average_is_rounded_to_two_decimals(student_client, db, me, cats):
    for score in (33.33, 33.33, 100):
        practice(db, me, cats["Aptitude"], score)
    assert get(student_client).json()["average_score"] == 55.55


def test_open_unscored_and_unfinished_attempts_are_not_counted(student_client, db, me, cats, test_apt):
    practice(db, me, cats["Aptitude"], 80)
    practice(db, me, cats["Aptitude"], None, status=SessionStatus.IN_PROGRESS)
    practice(db, me, cats["Aptitude"], None)  # completed but nothing scorable (all pending)
    mock(db, me, test_apt, None, status=AttemptStatus.IN_PROGRESS)
    assert get(student_client).json()["total_attempts"] == 1


# ------------------------------------------------------------------ IT_11 immediately up to date, never cached
def test_it11_a_new_attempt_changes_the_numbers_at_once_and_nothing_is_cached(student_client, db, me, cats):
    practice(db, me, cats["Aptitude"], 50, days_ago=1)
    first = get(student_client)
    assert first.json()["average_score"] == 50.0 and first.headers["cache-control"] == "no-store"
    practice(db, me, cats["Aptitude"], 100)
    second = get(student_client).json()
    assert (second["total_attempts"], second["average_score"], second["latest_score"]) == (2, 75.0, 100.0)
    assert get(student_client, "/api/analytics/attempts").headers["cache-control"] == "no-store"


# ------------------------------------------------------------------ UT_18 isolation (SEC-06)
def test_ut18_each_student_sees_only_their_own_data(client_factory, make_user, login, db, cats, test_apt, student_client, me):
    other = make_user("other@test.com")
    practice(db, me, cats["Aptitude"], 40)
    practice(db, other, cats["Aptitude"], 100)
    mock(db, other, test_apt, 100)
    mine = get(student_client).json()
    assert (mine["total_attempts"], mine["average_score"]) == (1, 40.0)
    theirs_client = client_factory()
    assert login(theirs_client, "other@test.com").status_code == 200
    theirs = get(theirs_client).json()
    assert (theirs["total_attempts"], theirs["average_score"]) == (2, 100.0)
    ids = {(r["kind"], r["id"]) for r in get(student_client, "/api/analytics/attempts").json()["items"]}
    assert len(ids) == 1


# ------------------------------------------------------------------ filters
def test_source_filter(student_client, db, me, cats, test_apt):
    practice(db, me, cats["Aptitude"], 20)
    mock(db, me, test_apt, 80)
    assert get(student_client, source="practice").json()["average_score"] == 20.0
    assert get(student_client, source="mock").json()["average_score"] == 80.0
    assert get(student_client, source="all").json()["total_attempts"] == 2
    assert get(student_client, source="bogus").status_code == 422


def test_date_range_filter_is_inclusive_of_both_days(student_client, db, me, cats):
    for days_ago, score in ((10, 10), (5, 50), (0, 90)):
        practice(db, me, cats["Aptitude"], score, days_ago=days_ago)
    day = lambda n: (NOW - timedelta(days=n)).date().isoformat()  # noqa: E731
    assert get(student_client, date_from=day(5), date_to=day(5)).json()["average_score"] == 50.0
    assert get(student_client, date_from=day(5)).json()["total_attempts"] == 2
    assert get(student_client, date_to=day(5)).json()["total_attempts"] == 2
    assert get(student_client, date_from=day(0), date_to=day(10)).status_code == 422
    assert get(student_client, date_from="not-a-date").status_code == 422


# ------------------------------------------------------------------ drill-down list
def test_attempts_list_is_newest_first_with_kind_and_id_for_drill_down(student_client, db, me, cats, test_apt):
    old = practice(db, me, cats["Aptitude"], 30, days_ago=5)
    new = mock(db, me, test_apt, 70, days_ago=1)
    body = get(student_client, "/api/analytics/attempts").json()
    assert body["total"] == 2
    assert [(r["kind"], r["id"], r["score_percent"]) for r in body["items"]] == [("mock", new.id, 70.0), ("practice", old.id, 30.0)]
    assert body["items"][0]["title"] == "Full Aptitude Mock" and body["items"][1]["title"] == "Aptitude practice"
    assert body["items"][0]["category"] == "Aptitude"


def test_attempts_limit(student_client, db, me, cats):
    for n in range(5):
        practice(db, me, cats["Aptitude"], 10 * n, days_ago=n)
    body = get(student_client, "/api/analytics/attempts", limit=2).json()
    assert len(body["items"]) == 2 and body["total"] == 5
    assert get(student_client, "/api/analytics/attempts", limit=0).status_code == 422


# ------------------------------------------------------------------ access
def test_guests_and_admins_are_refused(client, admin_client):
    assert client.get("/api/analytics/summary").status_code == 401
    assert client.get("/api/analytics/attempts").status_code == 401
    assert admin_client.get("/api/analytics/summary").status_code == 403
