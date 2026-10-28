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
