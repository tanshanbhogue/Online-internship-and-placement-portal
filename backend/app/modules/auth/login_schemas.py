# ==============================================================================
# FILE   : backend/app/modules/auth/login_schemas.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Pydantic models for login/session endpoints.
#
# EXPOSES
#   LoginRequest(email: EmailStr, password: str 1..128), UserOut(id, name, email, role), LoginResponse(user: UserOut). The token is NEVER in the body (cookie only).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
