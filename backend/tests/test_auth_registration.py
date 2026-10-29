

from sqlalchemy import func, inspect, select

from app.modules.auth.models import Role, User

VALID = {"name": "Asha Rao", "email": "asha@test.com", "password": "Pass@123", "college": "RVCE", "batch": "2026"}


def _count_users(db) -> int:
    return db.scalar(select(func.count(User.id)))


def test_ut04_blank_fields_rejected_with_field_errors(client, db):
    response = client.post("/api/auth/register", json={"name": "", "email": "", "password": ""})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "validation_error"
    assert {"name", "email", "password"} <= set(body["fields"])
    assert _count_users(db) == 0


def test_valid_registration_returns_profile_without_secrets_and_stores_argon2(client, db):
    response = client.post("/api/auth/register", json=VALID)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "asha@test.com" and body["role"] == "student"
    assert "password" not in body and "password_hash" not in body
    assert "Pass@123" not in response.text
    user = db.scalar(select(User).where(User.email == "asha@test.com"))
    assert user.password_hash.startswith("$argon2id$") and user.password_hash != "Pass@123"
    assert user.role == Role.STUDENT


def test_it02_duplicate_email_rejected_including_other_case(client, db):
    assert client.post("/api/auth/register", json=VALID).status_code == 201
    second = client.post("/api/auth/register", json=VALID)
    assert second.status_code == 409
    assert second.json()["detail"] == "Email already exists"
    assert second.json()["code"] == "duplicate_email"
    shouty = client.post("/api/auth/register", json={**VALID, "email": "Asha@Test.com"})
    assert shouty.status_code == 409
    assert _count_users(db) == 1


def test_weak_password_gives_message_under_fields_password(client, db):
    response = client.post("/api/auth/register", json={**VALID, "password": "abc"})
    assert response.status_code == 422
    assert response.json()["fields"]["password"]
    # Long enough to pass the schema but failing strength rules reaches the service check.
    response = client.post("/api/auth/register", json={**VALID, "password": "abcdefghij"})
    assert response.status_code == 422
    assert any("digit" in m for m in response.json()["fields"]["password"])
    assert _count_users(db) == 0


def test_role_admin_in_body_never_creates_an_admin(client, db):
    response = client.post("/api/auth/register", json={**VALID, "role": "admin"})
    assert response.status_code in (201, 422)
    assert db.scalar(select(func.count(User.id)).where(User.role == Role.ADMIN)) == 0


def test_sql_injection_strings_are_inert(client, db):
    attack_name = "Robert'); DROP TABLE users;--"
    response = client.post("/api/auth/register", json={**VALID, "name": attack_name, "email": "x@test.com"})
    assert response.status_code == 201
    bad_email = client.post("/api/auth/register", json={**VALID, "email": "a' OR '1'='1@x"})
    assert bad_email.status_code == 422
    assert "users" in inspect(db.get_bind()).get_table_names()
    assert db.scalar(select(User.name).where(User.email == "x@test.com")) == attack_name


def test_validation_errors_never_echo_the_submitted_password(client):
    response = client.post("/api/auth/register", json={**VALID, "password": "short", "email": "nope"})
    assert response.status_code == 422
    assert "short" not in response.text
