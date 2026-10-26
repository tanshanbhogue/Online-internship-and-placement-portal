# ==============================================================================
# FILE   : backend/app/modules/auth/login_router.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   HTTP endpoints for login, logout and session check.
#
# ROUTES
#   router = APIRouter(prefix="/api/auth", tags=["auth"])
#   POST /api/auth/login   body LoginRequest -> 200 LoginResponse + Set-Cookie access_token ; 401 invalid_credentials ; 429 too_many_attempts
#   POST /api/auth/logout  -> 204, always clears the cookie, revokes the token if one was presented (reusing the old token afterwards must give 401)
#   GET  /api/auth/me      Depends(get_current_user) -> UserOut  (the SPA calls this on page load to restore the session; also proves session persists across modules, IT_03)
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
