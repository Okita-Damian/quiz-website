
from bson import ObjectId
from bson.errors import InvalidId

from errorHandlers.exceptions import NotFoundError

from config.db import database

from schemas.ai_question import (
    AIGenerateQuestion,
    GeneratedQuestion,
)

from services.llm_service import (
    generate_questions_with_llm,
)

from services.image_service import (
    generate_image,
)


topics_collection = database.topics
subjects_collection = database.subjects
grades_collection = database.grades
questions_collection = database.questions


# -------------------------
# Validate ObjectId
# -------------------------

def validate_object_id(
    value: str,
    field_name: str,
):
    print(
        f"[DEBUG] Validating {field_name}: {value}"
    )

    try:
        object_id = ObjectId(value)

        print(
            f"[DEBUG] {field_name} is valid: {object_id}"
        )

        return object_id

    except (InvalidId, TypeError) as error:

        print(
            f"[DEBUG] Invalid {field_name}: {value}"
        )

        raise NotFoundError(
            f"The {field_name} you provided is not valid."
        ) from error


# -------------------------
# Get Topic
# -------------------------

async def get_topic(
    topic_id: str,
):

    print(
        "[STEP 1] Getting topic..."
    )

    topic_object_id = validate_object_id(
        topic_id,
        "topic ID",
    )

    topic = await topics_collection.find_one(
        {
            "_id": topic_object_id
        }
    )

    if not topic:

        print(
            "[ERROR] Topic was not found."
        )

        raise NotFoundError(
            "The topic you provided does not exist."
        )

    print(
        "[STEP 1] Topic loaded successfully."
    )

    return topic


# -------------------------
# Get Subject
# -------------------------

async def get_subject(
    subject_id: ObjectId,
):

    print(
        "[STEP 2] Getting subject..."
    )

    subject = await subjects_collection.find_one(
        {
            "_id": subject_id
        }
    )

    if not subject:

        print(
            "[ERROR] Subject was not found."
        )

        raise NotFoundError(
            "The subject associated with this topic "
            "does not exist."
        )

    print(
        "[STEP 2] Subject loaded successfully."
    )

    return subject


# -------------------------
# Get Grade
# -------------------------

async def get_grade(
    grade_id: ObjectId,
):

    print(
        "[STEP 3] Getting grade..."
    )

    grade = await grades_collection.find_one(
        {
            "_id": grade_id
        }
    )

    if not grade:

        print(
            "[ERROR] Grade was not found."
        )

        raise NotFoundError(
            "The grade associated with this topic "
            "does not exist."
        )

    print(
        "[STEP 3] Grade loaded successfully."
    )

    return grade


# -------------------------
# Validate Generated Question
# -------------------------

def validate_generated_question(
    question: GeneratedQuestion,
    requires_image: bool,
):

    print(
        "[STEP 7] Validating generated question..."
    )

    # -------------------------
    # Validate Options
    # -------------------------

    if len(question.options) != 4:

        print(
            "[ERROR] Generated question does not "
            "contain exactly 4 options."
        )

        raise NotFoundError(
            "AI generated questions must contain "
            "exactly 4 options."
        )

    print(
        "[DEBUG] Question contains exactly 4 options."
    )

    # -------------------------
    # Validate Correct Answer
    # -------------------------

    if question.correct_answer not in question.options:

        print(
            "[ERROR] Correct answer is not "
            "one of the options."
        )

        raise NotFoundError(
            "The correct answer must be one of the "
            "provided options."
        )

    print(
        "[DEBUG] Correct answer is valid."
    )

    # -------------------------
    # Validate Image Requirement
    # -------------------------

    if requires_image and not question.image_prompt:

        print(
            "[ERROR] Image is required but "
            "image_prompt is missing."
        )

        raise NotFoundError(
            "This topic requires an image, but the AI "
            "did not generate an image prompt."
        )

    # -------------------------
    # Validate No Image Requirement
    # -------------------------

    if not requires_image and question.image_prompt:

        print(
            "[ERROR] Image prompt was generated "
            "when image is not required."
        )

        raise NotFoundError(
            "This topic does not require an image."
        )

    print(
        "[STEP 7] Generated question validated successfully."
    )


# -------------------------
# Generate Questions
# -------------------------

