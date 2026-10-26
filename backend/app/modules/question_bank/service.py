# ==============================================================================
# FILE   : backend/app/modules/question_bank/service.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Business logic for reading and administering questions. Also exposes the internal answer-key lookup used by practice scoring (#22).
#
# EXPOSES (names used by #22, do not rename)
#   list_categories(db) -> list[tuple[Category, int]]          # with count of active questions
#   list_public_questions(db, category_id, count: int, difficulty: Difficulty | None) -> tuple[list[Question], int]
#       random sample of active questions (limit count, default settings.PRACTICE_DEFAULT_QUESTION_COUNT, max 50); NotFound if category missing; EMPTY list if none (IT_07)
#   pick_questions_for_practice(db, category_id, count) -> list[Question]     # same selection used when a practice session starts
#   get_answer_key(db, question_ids: list[int]) -> dict[int, AnswerKey]
#       AnswerKey = dataclass(question_id, type, correct_option_ids: set[int], explanation) ; INTERNAL ONLY, never returned by an HTTP route
#   Admin: create_category, create_question, update_question, soft_delete_question, list_admin_questions(db, category_id, page, page_size), get_admin_question
#
# RULES
#   Validation failures raise ValidationFailed with field messages. Every admin mutation writes a security.audit log line with admin id, action and question id (SEC-20). Parameterised ORM queries only.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
