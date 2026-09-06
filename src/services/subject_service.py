
from bson import ObjectId
from bson.errors import InvalidId
from errorHandlers.exceptions import NotFoundError


from config.db import database
from schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
)


subjects_collection = database.subjects
grades_collection = database.grades


# -------------------------
# Validate Object ID
# -------------------------

def validate_object_id(
    value: str,
    field_name: str,
):
    try:
        return ObjectId(value)

    except InvalidId:
        raise NotFoundError(
            f"The {field_name} ID you provided is not valid."
        )


# -------------------------
# Validate Grade IDs
# -------------------------

async def validate_grade_ids(
    grade_ids: list[str],
):
    grade_object_ids = []

    for grade_id in grade_ids:
        grade_object_ids.append(
            validate_object_id(
                grade_id,
                "grade",
            )
        )

    if not grade_object_ids:
        return []

    cursor = grades_collection.find(
        {
            "_id": {
                "$in": grade_object_ids
            }
        }
    )

    existing_grades = []

    async for grade in cursor:
        existing_grades.append(
            grade["_id"]
        )

    if len(existing_grades) != len(
        set(grade_object_ids)
    ):
        raise NotFoundError(
            "One or more grade IDs do not exist."
        )

    return grade_object_ids


# -------------------------
# Serialize Subject
# -------------------------

def serialize_subject(
    subject: dict,
):
    return {
        "id": str(subject["_id"]),
        "name": subject["name"],
        "description": subject.get(
            "description"
        ),
        "grade_ids": [
            str(grade_id)
            for grade_id in subject.get(
                "grade_ids",
                []
            )
        ],
    }


# -------------------------
# Create Subject
# -------------------------

async def create_subject(
    subject_data: SubjectCreate,
):
    # Check duplicate subject name

    existing_subject = (
        await subjects_collection.find_one(
            {
                "name": subject_data.name.strip()
            }
        )
    )

    if existing_subject:
        raise NotFoundError(
            "A subject with this name already exists."
        )

    grade_object_ids = (
        await validate_grade_ids(
            subject_data.grade_ids
        )
    )

    subject_document = {
        "name": subject_data.name.strip(),
        "description": (
            subject_data.description.strip()
            if subject_data.description
            else None
        ),
        "grade_ids": grade_object_ids,
    }

    result = await subjects_collection.insert_one(
        subject_document
    )

    subject = await subjects_collection.find_one(
        {
            "_id": result.inserted_id
        }
    )

    return serialize_subject(subject)


# -------------------------
# Get All Subjects
# -------------------------

async def get_subjects():

    cursor = subjects_collection.find(
        {}
    ).sort(
        "name",
        1,
    )

    subjects = []

    async for subject in cursor:
        subjects.append(
            serialize_subject(subject)
        )

    return subjects


# -------------------------
# Get One Subject
# -------------------------

async def get_subject(
    subject_id: str,
):
    subject_object_id = validate_object_id(
        subject_id,
        "subject",
    )

    subject = await subjects_collection.find_one(
        {
            "_id": subject_object_id
        }
    )

    if not subject:
        raise NotFoundError(
            "The subject you are looking for does not exist."
        )

    return serialize_subject(subject)


# -------------------------
# Get Subjects For Grade
# -------------------------

async def get_subjects_for_grade(
    grade_id: str,
):
    grade_object_id = validate_object_id(
        grade_id,
        "grade",
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

    cursor = subjects_collection.find(
        {
            "grade_ids": grade_object_id
        }
    ).sort(
        "name",
        1,
    )

    subjects = []

    async for subject in cursor:
        subjects.append(
            serialize_subject(subject)
        )

    return subjects


# -------------------------
# Update Subject
# -------------------------

async def update_subject(
    subject_id: str,
    subject_data: SubjectUpdate,
):
    subject_object_id = validate_object_id(
        subject_id,
        "subject",
    )

    update_data = subject_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise NotFoundError(
            "You must provide at least one field to update."
        )

    # -------------------------
    # Validate name
    # -------------------------

    if "name" in update_data:

        update_data["name"] = (
            update_data["name"].strip()
        )

        existing_subject = (
            await subjects_collection.find_one(
                {
                    "name": update_data["name"],
                    "_id": {
                        "$ne": subject_object_id
                    },
                }
            )
        )

        if existing_subject:
            raise NotFoundError(
                "A subject with this name already exists."
            )

    # -------------------------
    # Validate description
    # -------------------------

    if "description" in update_data:

        if update_data["description"]:
            update_data["description"] = (
                update_data[
                    "description"
                ].strip()
            )

    # -------------------------
    # Validate grades
    # -------------------------

    if "grade_ids" in update_data:

        update_data["grade_ids"] = (
            await validate_grade_ids(
                update_data["grade_ids"]
            )
        )

    # -------------------------
    # Update
    # -------------------------

    result = await subjects_collection.update_one(
        {
            "_id": subject_object_id
        },
        {
            "$set": update_data
        },
    )

    if result.matched_count == 0:
        raise NotFoundError(
            "The subject you are trying to update does not exist."
        )

    subject = await subjects_collection.find_one(
        {
            "_id": subject_object_id
        }
    )

    return serialize_subject(subject)


# -------------------------
# Delete Subject
# -------------------------

async def delete_subject(
    subject_id: str,
):
    subject_object_id = validate_object_id(
        subject_id,
        "subject",
    )

    result = await subjects_collection.delete_one(
        {
            "_id": subject_object_id
        }
    )

    if result.deleted_count == 0:
        raise NotFoundError(
            "The subject you are trying to delete does not exist."
        )

    return {
        "message": "Subject deleted successfully."
    }

