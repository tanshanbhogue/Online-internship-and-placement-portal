# ==============================================================================
# FILE   : backend/app/modules/application/router.py
# STORY  : #17 Apply for an Internship  [FR-002; SEC-15, SEC-16, SEC-18]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 6
# ==============================================================================
#
# PURPOSE
#   HTTP endpoints for submitting and viewing applications.
#
# ROUTES
#   router = APIRouter(prefix="/api/applications", tags=["applications"])
#   POST /api/applications   Depends(get_current_student)  multipart: internship_id (int Form), cover_note (Form, optional), resume (UploadFile) -> 201 ApplicationOut
#         errors: 404 not_found, 409 application_window_closed, 409 already_applied, 422 validation_error / invalid_file
#   GET  /api/applications/mine   Depends(get_current_student) -> 200 ApplicationListResponse (only the caller's rows; IT_04, IT_06)
#   Route order note: declare /mine before any /{id} style route. /check/{id} lives in duplicate_router.py (story #18)
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_student
from app.modules.application import service
from app.modules.application.schemas import ApplicationListResponse, ApplicationOut
from app.modules.auth.models import User

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(
    internship_id: int = Form(...),
    cover_note: str | None = Form(default=None),
    # Optional at the framework level so a missing resume yields OUR field-level message, after the listing checks.
    resume: UploadFile | None = File(default=None),
    student: User = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return service.apply(db, student, internship_id, cover_note, resume)


# /mine is declared before any /{id} style route.
@router.get("/mine", response_model=ApplicationListResponse)
def my_applications(student: User = Depends(get_current_student), db: Session = Depends(get_db)):
    return ApplicationListResponse(items=[ApplicationOut.model_validate(a) for a in service.list_for_student(db, student.id)])
