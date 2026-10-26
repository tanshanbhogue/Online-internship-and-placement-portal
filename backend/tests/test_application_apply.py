# ==============================================================================
# FILE   : backend/tests/test_application_apply.py
# STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
# ==============================================================================
#
# PURPOSE
#   Tests for applying to internships (backend).
#
# TEST CASES
#   - UT_06 student applies to an open listing with a valid PDF -> 201, status "Applied", appears in GET /mine
#   - UT_07 / SEC-15 POST the same application twice via HTTP -> second is 409 already_applied and only one row exists
#   - ST_04 / SEC-15 listing with a past deadline -> 409 application_window_closed even when the UI is bypassed
#   - IT_04 applied internship appears in My Applications with status Applied; IT_06 two different listings both recorded independently
#   - ST_03 (service level) listing -> apply -> check endpoint says applied -> /mine shows it
#   - SEC-16 uploads: .exe, 6 MB file, text file renamed to .pdf, and a missing resume are all rejected (422); stored file name is random and lives in the storage dir, not the web root
#   - SEC-06 student B cannot see student A's applications; SEC-07 guest 401, admin 403 on POST
#   - SEC-10/18: script tags in cover_note are stored as plain text; responses and logs contain no stored path, tokens or file content
#   Use a tmp_path storage dir via settings override; build tiny valid PDF/DOCX byte fixtures in the test.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
