

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
