# ==============================================================================
# FILE   : backend/tests/test_auth_login.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Tests for login, logout, session validation, throttling and the registration-then-login journeys.
#
# TEST CASES
#   - UT_01 valid credentials -> 200, cookie set with HttpOnly (and SameSite) flags, body.user has no password data
#   - UT_02 wrong password -> 401 "Invalid username or password"; UT_03 unknown email -> identical 401 body (SEC-04)
#   - IT_01 register (#14 endpoint) then log in with the same credentials -> success
#   - IT_03 after login, GET /api/auth/me and other protected endpoints keep working across several requests
#   - ST_01 register -> login -> /me returns the profile
#   - ST_02 logout then reuse the old cookie -> 401; hitting a protected URL while logged out -> 401 (SEC-01, SEC-05)
#   - SEC-03 five wrong passwords within 15 min -> 6th attempt 429 even with the correct password; after freezegun moves 16 min it succeeds
#   - SEC-05 token expires after 30 min of inactivity (freezegun) and the cookie is re-issued on activity
#   - SEC-07 dependency checks: student calling an admin-only dependency gets 403, guest gets 401 (use a tiny test-only route)
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
