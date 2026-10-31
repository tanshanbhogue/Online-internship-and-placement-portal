from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.modules.analytics.insights import IMPROVE_DELTA, STRONG, WEAK, classify, focus_areas
from app.modules.analytics.trends import moving_average, trend_direction
from app.modules.auth.models import User
from app.modules.mock_test.models import AttemptStatus, MockAttempt, MockTest
from app.modules.practice.models import PracticeSession, SessionStatus
from app.modules.question_bank.models import Category

BASE = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


# ------------------------------------------------------------------ pure functions
def test_it12_moving_average_matches_hand_calculation():
    assert moving_average([60, 75, 90], 3) == [60.0, 67.5, 75.0]
    assert moving_average([60, 75, 90, 30], 2) == [60.0, 67.5, 82.5, 60.0]
    assert moving_average([], 3) == []
    assert moving_average([50], 5) == [50.0]


@pytest.mark.parametrize(
    "scores, expected",
    [
        ([50, 60], "not_enough_data"),
        ([40, 55, 70], "improving"),
        ([90, 75, 60], "declining"),
        ([60, 61, 59, 60], "steady"),
        ([60, 62, 64], "steady"),  # +4 over the window is below the 5-point bar
        ([20] * 12 + [90, 90, 90], "improving"),  # only the last 10 count
    ],
)
def test_trend_direction(scores, expected):
    assert trend_direction(scores) == expected


@pytest.mark.parametrize(
    "scores, status",
    [
        ([80], "not_enough_data"),
        ([80, 90], "strong"),
        ([40, 45], "weak"),
        ([60, 65, 70], "average"),
        ([STRONG, STRONG], "strong"),  # boundary: exactly 75 is strong
        ([WEAK, WEAK], "average"),  # boundary: exactly 50 is not weak
        ([30, 35, 30, 90, 90, 90], "improved"),  # ST_11: weak earlier, good lately
        ([40, 45, 40, 52, 52, 52], "average"),  # better (+10), but not by 15 points
        ([30, 30, 30, 60, 60, 60], "improved"),  # exactly +30
        ([80, 80, 80, 40, 40, 40], "weak"),  # got worse
        ([70, 70, 70, 90, 90, 90], "strong"),  # earlier was never weak, so not "improved"
    ],
)
def test_classify(scores, status):
    assert classify("Cat", scores).status == status


def test_classify_numbers():
    insight = classify("Coding", [30, 35, 30, 90, 90, 90])
    assert (insight.attempts, insight.average, insight.recent_average, insight.earlier_average) == (6, 60.83, 90.0, 31.67)
    assert IMPROVE_DELTA == 15.0


def test_focus_areas_put_the_weakest_first_and_respect_the_limit():
    items = [classify("A", [90, 90]), classify("B", [40, 40]), classify("C", [20, 20]), classify("D", [60, 60]), classify("E", [30])]
    areas = focus_areas(items, limit=3)
    assert [(a.priority, a.category) for a in areas] == [(1, "C"), (2, "B"), (3, "D")]
    assert "20.0%" in areas[0].message
    assert [a.category for a in focus_areas(items, limit=10)] == ["C", "B", "D", "E"]  # strong categories are never listed


# ------------------------------------------------------------------ HTTP helpers
@pytest.fixture()
def cats(db):
    rows = {n: Category(name=n, slug=n.lower().replace(" ", "-")) for n in ("Aptitude", "Technical MCQ", "Coding")}
    db.add_all(rows.values())
    db.commit()
    return rows


@pytest.fixture()
def me(db, student_client):
    return db.scalar(select(User).where(User.email == "student@test.com"))


def add_practice(db, student, category, score, step):
    at = BASE + timedelta(hours=step)
    db.add(PracticeSession(student_id=student.id, category_id=category.id, status=SessionStatus.COMPLETED, total_questions=10,
                           started_at=at - timedelta(minutes=5), completed_at=at, score_percent=score))
    db.commit()


def trends(client, **params):
    return client.get("/api/analytics/trends", params=params)


def insights_of(client, **params):
    return client.get("/api/analytics/strengths-weaknesses", params=params)


# ------------------------------------------------------------------ ST_09 empty state
def test_st09_new_student_gets_empty_valid_answers(student_client):
    assert trends(student_client).json() == {"has_data": False, "window": 3, "direction": "not_enough_data", "points": []}
    assert insights_of(student_client).json() == {"has_data": False, "categories": [], "strengths": [], "weaknesses": [], "focus_areas": []}


# ------------------------------------------------------------------ UT_16 / IT_12 trend
def test_it12_trend_points_and_moving_average(student_client, db, me, cats):
    for step, score in enumerate([60, 75, 90]):
        add_practice(db, me, cats["Aptitude"], score, step)
    body = trends(student_client).json()
    assert body["has_data"] is True and body["direction"] == "improving" and body["window"] == 3
    assert [(p["index"], p["score"], p["moving_average"]) for p in body["points"]] == [(1, 60.0, 60.0), (2, 75.0, 67.5), (3, 90.0, 75.0)]
    assert body["points"][0]["kind"] == "practice" and body["points"][0]["category"] == "Aptitude"
    assert trends(student_client, window=2).json()["points"][2]["moving_average"] == 82.5
    assert trends(student_client, window=1).status_code == 422
    assert trends(student_client).headers["cache-control"] == "no-store"


