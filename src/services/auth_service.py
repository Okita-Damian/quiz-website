
import jwt

from datetime import datetime, timedelta, timezone
from errorHandlers.exceptions import NotFoundError
from bson import ObjectId
from bson.errors import InvalidId

from config.db import database
from config.settings import settings
from schemas.student import StudentLogin


students_collection = database.students


# -------------------------
# Validate Student ID
# -------------------------

def validate_student_id(
    student_id: str,
):
    try:
        return ObjectId(student_id)

    except InvalidId:
        raise NotFoundError(
            "The student ID you provided is not valid."
        )


# -------------------------
# Student Login
# -------------------------

async def login_student(
    login_data: StudentLogin,
):
    student_object_id = validate_student_id(
        login_data.student_id
    )

    student = await students_collection.find_one(
        {
            "_id": student_object_id
        }
    )

    if not student:
        raise NotFoundError(
            "Invalid student ID."
        )

    # -------------------------
    # JWT Expiration
    # -------------------------

    expiration = (
        datetime.now(timezone.utc)
        + timedelta(minutes=30)
    )

    # -------------------------
    # JWT Payload
    # -------------------------

    payload = {
        "user_id": str(student["_id"]),
        "role": "student",
        "exp": expiration,
    }

    access_token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "student": {
            "id": str(student["_id"]),
            "name": student["name"],
            "age": student["age"],
            "gender": student["gender"],
            "grade_id": str(
                student["grade_id"]
            ),
        },
    }

