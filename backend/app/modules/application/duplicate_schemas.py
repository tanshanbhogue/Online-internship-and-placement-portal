# ==============================================================================
# FILE   : backend/app/modules/application/duplicate_schemas.py
# STORY  : #18 Prevent Duplicate Internship Applications  [FR-002; SEC-15]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Response model for the 'have I applied?' check.
#
# EXPOSES
#   ApplicationCheckResponse: internship_id int, applied bool, status str | None (the ApplicationStatus value), applied_at datetime | None.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from datetime import datetime

from pydantic import BaseModel


class ApplicationCheckResponse(BaseModel):
    internship_id: int
    applied: bool
    status: str | None = None  # the ApplicationStatus value, e.g. "Applied"
    applied_at: datetime | None = None
