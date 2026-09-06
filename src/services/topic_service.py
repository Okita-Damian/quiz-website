
from bson import ObjectId
from bson.errors import InvalidId
from errorHandlers.exceptions import NotFoundError


from config.db import database
from schemas.topic import TopicCreate, TopicUpdate


topics_collection = database.topics
subjects_collection = database.subjects
grades_collection = database.grades


# -------------------------
# Validate Object ID
# -------------------------

def validate_object_id(
    value: str,
    field_name: str,
):
    try:
        return ObjectId(value)

    except InvalidId:
        raise NotFoundError(
            f"The {field_name} ID you provided is not valid."
        )


# -------------------------
# Validate Grade
# -------------------------

async def validate_grade(
    grade_id: str,
):
    grade_object_id = validate_object_id(
        grade_id,
        "grade",
    )

    grade = await grades_collection.find_one(
        {
            "_id": grade_object_id
        }
    )

    if not grade:
        raise NotFoundError(
            "The grade you provided does not exist."
        )

    return grade_object_id


# -------------------------
# Validate Subject
# -------------------------

async def validate_subject(
    subject_id: str,
):
    subject_object_id = validate_object_id(
        subject_id,
        "subject",
    )

    subject = await subjects_collection.find_one(
        {
            "_id": subject_object_id
        }
    )

    if not subject:
        raise NotFoundError(
            "The subject you provided does not exist."
        )

    return subject


# -------------------------
# Validate Subject + Grade
# -------------------------

async def validate_subject_for_grade(
    subject_id: str,
    grade_id: str,
):
    subject = await validate_subject(
        subject_id
    )

    grade_object_id = await validate_grade(
        grade_id
    )

    if grade_object_id not in subject["grade_ids"]:

        raise NotFoundError(
            "This subject is not available for the selected grade."
        )

    return (
        ObjectId(subject_id),
        grade_object_id,
    )


# -------------------------
# Serialize Topic
# -------------------------

def serialize_topic(
    topic: dict,
):
    return {
        "id": str(topic["_id"]),
        "name": topic["name"],
        "description": topic.get(
            "description"
        ),
        "subject_id": str(
            topic["subject_id"]
        ),
        "grade_id": str(
            topic["grade_id"]
        ),
        "requires_image":topic.get(
            "requires_image",
            False,
        )
    }


# -------------------------
# Create Topic
# -------------------------

async def create_topic(
    topic_data: TopicCreate,
):
    (
        subject_object_id,
        grade_object_id,
    ) = await validate_subject_for_grade(
        topic_data.subject_id,
        topic_data.grade_id,
    )

    topic_name = topic_data.name.strip()

    # Prevent duplicate topic inside
    # the same subject and grade

    existing_topic = (
        await topics_collection.find_one(
            {
                "name": topic_name,
                "subject_id": subject_object_id,
                "grade_id": grade_object_id,
            }
        )
    )

    if existing_topic:
        raise NotFoundError(
            "This topic already exists for this subject and grade."
        )

    topic_document = {
        "name": topic_name,
        "description": (
            topic_data.description.strip()
            if topic_data.description
            else None
        ),
        "subject_id": subject_object_id,
        "grade_id": grade_object_id,
        "requires_image": topic_data.requires_image
    }

    result = await topics_collection.insert_one(
        topic_document
    )

    topic = await topics_collection.find_one(
        {
            "_id": result.inserted_id
        }
    )

    return serialize_topic(topic)


# -------------------------
# Get All Topics
# -------------------------

async def get_topics():
    cursor = topics_collection.find(
        {}
    ).sort(
        "name",
        1,
    )

    topics = []

    async for topic in cursor:
        topics.append(
            serialize_topic(topic)
        )

    return topics


# -------------------------
# Get One Topic
# -------------------------

async def get_topic(
    topic_id: str,
):
    topic_object_id = validate_object_id(
        topic_id,
        "topic",
    )

    topic = await topics_collection.find_one(
        {
            "_id": topic_object_id
        }
    )

    if not topic:
        raise NotFoundError(
            "The topic you are looking for does not exist."
        )

    return serialize_topic(topic)


# -------------------------
# Get Topics By Grade
# -------------------------

async def get_topics_for_grade(
    grade_id: str,
):
    grade_object_id = await validate_grade(
        grade_id
    )

    cursor = topics_collection.find(
        {
            "grade_id": grade_object_id
        }
    ).sort(
        "name",
        1,
    )

    topics = []

    async for topic in cursor:
        topics.append(
            serialize_topic(topic)
        )

    return topics


# -------------------------
# Get Topics By Subject
# -------------------------

async def get_topics_for_subject(
    subject_id: str,
):
    subject_object_id = validate_object_id(
        subject_id,
        "subject",
    )

    subject = await subjects_collection.find_one(
        {
            "_id": subject_object_id
        }
    )

    if not subject:
        raise NotFoundError(
            "The subject you are looking for does not exist."
        )

    cursor = topics_collection.find(
        {
            "subject_id": subject_object_id
        }
    ).sort(
        "name",
        1,
    )

    topics = []

    async for topic in cursor:
        topics.append(
            serialize_topic(topic)
        )

    return topics


# -------------------------
# Get Topics By Grade + Subject
# -------------------------

async def get_topics_for_grade_and_subject(
    grade_id: str,
    subject_id: str,
):
    (
        subject_object_id,
        grade_object_id,
    ) = await validate_subject_for_grade(
        subject_id,
        grade_id,
    )

    cursor = topics_collection.find(
        {
            "grade_id": grade_object_id,
            "subject_id": subject_object_id,
        }
    ).sort(
        "name",
        1,
    )

    topics = []

    async for topic in cursor:
        topics.append(
            serialize_topic(topic)
        )

    return topics


# -------------------------
# Update Topic
# -------------------------

async def update_topic(
    topic_id: str,
    topic_data: TopicUpdate,
):
    topic_object_id = validate_object_id(
        topic_id,
        "topic",
    )

    existing_topic = await topics_collection.find_one(
        {
            "_id": topic_object_id
        }
    )

    if not existing_topic:
        raise NotFoundError(
            "The topic you are trying to update does not exist."
        )

    update_data = topic_data.model_dump(
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

    await topics_collection.update_one(
        {
            "_id": topic_object_id
        },
        {
            "$set": update_data
        },
    )

    updated_topic = await topics_collection.find_one(
        {
            "_id": topic_object_id
        }
    )

    return serialize_topic(
        updated_topic
    )


# -------------------------
# Delete Topic
# -------------------------

async def delete_topic(
    topic_id: str,
):
    topic_object_id = validate_object_id(
        topic_id,
        "topic",
    )

    result = await topics_collection.delete_one(
        {
            "_id": topic_object_id
        }
    )

    if result.deleted_count == 0:
        raise NotFoundError(
            "The topic you are trying to delete does not exist."
        )

    return {
        "message": "Topic deleted successfully."
    }

