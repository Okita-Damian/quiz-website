
from datetime import datetime, timezone

from errorHandlers.exceptions import NotFoundError

from bson import ObjectId
from bson.errors import InvalidId

from config.db import database

from ai_queue.redis_queue import (
    get_redis_pool,
)


# -------------------------
# Collections
# -------------------------

ai_jobs_collection = (
    database.ai_generation_jobs
)

questions_collection = (
    database.questions
)


# -------------------------
# Create AI Generation Job
# -------------------------

async def create_ai_generation_job(
    topic_id: str,
    number_of_questions: int,
    user_id: str,
):

    # -------------------------
    # Validate IDs
    # -------------------------

    try:

        topic_object_id = ObjectId(
            topic_id
        )

        user_object_id = ObjectId(
            user_id
        )

    except (InvalidId, TypeError):

        raise ValueError(
            "Invalid topic ID or user ID."
        )

    # -------------------------
    # Create Job
    # -------------------------

    job_document = {

        "user_id": user_object_id,

        "topic_id": topic_object_id,

        "number_of_questions": (
            number_of_questions
        ),

        "status": "queued",

        "total": number_of_questions,

        "completed": 0,

        "failed": 0,

        "question_ids": [],

        "error": None,

        "created_at": datetime.now(
            timezone.utc
        ),

        "started_at": None,

        "completed_at": None,
    }

    # -------------------------
    # Save Job
    # -------------------------

    result = await ai_jobs_collection.insert_one(
        job_document
    )

    job_id = str(
        result.inserted_id
    )

    # -------------------------
    # Add Job To Redis
    # -------------------------

    try:

        redis = await get_redis_pool()

        await redis.enqueue_job(
            "generate_questions_job",
            job_id,
        )

    except Exception as error:

        await ai_jobs_collection.update_one(
            {
                "_id": result.inserted_id
            },
            {
                "$set": {

                    "status": "failed",

                    "error": (
                        "The AI generation job "
                        "could not be queued."
                    ),

                    "completed_at": (
                        datetime.now(
                            timezone.utc
                        )
                    ),
                }
            },
        )

        raise ValueError(
            "The AI generation service is "
            "currently unavailable."
        ) from error

    # -------------------------
    # Return
    # -------------------------

    return {

        "job_id": job_id,

        "status": "queued",

        "message": (
            "Question generation has "
            "been queued."
        ),
    }


# -------------------------
# Get Job Status
# -------------------------

async def get_job_status(
    job_id: str,
    current_user: dict,
):

    # -------------------------
    # Validate Job ID
    # -------------------------

    try:

        job_object_id = ObjectId(
            job_id
        )

    except (InvalidId, TypeError):

        raise ValueError(
            "The AI job ID you provided is not valid."
        )

    # -------------------------
    # Get User ID
    # -------------------------

    try:

        user_object_id = ObjectId(
            current_user["user_id"]
        )

    except (InvalidId, TypeError):

        raise ValueError(
            "The authenticated user ID is not valid."
        )

    # -------------------------
    # Get Job
    # -------------------------

    job = await ai_jobs_collection.find_one(
        {
            "_id": job_object_id,

            "user_id": user_object_id,
        }
    )

    if not job:

        raise NotFoundError(
            "The AI generation job does not exist."
        )

    # -------------------------
    # Convert Question IDs
    # -------------------------

    question_ids = [
        str(question_id)
        for question_id in job[ "question_ids"]
    ]

    # -------------------------
    # Return
    # -------------------------

    return {

        "job_id": str(
            job["_id"]
        ),

        "status": job["status",
                    "unknown"],

        "total": job[ "total"],

        "completed": job[ "completed"],

        "failed": job["failed"],

        "question_ids": question_ids,

        "error": job[ "error"]
    }



# -------------------------
# Get Job Questions
# -------------------------

