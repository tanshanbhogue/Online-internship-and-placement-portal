from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import Conflict, NotFound
from app.modules.auth.models import User
from app.modules.mock_result.schemas import (
    BreakdownItem,
    DifficultyStat,
    HistoryItem,
    HistoryResponse,
    OptionView,
    ResultDetail,
    TestRef,
)
from app.modules.mock_test.finalize import auto_submit_if_expired
from app.modules.mock_test.models import AttemptStatus, MockAttempt, MockAttemptAnswer, MockAttemptQuestion
from app.modules.question_bank import service as question_bank
from app.modules.question_bank.models import Question

MIN_PERCENTILE_SAMPLE = 5
DIFFICULTIES = ("easy", "medium", "hard")


def _seconds(attempt: MockAttempt) -> int:
    if attempt.submitted_at is None:
        return 0
    return max(0, int((attempt.submitted_at - attempt.started_at).total_seconds()))


def _closed_attempt(db: Session, student: User, attempt_id: int) -> MockAttempt:
    attempt = db.scalar(
        select(MockAttempt)
        .where(MockAttempt.id == attempt_id, MockAttempt.student_id == student.id)
        .options(selectinload(MockAttempt.attempt_questions).selectinload(MockAttemptQuestion.question).selectinload(Question.options))
        .execution_options(populate_existing=True)
    )
    if attempt is None:
        raise NotFound("Result not found")
    if attempt.status == AttemptStatus.IN_PROGRESS:
        attempt, _ = auto_submit_if_expired(db, attempt.id, source="lazy")
        if attempt.status == AttemptStatus.IN_PROGRESS:
            raise Conflict("This test is still in progress", code="attempt_in_progress")
    return attempt


def _percentile(db: Session, attempt: MockAttempt) -> int | None:
    if attempt.score_percent is None:
        return None
    others = (MockAttempt.test_id == attempt.test_id, MockAttempt.student_id != attempt.student_id,
              MockAttempt.status != AttemptStatus.IN_PROGRESS, MockAttempt.score_percent.is_not(None))
    total = db.scalar(select(func.count(MockAttempt.id)).where(*others)) or 0
    if total < MIN_PERCENTILE_SAMPLE:
        return None
    lower = db.scalar(select(func.count(MockAttempt.id)).where(*others, MockAttempt.score_percent < attempt.score_percent)) or 0
    return round(lower * 100 / total)


def get_result(db: Session, student: User, attempt_id: int, difficulty: str | None = None, outcome: str | None = None) -> ResultDetail:
    attempt = _closed_attempt(db, student, attempt_id)
    answers = {a.question_id: a for a in db.scalars(select(MockAttemptAnswer).where(MockAttemptAnswer.attempt_id == attempt.id)).all()}
    keys = question_bank.get_answer_key(db, [aq.question_id for aq in attempt.attempt_questions])

    items: list[BreakdownItem] = []
    stats = {d: [0, 0] for d in DIFFICULTIES}  # difficulty -> [total, correct]
    for aq in attempt.attempt_questions:
        q, answer, key = aq.question, answers.get(aq.question_id), keys.get(aq.question_id)
        result = "skipped" if answer is None else ("correct" if answer.is_correct else "incorrect")
        stats[q.difficulty.value][0] += 1
        stats[q.difficulty.value][1] += 1 if result == "correct" else 0
        items.append(
            BreakdownItem(
                position=aq.position + 1,
                question_id=q.id,
                prompt=q.prompt,
                difficulty=q.difficulty.value,
                category_name=attempt.test.category.name,
                options=[OptionView(id=o.id, text=o.text) for o in q.options],
                selected_option_id=answer.selected_option_id if answer else None,
                correct_option_id=min(key.correct_option_ids) if key and key.correct_option_ids else None,
                outcome=result,
                explanation=key.explanation if key else None,
            )
        )

    shown = [i for i in items if (difficulty is None or i.difficulty == difficulty) and (outcome is None or i.outcome == outcome)]
    answered = attempt.answered_count
    return ResultDetail(
        attempt_id=attempt.id,
        test=TestRef(id=attempt.test.id, title=attempt.test.title),
        category_name=attempt.test.category.name,
        status=attempt.status.value,
        auto_submitted=attempt.status == AttemptStatus.AUTO_SUBMITTED,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        time_taken_seconds=_seconds(attempt),
        time_limit_seconds=attempt.test.duration_minutes * 60,
        total_questions=attempt.total_questions,
        answered_count=answered,
        correct_count=attempt.correct_count,
        incorrect_count=answered - attempt.correct_count,
        skipped_count=attempt.total_questions - answered,
        score_percent=attempt.score_percent,
        accuracy_percent=round(attempt.correct_count / answered * 100, 2) if answered else None,
        percentile=_percentile(db, attempt),
        by_difficulty=[DifficultyStat(difficulty=d, total=t, correct=c) for d, (t, c) in stats.items() if t],
        breakdown=shown,
        filtered_count=len(shown),
    )


def list_history(db: Session, student: User, limit: int = 100) -> HistoryResponse:
    rows = db.scalars(
        select(MockAttempt)
        .where(MockAttempt.student_id == student.id, MockAttempt.status != AttemptStatus.IN_PROGRESS)
        .order_by(MockAttempt.submitted_at.desc(), MockAttempt.id.desc())
        .limit(limit)
    ).unique().all()
    return HistoryResponse(
        items=[
            HistoryItem(
                attempt_id=a.id,
                test_title=a.test.title,
                category_name=a.test.category.name,
                status=a.status.value,
                score_percent=a.score_percent,
                correct_count=a.correct_count,
                total_questions=a.total_questions,
                submitted_at=a.submitted_at,
                time_taken_seconds=_seconds(a),
            )
            for a in rows
        ]
    )
