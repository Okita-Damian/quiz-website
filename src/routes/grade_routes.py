from fastapi import APIRouter, status

from schemas.grade_schema import (
    GradeCreate,
    GradeUpdate,
)
from services.grade_service import (
    create_grade,
    get_grades,
    get_grade,
    update_grade,
    delete_grade,
)


router = APIRouter(
    prefix="/grades",
    tags=["Grades"],
)


# -------------------------
# Create Grade
# -------------------------

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_grade_route(
    grade_data: GradeCreate,
):
        return await create_grade(
            grade_data
        )

   


# -------------------------
# Get All Grades
# -------------------------

@router.get("")
async def get_grades_route():

    return await get_grades()


# -------------------------
# Get One Grade
# -------------------------

@router.get("/{grade_id}")
async def get_grade_route(
    grade_id: str,
):
        return await get_grade(
            grade_id
        )


# -------------------------
# Update Grade
# -------------------------

@router.patch("/{grade_id}")
async def update_grade_route(
    grade_id: str,
    grade_data: GradeUpdate,
):
        return await update_grade(
            grade_id,
            grade_data,
        )


# -------------------------
# Delete Grade
# -------------------------

@router.delete("/{grade_id}")
async def delete_grade_route(
    grade_id: str,
):
        return await delete_grade(
            grade_id
        )

