


from bson import ObjectId
from bson.errors import InvalidId
from errorHandlers.exceptions import NotFoundError


from config.db import database
from schemas.teacher_schema import (
    TeacherCreate,
    TeacherUpdate,
)


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
# Serialize Teacher
# -------------------------

def serialize_teacher(
    teacher: dict,
):
    return {
        "id": str(teacher["_id"]),
        "name": teacher["name"],
    }


# -------------------------
# Register Teacher
# -------------------------

async def register_teacher(
    teacher_data: TeacherCreate,
):
    teacher_document = {
        "name": teacher_data.name.strip(),
        
    }

    result = await teachers_collection.insert_one(
        teacher_document
    )

    teacher = await teachers_collection.find_one(
        {
            "_id": result.inserted_id
        }
    )

    return serialize_teacher(
        teacher
    )


# -------------------------
# Get Teacher
# -------------------------

async def get_teacher(
    teacher_id: str,
):
    teacher_object_id = validate_teacher_id(
        teacher_id
    )

    teacher = await teachers_collection.find_one(
        {
            "_id": teacher_object_id
        }
    )

    if not teacher:
        raise NotFoundError(
            "The teacher you are looking for does not exist."
        )

    return serialize_teacher(
        teacher
    )


# -------------------------
# Update Teacher
# -------------------------

async def update_teacher(
    teacher_id: str,
    teacher_data: TeacherUpdate,
):
    teacher_object_id = validate_teacher_id(
        teacher_id
    )

    teacher = await teachers_collection.find_one(
        {
            "_id": teacher_object_id
        }
    )

    if not teacher:
        raise NotFoundError(
            "The teacher you are trying to update does not exist."
        )

    update_data = teacher_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise NotFoundError(
            "You must provide at least one field to update."
        )

    if "name" in update_data:
        update_data["name"] = (
            update_data["name"].strip()
        )

    await teachers_collection.update_one(
        {
            "_id": teacher_object_id
        },
        {
            "$set": update_data
        },
    )

    updated_teacher = (
        await teachers_collection.find_one(
            {
                "_id": teacher_object_id
            }
        )
    )

    return serialize_teacher(
        updated_teacher
    )


# -------------------------
# Delete Teacher
# -------------------------

async def delete_teacher(
    teacher_id: str,
):
    teacher_object_id = validate_teacher_id(
        teacher_id
    )

    result = await teachers_collection.delete_one(
        {
            "_id": teacher_object_id
        }
    )

    if result.deleted_count == 0:
        raise NotFoundError(
            "The teacher you are trying to delete does not exist."
        )

    return {
        "message": "Teacher profile deleted successfully."
    }
