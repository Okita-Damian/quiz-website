
import jwt

from bson import ObjectId
from bson.errors import InvalidId
from errorHandlers.exceptions import NotFoundError


from config.db import database
from config.settings import settings
from schemas.teacher_schema import TeacherLogin


teachers_collection = database.teachers


# -------------------------
# Validate Teacher ID
# -------------------------

def validate_teacher_id(
    teacher_id: str,
):
    try:
        return ObjectId(teacher_id)

    except InvalidId:
        raise NotFoundError(
            "The teacher ID you provided is not valid."
        )


# -------------------------
# Login Teacher
# -------------------------

async def login_teacher(
    login_data: TeacherLogin,
):
    teacher_object_id = validate_teacher_id(
        login_data.teacher_id
    )

    teacher = await teachers_collection.find_one(
        {
            "_id": teacher_object_id
        }
    )

    if not teacher:
        raise NotFoundError(
            "Invalid teacher ID."
        )

    # -------------------------
    # JWT Payload
    # -------------------------

    payload = {
        "user_id": str(teacher["_id"]),
        "role": "teacher",
    }

    access_token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "teacher": {
            "id": str(teacher["_id"]),
            "name": teacher["name"],
        },
    }
