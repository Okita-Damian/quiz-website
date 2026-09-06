from pydantic import BaseModel, Field


class GradeCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    level: int = Field(
        ...,
        ge=1,
        le=3,
    )


class GradeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    level: int | None = Field(
        default=None,
        ge=1,
        le=3,
    )


class GradeResponse(BaseModel):
    id: str
    name: str
    level: int



