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
