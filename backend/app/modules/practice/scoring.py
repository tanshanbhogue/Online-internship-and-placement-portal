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

from dataclasses import dataclass
from typing import NamedTuple


class AnswerResult(NamedTuple):
    """One submitted answer. `evaluation_status` may be an EvaluationStatus or its string value."""

    is_correct: bool | None
    evaluation_status: object


@dataclass(frozen=True)
class ScoreSummary:
    total_questions: int
    answered: int
    correct: int
    pending: int
    percent: float | None


def _is_pending(status: object) -> bool:
    return getattr(status, "value", status) == "pending"


def score_session(total_questions: int, results: list[AnswerResult]) -> ScoreSummary:
    """Pure scoring (no I/O).

    correct  = answers whose is_correct is True
    pending  = answers still awaiting evaluation (coding answers are stored, never executed)
    scorable = total_questions - pending           (pending questions are excluded from the denominator)
    percent  = round(correct / scorable * 100, 2)  (standard round-half-even to 2 decimals), or None when scorable <= 0
    Unanswered questions stay in `scorable`, so they count as not correct.

    The frontend shows score_percent exactly as returned (no re-rounding); keep any display code identical to this rule.
    """
    results = [AnswerResult(*r) for r in results]
    correct = sum(1 for r in results if r.is_correct is True)
    pending = sum(1 for r in results if _is_pending(r.evaluation_status))
    scorable = total_questions - pending
    percent = round(correct / scorable * 100, 2) if scorable > 0 else None
    return ScoreSummary(total_questions=total_questions, answered=len(results), correct=correct, pending=pending, percent=percent)
