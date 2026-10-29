

import io
import logging
import zipfile
from datetime import date, timedelta
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.modules.application.models import Application
from app.modules.internship.models import Internship

PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"


def make_docx() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", "<w:document/>")
    return buffer.getvalue()


@pytest.fixture(autouse=True)
def storage_dir(tmp_path, monkeypatch):
    target = tmp_path / "resumes"
    monkeypatch.setattr(settings, "RESUME_STORAGE_DIR", str(target))
    return target


@pytest.fixture()
def listing(db):
    row = Internship(title="Backend Intern - Acme Corp", company="Acme Corp", description="d", deadline=date.today() + timedelta(days=10))
    db.add(row)
    db.commit()
    return row


def _apply(client, internship_id, resume=("cv.pdf", PDF, "application/pdf"), cover_note=None):
    data = {"internship_id": str(internship_id)}
    if cover_note is not None:
        data["cover_note"] = cover_note
    files = {"resume": resume} if resume else None
    return client.post("/api/applications", data=data, files=files)


def test_ut06_apply_with_valid_pdf_then_listed_in_mine(student_client, listing):
    response = _apply(student_client, listing.id, cover_note="I love backend work.")
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "Applied" and body["internship"]["title"] == "Backend Intern - Acme Corp"
    assert body["resume_original_name"] == "cv.pdf" and body["cover_note"] == "I love backend work."
    mine = student_client.get("/api/applications/mine").json()["items"]
    assert [a["id"] for a in mine] == [body["id"]]


def test_docx_resume_is_accepted(student_client, listing):
    assert _apply(student_client, listing.id, resume=("cv.docx", make_docx(), "application/octet-stream")).status_code == 201


def test_ut07_sec15_second_application_is_409_and_one_row(student_client, listing, db):
    assert _apply(student_client, listing.id).status_code == 201
    second = _apply(student_client, listing.id)
    assert second.status_code == 409
    assert second.json()["code"] == "already_applied"
    assert second.json()["detail"] == "You have already applied to this internship"
    assert db.scalar(select(func.count(Application.id))) == 1
    assert len(list(Path(settings.RESUME_STORAGE_DIR).iterdir())) == 1  # the rejected duplicate stored nothing


def test_st04_expired_listing_rejected_even_when_ui_is_bypassed(student_client, db):
    expired = Internship(title="Old", company="Co", description="d", deadline=date.today() - timedelta(days=1))
    db.add(expired)
    db.commit()
    response = _apply(student_client, expired.id)
    assert response.status_code == 409
    assert response.json()["code"] == "application_window_closed" and response.json()["detail"] == "Application window closed"
    assert db.scalar(select(func.count(Application.id))) == 0


def test_it04_it06_two_listings_recorded_independently(student_client, db):
    rows = [Internship(title=t, company="Co", description="d", deadline=date.today() + timedelta(days=5)) for t in ("One", "Two")]
    db.add_all(rows)
    db.commit()
    for row in rows:
        assert _apply(student_client, row.id).status_code == 201
    mine = student_client.get("/api/applications/mine").json()["items"]
    assert {a["internship"]["title"] for a in mine} == {"One", "Two"} and all(a["status"] == "Applied" for a in mine)


def test_st03_listing_apply_check_mine(student_client, listing):
    assert student_client.get(f"/api/applications/check/{listing.id}").json()["applied"] is False
    _apply(student_client, listing.id)
    check = student_client.get(f"/api/applications/check/{listing.id}").json()
    assert check["applied"] is True and check["status"] == "Applied"
    assert len(student_client.get("/api/applications/mine").json()["items"]) == 1


@pytest.mark.parametrize("name, content, content_type", [
    ("virus.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload"),
    ("notes.pdf", b"just some plain text pretending to be a pdf", "application/pdf"),
    ("fake.docx", b"PK\x03\x04 not really a zip archive", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("plain.zip", None, "application/zip"),
    ("cv.exe", PDF, "application/pdf"),
    ("empty.pdf", b"", "application/pdf"),
])
def test_sec16_bad_files_are_rejected(student_client, listing, db, name, content, content_type):
    if content is None:  # a genuine zip that is NOT a docx
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("readme.txt", "hi")
        content = buffer.getvalue()
    response = _apply(student_client, listing.id, resume=(name, content, content_type))
    assert response.status_code == 422 and response.json()["code"] == "invalid_file"
    assert db.scalar(select(func.count(Application.id))) == 0
    assert not Path(settings.RESUME_STORAGE_DIR).exists() or not list(Path(settings.RESUME_STORAGE_DIR).iterdir())


def test_sec16_oversized_file_is_rejected(student_client, listing):
    big = PDF + b"0" * (6 * 1024 * 1024)
    response = _apply(student_client, listing.id, resume=("big.pdf", big, "application/pdf"))
    assert response.status_code == 422 and response.json()["code"] == "invalid_file"


def test_sec16_missing_resume_is_validation_error(student_client, listing):
    response = _apply(student_client, listing.id, resume=None)
    assert response.status_code == 422 and "resume" in response.json()["fields"]


def test_cover_note_too_long_is_rejected(student_client, listing):
    response = _apply(student_client, listing.id, cover_note="x" * 2001)
    assert response.status_code == 422 and "cover_note" in response.json()["fields"]


def test_sec16_stored_name_is_random_and_inside_storage_dir(student_client, listing, db):
    response = _apply(student_client, listing.id, resume=("../../etc/passwd/my cv.pdf", PDF, "application/pdf"))
    assert response.status_code == 201
    assert response.json()["resume_original_name"] == "my cv.pdf"  # path parts stripped, display only
    stored = db.scalar(select(Application.resume_stored_name))
    assert "/" not in stored and "my" not in stored and stored.endswith(".pdf")
    files = list(Path(settings.RESUME_STORAGE_DIR).iterdir())
    assert [f.name for f in files] == [stored]
    assert Path(settings.RESUME_STORAGE_DIR).resolve() in files[0].resolve().parents


def test_sec06_student_b_cannot_see_student_a_applications(student_client, client_factory, make_user, login, listing):
    _apply(student_client, listing.id)
    make_user("b@test.com")
    other = client_factory()
    login(other, "b@test.com")
    assert other.get("/api/applications/mine").json()["items"] == []


def test_sec07_guest_401_admin_403(client_factory, admin_client, listing):
    assert _apply(client_factory(), listing.id).status_code == 401
    assert _apply(admin_client, listing.id).status_code == 403
    assert admin_client.get("/api/applications/mine").status_code == 403


def test_sec10_18_script_in_cover_note_is_plain_text_and_nothing_sensitive_leaks(student_client, listing, db, caplog):
    script = "<script>alert('x')</script>"
    with caplog.at_level(logging.DEBUG):
        response = _apply(student_client, listing.id, cover_note=script)
    assert response.status_code == 201 and response.json()["cover_note"] == script  # stored inertly, escaped by React
    stored = db.scalar(select(Application.resume_stored_name))
    for forbidden in (stored, "resume_stored_name", "resume_content_type", str(settings.RESUME_STORAGE_DIR), "%PDF"):
        assert forbidden not in response.text
    assert stored not in caplog.text and "%PDF" not in caplog.text and "cv.pdf" not in caplog.text
    assert any("application_created" in r.getMessage() for r in caplog.records)
