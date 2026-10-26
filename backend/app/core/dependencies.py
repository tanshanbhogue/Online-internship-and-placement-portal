# ==============================================================================
# FILE   : backend/app/core/dependencies.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   FastAPI dependencies that every protected endpoint in the project uses for authentication and role checks. This file is the single
#   gatekeeper for SEC-01, SEC-06 and SEC-07.
#
# EXPOSES (other stories import these names)
#   get_current_user(request, response, db) -> User
#       read cookie access_token -> decode -> reject if revoked, user missing or inactive -> raise NotAuthenticated (401). On success re-issue the
#       cookie with a fresh 30-minute expiry (sliding expiry).
#   get_current_student(user=Depends(get_current_user)) -> User   # role must be STUDENT else Forbidden (403)
#   get_current_admin(user=Depends(get_current_user)) -> User     # role must be ADMIN else Forbidden (403); roles are checked server-side only
#   get_client_ip(request) -> str | None
#
# RULES
#   Guests get 401 not_authenticated; students on admin routes get 403 forbidden (test SEC-07). Ownership checks (SEC-06) are done by each service using user.id.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
