# services/llm_service.py

import json

from groq import AsyncGroq

from config.settings import settings
from errorHandlers.exceptions import NotFoundError


from schemas.ai_question import (
    GeneratedQuestions,
)

from prompt.system_prompt import (
    build_quiz_system_prompt,
)


# =========================================================
# Groq Client
# =========================================================

client = AsyncGroq(
    api_key=settings.groq_api_key
)


# =========================================================
# Generate Questions With LLM
# =========================================================

async def generate_questions_with_llm(
    grade_name: str,
    subject_name: str,
    topic_name: str,
    number_of_questions: int,
    requires_image: bool,
):

    print("\n========================================")
    print("[LLM SERVICE] Starting question generation")
    print("========================================")

    print(
        f"[LLM SERVICE] Grade: {grade_name}"
    )

    print(
        f"[LLM SERVICE] Subject: {subject_name}"
    )

    print(
        f"[LLM SERVICE] Topic: {topic_name}"
    )

    print(
        f"[LLM SERVICE] Number of questions: "
        f"{number_of_questions}"
    )

    print(
        f"[LLM SERVICE] Requires image: "
        f"{requires_image}"
    )

    # =====================================================
    # Build System Prompt
    # =====================================================

    print(
        "[LLM SERVICE] Building system prompt..."
    )

    system_prompt = build_quiz_system_prompt(
        grade_name=grade_name,
        subject_name=subject_name,
        topic_name=topic_name,
        number_of_questions=number_of_questions,
        requires_image=requires_image,
    )

    print(
        "[LLM SERVICE] System prompt created."
    )

    # =====================================================
    # Call Groq
    # =====================================================

    print(
        "[LLM SERVICE] Calling Groq..."
    )

    try:

        response = await client.chat.completions.create(

            model=settings.groq_model,

            temperature=0.2,

            response_format={
                "type": "json_object"
            },

            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        "Generate the requested questions "
                        "using the system instructions."
                    ),
                },
            ],
        )

    except Exception as error:

        print(
            "[LLM SERVICE] Groq request failed."
        )

        print(
            "[LLM SERVICE] ERROR:",
            repr(error),
        )

        raise NotFoundError(
            "The AI question generation service "
            "is currently unavailable."
        ) from error

    # =====================================================
    # Get Response
    # =====================================================

    print(
        "[LLM SERVICE] Groq returned successfully."
    )

    raw_content = response.choices[0].message.content

    print(
        "[LLM SERVICE] Raw LLM response received."
    )

    # =====================================================
    # Parse JSON
    # =====================================================

    try:

        data = json.loads(
            raw_content
        )

    except json.JSONDecodeError as error:

        print(
            "[LLM SERVICE] Failed to parse LLM JSON."
        )

        print(
            "[LLM SERVICE] Raw response:",
            raw_content,
        )

        raise NotFoundError(
            "The AI returned an invalid question format."
        ) from error

    # =====================================================
    # Validate With Pydantic
    # =====================================================

    try:

        generated_questions = (
            GeneratedQuestions.model_validate(
                data
            )
        )

    except Exception as error:

        print(
            "[LLM SERVICE] LLM response failed "
            "schema validation."
        )

        print(
            "[LLM SERVICE] Validation error:",
            repr(error),
        )

        raise NotFoundError(
            "The AI generated questions in an "
            "invalid format."
        ) from error

    # =====================================================
    # Final Debugging
    # =====================================================

    print(
        "[LLM SERVICE] Generated questions:",
        len(
            generated_questions.questions
        ),
    )

    for index, question in enumerate(
        generated_questions.questions,
        start=1,
    ):

        print(
            f"[LLM SERVICE] Question {index}: "
            f"{question.question}"
        )

        print(
            f"[LLM SERVICE] Correct answer: "
            f"{question.correct_answer}"
        )

        print(
            f"[LLM SERVICE] Image prompt: "
            f"{question.image_prompt}"
        )

    print(
        "========================================"
    )

    return generated_questions