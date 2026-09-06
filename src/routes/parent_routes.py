
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.auth import require_role


from schemas.parent_schema import (
    ParentCreate,
    ParentLogin,
    ParentUpdate,
    ParentResponse,
)

from services.parent_service import (
    register_parent,
    get_parent,
    update_parent,
    delete_parent,
)

from dependencies.parent_auth_service import (
    login_parent,
)


router = APIRouter(
    prefix="/parents",
    tags=["Parents"],
)


# -------------------------
# Register
# -------------------------

@router.post(
    "/register",
    response_model=ParentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_parent_route(
    parent_data: ParentCreate,
):
        return await register_parent(
            parent_data
        )

# -------------------------
# Login
# -------------------------

@router.post("/login")
async def login_parent_route(
    login_data: ParentLogin,
):
        return await login_parent(
            login_data
        )


# -------------------------
# Get My Profile
# -------------------------

@router.get(
    "/me",
    response_model=ParentResponse,
)
async def get_my_profile(
    current_user: dict = Depends(
        require_role("parent")
    ),
):
    
        return await get_parent(
            current_user["user_id"]
        )


# -------------------------
# Update My Profile
# -------------------------

@router.patch(
    "/me",
    response_model=ParentResponse,
)
async def update_my_profile(
    parent_data: ParentUpdate,
    current_user: dict = Depends(
        require_role("parent")
    ),
):
        return await update_parent(
            current_user["user_id"],
            parent_data,
        )



# -------------------------
# Delete My Profile
# -------------------------

@router.delete("/me")
async def delete_my_profile(
    current_user: dict = Depends(
        require_role("parent")
    ),
):
        return await delete_parent(
            current_user["user_id"]
        )

