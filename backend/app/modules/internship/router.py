# ==============================================================================
# FILE   : backend/app/modules/internship/router.py
# STORY  : #15 Browse Internship Listings  [FR-002; SEC-09, SEC-10]
# OWNER  : Tanmayi (@tanshanbhogue)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   HTTP endpoints for browsing listings.
#
# ROUTES
#   router = APIRouter(prefix="/api/internships", tags=["internships"])
#   GET /api/internships          Depends(get_current_user)  query InternshipFilters -> 200 InternshipListResponse (empty list is a normal 200, the UI shows the message)
#   GET /api/internships/{id}     Depends(get_current_user)  -> 200 InternshipDetail ; 404 not_found if missing or not ACTIVE
#
# RULES
#   Authentication required (SEC-01). Free-text fields are returned as plain strings; the React side escapes them (SEC-10). Out of scope: bookmarks, admin create/edit.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
