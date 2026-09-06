
from fastapi import APIRouter, HTTPException, status

from schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
)
from services.subject_service import (
    create_subject,
    get_subjects,
    get_subject,
    get_subjects_for_grade,
    update_subject,
    delete_subject,
)


router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"],
)


# -------------------------
# Create Subject
# -------------------------

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_subject_route(
    subject_data: SubjectCreate,
):
    try:
        return await create_subject(
            subject_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# -------------------------
# Get All Subjects
# -------------------------

@router.get("")
async def get_subjects_route():

    return await get_subjects()


# -------------------------
# Get Subjects For Grade
# -------------------------

@router.get("/grade/{grade_id}")
async def get_subjects_for_grade_route(
    grade_id: str,
):
    try:
        return await get_subjects_for_grade(
            grade_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# -------------------------
# Get One Subject
# -------------------------

@router.get("/{subject_id}")
async def get_subject_route(
    subject_id: str,
):
    try:
        return await get_subject(
            subject_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


# -------------------------
# Update Subject
# -------------------------

@router.patch("/{subject_id}")
async def update_subject_route(
    subject_id: str,
    subject_data: SubjectUpdate,
):
    try:
        return await update_subject(
            subject_id,
            subject_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


# -------------------------
# Delete Subject
# -------------------------

@router.delete("/{subject_id}")
async def delete_subject_route(
    subject_id: str,
):
    
        return await delete_subject(
            subject_id
        )

  