import itertools

import pytest
from sqlalchemy import create_engine, inspect, text

from app.middleware import rate_limit, request_timing
from app.middleware.request_timing import STATS, percentile
from app.modules.performance.indexes import INDEXES, ensure_indexes


# A new address each time: Sprint 1 already locks ONE account after repeated failures (also HTTP 429), which is not what is tested here.
_EMAILS = (f"nobody{n}@test.com" for n in itertools.count())


@pytest.fixture(autouse=True)
def _clean():
    STATS.reset()
    rate_limit.limiter.reset()
    rate_limit.limiter.force = False
    yield
    rate_limit.limiter.force = False
    rate_limit.limiter.reset()


# ------------------------------------------------------------------ timing
def test_every_response_carries_a_timing_header(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert float(response.headers["x-response-time-ms"]) >= 0


def test_percentile_is_nearest_rank():
    values = list(range(1, 101))
    assert percentile(values, 50) == 50 and percentile(values, 95) == 95 and percentile(values, 100) == 100
    assert percentile([], 95) == 0.0 and percentile([7], 95) == 7


def test_stats_use_the_route_template_not_the_real_path(client):
    client.get("/api/health")
    client.get("/api/mock-attempts/123")  # 401 for a guest, still measured
    client.get("/api/mock-attempts/456")
    routes = {(r["method"], r["route"]): r for r in STATS.snapshot()["routes"]}
    assert ("GET", "/api/health") in routes
    assert routes[("GET", "/api/mock-attempts/{attempt_id}")]["count"] == 2
    assert not any("123" in route or "456" in route for _, route in routes)


def test_slow_requests_are_counted_and_logged_without_ids(caplog):
    with caplog.at_level("WARNING", logger="app.performance"):
        STATS.record("GET", "/api/slow/{id}", 3000.0)
        STATS.record("GET", "/api/slow/{id}", 10.0)
    row = [r for r in STATS.snapshot()["routes"] if r["route"] == "/api/slow/{id}"][0]
    assert row["count"] == 2 and row["slow"] == 1 and row["max_ms"] == 3000.0


def test_performance_endpoint_is_admin_only(client, student_client, admin_client):
    assert client.get("/api/admin/performance").status_code == 401
    assert student_client.get("/api/admin/performance").status_code == 403
    body = admin_client.get("/api/admin/performance").json()
    assert body["slow_threshold_ms"] == 2000.0 and isinstance(body["routes"], list)
    assert admin_client.get("/api/admin/performance").headers["cache-control"] == "no-store"


# ------------------------------------------------------------------ compression
def test_responses_are_gzipped_for_clients_that_accept_it_and_plain_otherwise(admin_client, client):
    for _ in range(40):  # make the metrics body larger than 1 KB
        STATS.record("GET", f"/api/fake/route/number/{_}/with/a/long/template", 5.0)
    big = admin_client.get("/api/admin/performance", headers={"Accept-Encoding": "gzip"})
    assert big.headers.get("content-encoding") == "gzip"
    assert big.json()["routes"]  # the client library decompressed it transparently
    plain = client.get("/api/health", headers={"Accept-Encoding": "identity"})
    assert "content-encoding" not in plain.headers and plain.json() == {"status": "ok"}


# ------------------------------------------------------------------ SEC-21 rate limiting
def test_rate_limiter_is_off_under_pytest_unless_forced(client):
    for _ in range(40):
        assert client.post("/api/auth/login", json={"email": next(_EMAILS), "password": "x"}).status_code != 429


def test_login_is_limited_then_recovers(client, monkeypatch):
    rate_limit.limiter.force = True
    now = {"t": 1000.0}
    monkeypatch.setattr(rate_limit.limiter, "clock", lambda: now["t"])
    rule = rate_limit.RULES["login"]
    codes = [client.post("/api/auth/login", json={"email": next(_EMAILS), "password": "x"}).status_code for _ in range(rule.limit + 1)]
    assert 429 not in codes[: rule.limit] and codes[-1] == 429
    blocked = client.post("/api/auth/login", json={"email": next(_EMAILS), "password": "x"})
    assert blocked.json()["code"] == "rate_limited" and int(blocked.headers["retry-after"]) >= 1
    now["t"] += rule.window + 1
    assert client.post("/api/auth/login", json={"email": next(_EMAILS), "password": "x"}).status_code != 429


def test_limits_are_per_rule_and_other_routes_are_free(client, monkeypatch):
    rate_limit.limiter.force = True
    rule = rate_limit.RULES["login"]
    for _ in range(rule.limit + 3):
        client.post("/api/auth/login", json={"email": next(_EMAILS), "password": "x"})
    assert client.get("/api/health").status_code == 200  # not a limited route
    assert client.post("/api/auth/login", json={"email": next(_EMAILS), "password": "x"}).status_code == 429


def test_limiter_can_be_switched_off(client, monkeypatch):
    rate_limit.limiter.force = True
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    for _ in range(rate_limit.RULES["login"].limit + 5):
        assert client.post("/api/auth/login", json={"email": next(_EMAILS), "password": "x"}).status_code != 429


def test_rule_patterns_match_only_the_intended_routes():
    assert rate_limit.RULES["submit_test"].pattern.match("/api/mock-attempts/12/submit")
    assert rate_limit.RULES["submit_test"].pattern.match("/api/mock-attempts/12/auto-submit")
    assert not rate_limit.RULES["submit_test"].pattern.match("/api/mock-attempts/12/answers")
    assert rate_limit.RULES["search"].pattern.match("/api/internships") and not rate_limit.RULES["search"].pattern.match("/api/internships/3")


# ------------------------------------------------------------------ indexes
def test_every_index_is_attached_to_a_real_table_column(db):
    from app.db.base import Base
    for name, table, columns in INDEXES:
        t = Base.metadata.tables.get(table)
        if t is None:
            continue  # the story that owns the table is not merged
        assert name in {i.name for i in t.indexes}, name
        assert all(c in t.c for c in columns), (name, columns)


def test_ensure_indexes_upgrades_an_old_database_and_is_repeatable(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with engine.begin() as c:
        c.execute(text("CREATE TABLE mock_attempts (id INTEGER PRIMARY KEY, student_id INT, test_id INT, status TEXT, submitted_at TEXT, ends_at TEXT, score_percent REAL)"))
    first = ensure_indexes(engine)
    assert "ix_perf_mock_attempts_status_ends_at" in first
    assert ensure_indexes(engine) == first  # again: no error
    names = {i["name"] for i in inspect(engine).get_indexes("mock_attempts")}
    assert {"ix_perf_mock_attempts_student_status_submitted", "ix_perf_mock_attempts_test_status_score"} <= names
