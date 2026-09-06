
from fastapi import APIRouter, Depends,  status

from dependencies.auth import       get_current_user

from schemas.student import (
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)
from services.student_service import (
    register_student,
    get_student,
    update_student,
    delete_student,
)


router = APIRouter(
    prefix="/students",
    tags=["Students"],
)


# -------------------------
# Register Student
# -------------------------

@router.post(
    "/register",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_student_route(
    student_data: StudentCreate,
):
    
        return await register_student(
            student_data
        )

    


# -------------------------
# Get My Profile
# -------------------------

@router.get(
    "/me",
    response_model=StudentResponse,
)
async def get_my_profile(
    current_user: dict = Depends(
              get_current_user

    ),
):
    
        return await get_student(
            current_user["user_id"]
        )

   


# -------------------------
# Update My Profile
# -------------------------

@router.patch(
    "/me",
    response_model=StudentResponse,
)
async def update_my_profile(
    student_data: StudentUpdate,
    current_user: dict = Depends(
              get_current_user

    ),
):
    
        return await update_student(
            current_user["user_id"],
            student_data,
        )

   


# -------------------------
# Delete My Profile
# -------------------------

@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
)
async def delete_my_profile(
    current_user: dict = Depends(
              get_current_user

    ),
):
    
        return await delete_student(
            current_user["user_id"]
        )

   

