from datetime import datetime

from pydantic import BaseModel


class ApplicationCheckResponse(BaseModel):
    internship_id: int
    applied: bool
    status: str | None = None  # the ApplicationStatus value, e.g. "Applied"
    applied_at: datetime | None = None