import logging
import re
from collections.abc import Mapping
from threading import Lock
from typing import Any


REDACTED = "[REDACTED]"

_SENSITIVE_KEY = re.compile(
    r"password|passwd|token|access_token|authorization|cookie|"
    r"set-cookie|secret|resume",
    re.IGNORECASE,
)

# Handles key=value and key: value / "key": "value" formats.
_SENSITIVE_PAIR = re.compile(
    r"""(?P<prefix>["']?(?:password|passwd|token|access_token|"""
    r"""authorization|cookie|set-cookie|secret|resume)["']?"""
    r"""\s*[:=]\s*)"""
    r"""(?P<value>"[^"]*"|'[^']*'|[^,\s}\]]+)""",
    re.IGNORECASE,
)

_BEARER_TOKEN = re.compile(
    r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+"
)

_install_lock = Lock()
_installed = False


def _redact_text(value: str) -> str:
    """Redact sensitive key-value pairs and bearer credentials."""
    value = _BEARER_TOKEN.sub("Bearer " + REDACTED, value)
    value = _SENSITIVE_PAIR.sub(
        lambda match: match.group("prefix") + REDACTED,
        value,
    )
    return value


def _redact_value(value: Any) -> Any:
    """Recursively redact sensitive values in mappings and containers."""
    if isinstance(value, Mapping):
        result = {}
        for key, item in value.items():
            if _SENSITIVE_KEY.search(str(key)):
                result[key] = REDACTED
            else:
                result[key] = _redact_value(item)
        return result

    if isinstance(value, tuple):
        return tuple(_redact_value(item) for item in value)

    if isinstance(value, list):
        return [_redact_value(item) for item in value]

    if isinstance(value, str):
        return _redact_text(value)

    return value


class RedactingFilter(logging.Filter):
    """Scrub sensitive information from log messages and arguments."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Scrub sensitive information from the complete log message."""
        try:
            message = record.getMessage()
            record.msg = _redact_text(str(_redact_value(message)))
            record.args = ()
        except Exception:
            # Fail closed: never expose the original message if scrubbing fails.
            record.msg = REDACTED
            record.args = ()

        return True



def install() -> None:
    """Install the redaction filter on application and server loggers once."""
    global _installed

    with _install_lock:
        if _installed:
            return

        redacting_filter = RedactingFilter()
        logger_names = (
            "",
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
            "security.audit",
        )

        for name in logger_names:
            logger = logging.getLogger(name)
            logger.addFilter(redacting_filter)

            for handler in logger.handlers:
                handler.addFilter(redacting_filter)

        _installed = True