def test_trend_mixes_practice_and_mock_in_time_order(student_client, db, me, cats):
    test = MockTest(title="Full Aptitude Mock", category_id=cats["Aptitude"].id, duration_minutes=30)
    db.add(test)
    db.commit()
    add_practice(db, me, cats["Aptitude"], 50, 0)
    at = BASE + timedelta(hours=1)
    db.add(MockAttempt(student_id=me.id, test_id=test.id, status=AttemptStatus.SUBMITTED, started_at=at - timedelta(minutes=20),
                       ends_at=at + timedelta(minutes=10), submitted_at=at, total_questions=10, score_percent=80))
    db.commit()
    add_practice(db, me, cats["Aptitude"], 65, 2)
    assert [(p["kind"], p["score"]) for p in trends(student_client).json()["points"]] == [("practice", 50.0), ("mock", 80.0), ("practice", 65.0)]
    assert [p["kind"] for p in trends(student_client, source="mock").json()["points"]] == ["mock"]


# ------------------------------------------------------------------ UT_17 strengths and weaknesses per category
def test_ut17_categories_are_classified_and_listed(student_client, db, me, cats):
    for step, score in enumerate([85, 90]):
        add_practice(db, me, cats["Aptitude"], score, step)
    for step, score in enumerate([30, 40]):
        add_practice(db, me, cats["Coding"], score, 10 + step)
    add_practice(db, me, cats["Technical MCQ"], 60, 20)
    body = insights_of(student_client).json()
    status = {c["category"]: c["status"] for c in body["categories"]}
    assert status == {"Aptitude": "strong", "Coding": "weak", "Technical MCQ": "not_enough_data"}
    assert body["strengths"] == ["Aptitude"] and body["weaknesses"] == ["Coding"]
    assert [f["category"] for f in body["focus_areas"]] == ["Coding", "Technical MCQ"]
    assert "Coding" in body["focus_areas"][0]["message"]


# ------------------------------------------------------------------ ST_11 weak category improves
def test_st11_a_weak_category_becomes_improved_after_good_attempts(student_client, db, me, cats):
    for step, score in enumerate([30, 35, 30]):
        add_practice(db, me, cats["Coding"], score, step)
    before = insights_of(student_client).json()
    assert before["categories"][0]["status"] == "weak" and before["weaknesses"] == ["Coding"]
    for step, score in enumerate([90, 92, 95]):
        add_practice(db, me, cats["Coding"], score, 10 + step)
    after = insights_of(student_client).json()  # IT_11: the very next call already reflects the new attempts
    assert after["categories"][0]["status"] == "improved"
    assert after["weaknesses"] == [] and after["strengths"] == ["Coding"] and after["focus_areas"] == []


# ------------------------------------------------------------------ ST_10 combined history, UT_18 isolation, filters
def test_st10_combined_history_feeds_both_endpoints(student_client, db, me, cats):
    add_practice(db, me, cats["Aptitude"], 70, 0)
    add_practice(db, me, cats["Aptitude"], 80, 1)
    add_practice(db, me, cats["Technical MCQ"], 40, 2)
    assert len(trends(student_client).json()["points"]) == 3
    assert {c["category"] for c in insights_of(student_client).json()["categories"]} == {"Aptitude", "Technical MCQ"}


def test_ut18_other_students_attempts_never_appear(student_client, db, me, cats, make_user):
    other = make_user("other@test.com")
    add_practice(db, me, cats["Aptitude"], 70, 0)
    for step in range(4):
        add_practice(db, other, cats["Coding"], 10, step)
    assert len(trends(student_client).json()["points"]) == 1
    assert [c["category"] for c in insights_of(student_client).json()["categories"]] == ["Aptitude"]


def test_filters_apply_to_both_endpoints(student_client, db, me, cats):
    for step, score in enumerate([20, 30, 90]):
        add_practice(db, me, cats["Coding"], score, step * 24)
    day = (BASE + timedelta(days=2)).date().isoformat()
    only_last = insights_of(student_client, date_from=day).json()
    assert only_last["categories"][0]["attempts"] == 1 and only_last["categories"][0]["status"] == "not_enough_data"
    assert len(trends(student_client, date_from=day).json()["points"]) == 1
    assert insights_of(student_client, source="bogus").status_code == 422
    assert trends(student_client, date_from="2026-12-01", date_to="2026-01-01").status_code == 422


def test_guests_and_admins_are_refused(client, admin_client):
    for path in ("/api/analytics/trends", "/api/analytics/strengths-weaknesses"):
        assert client.get(path).status_code == 401
        assert admin_client.get(path).status_code == 403
