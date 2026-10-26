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

import logging

import pytest

from app.core import log_redaction
from app.core.security import (
    MAX_PASSWORD_LENGTH,
    hash_password,
    needs_rehash,
    validate_password_strength,
    verify_dummy,
    verify_password,
)


@pytest.mark.parametrize(
    "password, expected_fragment",
    [
        ("Ab1!", "at least 8"),
        ("Password!!", "digit"),
        ("Password123", "symbol"),
        ("12345678!@", "letter"),
        ("", "at least 8"),
        ("Aa1!" + "x" * 126, "at most 128"),
    ],
)
def test_weak_passwords_rejected(password, expected_fragment):
    problems = validate_password_strength(password)
    assert problems, f"{password!r} should be rejected"
    assert any(expected_fragment in p for p in problems)


@pytest.mark.parametrize("password", ["Pass@123", "Str0ng#Passw0rd", "Correct-Horse9"])
def test_strong_passwords_accepted(password):
    assert validate_password_strength(password) == []


def test_hash_is_salted_and_not_plaintext():
    first, second = hash_password("Pass@123"), hash_password("Pass@123")
    assert first != second
    assert "Pass@123" not in first
    assert first.startswith("$argon2id$")


def test_hash_password_rejects_empty_and_oversized():
    with pytest.raises(ValueError):
        hash_password("")
    with pytest.raises(ValueError):
        hash_password("a" * (MAX_PASSWORD_LENGTH + 1))


def test_verify_password_outcomes():
    hashed = hash_password("Pass@123")
    assert verify_password("Pass@123", hashed) is True
    assert verify_password("Wrong@123", hashed) is False
    assert verify_password("Pass@123", "not-a-real-hash") is False
    assert verify_password("Pass@123", "") is False


def test_verify_dummy_returns_none():
    assert verify_dummy("anything") is None


def test_needs_rehash_for_fresh_and_garbage_hash():
    assert needs_rehash(hash_password("Pass@123")) is False
    assert needs_rehash("garbage") is True


def test_log_redaction_hides_secrets(caplog):
    log_redaction.install()
    log_redaction.install()  # idempotent
    logger = logging.getLogger("security.audit")
    with caplog.at_level(logging.INFO):
        logger.info("login payload %s", {"email": "a@b.com", "password": "Sup3r@Secret"})
        logger.info("password=Sup3r@Secret1 seen")
        logger.info("Authorization: Bearer abc123.def456.ghi789")
        logger.info("headers %s", {"cookie": "access_token=eyJhbGciOi.eyJzdWIi.sigsig; theme=dark"})
    text = caplog.text
    assert "[REDACTED]" in text
    for secret in ("Sup3r@Secret", "abc123.def456", "eyJhbGciOi", "Sup3r@Secret1"):
        assert secret not in text
    assert "a@b.com" in text  # non-sensitive data is kept


def test_log_redaction_keeps_argument_structure_for_uvicorn_style_records(caplog):
    """uvicorn's access formatter unpacks record.args as a 5-tuple: redaction must not flatten it."""
    log_redaction.install()
    captured = []

    class Grab(logging.Handler):
        def emit(self, record):
            captured.append(record)

    logger = logging.getLogger("uvicorn.access")
    handler = Grab()
    logger.addHandler(handler)
    try:
        logger.warning('%s - "%s %s HTTP/%s" %d', "1.2.3.4", "GET", "/x?token=abc123&page=2", "1.1", 200)
    finally:
        logger.removeHandler(handler)
    record = captured[0]
    assert isinstance(record.args, tuple) and len(record.args) == 5 and record.args[4] == 200
    assert "abc123" not in record.getMessage() and "page=2" in record.getMessage()


def test_log_redaction_placeholder_templates_do_not_break_formatting(caplog):
    log_redaction.install()
    with caplog.at_level(logging.INFO):
        logging.getLogger("app.test").info("login password=%s ok=%s", "Hunter2!", True)
    assert "Hunter2!" not in caplog.text and "ok=True" in caplog.text
