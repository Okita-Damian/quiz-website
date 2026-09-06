

from bson import ObjectId
from bson.errors import InvalidId
from errorHandlers.exceptions import NotFoundError


from config.db import database
from schemas.student import StudentCreate, StudentUpdate


students_collection = database.students
grades_collection = database.grades


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
# Validate Grade ID
# -------------------------

async def validate_grade_id(
    grade_id: str,
):
    try:
        grade_object_id = ObjectId(
            grade_id
        )

    except InvalidId:
        raise NotFoundError(
            "The grade ID you provided is not valid."
        )

    grade = await grades_collection.find_one(
        {
            "_id": grade_object_id
        }
    )

    if not grade:
        raise NotFoundError(
            "The grade you selected does not exist."
        )

    return grade_object_id


# -------------------------
# Serialize Student
# -------------------------

def serialize_student(
    student: dict,
):
    return {
        "id": str(student["_id"]),
        "name": student["name"],
        "age": student["age"],
        "gender": student["gender"],
        "grade_id": str(
            student["grade_id"]
        ),
        "parent_id": (
            str(student["parent_id"])
            if student.get("parent_id")
            else None
        ),
    }

# -------------------------
# Register Student
# -------------------------

async def register_student(
    student_data: StudentCreate,
):
    # Make sure the grade exists

    grade_object_id = await validate_grade_id(
        student_data.grade_id
    )

    student_document = {
        "name": student_data.name.strip(),
        "age": student_data.age,
        "gender": student_data.gender.value,
        "grade_id": grade_object_id,

        # Student is not linked
        # to a parent yet.
        "parent_id": None,
    }

    result = await students_collection.insert_one(
        student_document
    )

    student = await students_collection.find_one(
        {
            "_id": result.inserted_id
        }
    )

    return serialize_student(
        student
    )


# -------------------------
# Get Student
# -------------------------

async def get_student(
    student_id: str,
):
    student_object_id = validate_student_id(
        student_id
    )

    student = await students_collection.find_one(
        {
            "_id": student_object_id
        }
    )

    if not student:
        raise NotFoundError(
            "The student you are looking for does not exist."
        )

    return serialize_student(
        student
    )


# -------------------------
# Update Student
# -------------------------

async def update_student(
    student_id: str,
    student_data: StudentUpdate,
):
    student_object_id = validate_student_id(
        student_id
    )

    student = await students_collection.find_one(
        {
            "_id": student_object_id
        }
    )

    if not student:
        raise NotFoundError(
            "The student you are trying to update does not exist."
        )

    update_data = student_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise NotFoundError(
            "You must provide at least one field to update."
        )

    # -------------------------
    # Name
    # -------------------------

    if "name" in update_data:
        update_data["name"] = (
            update_data["name"]
        )

    # -------------------------
    # Gender
    # -------------------------

    if "gender" in update_data:
        update_data["gender"] = (
            update_data["gender"]
        )

    # -------------------------
    # Grade
    # -------------------------

    if "grade_id" in update_data:
        update_data["grade_id"] = (
            await validate_grade_id(
                update_data["grade_id"]
            )
        )

    await students_collection.update_one(
        {
            "_id": student_object_id
        },
        {
            "$set": update_data
        },
    )

    updated_student = (
        await students_collection.find_one(
            {
                "_id": student_object_id
            }
        )
    )

    return serialize_student(
        updated_student
    )


# -------------------------
# Delete Student
# -------------------------

async def delete_student(
    student_id: str,
):
    student_object_id = validate_student_id(
        student_id
    )

    result = await students_collection.delete_one(
        {
            "_id": student_object_id
        }
    )

    if result.deleted_count == 0:
        raise NotFoundError(
            "The student you are trying to delete does not exist."
        )

    return {
        "message": "Student profile deleted successfully."
    }

