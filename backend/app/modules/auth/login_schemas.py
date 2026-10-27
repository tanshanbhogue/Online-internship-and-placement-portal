
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.auth.models import Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: Role


class LoginResponse(BaseModel):
    user: UserOut
