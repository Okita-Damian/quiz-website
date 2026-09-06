
from pydantic import BaseModel, Field


# -------------------------
# Generated Question
# -------------------------

class GeneratedQuestion(BaseModel):
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

    image_prompt: str | None = Field(
        default=None,
        max_length=1000,
    )


# -------------------------
# Generated Questions
# -------------------------

class GeneratedQuestions(BaseModel):
    questions: list[GeneratedQuestion] = Field(
        ...,
        min_length=1,
        max_length=20,
    )


# -------------------------
# AI Generation Request
# -------------------------

class AIGenerateQuestion(BaseModel):
    topic_id: str

    number_of_questions: int = Field(
        default=5,
        ge=1,
        le=20,
    )
