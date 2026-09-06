
from bson import ObjectId
from bson.errors import InvalidId
from errorHandlers.exceptions import NotFoundError


from config.db import database
from schemas.quiz import (
    QuizCreate,
    QuizUpdate,
)


quizzes_collection = database.quizzes
topics_collection = database.topics
questions_collection = database.questions


# -------------------------
# Validate ObjectId
# -------------------------

def validate_object_id(
    value: str,
    field_name: str,
):
    try:
        return ObjectId(value)

    except InvalidId:
        raise NotFoundError(
            f"The {field_name} you provided is not valid."
        )


# -------------------------
# Validate Topic
# -------------------------

async def validate_topic(
    topic_id: str,
):
    topic_object_id = validate_object_id(
        topic_id,
        "topic ID",
    )

    topic = await topics_collection.find_one(
        {
            "_id": topic_object_id
        }
    )

    if not topic:
        raise NotFoundError(
            "The topic you provided does not exist."
        )

    return topic_object_id


# -------------------------
# Validate Questions
# -------------------------

async def validate_questions(
    question_ids: list[str],
    topic_id: ObjectId,
):
    question_object_ids = []

    for question_id in question_ids:
        question_object_id = validate_object_id(
            question_id,
            "question ID",
        )

        question_object_ids.append(
            question_object_id
        )

    # Remove duplicate question IDs
    if len(question_object_ids) != len(
        set(question_object_ids)
    ):
        raise NotFoundError(
            "A quiz cannot contain duplicate questions."
        )

    questions = await questions_collection.find(
        {
            "_id": {
                "$in": question_object_ids
            }
        }
    ).to_list(
        length=len(question_object_ids)
    )

    # Check that every question exists
    if len(questions) != len(
        question_object_ids
    ):
        raise NotFoundError(
            "One or more questions do not exist."
        )

    # Check that every question belongs
    # to the selected topic
    for question in questions:
        if question["topic_id"] != topic_id:
            raise NotFoundError(
                "All questions in a quiz must belong to the selected topic."
            )

    return question_object_ids


# -------------------------
# Serialize Quiz
# -------------------------

def serialize_quiz(
    quiz: dict,
):
    return {
        "id": str(quiz["_id"]),
        "title": quiz["title"],
        "topic_id": str(
            quiz["topic_id"]
        ),
        "question_ids": [
            str(question_id)
            for question_id in quiz[
                "question_ids"
            ]
        ],
        "created_by": (
            str(quiz["created_by"])
            if quiz.get("created_by")
            else None
        ),
    }


# -------------------------
# Create Quiz
# -------------------------

async def create_quiz(
    quiz_data: QuizCreate,
    user_id: str,
):
    topic_object_id = await validate_topic(
        quiz_data.topic_id
    )

    question_object_ids = (
        await validate_questions(
            quiz_data.question_ids,
            topic_object_id,
        )
    )

    user_object_id = validate_object_id(
        user_id,
        "user ID",
    )

    quiz_document = {
        "title": quiz_data.title.strip(),
        "topic_id": topic_object_id,
        "question_ids": question_object_ids,
        "created_by": user_object_id,
    }

    result = await quizzes_collection.insert_one(
        quiz_document
    )

    quiz = await quizzes_collection.find_one(
        {
            "_id": result.inserted_id
        }
    )

    return serialize_quiz(
        quiz
    )


# -------------------------
# Get Quiz
# -------------------------

async def get_quiz(
    quiz_id: str,
):
    quiz_object_id = validate_object_id(
        quiz_id,
        "quiz ID",
    )

    quiz = await quizzes_collection.find_one(
        {
            "_id": quiz_object_id
        }
    )

    if not quiz:
        raise NotFoundError(
            "The quiz you are looking for does not exist."
        )

    return serialize_quiz(
        quiz
    )


# -------------------------
# Get Quizzes By Topic
# -------------------------

async def get_quizzes_by_topic(
    topic_id: str,
):
    topic_object_id = await validate_topic(
        topic_id
    )

    quizzes = []

    cursor = quizzes_collection.find(
        {
            "topic_id": topic_object_id
        }
    )

    async for quiz in cursor:
        quizzes.append(
            serialize_quiz(quiz)
        )

    return quizzes


# -------------------------
# Update Quiz
# -------------------------

async def update_quiz(
    quiz_id: str,
    quiz_data: QuizUpdate,
    user_id: str,
):
    quiz_object_id = validate_object_id(
        quiz_id,
        "quiz ID",
    )

    user_object_id = validate_object_id(
        user_id,
        "user ID",
    )

    quiz = await quizzes_collection.find_one(
        {
            "_id": quiz_object_id
        }
    )

    if not quiz:
        raise NotFoundError(
            "The quiz you are trying to update does not exist."
        )

    # Only the creator can update the quiz
    if quiz.get("created_by") != user_object_id:
        raise NotFoundError(
            "You are not allowed to update this quiz."
        )

    update_data = quiz_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise NotFoundError(
            "You must provide at least one field to update."
        )

    if "title" in update_data:
        update_data["title"] = (
            update_data["title"].strip()
        )

    # If questions are being changed,
    # validate them against the quiz topic.
    if "question_ids" in update_data:
        question_object_ids = (
            await validate_questions(
                update_data["question_ids"],
                quiz["topic_id"],
            )
        )

        update_data[
            "question_ids"
        ] = question_object_ids

    await quizzes_collection.update_one(
        {
            "_id": quiz_object_id
        },
        {
            "$set": update_data
        },
    )

    updated_quiz = (
        await quizzes_collection.find_one(
            {
                "_id": quiz_object_id
            }
        )
    )

    return serialize_quiz(
        updated_quiz
    )


# -------------------------
# Delete Quiz
# -------------------------

async def delete_quiz(
    quiz_id: str,
    user_id: str,
):
    quiz_object_id = validate_object_id(
        quiz_id,
        "quiz ID",
    )

    user_object_id = validate_object_id(
        user_id,
        "user ID",
    )

    quiz = await quizzes_collection.find_one(
        {
            "_id": quiz_object_id
        }
    )

    if not quiz:
        raise NotFoundError(
            "The quiz you are trying to delete does not exist."
        )

    # Only the creator can delete the quiz
    if quiz.get("created_by") != user_object_id:
        raise NotFoundError(
            "You are not allowed to delete this quiz."
        )

    await quizzes_collection.delete_one(
        {
            "_id": quiz_object_id
        }
    )

    return {
        "message": "Quiz deleted successfully."
    }
