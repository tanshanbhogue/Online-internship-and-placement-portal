import re

from argon2 import PasswordHasher, Type
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

_password_hasher = PasswordHasher(
    type=Type.ID,
    salt_len=16,
)

# Created once so unknown-user verification can use a real Argon2 hash.
_DUMMY_HASH = _password_hasher.hash("DummyCredential9!")


def validate_password_strength(plain: str) -> list[str]:
    """Return password-policy problems; an empty list means acceptable."""
    if not isinstance(plain, str):
        return ["Password must be a string"]

    problems = []

    if len(plain) < MIN_PASSWORD_LENGTH:
        problems.append("Password must be at least 8 characters")
    if len(plain) > MAX_PASSWORD_LENGTH:
        problems.append("Password must be at most 128 characters")
    if not re.search(r"[A-Za-z]", plain):
        problems.append("Password must contain a letter")
    if not re.search(r"\d", plain):
        problems.append("Password must contain a digit")
    if not re.search(r"[^A-Za-z0-9]", plain):
        problems.append("Password must contain a symbol")

    return problems


def hash_password(plain: str) -> str:
    """Hash a password using Argon2id with a randomly generated salt."""
    if not isinstance(plain, str) or not plain or len(plain) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password must be non-empty and at most 128 characters")

    return _password_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return False for incorrect credentials or an invalid stored hash."""
    if not isinstance(plain, str) or not isinstance(hashed, str):
        return False

    try:
        return _password_hasher.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def verify_dummy(plain: str) -> None:
    """Perform a dummy password verification for unknown-user login attempts."""
    if not isinstance(plain, str):
        plain = ""

    verify_password(plain, _DUMMY_HASH)
    return None


def needs_rehash(hashed: str) -> bool:
    """Return whether a stored hash should be regenerated."""
    if not isinstance(hashed, str):
        return True

    try:
        return _password_hasher.check_needs_rehash(hashed)
    except (VerificationError, InvalidHashError):
        return True