async def get_job_questions(
    job_id: str,
    current_user: dict,
):

    print("\n")
    print("========================================")
    print("[START] get_job_questions()")
    print("========================================")

    # -------------------------
    # STEP 1: Validate Job ID
    # -------------------------

    print("[STEP 1] Validating AI job ID...")
    print("[DEBUG] Job ID:", job_id)
    print("[DEBUG] Job ID type:", type(job_id))

    try:

        job_object_id = ObjectId(
            job_id
        )

        print(
            "[DEBUG] Job ID is valid:",
            job_object_id,
        )

    except (InvalidId, TypeError) as error:

        print(
            "[ERROR] Invalid AI job ID:",
            repr(error),
        )

        raise ValueError(
            "The AI job ID you provided is not valid."
        ) from error

    # -------------------------
    # STEP 2: Get Job
    # -------------------------

    print("[STEP 2] Looking for AI job in MongoDB...")

    job = await ai_jobs_collection.find_one(
        {
            "_id": job_object_id
        }
    )

    if not job:

        print(
            "[ERROR] AI generation job was not found."
        )

        raise NotFoundError(
            "The AI generation job does not exist."
        )

    print("[STEP 2] AI job found successfully.")

    print(
        "[DEBUG] Job ID:",
        job["_id"],
    )

    print(
        "[DEBUG] Job status:",
        job.get("status"),
    )

    print(
        "[DEBUG] Job owner:",
        job.get("user_id"),
    )

    print(
        "[DEBUG] Job owner type:",
        type(job.get("user_id")),
    )

    print(
        "[DEBUG] Job question IDs:",
        job.get("question_ids", []),
    )

    # -------------------------
    # STEP 3: Get Current User
    # -------------------------

    print("[STEP 3] Getting authenticated user...")

    print(
        "[DEBUG] Current user:",
        current_user,
    )

    user_id = current_user.get(
        "user_id"
    )

    print(
        "[DEBUG] Current user ID:",
        user_id,
    )

    print(
        "[DEBUG] Current user ID type:",
        type(user_id),
    )

    if not user_id:

        print(
            "[ERROR] Current user does not contain user_id."
        )

        raise NotFoundError(
            "The authenticated user ID is missing."
        )

    # -------------------------
    # STEP 4: Convert User ID
    # -------------------------

    print("[STEP 4] Converting user ID to ObjectId...")

    try:

        user_object_id = ObjectId(
            str(user_id)
        )

        print(
            "[DEBUG] Converted user ID:",
            user_object_id,
        )

        print(
            "[DEBUG] Converted user ID type:",
            type(user_object_id),
        )

    except (InvalidId, TypeError) as error:

        print(
            "[ERROR] Invalid authenticated user ID:",
            repr(error),
        )

        raise ValueError(
            "The user ID is not valid."
        ) from error

    # -------------------------
    # STEP 5: Check Ownership
    # -------------------------

    print("[STEP 5] Checking job ownership...")

    job_user_id = job["user_id"]

    print(
        "[DEBUG] Job owner:",
        job_user_id,
    )

    print(
        "[DEBUG] Authenticated user:",
        user_object_id,
    )

    print(
        "[DEBUG] Job owner type:",
        type(job_user_id),
    )

    print(
        "[DEBUG] Authenticated user type:",
        type(user_object_id),
    )

    ownership_match = (
        job_user_id == user_object_id
    )

    print(
        "[DEBUG] Ownership match:",
        ownership_match,
    )

    if not ownership_match:

        print(
            "[ERROR] Permission check failed."
        )

        print(
            "[ERROR] Job belongs to:",
            job_user_id,
        )

        print(
            "[ERROR] Current user is:",
            user_object_id,
        )

        raise NotFoundError(
            "You do not have permission to access "
            "this AI generation job."
        )

    print(
        "[STEP 5] Ownership verification successful."
    )

    # -------------------------
    # STEP 6: Check Job Status
    # -------------------------

    print("[STEP 6] Checking job status...")

    job_status = job["status"]

    print(
        "[DEBUG] Job status:",
        job_status,
    )

    if job_status != "completed":

        print(
            "[ERROR] Job is not completed."
        )

        raise ValueError(
            "The AI generation job has not completed yet."
        )

    print(
        "[STEP 6] Job is completed."
    )

    # -------------------------
    # STEP 7: Get Question IDs
    # -------------------------

    print("[STEP 7] Getting question IDs...")

    question_ids = job["question_ids"]

    print(
        "[DEBUG] Question IDs:",
        question_ids,
    )

    print(
        "[DEBUG] Number of question IDs:",
        len(question_ids),
    )

    if not question_ids:

        print(
            "[WARNING] Job contains no question IDs."
        )

        return {
            "job_id": job_id,

            "status": job_status,

            "questions": [],
        }

    # -------------------------
    # STEP 8: Convert Question IDs
    # -------------------------

    print(
        "[STEP 8] Converting question IDs to ObjectIds..."
    )

    question_object_ids = []

    for index, question_id in enumerate(
        question_ids,
        start=1,
    ):

        print(
            f"[DEBUG] Converting question ID {index}:",
            question_id,
        )

        try:

            question_object_id = ObjectId(
                str(question_id)
            )

            question_object_ids.append(
                question_object_id
            )

            print(
                f"[DEBUG] Question ID {index} is valid:",
                question_object_id,
            )

        except (InvalidId, TypeError) as error:

            print(
                f"[ERROR] Invalid question ID {index}:",
                question_id,
            )

            print(
                "[ERROR] Exception:",
                repr(error),
            )

            continue

    # -------------------------
    # STEP 9: Validate Question IDs
    # -------------------------

    print(
        "[STEP 9] Validating converted question IDs..."
    )

    print(
        "[DEBUG] Valid question ObjectIds:",
        question_object_ids,
    )

    if not question_object_ids:

        print(
            "[ERROR] No valid question IDs were found."
        )

        raise NotFoundError(
            "The AI job contains invalid question IDs."
        )

    # -------------------------
    # STEP 10: Get Questions
    # -------------------------

    print(
        "[STEP 10] Looking for questions in MongoDB..."
    )

    questions_cursor = (
        questions_collection.find(
            {
                "_id": {
                    "$in": question_object_ids
                }
            }
        )
    )

    questions = (
        await questions_cursor.to_list(
            length=None
        )
    )

    print(
        "[STEP 10] Questions retrieved successfully."
    )

    print(
        "[DEBUG] Number of questions found:",
        len(questions),
    )

    # -------------------------
    # STEP 11: Check Missing Questions
    # -------------------------

    if len(questions) != len(
        question_object_ids
    ):

        print(
            "[WARNING] Some question IDs were not found."
        )

        print(
            "[DEBUG] Requested question count:",
            len(question_object_ids),
        )

        print(
            "[DEBUG] Retrieved question count:",
            len(questions),
        )

    # -------------------------
    # STEP 12: Serialize Questions
    # -------------------------

    print(
        "[STEP 12] Serializing questions..."
    )

    serialized_questions = []

    for index, question in enumerate(
        questions,
        start=1,
    ):

        print(
            f"[DEBUG] Serializing question {index}:",
            question.get("_id"),
        )

        serialized_questions.append(
            {
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

                "explanation": question["explanation"],

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

                "image_url": question["image_url"]
            }
        )

    print(
        "[STEP 12] Questions serialized successfully."
    )

    # -------------------------
    # STEP 13: Return
    # -------------------------

    print(
        "[STEP 13] Preparing final response..."
    )

    response = {
        "job_id": job_id,

        "status": job_status,

        "questions": serialized_questions,
    }

    print(
        "[DEBUG] Number of serialized questions:",
        len(serialized_questions),
    )

    print(
        "[DEBUG] Final response:",
        response,
    )

    print("\n")
    print("========================================")
    print("[SUCCESS] get_job_questions() completed")
    print("========================================")
    print("\n")

    return response

