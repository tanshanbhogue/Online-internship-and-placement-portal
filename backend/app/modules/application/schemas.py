# ==============================================================================
# FILE   : backend/app/modules/application/schemas.py
# STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
# ==============================================================================
#
# PURPOSE
#   Pydantic models for the application endpoints.
#
# EXPOSES
#   ApplicationInternshipRef: id, title, company, deadline
#   ApplicationOut: id, internship: ApplicationInternshipRef, status, cover_note, applied_at, resume_original_name  (NEVER stored name, paths or content, SEC-18)
#   ApplicationListResponse: items: list[ApplicationOut]
#   The create endpoint takes multipart form fields (not JSON), so there is no ApplicationCreate JSON model; validate cover_note length <= 2000 in the service.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

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
