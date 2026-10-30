# Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
# File: backend/app/modules/mock_test/auto_submit_router.py
#
# Contract
#   POST /api/mock-attempts/{attempt_id}/auto-submit     student; called by the browser when its countdown hits 0.
#        The server does NOT trust the browser: 409 code=not_expired while its own clock says time remains.
#        Idempotent: if the attempt is already closed it answers 200 with already_final=true (no duplicate).
#        Someone else's attempt is indistinguishable from a missing one -> 404 (SEC-06).
#   POST /api/admin/mock-attempts/sweep                  admin only (SEC-07); same job as scripts/sweep_expired_attempts.py
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin, get_current_student
from app.core.errors import Conflict, NotFound
from app.modules.auth.models import User
from app.modules.mock_test.auto_submit_schemas import AutoSubmitResponse, SweepResponse
from app.modules.mock_test.finalize import auto_submit_if_expired, sweep_expired
from app.modules.mock_test.models import AttemptStatus, MockAttempt
from app.modules.mock_test.timing import is_expired

router = APIRouter(prefix="/api", tags=["mock-test-auto-submit"])


@router.post("/mock-attempts/{attempt_id}/auto-submit", response_model=AutoSubmitResponse)
def auto_submit(attempt_id: int, student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    attempt = db.scalar(
        select(MockAttempt)
        .where(MockAttempt.id == attempt_id, MockAttempt.student_id == student.id)
        .execution_options(populate_existing=True)
    )
    if attempt is None:
        raise NotFound("Attempt not found")
    if attempt.status == AttemptStatus.IN_PROGRESS and not is_expired(attempt):
        raise Conflict("The time limit has not expired yet", code="not_expired")

    attempt, transitioned = auto_submit_if_expired(db, attempt.id, source="client")
    auto = attempt.status == AttemptStatus.AUTO_SUBMITTED
    return AutoSubmitResponse(
        attempt_id=attempt.id,
        status=attempt.status.value,
        auto_submitted=auto,
        already_final=not transitioned,
        submitted_at=attempt.submitted_at,
        message=(
            "Time is up. Your test was submitted automatically."
            if auto
            else "Your test had already been submitted."
        ),
    )


@router.post("/admin/mock-attempts/sweep", response_model=SweepResponse)
def sweep(_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return SweepResponse(auto_submitted=sweep_expired(db))
