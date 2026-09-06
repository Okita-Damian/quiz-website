
from fastapi import APIRouter, Depends,  status

from dependencies.auth import require_role

from schemas.teacher_schema import (
    TeacherCreate,
    TeacherLogin,
    TeacherUpdate,
    TeacherResponse,
)

from services.teacher_service import (
    register_teacher,
    get_teacher,
    update_teacher,
    delete_teacher,
)

from dependencies.teacher_auth_service import (
    login_teacher,
)


router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"],
)


# -------------------------
# Register Teacher
# -------------------------

@router.post(
    "/register",
    response_model=TeacherResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_teacher_route(
    teacher_data: TeacherCreate,
):
    
        return await register_teacher(
            teacher_data
        )

    

# -------------------------
# Login Teacher
# -------------------------

@router.post("/login")
async def login_teacher_route(
    login_data: TeacherLogin,
):
    
        return await login_teacher(
            login_data
        )

   


# -------------------------
# Get My Profile
# -------------------------

@router.get(
    "/me",
    response_model=TeacherResponse,
)
async def get_my_profile(
    current_user: dict = Depends(
        require_role("teacher")
    ),
):
    
        return await get_teacher(
            current_user["user_id"]
        )

    


# -------------------------
# Update My Profile
# -------------------------

@router.patch(
    "/me",
    response_model=TeacherResponse,
)
async def update_my_profile(
    teacher_data: TeacherUpdate,
    current_user: dict = Depends(
        require_role("teacher")
    ),
):
    
        return await update_teacher(
            current_user["user_id"],
            teacher_data,
        )

    

# -------------------------
# Delete My Profile
# -------------------------

@router.delete("/me")
async def delete_my_profile(
    current_user: dict = Depends(
        require_role("teacher")
    ),
):
    
        return await delete_teacher(
            current_user["user_id"]
        )

    