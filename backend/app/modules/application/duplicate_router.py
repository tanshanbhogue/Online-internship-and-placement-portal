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