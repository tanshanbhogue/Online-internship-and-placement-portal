# ==============================================================================
# FILE   : backend/tests/test_auth_login.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Tests for login, logout, session validation, throttling and the registration-then-login journeys.
#
# TEST CASES
#   - UT_01 valid credentials -> 200, cookie set with HttpOnly (and SameSite) flags, body.user has no password data
#   - UT_02 wrong password -> 401 "Invalid username or password"; UT_03 unknown email -> identical 401 body (SEC-04)
#   - IT_01 register (#14 endpoint) then log in with the same credentials -> success
#   - IT_03 after login, GET /api/auth/me and other protected endpoints keep working across several requests
#   - ST_01 register -> login -> /me returns the profile
#   - ST_02 logout then reuse the old cookie -> 401; hitting a protected URL while logged out -> 401 (SEC-01, SEC-05)
#   - SEC-03 five wrong passwords within 15 min -> 6th attempt 429 even with the correct password; after freezegun moves 16 min it succeeds
#   - SEC-05 token expires after 30 min of inactivity (freezegun) and the cookie is re-issued on activity
#   - SEC-07 dependency checks: student calling an admin-only dependency gets 403, guest gets 401 (use a tiny test-only route)
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from datetime import timedelta

import pytest
from fastapi import Depends
from freezegun import freeze_time

from app.core.dependencies import get_current_admin, get_current_student

PASSWORD = "Pass@123"


def _register(client, email="stu@test.com", password=PASSWORD):
    return client.post("/api/auth/register", json={"name": "Stu Dent", "email": email, "password": password})


def test_ut01_valid_login_sets_secure_cookie_and_no_password_data(client, make_user, login):
    make_user("a@test.com")
    response = login(client, "a@test.com")
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "a@test.com"
    assert set(response.json()["user"]) == {"id", "name", "email", "role"}
    assert "token" not in response.text.lower()
    cookie = response.headers["set-cookie"].lower()
    assert "access_token=" in cookie and "httponly" in cookie and "samesite=lax" in cookie


def test_ut02_ut03_wrong_password_and_unknown_email_are_identical(client, make_user, login):
    make_user("a@test.com")
    wrong = login(client, "a@test.com", "Wrong@123")
    unknown = login(client, "nobody@test.com", "Wrong@123")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert wrong.json()["detail"] == "Invalid username or password"
    assert wrong.json()["code"] == "invalid_credentials"


def test_it01_register_then_login(client, login):
    assert _register(client).status_code == 201
    assert login(client, "stu@test.com").status_code == 200


def test_it03_session_persists_across_requests(student_client):
    for _ in range(3):
        assert student_client.get("/api/auth/me").status_code == 200
    assert student_client.get("/api/internships").status_code == 200


def test_st01_register_login_me(client, login):
    _register(client, "Journey@Test.com")
    login(client, "journey@test.com")
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "journey@test.com" and me.json()["role"] == "student"


def test_st02_logout_invalidates_old_cookie_and_guests_get_401(client_factory, make_user, login):
    make_user("a@test.com")
    client = client_factory()
    login(client, "a@test.com")
    stolen = client.cookies.get("access_token")
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401

    replay = client_factory()
    replay.cookies.set("access_token", stolen)
    assert replay.get("/api/auth/me").status_code == 401

    guest = client_factory()
    response = guest.get("/api/internships")
    assert response.status_code == 401 and response.json()["code"] == "not_authenticated"


def test_logout_without_a_session_is_still_204(client):
    assert client.post("/api/auth/logout").status_code == 204


def test_sec03_throttle_after_five_failures_then_recovers(client, make_user, login):
    make_user("a@test.com")
    with freeze_time("2026-01-01 10:00:00") as clock:
        for _ in range(5):
            assert login(client, "a@test.com", "Wrong@123").status_code == 401
        blocked = login(client, "a@test.com", PASSWORD)  # correct password is refused while throttled
        assert blocked.status_code == 429 and blocked.json()["code"] == "too_many_attempts"
        clock.tick(timedelta(minutes=16))
        assert login(client, "a@test.com", PASSWORD).status_code == 200


def test_sec03_throttle_also_applies_to_unknown_emails(client, login):
    for _ in range(5):
        assert login(client, "ghost@test.com", "Wrong@123").status_code == 401
    assert login(client, "ghost@test.com", "Wrong@123").status_code == 429


def test_sec05_token_expires_after_30_idle_minutes_and_slides_on_activity(client, make_user, login):
    make_user("a@test.com")
    with freeze_time("2026-01-01 10:00:00") as clock:
        login(client, "a@test.com")
        clock.tick(timedelta(minutes=20))
        active = client.get("/api/auth/me")
        assert active.status_code == 200
        assert "access_token=" in active.headers["set-cookie"]  # cookie re-issued on activity
        clock.tick(timedelta(minutes=20))  # 40 min after login but only 20 since last activity
        assert client.get("/api/auth/me").status_code == 200
        clock.tick(timedelta(minutes=31))
        assert client.get("/api/auth/me").status_code == 401


def test_sec07_role_dependencies(client_factory, make_user, login):
    from app.main import app

    @app.get("/api/_test/admin-only")
    def admin_only(_user=Depends(get_current_admin)):
        return {"ok": True}

    @app.get("/api/_test/student-only")
    def student_only(_user=Depends(get_current_student)):
        return {"ok": True}

    try:
        make_user("s@test.com")
        make_user("adm@test.com", role="admin")
        guest, student, admin = client_factory(), client_factory(), client_factory()
        login(student, "s@test.com")
        login(admin, "adm@test.com")

        assert guest.get("/api/_test/admin-only").status_code == 401
        assert student.get("/api/_test/admin-only").status_code == 403
        assert student.get("/api/_test/admin-only").json()["code"] == "forbidden"
        assert admin.get("/api/_test/admin-only").status_code == 200
        assert admin.get("/api/_test/student-only").status_code == 403
        assert student.get("/api/_test/student-only").status_code == 200
    finally:
        app.router.routes[:] = [r for r in app.router.routes if not getattr(r, "path", "").startswith("/api/_test/")]


def test_tampered_token_is_rejected(client_factory):
    c = client_factory()
    c.cookies.set("access_token", "not.a.jwt")
    assert c.get("/api/auth/me").status_code == 401
