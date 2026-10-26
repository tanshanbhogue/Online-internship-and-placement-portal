# ==============================================================================
# FILE   : backend/app/modules/auth/login_schemas.py
# STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
# OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
# ==============================================================================
#
# PURPOSE
#   Pydantic models for login/session endpoints.
#
# EXPOSES
#   LoginRequest(email: EmailStr, password: str 1..128), UserOut(id, name, email, role), LoginResponse(user: UserOut). The token is NEVER in the body (cookie only).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str

    @field_validator("role", mode="before")
    @classmethod
    def _role_value(cls, value):
        return getattr(value, "value", value)


class LoginResponse(BaseModel):
    user: UserOut  # the token is NEVER in the body; it only travels in the HttpOnly cookie
