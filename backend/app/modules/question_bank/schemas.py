# ==============================================================================
# FILE   : backend/app/modules/question_bank/schemas.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Pydantic models for question-bank endpoints; separates the STUDENT shape (no answers) from the ADMIN shape.
#
# EXPOSES
#   CategoryOut: id, name, slug, question_count        CategoryCreate: name (1..60)
#   OptionPublic: id, text                              (NO is_correct)
#   QuestionPublic: id, category_id, type, prompt, difficulty, options: list[OptionPublic], starter_code     <- the only shape students ever receive (SEC-12)
#   OptionAdmin: id, text, is_correct, position
#   QuestionAdminOut: all fields incl. options with is_correct, explanation, test_cases, is_active
#   QuestionCreate: category_id, type, prompt (1..5000), difficulty, explanation?, options (for mcq), starter_code?, test_cases?   model validator: mcq needs 2..6 options with exactly one correct; coding forbids options
#   QuestionUpdate: same fields, all optional, same validation after merge
#   PublicQuestionList: items, total
#
# RULES
#   model_config forbids extra fields. Student schemas must be impossible to extend with answer data by accident: keep them as separate classes.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
