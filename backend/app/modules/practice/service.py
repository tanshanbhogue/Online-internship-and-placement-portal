# ==============================================================================
# FILE   : backend/app/modules/practice/service.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Orchestration of practice sessions: start, answer, finish, result, history.
#
# EXPOSES
#   start_session(db, student, category_id, count) -> PracticeSession(+questions)
#       uses question_bank.service.pick_questions_for_practice; zero questions -> NotFound(code="no_questions", message="No questions found") (IT_07);
#       stores PracticeSessionQuestion rows (fixed set, ST_06: a new category means a NEW session with only that category's questions)
#   submit_answer(db, student, session_id, payload) -> AnswerFeedback
#       load session owned by student else NotFound (never reveal other students' sessions, SEC-06); session must be IN_PROGRESS; question must belong to the session; one answer per question (Conflict otherwise)
#       mcq: compare with question_bank.service.get_answer_key; coding: get_code_evaluator(); persist immediately (so exiting mid-session keeps progress, use case A2); update counters
#   finish_session(db, student, session_id) -> SessionResult      # idempotent; computes score via scoring.score_session, sets COMPLETED, completed_at
#   get_result(db, student, session_id) -> SessionResult         # only when COMPLETED (else Conflict 'Session not finished'); breakdown may include answers/explanations now
#   list_history(db, student) -> list[PracticeSession]           # COMPLETED only, newest first (IT_08)
#
# RULES
#   Never send answer keys before the question is answered (SEC-12). student_id always from the authenticated user. Write audit-free, no answers in logs.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
