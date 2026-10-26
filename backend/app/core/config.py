# ==============================================================================
# FILE   : backend/app/core/config.py
# STORY  : Foundation - shared scaffold (chore, no backlog issue)
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
# ==============================================================================
#
# PURPOSE
#   Central typed settings loaded from environment / .env. The only place that reads os.environ.
#
# CODE TO WRITE
#   class Settings(BaseSettings) (pydantic-settings) with the variables listed in backend/.env.example, typed and defaulted:
#     APP_ENV, DATABASE_URL, SECRET_KEY (no default in production: raise if empty when APP_ENV != "development"),
#     ACCESS_TOKEN_EXPIRE_MINUTES=30, COOKIE_SECURE (bool), COOKIE_SAMESITE, LOGIN_MAX_FAILURES=5, LOGIN_WINDOW_MINUTES=15,
#     RESUME_STORAGE_DIR, RESUME_MAX_BYTES=5*1024*1024, PRACTICE_DEFAULT_QUESTION_COUNT=10, CORS_ORIGINS (list parsed from comma string),
#     ADMIN_EMAIL, ADMIN_PASSWORD (optional).
#   get_settings() cached with functools.lru_cache; export `settings = get_settings()`.
#   Tests override values by clearing the cache or monkeypatching attributes (document this in conftest).
#
# SECURITY
#   SEC-24: no secret has a committed default value. Never print settings that contain secrets.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
