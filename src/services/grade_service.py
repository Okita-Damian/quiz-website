from bson import ObjectId
from bson.errors import InvalidId

from errorHandlers.exceptions import NotFoundError

from config.db import database
from schemas.grade_schema import GradeCreate, GradeUpdate


grades_collection = database.grades


# -------------------------
# Validate Grade ID
# -------------------------

def validate_grade_id(grade_id: str):
    try:
        return ObjectId(grade_id)

    except InvalidId:
        raise NotFoundError(
            "The grade ID you provided is not valid."
        )


# -------------------------
# Serialize Grade
# -------------------------

def serialize_grade(grade: dict) -> dict:
    return {
        "id": str(grade["_id"]),
        "name": grade["name"],
        "level": grade["level"],
    }


# -------------------------
# Create Grade
# -------------------------

async def create_grade(
    grade_data: GradeCreate,
):
    # Prevent duplicate grade levels

    existing_grade = await grades_collection.find_one(
        {
            "level": grade_data.level
        }
    )

    if existing_grade:
        raise NotFoundError(
            "A grade with this level already exists."
        )

    grade_document = {
        "name": grade_data.name.strip(),
        "level": grade_data.level,
    }

    result = await grades_collection.insert_one(
        grade_document
    )

    grade = await grades_collection.find_one(
        {
            "_id": result.inserted_id
        }
    )

    return serialize_grade(grade)


# -------------------------
# Get All Grades
# -------------------------

async def get_grades():

    cursor = grades_collection.find(
        {}
    ).sort(
        "level",
        1,
    )

    grades = []

    async for grade in cursor:
        grades.append(
            serialize_grade(grade)
        )

    return grades


# -------------------------
# Get One Grade
# -------------------------

async def get_grade(
    grade_id: str,
):
    grade_object_id = validate_grade_id(
        grade_id
    )

    

    grade = await grades_collection.find_one(
        {
            "_id": grade_object_id
        }
    )

    if not grade:
        raise NotFoundError(
            "The grade you are looking for does not exist."
        )

    return serialize_grade(grade)


# -------------------------
# Update Grade
# -------------------------

async def update_grade(
    grade_id: str,
    grade_data: GradeUpdate,
):
    grade_object_id = validate_grade_id(
        grade_id
    )

    update_data = grade_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise NotFoundError(
            "You must provide at least one field to update."
        )

    if "name" in update_data:
        update_data["name"] = (
            update_data["name"]
        )

    if "level" in update_data:

        existing_grade = await grades_collection.find_one(
            {
                "level": update_data["level"],
                "_id": {
                    "$ne": grade_object_id
                },
            }
        )

        if existing_grade:
            raise NotFoundError(
                "A grade with this level already exists."
            )

    result = await grades_collection.update_one(
        {
            "_id": grade_object_id
        },
        {
            "$set": update_data
        },
    )

    if result.matched_count == 0:
        raise NotFoundError(
            "The grade you are trying to update does not exist."
        )

    grade = await grades_collection.find_one(
        {
            "_id": grade_object_id
        }
    )

    return serialize_grade(grade)


# -------------------------
# Delete Grade
# -------------------------

async def delete_grade(
    grade_id: str,
):
    grade_object_id = validate_grade_id(
        grade_id
    )

    result = await grades_collection.delete_one(
        {
            "_id": grade_object_id
        }
    )

    if result.deleted_count == 0:
        raise NotFoundError(
            "The grade you are trying to delete does not exist."
        )

    return {
        "message": "Grade deleted successfully."
    }
