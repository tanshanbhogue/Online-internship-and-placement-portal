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

import logging
import re

REDACTED = "[REDACTED]"

_SENSITIVE_WORDS = r"(?:password|passwd|token|secret|resume|authorization|cookie)"
# key (may be quoted, may have a prefix/suffix such as new_password or set-cookie) then : or = then a value
_KEY = rf"[\w\-]*{_SENSITIVE_WORDS}[\w\-]*"
_HEADER_KEY = r"[\w\-]*(?:authorization|cookie)[\w\-]*"

# Headers: the value runs to the end of the quoted string / line (it may contain spaces and semicolons).
_HEADER_RE = re.compile(
    rf"""(?P<key>["']?{_HEADER_KEY}["']?\s*[:=]\s*)(?P<quote>["'])?(?P<value>(?(quote)[^"'\r\n]*|[^\r\n,}}]*))""",
    re.IGNORECASE,
)
# Everything else: quoted value, or a run of non-separator characters.
_KV_RE = re.compile(
    rf"""(?P<key>["']?{_KEY}["']?\s*[:=]\s*)(?:(?P<q>["'])(?P<qv>.*?)(?P=q)|(?P<v>[^\s,;&}})\]]+))""",
    re.IGNORECASE,
)
_BEARER_RE = re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9\-._~+/]+=*")
_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*")
_SENSITIVE_KEY_RE = re.compile(_SENSITIVE_WORDS, re.IGNORECASE)


def redact(text: str) -> str:
    """Return `text` with secrets replaced by [REDACTED]."""
    text = _BEARER_RE.sub(lambda m: f"{m.group(1)} {REDACTED}", text)
    text = _HEADER_RE.sub(lambda m: f"{m.group('key')}{m.group('quote') or ''}{REDACTED}", text)

    def _kv(match: re.Match) -> str:
        key = match.group("key")
        if match.group("q"):
            return f"{key}{match.group('q')}{REDACTED}{match.group('q')}"
        return f"{key}{REDACTED}"

    # Skip values the earlier passes already redacted.
    text = _KV_RE.sub(lambda m: m.group(0) if "[REDACTED" in m.group(0) else _kv(m), text)
    return _JWT_RE.sub(REDACTED, text)


def _scrub(value):
    """Redact inside log arguments while preserving their types/shape (uvicorn's access formatter needs its tuple)."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return {k: (REDACTED if _SENSITIVE_KEY_RE.search(str(k)) else _scrub(v)) for k, v in value.items()}
    if isinstance(value, tuple):
        return tuple(_scrub(v) for v in value)
    if isinstance(value, list):
        return [_scrub(v) for v in value]
    return value


class RedactingFilter(logging.Filter):
    """Scrubs credentials from every record before any handler formats it.

    Arguments are scrubbed in place (keeping their structure so formatters such as uvicorn's access log keep working).
    The format string itself is left alone when arguments exist, since it may contain placeholders like "password=%s".
    As a final guard the formatted message is checked once more; only if a secret still shows up is the record
    flattened to its redacted text.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, "_redacted", False):
            return True
        record._redacted = True
        if record.args:
            record.args = _scrub(record.args)
        else:
            record.msg = redact(record.msg) if isinstance(record.msg, str) else record.msg
        try:
            formatted = record.getMessage()
        except Exception:
            return True
        safe = redact(formatted)
        if safe != formatted:
            record.msg, record.args = safe, ()
        return True


_FILTER = RedactingFilter()
_LOGGER_NAMES = ("", "uvicorn", "uvicorn.access", "uvicorn.error", "security.audit")
_installed = False


def install() -> None:
    """Attach the filter everywhere. Idempotent.

    A filter on a *logger* only sees records created by that exact logger, and handlers can be added later
    (uvicorn, pytest's caplog). So in addition to loggers and their current handlers we wrap the LogRecord
    factory: every record is scrubbed the moment it is created, before any handler can see it.
    """
    global _installed
    for name in _LOGGER_NAMES:
        logger = logging.getLogger(name)
        if _FILTER not in logger.filters:
            logger.addFilter(_FILTER)
        for handler in logger.handlers:
            if _FILTER not in handler.filters:
                handler.addFilter(_FILTER)

    if not _installed:
        previous_factory = logging.getLogRecordFactory()

        def factory(*args, **kwargs):
            record = previous_factory(*args, **kwargs)
            _FILTER.filter(record)
            return record

        logging.setLogRecordFactory(factory)
        _installed = True
