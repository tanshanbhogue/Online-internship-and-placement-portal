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

from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

_Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class RegisterRequest(BaseModel):
    # Unknown fields (e.g. "role": "admin") are rejected, never trusted (SEC-07).
    model_config = ConfigDict(extra="forbid")

    name: _Name
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)  # strength rules are applied in the service
    college: Annotated[str | None, StringConstraints(strip_whitespace=True, max_length=100)] = None
    batch: Annotated[str | None, StringConstraints(strip_whitespace=True, max_length=20)] = None

    @field_validator("email")
    @classmethod
    def _lowercase_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("college", "batch")
    @classmethod
    def _blank_to_none(cls, value: str | None) -> str | None:
        return value or None


class RegisterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    college: str | None = None
    batch: str | None = None

    @field_validator("role", mode="before")
    @classmethod
    def _role_value(cls, value):
        return getattr(value, "value", value)
