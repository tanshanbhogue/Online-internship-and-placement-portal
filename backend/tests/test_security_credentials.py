import logging

import pytest

from backend.app.core.security import (
    hash_password,
    needs_rehash,
    validate_password_strength,
    verify_dummy,
    verify_password,
)
from backend.app.core.log_redaction import RedactingFilter


@pytest.mark.parametrize(
    "password",
    [
        "Ab1!",             # Too short
        "Password!",        # No digit
        "Password123",      # No symbol
        "12345678!",        # No letter
        "",                 # Empty
        "A" * 128 + "1!",   # 129 characters
    ],
)
def test_weak_passwords_are_rejected(password):
    assert validate_password_strength(password)


def test_strong_password_is_accepted():
    assert validate_password_strength("Pass@123") == []


def test_hash_password_uses_random_salt():
    password = "Pass@123"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert first_hash != password
    assert second_hash != password


def test_hash_password_rejects_empty_password():
    with pytest.raises(ValueError):
        hash_password("")


def test_hash_password_rejects_password_over_maximum_length():
    with pytest.raises(ValueError):
        hash_password("A" * 129)


def test_verify_password_accepts_correct_password():
    hashed = hash_password("Pass@123")

    assert verify_password("Pass@123", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("Pass@123")

    assert verify_password("Wrong@123", hashed) is False


def test_verify_password_handles_malformed_hash():
    assert verify_password("Pass@123", "not-a-valid-hash") is False


def test_verify_password_handles_non_string_inputs():
    assert verify_password(None, "some-hash") is False
    assert verify_password("Pass@123", None) is False


def test_verify_dummy_returns_none():
    assert verify_dummy("Pass@123") is None


def test_needs_rehash_handles_malformed_hash():
    assert needs_rehash("not-a-valid-hash") is True


def test_log_redaction_hides_sensitive_values(caplog):
    logger = logging.getLogger("credential_redaction_test")
    logger.addFilter(RedactingFilter())

    password = "MySecretPassword123!"
    token = "abc123secret"
    cookie = "CookieSecret456"

    with caplog.at_level(logging.INFO, logger="credential_redaction_test"):
        logger.info(
            "password=%s Authorization: Bearer %s cookie=%s",
            password,
            token,
            cookie,
        )
        logger.info(
            "payload=%s",
            {"password": password, "name": "test-user"},
        )

    output = caplog.text

    assert password not in output
    assert token not in output
    assert cookie not in output
    assert output.count("[REDACTED]") >= 4
    assert "test-user" in output
