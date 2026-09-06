
from fastapi import (
    APIRouter,
    Depends,
    status,
)

from dependencies.auth import require_role

from schemas.question import (
    QuestionCreate,
    QuestionUpdate,
)

from services.question_service import (
    create_question,
    get_question,
    get_questions,
    update_question,
    delete_question,
)


router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
)


# ============================================================
# GET ALL QUESTIONS
# ============================================================

@router.get("")
async def get_questions_route(
    grade_id: str | None = None,
    subject_id: str | None = None,
    topic_id: str | None = None,
):
        return await get_questions(
            grade_id=grade_id,
            subject_id=subject_id,
            topic_id=topic_id,
        )

 


# ============================================================
# GET ONE QUESTION
# ============================================================

@router.get("/{question_id}")
async def get_question_route(
    question_id: str,
):
        return await get_question(
            question_id
        )



# ============================================================
# CREATE QUESTION
# Parent / Teacher
# ============================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_question_route(
    question_data: QuestionCreate,

    current_user: dict = Depends(
        require_role(
            "parent",
            "teacher",
        )
    ),
):
        return await create_question(
            question_data=question_data,
            created_by=current_user["user_id"],
            source=current_user["role"],
        )



# ============================================================
# UPDATE QUESTION
# Parent / Teacher
# ============================================================

@router.patch("/{question_id}")
async def update_question_route(
    question_id: str,

    question_data: QuestionUpdate,

    current_user: dict = Depends(
        require_role(
            "parent",
            "teacher",
        )
    ),
):
        return await update_question(
            question_id=question_id,
            question_data=question_data,
            current_user=current_user,
        )



# ============================================================
# DELETE QUESTION
# Parent / Teacher
# ============================================================

@router.delete("/{question_id}")
async def delete_question_route(
    question_id: str,

    current_user: dict = Depends(
        require_role(
            "parent",
            "teacher",
        )
    ),
):
        return await delete_question(
            question_id=question_id,
            current_user=current_user,
        )



