# ==============================================================================
# FILE   : backend/scripts/seed_admin.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   One-off script creating the admin account (admins cannot self-register).
#
# BEHAVIOUR
#   Run: python -m scripts.seed_admin  (from backend/). Reads ADMIN_EMAIL and ADMIN_PASSWORD from settings/env, validates strength, creates a User with role ADMIN if the email is not present,
#   otherwise prints 'already exists'. Idempotent. Never prints the password. Add backend/scripts/__init__.py as an empty package marker if needed.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
