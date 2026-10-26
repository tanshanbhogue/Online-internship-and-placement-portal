# ==============================================================================
# FILE   : backend/app/modules/application/duplicate_router.py
# STORY  : #18 Prevent Duplicate Internship Applications  [FR-002; SEC-15]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Endpoint the UI uses to know whether to show 'Apply' or 'Already applied'.
#
# ROUTE
#   router = APIRouter(prefix="/api/applications", tags=["applications"])
#   GET /api/applications/check/{internship_id}  Depends(get_current_student) -> 200 ApplicationCheckResponse ; 404 not_found if the listing does not exist (use internship.service.get_listing).
#   Only reports on the CALLING student's own record (SEC-06).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.modules.application.duplicate_check import get_existing
from app.modules.application.duplicate_schemas import ApplicationCheckResponse
from app.modules.auth.models import User
from app.modules.internship.service import get_listing

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("/check/{internship_id}", response_model=ApplicationCheckResponse)
def check_application(internship_id: int, student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    get_listing(db, internship_id)  # 404 not_found when the listing does not exist / is not active
    existing = get_existing(db, student.id, internship_id)  # only the CALLER's own record (SEC-06)
    if existing is None:
        return ApplicationCheckResponse(internship_id=internship_id, applied=False)
    return ApplicationCheckResponse(
        internship_id=internship_id, applied=True, status=existing.status.value, applied_at=existing.applied_at
    )
