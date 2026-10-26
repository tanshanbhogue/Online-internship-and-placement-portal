# ==============================================================================
# FILE   : backend/app/modules/application/service.py
# STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
# ==============================================================================
#
# PURPOSE
#   Business logic for applying and listing a student's applications (use case 'Apply for Internship').
#
# EXPOSES
#   apply(db, student: User, internship_id: int, cover_note: str | None, resume: UploadFile) -> Application
#   list_for_student(db, student_id: int) -> list[Application]      # newest first, each with its Internship loaded
#
# apply() FLOW (order matters)
#   1. listing = internship.service.get_listing(db, internship_id)            (404 if missing)
#   2. internship.service.ensure_open(listing)                               (409 'Application window closed', ST_04, SEC-15)
#   3. application.duplicate_check.ensure_not_already_applied(...)           (409 'You have already applied to this internship', UT_07)
#   4. validate: resume present (else ValidationFailed fields={"resume": [...]}), cover_note <= 2000 chars, strip it
#   5. stored = resume_storage.save_resume(resume)
#   6. insert Application(status=APPLIED); commit. On IntegrityError: rollback, delete_resume(stored.stored_name), raise duplicate_check.translate_integrity_error(exc)
#   7. write security.audit log 'application_created' with student id and application id only
#   8. return the Application
#
# RULES
#   student_id always comes from the authenticated user, never from the request (SEC-06).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
