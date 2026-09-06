from fastapi import (
    APIRouter,
    Depends,
    status,
)

from dependencies.auth import require_role

from schemas.ai_question import (
    AIGenerateQuestion,
)

from services.ai_job_service import (
    create_ai_generation_job,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# -------------------------
# Generate Questions
# -------------------------

@router.post(
    "/questions/generate",
    status_code=status.HTTP_202_ACCEPTED,
)
async def generate_questions_route(
    request: AIGenerateQuestion,

    current_user: dict = Depends(
        require_role(
            "teacher",
            "parent",
            "student",
        )
    ),
):

    return await create_ai_generation_job(
        topic_id=request.topic_id,

        number_of_questions=(
            request.number_of_questions
        ),

        user_id=current_user["user_id"],
    )