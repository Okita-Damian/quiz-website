from bson import ObjectId
from bson.errors import InvalidId

from config.db import database
from errorHandlers.exceptions import NotFoundError


from schemas.question import (
    QuestionCreate,
    QuestionUpdate,
)


# ============================================================
# COLLECTIONS
# ============================================================

questions_collection = database.questions
grades_collection = database.grades
subjects_collection = database.subjects
topics_collection = database.topics


# ============================================================
# VALIDATE OBJECT ID
# ============================================================

def validate_object_id(
    value: str,
    field_name: str,
) -> ObjectId:

    try:
        return ObjectId(value)

    except (InvalidId, TypeError):
        raise NotFoundError(
            f"The {field_name} ID you provided is not valid."
        )


# ============================================================
# GET GRADE
# ============================================================

async def get_grade(
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

    if grade is None:
        raise NotFoundError(
            "The selected grade does not exist."
        )

    return grade


# ============================================================
# GET TOPIC
# ============================================================

async def get_topic(
    topic_id: str,
):

    topic_object_id = validate_object_id(
        topic_id,
        "topic",
    )

    topic = await topics_collection.find_one(
        {
            "_id": topic_object_id
        }
    )

    if topic is None:
        raise NotFoundError(
            "The selected topic does not exist."
        )

    return topic


# ============================================================
# GET SUBJECT
# ============================================================

async def get_subject(
    subject_id: ObjectId,
):

    subject = await subjects_collection.find_one(
        {
            "_id": subject_id
        }
    )

    if subject is None:
        raise NotFoundError(
            "The subject associated with this topic "
            "does not exist."
        )

    return subject


# ============================================================
# VALIDATE QUESTION CONTENT
# ============================================================

def validate_question_content(
    question_data: QuestionCreate,
):

    # Must have exactly 4 options

    if len(question_data.options) != 4:
        raise NotFoundError(
            "A question must have exactly 4 options."
        )

    # Options must be unique

    if len(set(question_data.options)) != 4:
        raise NotFoundError(
            "All answer options must be different."
        )

    # Correct answer must exist in options

    if (
        question_data.correct_answer
        not in question_data.options
    ):
        raise NotFoundError(
            "The correct answer must be one of "
            "the provided options."
        )


# ============================================================
# VALIDATE QUESTION CONTEXT
#
# Grade
#   ↓
# Subject
#   ↓
# Topic
# ============================================================

async def validate_question_context(
    grade_id: str,
    topic_id: str,
):

    # --------------------------------------------------------
    # Get Grade
    # --------------------------------------------------------

    grade = await get_grade(
        grade_id
    )

    grade_object_id = grade["_id"]

    # --------------------------------------------------------
    # Get Topic
    # --------------------------------------------------------

    topic = await get_topic(
        topic_id
    )

    # --------------------------------------------------------
    # Topic must have subject_id
    # --------------------------------------------------------

    if "subject_id" not in topic:
        raise NotFoundError(
            "This topic is not associated with a subject."
        )

    subject_id = topic["subject_id"]

    # --------------------------------------------------------
    # Get Subject
    # --------------------------------------------------------

    subject = await get_subject(
        subject_id
    )

    # --------------------------------------------------------
    # Check Topic Grade
    #
    # Your topic document contains:
    #
    # grade_id: ObjectId(...)
    #
    # --------------------------------------------------------

    if "grade_id" not in topic:
        raise NotFoundError(
            "This topic is not associated with a grade."
        )

    topic_grade_id = topic["grade_id"]

    if topic_grade_id != grade_object_id:
        raise NotFoundError(
            "The selected topic does not belong "
            "to the selected grade."
        )

    # --------------------------------------------------------
    # Check Subject Grades
    #
    # Your subject document contains:
    #
    # grade_ids: [ObjectId(...), ObjectId(...)]
    #
    # --------------------------------------------------------

    if "grade_ids" not in subject:
        raise NotFoundError(
            "This subject is not associated with any grade."
        )

    subject_grade_ids = subject["grade_ids"]

    if grade_object_id not in subject_grade_ids:
        raise NotFoundError(
            "The selected grade is not available "
            "for this subject."
        )

    # --------------------------------------------------------
    # Everything is valid
    # --------------------------------------------------------

    return (
        grade,
        subject,
        topic,
    )


# ============================================================
# SERIALIZE QUESTION
# ============================================================

def serialize_question(
    question: dict,
):

    created_by = None

    if (
        "created_by" in question
        and question["created_by"] is not None
    ):
        created_by = str(
            question["created_by"]
        )

    return {
        "id": str(
            question["_id"]
        ),

        "question": question[
            "question"
        ],

        "options": question[
            "options"
        ],

        "correct_answer": question[
            "correct_answer"
        ],

        "explanation": question.get(
            "explanation"
        ),

        "grade_id": str(
            question["grade_id"]
        ),

        "subject_id": str(
            question["subject_id"]
        ),

        "topic_id": str(
            question["topic_id"]
        ),

        "question_type": question[
            "question_type"
        ],

        "source": question[
            "source"
        ],

        "created_by": created_by,

        "image_url": question.get(
            "image_url"
        ),
    }


# ============================================================
# CREATE QUESTION
# ============================================================

async def create_question(
    question_data: QuestionCreate,
    created_by: str,
    source: str,
):

    # --------------------------------------------------------
    # Validate Question Content
    # --------------------------------------------------------

    validate_question_content(
        question_data
    )

    # --------------------------------------------------------
    # Validate Grade + Subject + Topic
    # --------------------------------------------------------

    (
        grade,
        subject,
        topic,
    ) = await validate_question_context(
        grade_id=question_data.grade_id,
        topic_id=question_data.topic_id,
    )

    # --------------------------------------------------------
    # Validate Creator
    # --------------------------------------------------------

    creator_object_id = validate_object_id(
        created_by,
        "creator",
    )

    # --------------------------------------------------------
    # Create Question Document
    # --------------------------------------------------------

    question_document = {
        "question": (
            question_data.question.strip()
        ),

        "options": question_data.options,

        "correct_answer": (
            question_data.correct_answer
        ),

        "explanation": (
            question_data.explanation.strip()
            if question_data.explanation
            else None
        ),

        "grade_id": grade["_id"],

        "subject_id": subject["_id"],

        "topic_id": topic["_id"],

        "question_type": (
            question_data.question_type.value
        ),

        "source": source,

        "created_by": creator_object_id,

        "image_url": (
            question_data.image_url
        ),
    }

    # --------------------------------------------------------
    # Save Question
    # --------------------------------------------------------

    result = await questions_collection.insert_one(
        question_document
    )

    # --------------------------------------------------------
    # Get Saved Question
    # --------------------------------------------------------

    question = await questions_collection.find_one(
        {
            "_id": result.inserted_id
        }
    )

    if question is None:
        raise NotFoundError(
            "Question was created but could not be retrieved."
        )

    return serialize_question(
        question
    )


# ============================================================
# GET ONE QUESTION
# ============================================================

async def get_question(
    question_id: str,
):

    question_object_id = validate_object_id(
        question_id,
        "question",
    )

    question = await questions_collection.find_one(
        {
            "_id": question_object_id
        }
    )

    if question is None:
        raise NotFoundError(
            "The question you are looking for "
            "does not exist."
        )

    return serialize_question(
        question
    )


# ============================================================
# GET QUESTIONS
# ============================================================

async def get_questions(
    grade_id: str | None = None,
    subject_id: str | None = None,
    topic_id: str | None = None,
):

    query = {}

    # --------------------------------------------------------
    # Grade Filter
    # --------------------------------------------------------

    if grade_id is not None:

        query["grade_id"] = validate_object_id(
            grade_id,
            "grade",
        )

    # --------------------------------------------------------
    # Subject Filter
    # --------------------------------------------------------

    if subject_id is not None:

        query["subject_id"] = validate_object_id(
            subject_id,
            "subject",
        )

    # --------------------------------------------------------
    # Topic Filter
    # --------------------------------------------------------

    if topic_id is not None:

        query["topic_id"] = validate_object_id(
            topic_id,
            "topic",
        )

    # --------------------------------------------------------
    # Find Questions
    # --------------------------------------------------------

    cursor = questions_collection.find(
        query
    )

    questions = []

    async for question in cursor:

        questions.append(
            serialize_question(
                question
            )
        )

    return questions



# -------------------------
# Update Question
# -------------------------

async def update_question(
    question_id: str,
    question_data: QuestionUpdate,
    current_user: dict,
):
    # -------------------------
    # Validate Question ID
    # -------------------------

    question_object_id = validate_object_id(
        question_id,
        "question",
    )

    # -------------------------
    # Get Existing Question
    # -------------------------

    existing_question = (
        await questions_collection.find_one(
            {
                "_id": question_object_id
            }
        )
    )

    if not existing_question:
        raise NotFoundError(
            "The question you are trying to update "
            "does not exist."
        )

    # -------------------------
    # Validate Current User
    # -------------------------

    current_user_id = validate_object_id(
        current_user["user_id"],
        "user",
    )

    # -------------------------
    # Check Ownership
    # -------------------------

    if (
        existing_question["created_by"]
        != current_user_id
    ):
        raise NotFoundError(
            "You are not allowed to update this question."
        )

    # -------------------------
    # Get Update Data
    # -------------------------

    update_data = question_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise NotFoundError(
            "You must provide at least one field "
            "to update."
        )

    # -------------------------
    # Validate Options
    # -------------------------

    options = update_data.get(
        "options",
        existing_question["options"],
    )

    correct_answer = update_data.get(
        "correct_answer",
        existing_question["correct_answer"],
    )

    if len(options) != 4:
        raise NotFoundError(
            "A question must have exactly 4 options."
        )

    if len(set(options)) != 4:
        raise NotFoundError(
            "All answer options must be different."
        )

    if correct_answer not in options:
        raise NotFoundError(
            "The correct answer must be one of "
            "the options."
        )

    # -------------------------
    # Determine Topic
    # -------------------------

    topic_id = update_data.get(
        "topic_id",
        str(
            existing_question[
                "topic_id"
            ]
        ),
    )

    # -------------------------
    # Get Question Hierarchy
    # -------------------------

    (
        grade,
        subject,
        topic,
    ) = await validate_question_context(
        grade_id=update_data.get(
            "grade_id",
            str(
                existing_question[
                    "grade_id"
                ]
            ),
        ),
        topic_id=topic_id,
    )

    # -------------------------
    # Prepare Update
    # -------------------------

    update_document = {
        "grade_id": grade["_id"],
        "subject_id": subject["_id"],
        "topic_id": topic["_id"],
        "options": options,
        "correct_answer": correct_answer,
    }

    # -------------------------
    # Question Text
    # -------------------------

    if "question" in update_data:
        update_document["question"] = (
            update_data["question"].strip()
        )

    # -------------------------
    # Explanation
    # -------------------------

    if "explanation" in update_data:
        update_document["explanation"] = (
            update_data["explanation"].strip()
            if update_data["explanation"]
            else None
        )

    # -------------------------
    # Question Type
    # -------------------------

    if "question_type" in update_data:
        update_document["question_type"] = (
            update_data[
                "question_type"
            ].value
        )

    # -------------------------
    # Image URL
    # -------------------------

    if "image_url" in update_data:
        update_document["image_url"] = (
            update_data["image_url"]
        )

    # -------------------------
    # Update Question
    # -------------------------

    await questions_collection.update_one(
        {
            "_id": question_object_id
        },
        {
            "$set": update_document
        },
    )

    # -------------------------
    # Get Updated Question
    # -------------------------

    question = await questions_collection.find_one(
        {
            "_id": question_object_id
        }
    )

    return serialize_question(
        question
    )


# -------------------------
# Delete Question
# -------------------------

async def delete_question(
    question_id: str,
    current_user: dict,
):
    # -------------------------
    # Validate Question ID
    # -------------------------

    question_object_id = validate_object_id(
        question_id,
        "question",
    )

    # -------------------------
    # Get Existing Question
    # -------------------------

    existing_question = (
        await questions_collection.find_one(
            {
                "_id": question_object_id
            }
        )
    )

    if not existing_question:
        raise NotFoundError(
            "The question you are trying to delete "
            "does not exist."
        )

    # -------------------------
    # Validate Current User
    # -------------------------

    current_user_id = validate_object_id(
        current_user["user_id"],
        "user",
    )

    # -------------------------
    # Check Ownership
    # -------------------------

    if (
        existing_question["created_by"]
        != current_user_id
    ):
        raise NotFoundError(
            "You are not allowed to delete this question."
        )

    # -------------------------
    # Delete Question
    # -------------------------

    result = await questions_collection.delete_one(
        {
            "_id": question_object_id
        }
    )

    if result.deleted_count == 0:
        raise NotFoundError(
            "The question could not be deleted."
        )

    return {
        "message": "Question deleted successfully."
    }

