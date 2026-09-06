from fastapi import (
    APIRouter,
    Depends,
    status,
)

from dependencies.auth import require_role

from schemas.ai_job import (
    AIJobResponse,
    AIJobQuestionsResponse,
)

from services.ai_job_service import (
    get_job_status,
    get_job_questions,
)


router = APIRouter(
    prefix="/ai/jobs",
    tags=["AI Jobs"],
)


# -------------------------
# Get AI Job Status
# -------------------------

@router.get(
    "/{job_id}",
    response_model=AIJobResponse,
    status_code=status.HTTP_200_OK,
)
async def get_ai_job_status(
    job_id: str,

    current_user: dict = Depends(
        require_role(
            "teacher",
            "parent",
            "student",
        )
    ),
):

        return await get_job_status(
            job_id,
            current_user,
        )


# -------------------------
# Get AI Job Questions
# -------------------------

@router.get(
    "/{job_id}/questions",
    response_model=AIJobQuestionsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_ai_job_questions(
    job_id: str,

    current_user: dict = Depends(
        require_role(
            "teacher",
            "parent",
            "student",
        )
    ),
):

        return await get_job_questions(
            job_id=job_id,
            current_user=current_user,
        )

   