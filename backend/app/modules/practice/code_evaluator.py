from dataclasses import dataclass
from typing import Protocol

from app.modules.practice.models import EvaluationStatus


@dataclass(frozen=True)
class EvaluationResult:
    is_correct: bool | None
    status: EvaluationStatus


class CodeEvaluator(Protocol):
    def evaluate(self, question, code: str) -> EvaluationResult: ...


class PendingCodeEvaluator:
    """Safe placeholder: the answer is stored and left pending.

    It must NEVER execute, import, compile or eval the submitted code. The real sandbox (SEC-17) is a later story.
    """

    def evaluate(self, question, code: str) -> EvaluationResult:
        return EvaluationResult(is_correct=None, status=EvaluationStatus.PENDING)


def get_code_evaluator() -> CodeEvaluator:
    return PendingCodeEvaluator()
