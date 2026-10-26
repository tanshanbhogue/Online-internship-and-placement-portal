# ==============================================================================
# FILE   : backend/app/modules/question_bank/admin_router.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Admin-only endpoints to manage categories and questions (use case 'Manage Categorized Question Bank').
#
# ROUTES
#   router = APIRouter(prefix="/api/admin/question-bank", tags=["admin-question-bank"]) ; every route Depends(get_current_admin) (SEC-07)
#   GET    /categories -> list[CategoryOut]          POST /categories (CategoryCreate) -> 201 CategoryOut (duplicate name -> 409 conflict)
#   GET    /questions?category_id=&page=&page_size= -> paginated list[QuestionAdminOut]
#   POST   /questions (QuestionCreate) -> 201 QuestionAdminOut          GET /questions/{id} -> QuestionAdminOut
#   PUT    /questions/{id} (QuestionUpdate) -> QuestionAdminOut         DELETE /questions/{id} -> 204 (soft delete)
#   Incomplete data (e.g. no correct option) -> 422 with field errors (use case A1).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
