# ==============================================================================
# FILE   : backend/app/modules/auth/session_models.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Tables that support sessions and login throttling.
#
# EXPOSES
#   RevokedToken: jti str(36) PK ; expires_at datetime ; revoked_at datetime default now  (logout / invalidation list, SEC-05)
#   LoginAttempt: id PK ; email str(254) indexed (lowercase) ; ip str(45) null ; success bool ; attempted_at datetime(UTC) indexed  (SEC-03)
#   Add a cleanup helper purge_expired(db) removing rows older than the throttle window / past expires_at.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
