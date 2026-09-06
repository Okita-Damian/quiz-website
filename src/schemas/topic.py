
from pydantic import BaseModel, Field


class TopicCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    subject_id: str

    grade_id: str

    requires_image:bool = False


class TopicUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    subject_id: str | None = None

    grade_id: str | None = None

    requires_image:bool | None = None



class TopicResponse(BaseModel):
    id: str
    name: str
    description: str | None
    subject_id: str
    grade_id: str

    requires_image: bool


