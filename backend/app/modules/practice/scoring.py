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