async def generate_questions(
    request: AIGenerateQuestion,
    current_user: dict,
):

    print(
        "\n========================================"
    )

    print(
        "[START] generate_questions()"
    )

    print(
        "========================================\n"
    )

    # -------------------------
    # STEP 1
    # Get Topic
    # -------------------------

    topic = await get_topic(
        request.topic_id
    )

    # -------------------------
    # STEP 2
    # Get Subject
    # -------------------------

    print(
        "[STEP 2] Extracting subject ID..."
    )

    subject_id = topic["subject_id"]

    if not subject_id:

        print(
            "[ERROR] Topic has no subject ID."
        )

        raise NotFoundError(
            "This topic is not associated with a subject."
        )

    subject = await get_subject(
        subject_id
    )

    # -------------------------
    # STEP 3
    # Get Grade
    # -------------------------

    print(
        "[STEP 3] Extracting grade ID..."
    )

    topic_grade_id = topic["grade_id"]

    if not topic_grade_id:

        print(
            "[ERROR] Topic has no grade ID."
        )

        raise NotFoundError(
            "This topic is not associated with a grade."
        )

    grade_object_id = validate_object_id(
        str(topic_grade_id),
        "grade ID",
    )

    grade = await get_grade(
        grade_object_id
    )

    # -------------------------
    # STEP 4
    # Verify Subject / Grade
    # -------------------------

    print(
        "[STEP 4] Verifying subject and grade..."
    )

    subject_grade_ids = subject["grade_ids"]
    

    normalized_grade_ids = []

    for grade_id in subject_grade_ids:

        try:

            normalized_grade_ids.append(
                ObjectId(
                    str(grade_id)
                )
            )

        except (InvalidId, TypeError):

            print(
                f"[DEBUG] Skipping invalid grade ID: {grade_id}"
            )

            continue

    if grade_object_id not in normalized_grade_ids:

        print(
            "[ERROR] Grade is not associated with subject."
        )

        raise NotFoundError(
            "The selected grade is not associated "
            "with this subject."
        )

    print(
        "[STEP 4] Subject / grade verification successful."
    )

    # -------------------------
    # STEP 5
    # Verify Topic / Subject
    # -------------------------

    print(
        "[STEP 5] Verifying topic / subject relationship..."
    )

    if topic["subject_id"] != subject["_id"]:

        print(
            "[ERROR] Topic does not belong to subject."
        )

        raise NotFoundError(
            "The selected topic does not belong "
            "to this subject."
        )

    print(
        "[STEP 5] Topic / subject verification successful."
    )

    # -------------------------
    # STEP 6
    # Get Names
    # -------------------------

    print(
        "[STEP 6] Preparing generation information..."
    )

    grade_name = grade["name"]

    subject_name = subject["name"]

    topic_name = topic["name"]

    # -------------------------
    # Determine Image Requirement
    # -------------------------

    requires_image = topic["requires_image"],False,
    

    print(
        f"[DEBUG] Grade: {grade_name}"
    )

    print(
        f"[DEBUG] Subject: {subject_name}"
    )

    print(
        f"[DEBUG] Topic: {topic_name}"
    )

    print(
        f"[DEBUG] Number of questions: "
        f"{request.number_of_questions}"
    )

    print(
        f"[DEBUG] Requires image: "
        f"{requires_image}"
    )

    # -------------------------
    # STEP 6
    # Generate With LLM
    # -------------------------

    print(
        "\n[STEP 6] Calling Groq LLM..."
    )

    generated_questions = (
        await generate_questions_with_llm(
            grade_name=grade_name,
            subject_name=subject_name,
            topic_name=topic_name,
            number_of_questions=(
                request.number_of_questions
            ),
            requires_image=requires_image,
        )
    )

    print(
        "[STEP 6] Groq LLM returned successfully."
    )

    print(
        "[DEBUG] Number of generated questions:",
        len(
            generated_questions.questions
        ),
    )

    # -------------------------
    # Prepare Saved Questions
    # -------------------------

    saved_questions = []

    # -------------------------
    # STEP 7
    # Process Questions
    # -------------------------

    for index, question in enumerate(
        generated_questions.questions,
        start=1,
    ):

        print(
            "\n----------------------------------------"
        )

        print(
            f"[STEP 7] Processing question "
            f"{index}/{len(generated_questions.questions)}"
        )

        print(
            "----------------------------------------"
        )

        print(
            "[DEBUG] Question:",
            question.question,
        )

        # -------------------------
        # Validate Question
        # -------------------------

        validate_generated_question(
            question,
            requires_image,
        )

        # -------------------------
        # STEP 8
        # Generate Image
        # -------------------------

        image_url = None

        if requires_image:

            print(
                f"[STEP 8] Generating image "
                f"for question {index}..."
            )

            print(
                "[DEBUG] Image prompt:",
                question.image_prompt,
            )

            image_url = await generate_image(
                question.image_prompt
            )

            print(
                f"[STEP 8] Image generated successfully "
                f"for question {index}."
            )

            print(
                "[DEBUG] Image URL:",
                image_url,
            )

        else:

            print(
                f"[STEP 8] Image not required "
                f"for question {index}."
            )

        # -------------------------
        # STEP 9
        # Creator
        # -------------------------

        print(
            "[STEP 9] Validating creator ID..."
        )

        created_by = validate_object_id(
            current_user["user_id"],
            "user ID",
        )

        print(
            "[STEP 9] Creator ID validated."
        )

        # -------------------------
        # STEP 10
        # Create Document
        # -------------------------

        print(
            f"[STEP 10] Building MongoDB document "
            f"for question {index}..."
        )

        question_document = {

            "question": question.question,

            "options": question.options,

            "correct_answer": (
                question.correct_answer
            ),

            "explanation": (
                question.explanation
            ),

            "grade_id": grade["_id"],

            "subject_id": subject["_id"],

            "topic_id": topic["_id"],

            "question_type": (
                "image"
                if requires_image
                else "text"
            ),

            "source": "llm",

            "created_by": created_by,

            "image_prompt": (
                question.image_prompt
                if requires_image
                else None
            ),

            "image_url": image_url,
        }

        print(
            "[STEP 10] MongoDB document prepared."
        )

        # -------------------------
        # STEP 11
        # Save Question
        # -------------------------

        print(
            f"[STEP 11] Saving question "
            f"{index} to MongoDB..."
        )

        result = (
            await questions_collection.insert_one(
                question_document
            )
        )

        print(
            f"[STEP 11] Question {index} saved."
        )

        print(
            "[DEBUG] MongoDB question ID:",
            result.inserted_id,
        )

        # -------------------------
        # STEP 12
        # Build Response
        # -------------------------

        print(
            f"[STEP 12] Building response "
            f"for question {index}..."
        )

        saved_questions.append(
            {
                "id": str(
                    result.inserted_id
                ),

                "question": question.question,

                "options": question.options,

                "correct_answer": (
                    question.correct_answer
                ),

                "explanation": (
                    question.explanation
                ),

                "grade_id": str(
                    grade["_id"]
                ),

                "subject_id": str(
                    subject["_id"]
                ),

                "topic_id": str(
                    topic["_id"]
                ),

                "question_type": (
                    "image"
                    if requires_image
                    else "text"
                ),

                "source": "llm",

                "created_by": str(
                    created_by
                ),

                "image_url": image_url,
            }
        )

        print(
            f"[STEP 12] Question {index} "
            "response prepared."
        )

    # -------------------------
    # STEP 13
    # Final Result
    # -------------------------

    print(
        "\n[STEP 13] All questions processed."
    )

    print(
        "[DEBUG] Total saved questions:",
        len(saved_questions),
    )

    print(
        "[DEBUG] Saved question IDs:",
        [
            question["id"]
            for question in saved_questions
        ],
    )

    final_result = {

        "grade": grade_name,

        "subject": subject_name,

        "topic": topic_name,

        "requires_image": requires_image,

        "questions": saved_questions,
    }

    # -------------------------
    # STEP 14
    # Return
    # -------------------------

    print(
        "\n[STEP 14] Returning generated questions "
        "to AI worker..."
    )

    print(
        "[DEBUG] Final result:",
        final_result,
    )

    print(
        "\n========================================"
    )

    print(
        "[SUCCESS] generate_questions() completed"
    )

    print(
        "========================================\n"
    )

    return final_result

