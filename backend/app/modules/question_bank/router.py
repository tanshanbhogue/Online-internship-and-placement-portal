# ==============================================================================
# FILE   : backend/app/modules/question_bank/router.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Student-facing read endpoints for categories and questions.
#
# ROUTES
#   router = APIRouter(prefix="/api/question-bank", tags=["question-bank"])
#   GET /api/question-bank/categories                                  Depends(get_current_user) -> list[CategoryOut]
#   GET /api/question-bank/categories/{category_id}/questions?count=&difficulty=   Depends(get_current_user) -> PublicQuestionList of QuestionPublic
#         unknown category -> 404 ; category with zero questions -> 200 with items [] (UI shows 'No questions found', IT_07)
#
# RULES
#   Response models MUST be QuestionPublic so correct options, explanations and test cases cannot leak (SEC-12). Inspect the JSON in tests.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
