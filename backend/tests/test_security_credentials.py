# ==============================================================================
# FILE   : backend/tests/test_security_credentials.py
# STORY  : #20 Secure Credential Handling  [NFR002; SEC-02, SEC-19, SEC-20]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 1
# ==============================================================================
#
# PURPOSE
#   Tests for password policy, hashing and log redaction. Pure unit tests, no DB needed.
#
# TEST CASES
#   - weak passwords rejected: too short, no digit, no symbol, no letter, empty, 129 chars (SEC-02)
#   - strong password accepted ("Pass@123" style values from the Test Plan)
#   - hash_password returns a different string on each call for the same input (salted) and never equals the plaintext
#   - verify_password: right password True, wrong False, malformed hash False (no exception)
#   - verify_dummy does not raise and returns None
#   - redaction: logging a message/dict containing password=..., Authorization header and cookie shows [REDACTED] and not the secret (use caplog)
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
