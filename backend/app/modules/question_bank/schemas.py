import json
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationInfo, field_validator

from app.modules.question_bank.models import Difficulty, QuestionType

_Text = Annotated[str, StringConstraints(strip_whitespace=True)]


# ----------------------------------------------------------------------------- student shapes (NO answers, SEC-12)
class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    name: str
    slug: str
    question_count: int


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]


class OptionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    text: str  # deliberately NO is_correct


class QuestionPublic(BaseModel):
    """The only question shape students ever receive. Do not add answer-related fields here."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    category_id: int
    type: QuestionType
    prompt: str
    difficulty: Difficulty
    options: list[OptionPublic]
    starter_code: str | None = None


class PublicQuestionList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[QuestionPublic]
    total: int


# ----------------------------------------------------------------------------- admin shapes
class OptionAdmin(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    text: str
    is_correct: bool
    position: int


class QuestionAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    category_id: int
    type: QuestionType
    prompt: str
    difficulty: Difficulty
    explanation: str | None = None
    starter_code: str | None = None
    test_cases: str | None = None
    is_active: bool
    options: list[OptionAdmin]


class AdminQuestionPage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[QuestionAdminOut]
    total: int
    page: int
    page_size: int


class OptionIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    is_correct: bool = False


def _check_options(options: list[OptionIn] | None, question_type: QuestionType | None) -> list[OptionIn]:
    options = options or []
    if question_type == QuestionType.CODING:
        if options:
            raise ValueError("Coding questions must not have options")
    elif question_type == QuestionType.MCQ:
        if not 2 <= len(options) <= 6:
            raise ValueError("A multiple-choice question needs between 2 and 6 options")
        if sum(1 for o in options if o.is_correct) != 1:
            raise ValueError("Exactly one option must be marked correct")
    return options


def _check_test_cases(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    try:
        json.loads(value)
    except ValueError:
        raise ValueError("Test cases must be valid JSON")
    return value


class QuestionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category_id: int
    type: QuestionType
    prompt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)]
    difficulty: Difficulty
    explanation: str | None = None
    # validate_default makes the rule fire when `options` is omitted for an MCQ.
    options: list[OptionIn] = Field(default_factory=list, validate_default=True)
    starter_code: str | None = None
    test_cases: str | None = None

    @field_validator("options")
    @classmethod
    def _options_match_type(cls, value, info: ValidationInfo):
        return _check_options(value, info.data.get("type"))

    @field_validator("test_cases")
    @classmethod
    def _test_cases_json(cls, value):
        return _check_test_cases(value)


class QuestionUpdate(BaseModel):
    """Every field optional. The service merges this onto the stored question and re-validates the result."""

    model_config = ConfigDict(extra="forbid")

    category_id: int | None = None
    type: QuestionType | None = None
    prompt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)] | None = None
    difficulty: Difficulty | None = None
    explanation: str | None = None
    options: list[OptionIn] | None = None
    starter_code: str | None = None
    test_cases: str | None = None
