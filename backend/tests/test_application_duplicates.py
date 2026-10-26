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
