
from pydantic import BaseModel, Field


# -------------------------
# Create Teacher
# -------------------------

class TeacherCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )


# -------------------------
# Teacher Login
# -------------------------

class TeacherLogin(BaseModel):
    teacher_id: str


# -------------------------
# Update Teacher
# -------------------------

class TeacherUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )


# -------------------------
# Teacher Response
# -------------------------

class TeacherResponse(BaseModel):
    id: str
    name: str
