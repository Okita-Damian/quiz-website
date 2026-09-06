
from fastapi import APIRouter, Depends, status

from dependencies.auth import require_role

from schemas.quiz import (
    QuizCreate,
    QuizResponse,
    QuizUpdate,
)

from services.quiz_service import (
    create_quiz,
    get_quiz,
    get_quizzes_by_topic,
    update_quiz,
    delete_quiz,
)


router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"],
)


# -------------------------
# Create Quiz
# Teacher / Parent
# -------------------------

@router.post(
    "",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_quiz_route(
    quiz_data: QuizCreate,
    current_user: dict = Depends(
        require_role(
            "teacher",
            "parent",
        )
    ),
):
        return await create_quiz(
            quiz_data,
            current_user["user_id"],
        )




# -------------------------
# Get Quiz
# Authenticated users
# -------------------------

@router.get(
    "/{quiz_id}",
    response_model=QuizResponse,
)
async def get_quiz_route(
    quiz_id: str,
    current_user: dict = Depends(
        require_role(
            "student",
            "teacher",
            "parent",
        )
    ),
):
    
        return await get_quiz(
            quiz_id,
            current_user["user_id"]
        )


# -------------------------
# Get Quizzes By Topic
# Authenticated users
# -------------------------

@router.get(
    "/topic/{topic_id}",
    response_model=list[QuizResponse],
)
async def get_quizzes_by_topic_route(
    topic_id: str,
    current_user: dict = Depends(
        require_role(
            "student",
            "teacher",
            "parent",
        )
    ),
):
        return await get_quizzes_by_topic(
            topic_id,
            current_user["user_id"]
        )

  


# -------------------------
# Update Quiz
# Teacher / Parent
# -------------------------

@router.patch(
    "/{quiz_id}",
    response_model=QuizResponse,
)
async def update_quiz_route(
    quiz_id: str,
    quiz_data: QuizUpdate,
    current_user: dict = Depends(
        require_role(
            "teacher",
            "parent",
        )
    ),
):
        return await update_quiz(
            quiz_id,
            quiz_data,
            current_user["user_id"],
        )

  


# -------------------------
# Delete Quiz
# Teacher / Parent
# -------------------------

@router.delete(
    "/{quiz_id}",
)
async def delete_quiz_route(
    quiz_id: str,
    current_user: dict = Depends(
        require_role(
            "teacher",
            "parent",
        )
    ),
):
        return await delete_quiz(
            quiz_id,
            current_user["user_id"],
        )

  

