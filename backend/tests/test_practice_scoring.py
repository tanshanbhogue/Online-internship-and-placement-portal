# ==============================================================================
# FILE   : backend/tests/test_practice_scoring.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Tests for scoring, sessions and history.
#
# TEST CASES
#   - unit: score_session with 5 answers (e.g. 3 correct) -> correct 3, percent 60.0; zero questions; all pending -> percent None; unanswered count as wrong (UT_11)
#   - UT_11 API: start session, answer 5 MCQs (mix), finish -> result correct_count equals the number of right answers
#   - ST_05 end-to-end: category -> all questions -> submit -> result screen data shows score and category
#   - ST_06: session for Aptitude, then a new session for Technical MCQ -> second question set has only Technical MCQ questions, none carried over
#   - IT_07: empty category -> start_session returns 404 code no_questions, no crash
#   - IT_08: completed session appears in /history with date and score; in-progress sessions do not
#   - SEC-06: student B cannot answer, finish or read student A's session (404); answering twice -> 409; answering after finish -> 409
#   - SEC-12: start response and answer endpoint never expose correct options before the question is answered; result is refused until finished
#   - coding answer is stored as pending, never executed, excluded from the percent denominator
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
