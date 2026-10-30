# Story #24 Automatic Test Submission - owner: Eshwar (ESHWAR1024)
# File: backend/app/modules/mock_test/models.py
#
# Owns EVERY table of the mock-test domain (like story #18 owned application/models.py), so the later stories
# (#23 take a test, #25 results, #26/#27 analytics) only import from here and never edit it.
#
# Contract
#   MockTest             a test definition: title, category, duration_minutes, fixed MCQ question set
#   MockAttempt          one student's try. started_at/ends_at are SERVER times (SEC-13); status is
#                        in_progress -> submitted | auto_submitted and never goes back (SEC-14)
#   MockAttemptQuestion  the FIXED question set of one attempt (a later edit of the test cannot change it)
#   MockAttemptAnswer    the student's saved choice; is_correct stays NULL until the attempt is finalized (SEC-12)
#   AutoSubmitEvent      audit row for every attempt closed by the timer (UC-6 step 10, SEC-20)
# Tests: tests/test_mock_auto_submit.py
import enum
from datetime import datetime

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UTCDateTime, utcnow
from app.modules.auth.models import User  # noqa: F401  (FK target must be registered)
from app.modules.question_bank.models import Category, Question


def _enum(cls, length: int = 20):
    return Enum(cls, values_callable=lambda e: [m.value for m in e], native_enum=False, length=length, validate_strings=True)


class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"  # the student pressed Submit before the time ran out
    AUTO_SUBMITTED = "auto_submitted"  # closed by the timer (UC-6)


class MockTest(Base):
    __tablename__ = "mock_tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)

    category: Mapped[Category] = relationship(lazy="joined")
    test_questions: Mapped[list["MockTestQuestion"]] = relationship(
        back_populates="test", cascade="all, delete-orphan", order_by="MockTestQuestion.position"
    )


class MockTestQuestion(Base):
    __tablename__ = "mock_test_questions"
    __table_args__ = (UniqueConstraint("test_id", "question_id", name="uq_mock_test_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("mock_tests.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False, default=0)

    test: Mapped[MockTest] = relationship(back_populates="test_questions")
    question: Mapped[Question] = relationship(lazy="joined")


class MockAttempt(Base):
    __tablename__ = "mock_attempts"
    __table_args__ = (
        # Database backstop: a student can have only ONE open attempt per test (double-click / two tabs).
        Index(
            "uq_mock_attempt_one_open",
            "student_id",
            "test_id",
            unique=True,
            sqlite_where=text("status = 'in_progress'"),
            postgresql_where=text("status = 'in_progress'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("mock_tests.id"), index=True, nullable=False)
    status: Mapped[AttemptStatus] = mapped_column(_enum(AttemptStatus), nullable=False, default=AttemptStatus.IN_PROGRESS)
    started_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    # started_at + the test duration, fixed when the attempt starts: this is the ONLY clock that counts (SEC-13).
    ends_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    # Manual submit: the moment of submission. Auto-submit: ends_at (UC-6 step 6).
    submitted_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    total_questions: Mapped[int] = mapped_column(nullable=False)
    answered_count: Mapped[int] = mapped_column(nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(nullable=False, default=0)
    score_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    test: Mapped[MockTest] = relationship(lazy="joined")
    attempt_questions: Mapped[list["MockAttemptQuestion"]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan", order_by="MockAttemptQuestion.position"
    )
    answers: Mapped[list["MockAttemptAnswer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class MockAttemptQuestion(Base):
    __tablename__ = "mock_attempt_questions"
    __table_args__ = (UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("mock_attempts.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)

    attempt: Mapped[MockAttempt] = relationship(back_populates="attempt_questions")
    question: Mapped[Question] = relationship(lazy="joined")


class MockAttemptAnswer(Base):
    __tablename__ = "mock_attempt_answers"
    __table_args__ = (UniqueConstraint("attempt_id", "question_id", name="uq_attempt_answer"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("mock_attempts.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    selected_option_id: Mapped[int] = mapped_column(nullable=False)
    is_correct: Mapped[bool | None] = mapped_column(nullable=True)  # NULL until the attempt is finalized
    answered_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow)

    attempt: Mapped[MockAttempt] = relationship(back_populates="answers")


class AutoSubmitEvent(Base):
    """One row per attempt closed by the timer. `source` says who noticed: client, lazy (a read) or sweeper."""

    __tablename__ = "mock_auto_submit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("mock_attempts.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)  # the attempt's ends_at
    recorded_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
