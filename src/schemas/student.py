
from enum import Enum

from pydantic import BaseModel, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


# -------------------------
# Create Student
# -------------------------

class StudentCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    gender: Gender

    age: int = Field(
        ...,
        ge=5,
        le=15,
    )

    grade_id: str

# -------------------------
# Student Login
# -------------------------

class StudentLogin(BaseModel):
    student_id: str

  


# -------------------------
# Update Student
# -------------------------

class StudentUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    age: int | None = Field(
        default=None,
        ge=5,
        le=15,
    )

    gender: Gender | None = None

    grade_id: str | None = None


# -------------------------
# Student Response
# -------------------------

class StudentResponse(BaseModel):
    id: str
    name: str
    age: int
    gender: Gender
    grade_id: str

