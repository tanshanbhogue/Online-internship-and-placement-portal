
import pytest


def test_valid_login_sets_secure_session_cookie(client, make_user, login):
    make_user("student@test.com", role="student", name="Student One")

    response = login(client, "student@test.com")

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "student@test.com"

    user_data = response.json()["user"]
    assert "password" not in user_data
    assert "password_hash" not in user_data

    cookie_header = response.headers.get("set-cookie", "").lower()
    assert "access_token=" in cookie_header
    assert "httponly" in cookie_header
    assert "samesite" in cookie_header


def test_wrong_password_returns_401(client, make_user, login):
    make_user("student@test.com")

    response = login(client, "student@test.com", "WrongPassword123!")

    assert response.status_code == 401


def test_unknown_email_has_same_error_as_wrong_password(
    client_factory, make_user, login
):
    make_user("existing@test.com")

    wrong_password_client = client_factory()
    unknown_email_client = client_factory()

    wrong_password_response = login(
        wrong_password_client,
        "existing@test.com",
        "WrongPassword123!",
    )
    unknown_email_response = login(
        unknown_email_client,
        "unknown@test.com",
        "WrongPassword123!",
    )

    assert wrong_password_response.status_code == 401
    assert unknown_email_response.status_code == 401
    assert wrong_password_response.json() == unknown_email_response.json()


def test_login_then_me_returns_current_user(client, make_user, login):
    make_user("student@test.com", role="student", name="Student One")

    login_response = login(client, "student@test.com")
    assert login_response.status_code == 200

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "student@test.com"
    assert response.json()["name"] == "Student One"
    assert "password_hash" not in response.json()


def test_logged_out_user_cannot_access_me(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_logout_revokes_previous_session(
    client, make_user, login
):
    make_user("student@test.com")

    login_response = login(client, "student@test.com")
    assert login_response.status_code == 200

    old_token = client.cookies.get("access_token")
    assert old_token

    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 204

    # Reuse the original token to verify server-side revocation.
    client.cookies.set("access_token", old_token)
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_sixth_failed_login_is_throttled(
    client, make_user, login
):
    make_user("student@test.com")

    for attempt in range(5):
        response = login(
            client,
            "student@test.com",
            "WrongPassword123!",
        )
        assert response.status_code == 401, (
            f"Attempt {attempt + 1} returned {response.status_code}"
        )

    response = login(client, "student@test.com")

    assert response.status_code == 429
