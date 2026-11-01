# Story #29 Cross-Browser and Responsive Testing - owner: Tanmayi (tanshanbhogue)
# File: backend/scripts/seed_ui_test_data.py
#
# Prepares a DEVELOPMENT database for the browser tests: two known accounts, the question bank, the mock tests and a
# few finished attempts, so every screen (dashboard, history, results) has something to show on every browser/device.
# Idempotent. Run from backend/:   python -m scripts.seed_ui_test_data
# Accounts (development only, never use these passwords anywhere real):
#   student  ui.student@example.com / Student@123        admin  ui.admin@example.com / Admin@12345
import sys
from datetime import timedelta

from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.db.base import utcnow
from app.modules.auth.models import Role, User
from app.modules.mock_test.finalize import finalize_attempt
from app.modules.mock_test.models import MockAttempt, MockAttemptAnswer, MockAttemptQuestion, MockTest
from app.modules.practice.models import PracticeSession, SessionStatus
from app.modules.question_bank.models import Category, QuestionOption
from scripts import seed_mock_tests, seed_questions

STUDENT = ("UI Student", "ui.student@example.com", "Student@123")
ADMIN = ("UI Admin", "ui.admin@example.com", "Admin@12345")


def _user(db, name, email, password, role):
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(name=name, email=email, password_hash=hash_password(password), role=role)
        db.add(user)
        db.commit()
    return user


def main() -> int:
    if settings.APP_ENV.lower() != "development":
        print("Refusing to create demo accounts outside APP_ENV=development.")
        return 1
    init_db()
    seed_questions.main()
    seed_mock_tests.main()
    with SessionLocal() as db:
        student = _user(db, *STUDENT, Role.STUDENT)
        _user(db, *ADMIN, Role.ADMIN)

        if db.scalar(select(PracticeSession.id).where(PracticeSession.student_id == student.id)) is None:
            now = utcnow()
            aptitude = db.scalar(select(Category).where(Category.name == "Aptitude"))
            technical = db.scalar(select(Category).where(Category.name == "Technical MCQ"))
            for days_ago, category, score in ((6, aptitude, 40.0), (4, technical, 60.0), (2, aptitude, 70.0), (1, technical, 85.0)):
                at = now - timedelta(days=days_ago)
                db.add(PracticeSession(student_id=student.id, category_id=category.id, status=SessionStatus.COMPLETED, total_questions=10,
                                       answered_count=10, correct_count=int(score / 10), score_percent=score,
                                       started_at=at - timedelta(minutes=8), completed_at=at))
            db.commit()

            test = db.scalar(select(MockTest).where(MockTest.title == "Full Aptitude Mock - 30 min"))
            if test is not None:
                started = now - timedelta(days=3)
                attempt = MockAttempt(student_id=student.id, test_id=test.id, started_at=started, ends_at=started + timedelta(minutes=30),
                                      total_questions=len(test.test_questions))
                attempt.attempt_questions = [MockAttemptQuestion(question_id=tq.question_id, position=i) for i, tq in enumerate(test.test_questions)]
                for tq in test.test_questions[:6]:
                    correct = db.scalar(select(QuestionOption.id).where(QuestionOption.question_id == tq.question_id, QuestionOption.is_correct.is_(True)))
                    attempt.answers.append(MockAttemptAnswer(question_id=tq.question_id, selected_option_id=correct))
                db.add(attempt)
                db.commit()
                finalize_attempt(db, attempt.id, auto=True, source="sweeper")  # expired long ago, so it closes as auto-submitted
    print("UI test data ready: ui.student@example.com / Student@123 and ui.admin@example.com / Admin@12345")
    return 0


if __name__ == "__main__":
    sys.exit(main())
