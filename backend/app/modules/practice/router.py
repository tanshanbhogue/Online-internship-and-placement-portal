# ==============================================================================
# FILE   : backend/app/modules/practice/router.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   HTTP endpoints for practice sessions.
#
# ROUTES
#   router = APIRouter(prefix="/api/practice", tags=["practice"]) ; every route Depends(get_current_student)
#   POST /api/practice/sessions                      StartSessionRequest -> 201 SessionStartResponse ; 404 no_questions
#   POST /api/practice/sessions/{id}/answers         AnswerRequest -> 200 AnswerFeedback ; 404 other student's session ; 409 already answered / finished
#   POST /api/practice/sessions/{id}/finish          -> 200 SessionResult (partial sessions allowed, unanswered count as not correct)
#   GET  /api/practice/sessions/{id}                 -> 200 SessionResult (completed only)
#   GET  /api/practice/history                       -> 200 HistoryResponse
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
