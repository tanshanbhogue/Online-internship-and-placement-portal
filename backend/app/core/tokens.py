# ==============================================================================
# FILE   : backend/app/core/tokens.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Creation and verification of session tokens and the cookie helpers.
#
# EXPOSES
#   create_access_token(user_id: int, role: str) -> tuple[str, str, datetime]   # (jwt, jti, expires_at); claims sub, role, jti, iat, exp (+30 min)
#   decode_access_token(token: str) -> dict   # raises NotAuthenticated on bad signature/expired/malformed; algorithm pinned to HS256, secret from settings
#   set_session_cookie(response, token) -> None   # name "access_token", HttpOnly=True, Secure=settings.COOKIE_SECURE, SameSite=settings.COOKIE_SAMESITE, path="/", max_age 30 min
#   clear_session_cookie(response) -> None
#   is_revoked(db, jti) -> bool ; revoke(db, jti, expires_at) -> None
#
# SECURITY
#   SEC-05: unpredictable jti (uuid4), HttpOnly + Secure cookie, expiry after 30 minutes of inactivity (sliding: dependencies re-issue the cookie), invalidated on logout. Never log tokens.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
