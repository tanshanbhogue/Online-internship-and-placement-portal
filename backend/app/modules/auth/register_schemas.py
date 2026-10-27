

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
