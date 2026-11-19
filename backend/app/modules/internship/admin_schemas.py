from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.internship.models import ListingStatus


class _Clean(BaseModel):
    """Trims text; blank optional text becomes None."""

    @field_validator("*", mode="before")
    @classmethod
    def _strip(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return value


class InternshipWrite(_Clean):
    title: str = Field(min_length=1, max_length=150)
    company: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=5000)
    eligibility: str | None = Field(default=None, max_length=2000)
    location: str | None = Field(default=None, max_length=100)
    domain: str | None = Field(default=None, max_length=60)
    stipend_per_month: int | None = Field(default=None, ge=0, le=10_000_000)
    duration_months: int | None = Field(default=None, ge=1, le=36)
    deadline: date
    status: ListingStatus = ListingStatus.ACTIVE

    @field_validator("eligibility", "location", "domain", mode="after")
    @classmethod
    def _blank_to_none(cls, value):
        return value or None


class InternshipAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    description: str
    eligibility: str | None = None
    location: str | None = None
    domain: str | None = None
    stipend_per_month: int | None = None
    duration_months: int | None = None
    deadline: date
    status: str
    application_count: int = 0
    created_at: datetime

    @field_validator("status", mode="before")
    @classmethod
    def _status_value(cls, value):
        return getattr(value, "value", value)


class InternshipAdminPage(BaseModel):
    items: list[InternshipAdminOut]
    total: int
    page: int
    page_size: int