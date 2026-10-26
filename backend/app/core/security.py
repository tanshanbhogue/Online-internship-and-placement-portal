# ==============================================================================
# FILE   : backend/app/core/security.py
# STORY  : #20 Secure Credential Handling  [NFR002; SEC-02, SEC-19, SEC-20]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 1
# ==============================================================================
#
# PURPOSE
#   Password security primitives: strength policy, salted hashing, verification. Pure functions with no database or HTTP code,
#   so registration (#14) and login (#19) both call them.
#
# ROLE
#   Security building block under the Authentication component. Merged FIRST so #14 and #19 can import it.
#
# EXPOSES (exact names; other stories import these)
#   MIN_PASSWORD_LENGTH = 8 ; MAX_PASSWORD_LENGTH = 128
#   validate_password_strength(plain: str) -> list[str]
#       Returns human-readable problems; [] means acceptable. Rules (SEC-02): length 8..128, at least one letter, one digit and one symbol.
#       Messages e.g. "Password must be at least 8 characters", "Password must contain a digit", "... a symbol", "... a letter".
#   hash_password(plain: str) -> str
#       Argon2id via argon2-cffi PasswordHasher (random salt built in). Raise ValueError if plain is empty or > MAX length (stops hashing-DoS).
#   verify_password(plain: str, hashed: str) -> bool
#       Returns False on mismatch AND on malformed hash; never raises for bad credentials.
#   verify_dummy(plain: str) -> None
#       Verify against a precomputed dummy hash so "unknown email" takes the same time as "wrong password" (supports SEC-04, no user enumeration).
#   needs_rehash(hashed: str) -> bool
#
# RULES
#   Never log, print or return passwords or hashes. Never compare secrets with ==; rely on the library's constant-time verify. No custom crypto.
#
# TESTS COVERED
#   backend/tests/test_security_credentials.py (SEC-02).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
