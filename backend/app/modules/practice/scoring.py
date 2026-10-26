# ==============================================================================
# FILE   : backend/app/modules/practice/scoring.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   PURE scoring logic with no database or HTTP code, so it is trivially unit-testable (acceptance: 'scored result', FR-003).
#
# EXPOSES
#   @dataclass ScoreSummary: total_questions, answered, correct, pending, percent (float | None)
#   score_session(total_questions: int, results: list[AnswerResult]) -> ScoreSummary
#       AnswerResult = (is_correct: bool | None, evaluation_status)
#       correct = count True ; pending = count of PENDING (coding not executed) ; scorable = total_questions - pending
#       percent = round(correct / scorable * 100, 2), or None when scorable == 0. Unanswered questions count as not correct.
#   Document the rounding rule in the docstring and keep it identical in the frontend display.
#
# TESTS
#   test_practice_scoring.py, UT_11 (5 MCQ answers, mixed correct/incorrect -> exact count and percent).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
