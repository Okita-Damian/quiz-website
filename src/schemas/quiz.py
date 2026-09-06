
from pydantic import BaseModel, Field


# -------------------------
# Create Quiz
# -------------------------

class QuizCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    topic_id: str

    question_ids: list[str] = Field(
        ...,
        min_length=1,
    )


# -------------------------
# Update Quiz
# -------------------------

class QuizUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    question_ids: list[str] | None = Field(
        default=None,
        min_length=1,
    )


# -------------------------
# Quiz Response
# -------------------------

class QuizResponse(BaseModel):
    id: str

    title: str

    topic_id: str

    question_ids: list[str]

    created_by: str | None = None
