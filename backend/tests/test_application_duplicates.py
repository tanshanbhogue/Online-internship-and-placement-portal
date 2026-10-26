# ==============================================================================
# FILE   : backend/tests/test_application_duplicates.py
# STORY  : #18 Prevent Duplicate Internship Applications  [FR-002; SEC-15]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Tests for duplicate prevention (service, constraint and check endpoint).
#
# TEST CASES
#   - ensure_not_already_applied passes for a first application and raises AlreadyApplied after one exists (message "You have already applied to this internship", UT_07)
#   - DB constraint: inserting two Application rows for the same (student, internship) raises IntegrityError and translate_integrity_error returns AlreadyApplied (SEC-15)
#   - same student on a different listing is allowed (IT_06 groundwork); two different students on the same listing are allowed
#   - GET /api/applications/check/{id}: applied=false before, applied=true with status "Applied" after; student B never sees student A's record (SEC-06); guest 401; admin 403
#   NOTE: the HTTP-level 'POST /api/applications twice' test is in test_application_apply.py (story #17).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from datetime import date, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.errors import AlreadyApplied
from app.modules.application.duplicate_check import ensure_not_already_applied, has_applied, translate_integrity_error
from app.modules.application.models import Application
from app.modules.internship.models import Internship


def _listing(db, title="Backend Intern - Acme Corp"):
    row = Internship(title=title, company="Acme", description="d", deadline=date.today() + timedelta(days=10))
    db.add(row)
    db.commit()
    return row


def _application(student_id, internship_id):
    return Application(
        student_id=student_id, internship_id=internship_id, resume_stored_name="abc.pdf",
        resume_original_name="cv.pdf", resume_content_type="application/pdf", resume_size_bytes=10,
    )


def test_ensure_not_already_applied_passes_then_raises(db, make_user):
    student, listing = make_user("a@test.com"), _listing(db)
    ensure_not_already_applied(db, student.id, listing.id)  # first application: fine
    db.add(_application(student.id, listing.id))
    db.commit()
    assert has_applied(db, student.id, listing.id) is True
    with pytest.raises(AlreadyApplied) as caught:
        ensure_not_already_applied(db, student.id, listing.id)
    assert caught.value.message == "You have already applied to this internship"
    assert caught.value.status_code == 409


def test_db_constraint_blocks_duplicates_and_is_translated(db, make_user):
    student, listing = make_user("a@test.com"), _listing(db)
    db.add(_application(student.id, listing.id))
    db.commit()
    db.add(_application(student.id, listing.id))
    with pytest.raises(IntegrityError) as caught:
        db.commit()
    db.rollback()
    assert isinstance(translate_integrity_error(caught.value), AlreadyApplied)


def test_other_integrity_errors_are_re_raised(db, make_user):
    student = make_user("a@test.com")
    db.add(_application(student.id, 99999))  # foreign key violation, not a duplicate
    with pytest.raises(IntegrityError) as caught:
        db.commit()
    db.rollback()
    with pytest.raises(IntegrityError):
        translate_integrity_error(caught.value)


def test_different_listing_and_different_student_are_allowed(db, make_user):
    a, b = make_user("a@test.com"), make_user("b@test.com")
    first, second = _listing(db, "One"), _listing(db, "Two")
    db.add_all([_application(a.id, first.id), _application(a.id, second.id), _application(b.id, first.id)])
    db.commit()
    assert has_applied(db, a.id, second.id) and has_applied(db, b.id, first.id)
    assert not has_applied(db, b.id, second.id)


def test_check_endpoint_before_and_after(student_client, db):
    listing = _listing(db)
    before = student_client.get(f"/api/applications/check/{listing.id}")
    assert before.status_code == 200
    assert before.json() == {"internship_id": listing.id, "applied": False, "status": None, "applied_at": None}
    student_id = student_client.get("/api/auth/me").json()["id"]
    db.add(_application(student_id, listing.id))
    db.commit()
    after = student_client.get(f"/api/applications/check/{listing.id}").json()
    assert after["applied"] is True and after["status"] == "Applied" and after["applied_at"]


def test_sec06_student_never_sees_another_students_record(student_client, make_user, client_factory, login, db):
    listing = _listing(db)
    other = make_user("other@test.com")
    db.add(_application(other.id, listing.id))
    db.commit()
    assert student_client.get(f"/api/applications/check/{listing.id}").json()["applied"] is False


def test_check_unknown_listing_guest_and_admin(student_client, client_factory, admin_client, db):
    assert student_client.get("/api/applications/check/9999").status_code == 404
    listing = _listing(db)
    assert client_factory().get(f"/api/applications/check/{listing.id}").status_code == 401
    assert admin_client.get(f"/api/applications/check/{listing.id}").status_code == 403
