# NFR-001 performance run - dummy data for a throw-away database
# File: backend/perf/seed_nfr01.py
#
# Called by run_nfr01.py in a child process whose environment already points DATABASE_URL at a temp database.
# Creates: the question bank, the demo mock tests, the demo internships, `iterations` extra open "Perf Intern N" listings
# (so every virtual user can apply to a different listing every time), one admin, and `users` dummy students who each
# already have some practice and mock-test history (the "seeded history" of case PT-N01_07).
from datetime import timedelta

from sqlalchemy import select


def seed(users: int, iterations: int, password: str, admin_email: str, admin_password: str) -> None:
    from app.core.database import SessionLocal, init_db
    from app.core.security import hash_password
    from app.db.base import utcnow
    from app.modules.auth.models import Role, User
    from app.modules.internship.models import Internship, ListingStatus
    from app.modules.mock_test.finalize import finalize_attempt
    from app.modules.mock_test.models import MockAttempt, MockAttemptAnswer, MockAttemptQuestion, MockTest
    from app.modules.practice.models import PracticeSession, SessionStatus
    from app.modules.question_bank.models import Category, QuestionOption
    from scripts import seed_internships, seed_mock_tests, seed_questions

    init_db()
    seed_questions.main()
    seed_mock_tests.main()
    seed_internships.main()

    with SessionLocal() as db:
        today = utcnow().date()
        for n in range(iterations):
            db.add(Internship(title=f"Perf Intern {n + 1}", company="Perf Corp", domain="Backend", location="Remote", stipend_per_month=20000,
                              duration_months=3, deadline=today + timedelta(days=60), status=ListingStatus.ACTIVE,
                              description="Dummy listing created for the NFR-001 performance run.", eligibility="Anyone (dummy data)."))
        db.add(User(name="Perf Admin", email=admin_email, password_hash=hash_password(admin_password), role=Role.ADMIN))
        students = []
        for i in range(users):
            student = User(name=f"Perf Student {i}", email=f"perf.student{i}@example.com", password_hash=hash_password(password), role=Role.STUDENT)
            db.add(student)
            students.append(student)
        db.commit()

        categories = [db.scalar(select(Category).where(Category.name == n)) for n in ("Aptitude", "Technical MCQ")]
        test = db.scalar(select(MockTest).where(MockTest.title == "Full Aptitude Mock - 30 min"))
        now = utcnow()
        for student in students:
            for k in range(10):  # practice history
                at = now - timedelta(days=k + 1)
                score = 40.0 + (k * 7) % 55
                db.add(PracticeSession(student_id=student.id, category_id=categories[k % 2].id, status=SessionStatus.COMPLETED, total_questions=10,
                                       answered_count=10, correct_count=int(score / 10), score_percent=score,
                                       started_at=at - timedelta(minutes=8), completed_at=at))
            db.commit()
            for k in range(8):  # finished mock tests
                started = now - timedelta(days=k + 1, hours=1)
                attempt = MockAttempt(student_id=student.id, test_id=test.id, started_at=started, ends_at=started + timedelta(minutes=30),
                                      total_questions=len(test.test_questions))
                attempt.attempt_questions = [MockAttemptQuestion(question_id=tq.question_id, position=p) for p, tq in enumerate(test.test_questions)]
                for tq in test.test_questions[: 3 + k % 5]:
                    correct = db.scalar(select(QuestionOption.id).where(QuestionOption.question_id == tq.question_id, QuestionOption.is_correct.is_(True)))
                    attempt.answers.append(MockAttemptAnswer(question_id=tq.question_id, selected_option_id=correct))
                db.add(attempt)
                db.commit()
                finalize_attempt(db, attempt.id, auto=True, source="sweeper")
