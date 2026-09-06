
from fastapi import APIRouter,  status

from schemas.topic import (
    TopicCreate,
    TopicUpdate,
)
from services.topic_service import (
    create_topic,
    get_topics,
    get_topic,
    get_topics_for_grade,
    get_topics_for_subject,
    get_topics_for_grade_and_subject,
    update_topic,
    delete_topic,
)


router = APIRouter(
    prefix="/topics",
    tags=["Topics"],
)


# -------------------------
# Create Topic
# -------------------------

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_topic_route(
    topic_data: TopicCreate,
):
   
        return await create_topic(
            topic_data
        )

   


# -------------------------
# Get All Topics
# -------------------------

@router.get("")
async def get_topics_route():

    return await get_topics()


# -------------------------
# Get Topics For Grade
# -------------------------

@router.get("/grade/{grade_id}")
async def get_topics_for_grade_route(
    grade_id: str,
):
   
        return await get_topics_for_grade(
            grade_id
        )

   


# -------------------------
# Get Topics For Subject
# -------------------------

@router.get("/subject/{subject_id}")
async def get_topics_for_subject_route(
    subject_id: str,
):
   
        return await get_topics_for_subject(
            subject_id
        )

  

# -------------------------
# Get Topics For Grade + Subject
# -------------------------

@router.get(
    "/grade/{grade_id}/subject/{subject_id}"
)
async def get_topics_for_grade_and_subject_route(
    grade_id: str,
    subject_id: str,
):
   
        return await get_topics_for_grade_and_subject(
            grade_id,
            subject_id,
        )

  

# -------------------------
# Get One Topic
# -------------------------

@router.get("/{topic_id}")
async def get_topic_route(
    topic_id: str,
):
   
        return await get_topic(
            topic_id
        )

   

# -------------------------
# Update Topic
# -------------------------

@router.patch("/{topic_id}")
async def update_topic_route(
    topic_id: str,
    topic_data: TopicUpdate,
):
   
        return await update_topic(
            topic_id,
            topic_data,
        )

   


# -------------------------
# Delete Topic
# -------------------------

@router.delete("/{topic_id}")
async def delete_topic_route(
    topic_id: str,
):
   
        return await delete_topic(
            topic_id
        )

   