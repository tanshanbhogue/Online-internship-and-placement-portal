# ==============================================================================
# FILE   : backend/app/modules/auth/register_schemas.py
# STORY  : #14 Student Registration  [FR-001; SEC-02, SEC-08, SEC-09]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 2
# ==============================================================================
#
# PURPOSE
#   Pydantic request/response models for registration.
#
# EXPOSES
#   RegisterRequest: name (strip, 1..100), email (EmailStr, lowercased, <=254), password (8..128 length only; strength is checked in the service),
#       college (optional <=100), batch (optional <=20). model_config forbids extra fields so "role": "admin" is rejected/ignored (never trusted).
#   RegisterResponse: id, name, email, role, college, batch. NEVER include password or password_hash.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
