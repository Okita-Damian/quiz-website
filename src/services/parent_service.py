

from bson import ObjectId
from bson.errors import InvalidId
from errorHandlers.exceptions import NotFoundError


from config.db import database
from schemas.parent_schema import (
    ParentCreate,
    ParentUpdate,
)


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
# Serialize Parent
# -------------------------

def serialize_parent(
    parent: dict,
):
    return {
        "id": str(parent["_id"]),
        "name": parent["name"],
    }


# -------------------------
# Register Parent
# -------------------------

async def register_parent(
    parent_data: ParentCreate,
):
    parent_document = {
        "name": parent_data.name.strip(),
    }

    result = await parents_collection.insert_one(
        parent_document
    )

    parent = await parents_collection.find_one(
        {
            "_id": result.inserted_id
        }
    )

    return serialize_parent(
        parent
    )


# -------------------------
# Get Parent
# -------------------------

async def get_parent(
    parent_id: str,
):
    parent_object_id = validate_parent_id(
        parent_id
    )

    parent = await parents_collection.find_one(
        {
            "_id": parent_object_id
        }
    )

    if not parent:
        raise NotFoundError(
            "The parent you are looking for does not exist."
        )

    return serialize_parent(
        parent
    )


# -------------------------
# Update Parent
# -------------------------

async def update_parent(
    parent_id: str,
    parent_data: ParentUpdate,
):
    parent_object_id = validate_parent_id(
        parent_id
    )

    parent = await parents_collection.find_one(
        {
            "_id": parent_object_id
        }
    )

    if not parent:
        raise NotFoundError(
            "The parent you are trying to update does not exist."
        )

    update_data = parent_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise NotFoundError(
            "You must provide at least one field to update."
        )

    if "name" in update_data:
        update_data["name"] = (
            update_data["name"].strip()
        )

    await parents_collection.update_one(
        {
            "_id": parent_object_id
        },
        {
            "$set": update_data
        },
    )

    updated_parent = (
        await parents_collection.find_one(
            {
                "_id": parent_object_id
            }
        )
    )

    return serialize_parent(
        updated_parent
    )


# -------------------------
# Delete Parent
# -------------------------

async def delete_parent(
    parent_id: str,
):
    parent_object_id = validate_parent_id(
        parent_id
    )

    result = await parents_collection.delete_one(
        {
            "_id": parent_object_id
        }
    )

    if result.deleted_count == 0:
        raise NotFoundError(
            "The parent you are trying to delete does not exist."
        )

    return {
        "message": "Parent profile deleted successfully."
    }

