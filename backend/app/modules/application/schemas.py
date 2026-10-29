
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ApplicationInternshipRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    deadline: date


class ApplicationOut(BaseModel):
    """What the client sees. NEVER the stored name, any path or the file content (SEC-18)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    internship: ApplicationInternshipRef
    status: str
    cover_note: str | None = None
    applied_at: datetime
    resume_original_name: str

    @field_validator("status", mode="before")
    @classmethod
    def _status_value(cls, value):
        return getattr(value, "value", value)


class ApplicationListResponse(BaseModel):
    items: list[ApplicationOut]
