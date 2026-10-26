# ==============================================================================
# FILE   : backend/app/modules/question_bank/models.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   SQLAlchemy models for the categorized question bank (Question Bank Service component).
#
# EXPOSES
#   class QuestionType(str, enum.Enum): MCQ="mcq", CODING="coding"
#   class Difficulty(str, enum.Enum): EASY="easy", MEDIUM="medium", HARD="hard"
#   Category: id PK ; name str(60) unique ; slug str(60) unique ; created_at          (seeded: Aptitude, Technical MCQ, Coding)
#   Question: id PK ; category_id FK categories.id (indexed) ; type QuestionType ; prompt text ; difficulty Difficulty ; explanation text null ;
#             starter_code text null (coding) ; test_cases text null (coding, JSON string, NEVER sent to students) ; is_active bool default True ; created_at, updated_at
#   QuestionOption: id PK ; question_id FK questions.id ondelete cascade ; text str(500) ; is_correct bool ; position int
#
# RULES
#   Deleting a question is a soft delete (is_active False) so practice history keeps working. MCQ: 2..6 options and exactly one correct. Coding: no options.
#
# USED BY
#   practice/models.py (#22) has FKs to questions and categories.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
