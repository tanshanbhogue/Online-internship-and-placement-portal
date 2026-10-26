# ==============================================================================
# FILE   : backend/app/core/log_redaction.py
# STORY  : #20 Secure Credential Handling  [NFR002; SEC-02, SEC-19, SEC-20]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 1
# ==============================================================================
#
# PURPOSE
#   Logging filter that scrubs credentials and tokens from every log line (SEC-18, SEC-19, SEC-20: logs must not leak secrets).
#
# EXPOSES
#   class RedactingFilter(logging.Filter): rewrites record.msg/args, replacing the value of keys such as password, passwd, token, access_token,
#       authorization, cookie, set-cookie, secret, resume (case-insensitive; handles key=value, "key": "value" and dict args) with "[REDACTED]".
#   install() -> None : attach the filter to the root logger and to uvicorn / uvicorn.access / uvicorn.error / security.audit handlers. Idempotent.
#   app/main.py calls install() automatically if this module exists.
#
# TESTS COVERED
#   test_security_credentials.py: a logged dict containing a password and a Bearer/cookie string appears redacted in caplog.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
