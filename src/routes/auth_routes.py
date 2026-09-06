
from fastapi import APIRouter

from schemas.student import StudentLogin
from services.auth_service import login_student


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
async def login_student_route(
    login_data: StudentLogin,
):
        return await login_student(
            login_data
        )

   
