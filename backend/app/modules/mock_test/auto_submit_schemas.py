# Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
# File: backend/app/modules/mock_test/auto_submit_schemas.py
#
# Contract
#   AutoSubmitResponse   what the browser learns after the timer hit zero
#   SweepResponse        admin sweep result
from datetime import datetime

from pydantic import BaseModel


class AutoSubmitResponse(BaseModel):
    attempt_id: int
    status: str  # submitted | auto_submitted
    auto_submitted: bool  # True when the TIMER closed it (drives the on-screen notice, UC-6 step 8)
    already_final: bool  # True when it was closed earlier (e.g. the student pressed Submit a moment before)
    submitted_at: datetime | None
    message: str


class SweepResponse(BaseModel):
    auto_submitted: int
