# ==============================================================================
# FILE   : backend/app/modules/auth/register_router.py
# STORY  : #14 Student Registration  [FR-001; SEC-02, SEC-08, SEC-09]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 2
# ==============================================================================
#
# PURPOSE
#   HTTP endpoint for student registration.
#
# ROUTE
#   router = APIRouter(prefix="/api/auth", tags=["auth"])
#   POST /api/auth/register  body RegisterRequest -> 201 RegisterResponse. No authentication required.
#   Errors: 422 validation_error (field-level messages, test UT_04), 409 duplicate_email (test IT_02).
#   Registration does NOT log the user in; the SPA redirects to /login with a success message (use case step 7).
#
# RULES
#   Thin router: parse -> call register_student -> return. No business logic here.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.register_schemas import RegisterRequest, RegisterResponse
from app.modules.auth.register_service import register_student

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return register_student(db, payload)
