# ==============================================================================
# FILE   : backend/app/modules/auth/login_service.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Authentication business logic (use case 'Register & Login', steps 8-10).
#
# EXPOSES
#   authenticate(db, email, password, ip) -> tuple[User, str token, datetime expires]
#   logout(db, token_payload) -> None   # revoke jti
#
# FLOW
#   1. normalise email (strip, lowercase). 2. ensure_not_throttled. 3. load user; if none -> core.security.verify_dummy(password).
#   4. verify_password; on any failure (unknown, wrong password, inactive) record_attempt(success=False), write security.audit log "login_failed" (email hash/id only, no password), raise InvalidCredentials().
#   5. on success clear_failures, record_attempt(success=True), create token, return.
#   Error text must be identical for unknown account and wrong password (tests UT_02, UT_03, SEC-04).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
