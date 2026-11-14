# Covers UC-9 / UC-11, IT_05, ST_03 (admin posting visible to students, status tracked), SEC-07.
from datetime import date, timedelta

BODY = {
    "title": "QA Intern - Gamma Ltd", "company": "Gamma Ltd", "description": "Test the product.",
    "deadline": (date.today() + timedelta(days=20)).isoformat(),
}


def test_admin_endpoints_are_admin_only(client, student_client, admin_client):
    for method, url in (("get", "/api/admin/internships"), ("post", "/api/admin/internships"), ("get", "/api/admin/applications")):
        kwargs = {"json": BODY} if method == "post" else {}
        assert getattr(client, method)(url, **kwargs).status_code == 401
        assert getattr(student_client, method)(url, **kwargs).status_code == 403
    assert student_client.patch("/api/admin/applications/1/status", json={"status": "Selected"}).status_code == 403


def test_it05_posted_listing_is_visible_to_students_immediately(client_factory, make_user, login, admin_client):
    created = admin_client.post("/api/admin/internships", json=BODY)
    assert created.status_code == 201 and created.json()["status"] == "active"
    make_user("stud@test.com")
    student = client_factory()
    login(student, "stud@test.com")
    titles = [i["title"] for i in student.get("/api/internships").json()["items"]]
    assert "QA Intern - Gamma Ltd" in titles


def test_draft_and_inactive_are_hidden_from_students_but_listed_for_admin(client_factory, make_user, login, admin_client):
    admin_client.post("/api/admin/internships", json={**BODY, "title": "Hidden", "status": "draft"})
    make_user("stud2@test.com")
    student = client_factory()
    login(student, "stud2@test.com")
    assert student.get("/api/internships").json()["items"] == []
    assert [i["title"] for i in admin_client.get("/api/admin/internships").json()["items"]] == ["Hidden"]


def test_update_and_validation(admin_client):
    listing = admin_client.post("/api/admin/internships", json=BODY).json()
    changed = admin_client.put(f"/api/admin/internships/{listing['id']}", json={**BODY, "title": "Renamed", "location": "  "})
    assert changed.status_code == 200 and changed.json()["title"] == "Renamed" and changed.json()["location"] is None
    bad = admin_client.post("/api/admin/internships", json={**BODY, "title": "", "duration_months": 0})
    assert bad.status_code == 422 and {"title", "duration_months"} <= set(bad.json()["fields"])
    assert admin_client.put("/api/admin/internships/9999", json=BODY).status_code == 404


def test_st03_admin_sees_application_and_updates_status(client_factory, make_user, login, admin_client, db):
    from app.modules.application.models import Application

    listing = admin_client.post("/api/admin/internships", json=BODY).json()
    student_user = make_user("applicant@test.com", name="Appli Cant")
    db.add(Application(student_id=student_user.id, internship_id=listing["id"], resume_stored_name="x.pdf",
                       resume_original_name="cv.pdf", resume_content_type="application/pdf", resume_size_bytes=10))
    db.commit()
    rows = admin_client.get("/api/admin/applications").json()["items"]
    assert rows[0]["student_email"] == "applicant@test.com" and rows[0]["status"] == "Applied"
    assert "resume_stored_name" not in rows[0]
    done = admin_client.patch(f"/api/admin/applications/{rows[0]['id']}/status", json={"status": "Shortlisted"})
    assert done.status_code == 200 and done.json()["status"] == "Shortlisted"
    student = client_factory()
    login(student, "applicant@test.com")
    assert student.get("/api/applications/mine").json()["items"][0]["status"] == "Shortlisted"
    assert admin_client.patch(f"/api/admin/applications/{rows[0]['id']}/status", json={"status": "Bogus"}).status_code == 422
    assert admin_client.get("/api/admin/internships").json()["items"][0]["application_count"] == 1
