
import jwt

from bson import ObjectId
from bson.errors import InvalidId
from errorHandlers.exceptions import NotFoundError


from config.db import database
from config.settings import settings
from schemas.parent_schema import ParentLogin


parents_collection = database.parents


# -------------------------
# Validate Parent ID
# -------------------------

def validate_parent_id(
    parent_id: str,
):
    try:
        return ObjectId(parent_id)

    except InvalidId:
        raise NotFoundError(
            "The parent ID you provided is not valid."
        )


# -------------------------
# Parent Login
# -------------------------

async def login_parent(
    login_data: ParentLogin,
):
    parent_object_id = validate_parent_id(
        login_data.parent_id
    )

    parent = await parents_collection.find_one(
        {
            "_id": parent_object_id
        }
    )

    if not parent:
        raise NotFoundError(
            "Invalid parent ID."
        )

    payload = {
        "user_id": str(parent["_id"]),
        "role": "parent",
    }

    access_token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "parent": {
            "id": str(parent["_id"]),
            "name": parent["name"],
        },
    }

