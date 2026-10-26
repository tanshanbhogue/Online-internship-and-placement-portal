# ==============================================================================
# FILE   : backend/app/modules/question_bank/models.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   SQLAlchemy models for the categorized question bank (Question Bank Service component).
#
# EXPOSES
#   class QuestionType(str, enum.Enum): MCQ="mcq", CODING="coding"
#   class Difficulty(str, enum.Enum): EASY="easy", MEDIUM="medium", HARD="hard"
#   Category: id PK ; name str(60) unique ; slug str(60) unique ; created_at          (seeded: Aptitude, Technical MCQ, Coding)
#   Question: id PK ; category_id FK categories.id (indexed) ; type QuestionType ; prompt text ; difficulty Difficulty ; explanation text null ;
#             starter_code text null (coding) ; test_cases text null (coding, JSON string, NEVER sent to students) ; is_active bool default True ; created_at, updated_at
#   QuestionOption: id PK ; question_id FK questions.id ondelete cascade ; text str(500) ; is_correct bool ; position int
#
# RULES
#   Deleting a question is a soft delete (is_active False) so practice history keeps working. MCQ: 2..6 options and exactly one correct. Coding: no options.
#
# USED BY
#   practice/models.py (#22) has FKs to questions and categories.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

import enum
from datetime import datetime

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UTCDateTime, utcnow


def _enum(cls, length: int = 20):
    return Enum(cls, values_callable=lambda e: [m.value for m in e], native_enum=False, length=length, validate_strings=True)


class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    CODING = "coding"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True, nullable=False)
    type: Mapped[QuestionType] = mapped_column(_enum(QuestionType), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(_enum(Difficulty), nullable=False, default=Difficulty.MEDIUM)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    starter_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    test_cases: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string, NEVER sent to students
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)  # soft delete flag
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow)

    options: Mapped[list["QuestionOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.position",
    )


class QuestionOption(Base):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    position: Mapped[int] = mapped_column(nullable=False, default=0)

    question: Mapped[Question] = relationship(back_populates="options")
