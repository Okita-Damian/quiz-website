from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    grade_ids: list[str] = Field(
        default_factory=list,
    )


class SubjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    grade_ids: list[str] | None = None


class SubjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    grade_ids: list[str]
