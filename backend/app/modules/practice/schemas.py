# ==============================================================================
# FILE   : backend/app/modules/practice/schemas.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Pydantic models for practice endpoints.
#
# EXPOSES
#   StartSessionRequest: category_id, count (optional 1..50)
#   SessionStartResponse: session_id, category {id,name}, total_questions, questions: list[QuestionPublic] (from question_bank.schemas; NO answers)
#   AnswerRequest: question_id, selected_option_id (mcq) OR code (coding, <= 20000 chars); exactly one of the two
#   AnswerFeedback: question_id, is_correct (bool | null when pending), evaluation_status, correct_option_id (mcq only), explanation   <- allowed ONLY after that question is answered (use case step 7)
#   BreakdownItem: question_id, prompt, selected_option_id, correct_option_id, is_correct, explanation
#   SessionResult: session_id, category, status, total_questions, answered_count, correct_count, score_percent, completed_at, breakdown
#   HistoryItem: session_id, category_name, correct_count, total_questions, score_percent, completed_at ; HistoryResponse: items
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
