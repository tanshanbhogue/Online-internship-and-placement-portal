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
