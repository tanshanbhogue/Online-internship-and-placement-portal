# ==============================================================================
# FILE   : backend/app/modules/practice/models.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   SQLAlchemy models for practice sessions, the fixed question set of a session, and the submitted answers.
#   Practice history stored here is what the later analytics stories (#26, #27) will read.
#
# EXPOSES
#   class SessionStatus(str, enum.Enum): IN_PROGRESS="in_progress", COMPLETED="completed"
#   class EvaluationStatus(str, enum.Enum): EVALUATED="evaluated", PENDING="pending"      (pending = coding answer not executed yet)
#   PracticeSession: id PK ; student_id FK users.id (indexed) ; category_id FK categories.id ; status ; total_questions int ; answered_count int default 0 ; correct_count int default 0
#                    score_percent float null ; started_at, completed_at null
#   PracticeSessionQuestion: id PK ; session_id FK ; question_id FK ; position int ; UniqueConstraint(session_id, question_id)
#   PracticeAnswer: id PK ; session_id FK ; question_id FK ; selected_option_id int null ; submitted_code text null ; is_correct bool null ; evaluation_status ; answered_at
#                   UniqueConstraint(session_id, question_id) so a question is answered once per session
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
