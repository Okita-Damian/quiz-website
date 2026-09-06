from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from errorHandlers.exceptions import NotFoundError


from arq.connections import RedisSettings

from config.db import database
from config.settings import settings

from services.ai_question_service import (
    generate_questions,
)


ai_jobs_collection = (
    database.ai_generation_jobs
)


# -------------------------
# AI Generation Job
# -------------------------

async def generate_questions_job(
    ctx,
    job_id: str,
):
    print(
        f"Starting AI generation job: {job_id}"
    )

    # -------------------------
    # Validate Job ID
    # -------------------------

    try:

        job_object_id = ObjectId(
            job_id
        )

    except (InvalidId, TypeError) as error:

        print(
            f"Invalid job ID: {job_id}"
        )

        raise NotFoundError(
            "Invalid AI generation job ID."
        ) from error

    # -------------------------
    # Get Job
    # -------------------------

    job = await ai_jobs_collection.find_one(
        {
            "_id": job_object_id
        }
    )

    if not job:

        print(
            f"AI job not found: {job_id}"
        )

        return

    # -------------------------
    # Prevent Duplicate Work
    # -------------------------

    job_status = job["status"]

    if job_status == "completed":

        print(
            f"AI job already completed: {job_id}"
        )

        return

    # -------------------------
    # Mark Processing
    # -------------------------

    await ai_jobs_collection.update_one(
        {
            "_id": job_object_id
        },
        {
            "$set": {
                "status": "processing",

                "started_at": (
                    datetime.now(
                        timezone.utc
                    )
                ),

                "error": None,
            }
        },
    )

    try:

        # -------------------------
        # Rebuild AI Request
        # -------------------------

        from schemas.ai_question import (
            AIGenerateQuestion,
        )

        request = AIGenerateQuestion(

            topic_id=str(
                job["topic_id"]
            ),

            number_of_questions=(
                job["number_of_questions"]
            ),
        )

        # -------------------------
        # Rebuild User
        # -------------------------

        current_user = {
            "user_id": str(
                job["user_id"]
            ),
        }

        # -------------------------
        # Generate Questions
        # -------------------------

        print("WORKER STEP 1: Calling generate_questions")


        result = await generate_questions(
            request,
            current_user,
        )

        print("WORKER STEP 2: generate_questions returned")

        print("AI GENERATION RESULT:", result)

        # -------------------------
        # Extract Question IDs
        # -------------------------

        question_ids = [
            question["id"]
            for question in result["questions"]
        ]

        print(
            "GENERATED QUESTION IDS:",
            question_ids,
        )

        # -------------------------
        # Number Successfully Created
        # -------------------------

        completed_count = len(
            question_ids
        )

        total_count = job["total",job["number_of_questions"]],
        

        # -------------------------
        # Update Job
        # -------------------------

        await ai_jobs_collection.update_one(
            {
                "_id": job_object_id
            },
            {
                "$set": {

                    "status": "completed",

                    "total": total_count,

                    "completed": completed_count,

                    "failed": 0,

                    "question_ids": question_ids,

                    "error": None,

                    "completed_at": (
                        datetime.now(
                            timezone.utc
                        )
                    ),
                }
            },
        )

        print(
            f"AI job completed: {job_id}"
        )

        print(
            "SAVED QUESTION IDS:",
            question_ids,
        )

        # -------------------------
        # Return Worker Result
        # -------------------------

        return {
            "job_id": job_id,

            "status": "completed",

            "question_ids": question_ids,
        }

    except Exception as error:

        # -------------------------
        # Job Failed
        # -------------------------

        print(
            f"AI job failed: {job_id}"
        )

        print(
            "ERROR:",
            repr(error),
        )

        # -------------------------
        # Update Failed Job
        # -------------------------

        await ai_jobs_collection.update_one(
            {
                "_id": job_object_id
            },
            {
                "$set": {

                    "status": "failed",

                    "error": str(error),

                    "completed_at": (
                        datetime.now(
                            timezone.utc
                        )
                    ),
                }
            },
        )

        # -------------------------
        # Let ARQ Know Job Failed
        # -------------------------

        raise


# -------------------------
# Worker Settings
# -------------------------

class WorkerSettings:

    functions = [
        generate_questions_job,
    ]

    redis_settings = (
        RedisSettings.from_dsn(
            settings.redis_url
        )
    )

    # Maximum time one job can run
    job_timeout = 900

    # Number of jobs worker can process
    # concurrently
    max_jobs = 2