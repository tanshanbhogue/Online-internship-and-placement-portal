# ==============================================================================
# FILE   : backend/tests/test_auth_registration.py
# STORY  : #14 Student Registration  [FR-001; SEC-02, SEC-08, SEC-09]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 2
# ==============================================================================
#
# PURPOSE
#   Tests for registration (backend).
#
# TEST CASES
#   - UT_04: blank name/email/password -> 422, body.fields has entries for name, email and password, and no account is created
#   - valid registration -> 201, response has no password/password_hash, DB row stores an Argon2 hash (not plaintext) (SEC-02)
#   - IT_02: same email twice -> second is 409 with detail "Email already exists" and only one row exists; also for different letter case (Student1@Test.com)
#   - weak password (e.g. "abc") -> 422 with a message under fields.password (SEC-02)
#   - body containing "role": "admin" never produces an admin (SEC-07)
#   - SQL-injection style email/name strings are rejected or stored inertly and tables remain intact (SEC-09)
#   NOTE: IT_01 and ST_01 (register then login) live in test_auth_login.py because they need story #19.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
