
from enum import Enum

from pydantic import BaseModel, Field


# ============================================================
# QUESTION SOURCE
# ============================================================

class QuestionSource(str, Enum):
    TEACHER = "teacher"
    PARENT = "parent"
    LLM = "llm"


# ============================================================
# QUESTION TYPE
# ============================================================

class QuestionType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


# ============================================================
# CREATE QUESTION
# ============================================================

class QuestionCreate(BaseModel):

    question: str = Field(
        ...,
        min_length=5,
        max_length=1000,
    )

    options: list[str] = Field(
        ...,
        min_length=4,
        max_length=4,
    )

    correct_answer: str = Field(
        ...,
        min_length=1,
    )

    explanation: str | None = Field(
        default=None,
        max_length=1000,
    )

    # The grade is supplied by the client.
    grade_id: str

    # The subject is NOT supplied.
    # It is obtained from the topic.
    topic_id: str

    question_type: QuestionType = (
        QuestionType.TEXT
    )

    image_url: str | None = None


# ============================================================
# UPDATE QUESTION
# ============================================================

class QuestionUpdate(BaseModel):

    question: str | None = Field(
        default=None,
        min_length=5,
        max_length=1000,
    )

    options: list[str] | None = Field(
        default=None,
        min_length=4,
        max_length=4,
    )

    correct_answer: str | None = Field(
        default=None,
        min_length=1,
    )

    explanation: str | None = Field(
        default=None,
        max_length=1000,
    )

    # Optional because this is an update.
    grade_id: str | None = None

    # Optional because this is an update.
    # The service does not need subject_id because
    # subject is derived from topic_id.
    topic_id: str | None = None

    question_type: QuestionType | None = None

    image_url: str | None = None


# ============================================================
# QUESTION RESPONSE
# ============================================================

class QuestionResponse(BaseModel):

    id: str

    question: str

    options: list[str]

    correct_answer: str

    explanation: str | None

    grade_id: str

    subject_id: str

    topic_id: str

    question_type: QuestionType

    source: QuestionSource

    created_by: str | None = None

    image_url: str | None = None

