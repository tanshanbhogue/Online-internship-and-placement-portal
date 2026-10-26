# ==============================================================================
# FILE   : backend/app/modules/application/duplicate_check.py
# STORY  : #18 Prevent Duplicate Internship Applications  [FR-002; SEC-15]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Server-side duplicate-application guard (FR-002 fail condition 'duplicate applications are blocked', SEC-15). Story #17's service calls this.
#
# EXPOSES (exact names)
#   has_applied(db, student_id: int, internship_id: int) -> bool
#   get_existing(db, student_id, internship_id) -> Application | None
#   ensure_not_already_applied(db, student_id, internship_id) -> None     # raises AlreadyApplied ("You have already applied to this internship", 409)
#   translate_integrity_error(exc: IntegrityError) -> AppError          # maps a violation of uq_application_student_internship to AlreadyApplied; re-raises other IntegrityErrors
#
# RULES
#   The check by itself is not enough: #17 must also wrap the insert and call translate_integrity_error so two simultaneous requests yield exactly one row (test below).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
