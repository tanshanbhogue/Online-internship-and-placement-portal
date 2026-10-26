# ==============================================================================
# FILE   : backend/tests/test_internship_listings.py
# STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Tests for listing browse and filters.
#
# TEST CASES
#   - UT_05 active listings returned with title, company, deadline for an authenticated student; guest gets 401 (SEC-01)
#   - IT_05 a listing inserted after the first request appears on the next request immediately (no stale cache)
#   - DRAFT/INACTIVE listings are not returned; GET detail of one gives 404
#   - expired-deadline listing is returned with is_open == false and sorted after open ones (supports ST_04)
#   - filters: q by title/company, location, domain, min_stipend, max_duration_months, open_only; no-match returns items == [] with 200
#   - injection strings and '%' / '_' in q behave as plain text (SEC-09); pagination bounds enforced (page_size > 50 -> 422)
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from datetime import date, timedelta

import pytest

from app.modules.internship.models import Internship, ListingStatus


@pytest.fixture()
def add_listing(db):
    def _add(title="Backend Intern - Acme Corp", company="Acme Corp", days=30, status=ListingStatus.ACTIVE, **kw):
        row = Internship(
            title=title, company=company, description=kw.pop("description", "A great internship."),
            deadline=date.today() + timedelta(days=days), status=status, **kw,
        )
        db.add(row)
        db.commit()
        return row

    return _add


def _titles(response):
    return [i["title"] for i in response.json()["items"]]


def test_ut05_active_listings_for_student_and_guest_gets_401(student_client, client_factory, add_listing):
    add_listing()
    response = student_client.get("/api/internships")
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert {"title", "company", "deadline", "is_open"} <= set(item)
    assert item["title"] == "Backend Intern - Acme Corp" and item["is_open"] is True
    assert client_factory().get("/api/internships").status_code == 401


def test_it05_new_listing_visible_on_next_request(student_client, add_listing):
    assert student_client.get("/api/internships").json()["items"] == []
    add_listing(title="QA Intern - Gamma Ltd", company="Gamma Ltd")
    assert _titles(student_client.get("/api/internships")) == ["QA Intern - Gamma Ltd"]


def test_draft_and_inactive_hidden_and_detail_404(student_client, add_listing):
    add_listing(title="Visible")
    draft = add_listing(title="Draft", status=ListingStatus.DRAFT)
    inactive = add_listing(title="Inactive", status=ListingStatus.INACTIVE)
    assert _titles(student_client.get("/api/internships")) == ["Visible"]
    for hidden in (draft, inactive):
        response = student_client.get(f"/api/internships/{hidden.id}")
        assert response.status_code == 404 and response.json()["code"] == "not_found"
    assert student_client.get("/api/internships/99999").status_code == 404


def test_detail_includes_description_and_eligibility(student_client, add_listing):
    row = add_listing(description="Full text", eligibility="Final years")
    body = student_client.get(f"/api/internships/{row.id}").json()
    assert body["description"] == "Full text" and body["eligibility"] == "Final years"


def test_expired_listing_is_closed_and_sorted_last(student_client, add_listing):
    add_listing(title="Expired", days=-3)
    add_listing(title="Later", days=40)
    add_listing(title="Soon", days=2)
    items = student_client.get("/api/internships").json()["items"]
    assert [i["title"] for i in items] == ["Soon", "Later", "Expired"]
    assert [i["is_open"] for i in items] == [True, True, False]


def test_deadline_today_is_still_open(student_client, add_listing):
    add_listing(title="Today", days=0)
    assert student_client.get("/api/internships").json()["items"][0]["is_open"] is True


def test_filters(student_client, add_listing):
    add_listing(title="Backend Intern - Acme Corp", company="Acme Corp", location="Bengaluru", domain="Backend", stipend_per_month=25000, duration_months=6)
    add_listing(title="Data Analyst Intern - Beta Inc", company="Beta Inc", location="Pune", domain="Data Analytics", stipend_per_month=15000, duration_months=3)
    add_listing(title="Old One", company="Gamma Ltd", location="Remote", domain="QA", stipend_per_month=5000, duration_months=2, days=-5)
    get = lambda **p: student_client.get("/api/internships", params=p)

    assert _titles(get(q="acme")) == ["Backend Intern - Acme Corp"]
    assert _titles(get(q="BETA")) == ["Data Analyst Intern - Beta Inc"]
    assert _titles(get(location="pune")) == ["Data Analyst Intern - Beta Inc"]
    assert _titles(get(domain="backend")) == ["Backend Intern - Acme Corp"]
    assert _titles(get(min_stipend=20000)) == ["Backend Intern - Acme Corp"]
    assert _titles(get(max_duration_months=3)) == ["Data Analyst Intern - Beta Inc", "Old One"]
    assert "Old One" not in _titles(get(open_only="true"))
    empty = get(q="no-such-thing")
    assert empty.status_code == 200 and empty.json()["items"] == [] and empty.json()["total"] == 0


def test_sec09_injection_and_wildcards_are_plain_text(student_client, add_listing, db):
    add_listing(title="Backend Intern - Acme Corp")
    add_listing(title="100%_Remote Role", company="Odd Co")
    get = lambda q: student_client.get("/api/internships", params={"q": q})
    assert get("' OR 1=1 --").json()["items"] == []
    assert get("%").json()["total"] == 1  # '%' only matches a literal percent sign
    assert get("_").json()["total"] == 1
    assert get("x'; DROP TABLE internships;--").status_code == 200
    assert db.query(Internship).count() == 2


def test_pagination_bounds(student_client, add_listing):
    for n in range(5):
        add_listing(title=f"Role {n}", days=10 + n)
    page = student_client.get("/api/internships", params={"page": 2, "page_size": 2}).json()
    assert page["total"] == 5 and page["page"] == 2 and page["page_size"] == 2
    assert _titles(student_client.get("/api/internships", params={"page": 2, "page_size": 2})) == ["Role 2", "Role 3"]
    assert student_client.get("/api/internships", params={"page_size": 51}).status_code == 422
    assert student_client.get("/api/internships", params={"page": 0}).status_code == 422


def test_short_description_is_truncated(student_client, add_listing):
    add_listing(description="x" * 500)
    short = student_client.get("/api/internships").json()["items"][0]["short_description"]
    assert len(short) <= 161
