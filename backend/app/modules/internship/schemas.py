

from datetime import date

from pydantic import BaseModel, Field

SHORT_DESCRIPTION_LENGTH = 160


class InternshipSummary(BaseModel):
    id: int
    title: str
    company: str
    short_description: str
    location: str | None = None
    domain: str | None = None
    stipend_per_month: int | None = None
    duration_months: int | None = None
    deadline: date
    is_open: bool  # computed on the server only


class InternshipDetail(InternshipSummary):
    description: str
    eligibility: str | None = None
    # Application status is NOT here: the SPA asks GET /api/applications/check/{id} (story #18).


class InternshipListResponse(BaseModel):
    items: list[InternshipSummary]
    total: int
    page: int
    page_size: int


class InternshipFilters(BaseModel):
    """Query parameters for GET /api/internships."""

    q: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=100)
    domain: str | None = Field(default=None, max_length=60)
    min_stipend: int | None = Field(default=None, ge=0)
    max_duration_months: int | None = Field(default=None, ge=1)
    open_only: bool = False
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)
