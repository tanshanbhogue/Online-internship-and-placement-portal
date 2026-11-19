# Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
# File: backend/scripts/seed_mock_tests.py
#
# Creates three demo tests from the questions that scripts/seed_questions.py already loaded (run that first):
#   Full Aptitude Mock - 30 min      Technical MCQ Mock - 20 min      Quick Check - 1 min (for auto-submit demos, UT_14)
# Idempotent: a test whose title already exists is left alone. Admin screens for tests are not part of Sprint 2.
import sys

from sqlalchemy import select

from app.core.database import SessionLocal, init_db
from app.modules.mock_test.models import MockTest, MockTestQuestion
from app.modules.question_bank.models import Category, Question, QuestionType

# (title, category name, minutes, max questions, description)
TESTS = [
    ("Full Aptitude Mock - 30 min", "Aptitude", 30, 10, "Ten aptitude questions in thirty minutes."),
    ("Technical MCQ Mock - 20 min", "Technical MCQ", 20, 10, "Ten technical multiple-choice questions in twenty minutes."),
    ("Quick Check - 1 min", "Aptitude", 1, 5, "A very short test, handy for seeing the automatic submission."),
]


def main() -> int:
    init_db()
    created = 0
    with SessionLocal() as db:
        for title, category_name, minutes, limit, description in TESTS:
            if db.scalar(select(MockTest.id).where(MockTest.title == title)) is not None:
                continue
            category = db.scalar(select(Category).where(Category.name == category_name))
            if category is None:
                print(f"Category '{category_name}' not found: run `python -m scripts.seed_questions` first.")
                return 1
            question_ids = db.scalars(
                select(Question.id)
                .where(Question.category_id == category.id, Question.is_active.is_(True), Question.type == QuestionType.MCQ)
                .order_by(Question.id)
                .limit(limit)
            ).all()
            if not question_ids:
                print(f"No MCQ questions in '{category_name}': skipped '{title}'.")
                continue
            test = MockTest(title=title, description=description, category_id=category.id, duration_minutes=minutes)
            test.test_questions = [MockTestQuestion(question_id=qid, position=i) for i, qid in enumerate(question_ids)]
            db.add(test)
            created += 1
        db.commit()
    print(f"Mock tests: {created} created.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
