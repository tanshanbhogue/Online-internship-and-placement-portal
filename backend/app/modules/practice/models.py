import enum
from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UTCDateTime, utcnow
from app.modules.auth.models import User  # noqa: F401  (FK targets must be registered)
from app.modules.question_bank.models import Category, Question


def _enum(cls):
    return Enum(cls, values_callable=lambda e: [m.value for m in e], native_enum=False, length=20, validate_strings=True)


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class EvaluationStatus(str, enum.Enum):
    EVALUATED = "evaluated"
    PENDING = "pending"  # coding answer stored but not executed yet


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(_enum(SessionStatus), nullable=False, default=SessionStatus.IN_PROGRESS)
    total_questions: Mapped[int] = mapped_column(nullable=False)
    answered_count: Mapped[int] = mapped_column(nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(nullable=False, default=0)
    score_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)

    category: Mapped[Category] = relationship(lazy="joined")
    session_questions: Mapped[list["PracticeSessionQuestion"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="PracticeSessionQuestion.position"
    )
    answers: Mapped[list["PracticeAnswer"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class PracticeSessionQuestion(Base):
    """The FIXED question set of one session."""

    __tablename__ = "practice_session_questions"
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_session_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("practice_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)

    session: Mapped[PracticeSession] = relationship(back_populates="session_questions")
    question: Mapped[Question] = relationship(lazy="joined")


class PracticeAnswer(Base):
    __tablename__ = "practice_answers"
    # A question can be answered only once per session.
    __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_answer_session_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("practice_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    selected_option_id: Mapped[int | None] = mapped_column(nullable=True)
    submitted_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(nullable=True)
    evaluation_status: Mapped[EvaluationStatus] = mapped_column(_enum(EvaluationStatus), nullable=False)
    answered_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)

    session: Mapped[PracticeSession] = relationship(back_populates="answers")
