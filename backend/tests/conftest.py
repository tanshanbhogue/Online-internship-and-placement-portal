"""Shared fixtures.

Settings in tests: `settings` (app.core.config) is a plain mutable object, so tests change values with
`monkeypatch.setattr(settings, "RESUME_STORAGE_DIR", str(tmp_path))`. Always read settings at call time in
application code (never copy a value into a module constant) so such overrides take effect.

Fixtures that need modules from later phases import them INSIDE the fixture and skip with a clear message if the
import fails, so this file works from Phase 0 onwards.
"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

TEST_PASSWORD = "Pass@123"


@pytest.fixture()
def engine():
    from app.db.base import Base
    from app.db.models_registry import load_all_models

    load_all_models()
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(eng, "connect")
    def _fk_on(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture()
def db(engine):
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client_factory(db, monkeypatch):
    """Returns a function creating independent TestClients (separate cookie jars) on the same test database."""
    from fastapi.testclient import TestClient

    from app.core.config import settings
    from app.core.database import get_db
    from app.main import app

    monkeypatch.setattr(settings, "COOKIE_SECURE", False)
    app.dependency_overrides[get_db] = lambda: db
    created: list[TestClient] = []

    def make() -> TestClient:
        c = TestClient(app)
        created.append(c)
        return c

    yield make
    for c in created:
        c.close()
    app.dependency_overrides.clear()


@pytest.fixture()
def client(client_factory):
    return client_factory()


@pytest.fixture()
def make_user(db):
    try:
        from app.core.security import hash_password
        from app.modules.auth.models import Role, User
    except ImportError as exc:  # pragma: no cover
        pytest.skip(f"User model / hashing not available yet: {exc}")

    def _make(email: str, password: str = TEST_PASSWORD, role: str = "student", name: str = "Test User"):
        user = User(
            name=name,
            email=email.strip().lower(),
            password_hash=hash_password(password),
            role=Role(role),
        )
        db.add(user)
        db.commit()
        return user

    return _make


@pytest.fixture()
def login():
    def _login(client, email: str, password: str = TEST_PASSWORD):
        return client.post("/api/auth/login", json={"email": email, "password": password})

    return _login


@pytest.fixture()
def student_client(client_factory, make_user, login):
    make_user("student@test.com", role="student", name="Student One")
    c = client_factory()
    response = login(c, "student@test.com")
    if response.status_code != 200:  # pragma: no cover
        pytest.skip(f"Login not available yet (status {response.status_code})")
    return c


@pytest.fixture()
def admin_client(client_factory, make_user, login):
    make_user("admin@test.com", role="admin", name="Admin One")
    c = client_factory()
    response = login(c, "admin@test.com")
    if response.status_code != 200:  # pragma: no cover
        pytest.skip(f"Login not available yet (status {response.status_code})")
    return c
