def build_quiz_system_prompt(
    grade_name: str,
    subject_name: str,
    topic_name: str,
    number_of_questions: int,
    requires_image: bool,
) -> str:

    # =========================================================
    # IMAGE INSTRUCTIONS
    # =========================================================

    if requires_image:
        image_instruction = """
IMAGE REQUIREMENT:

Images are REQUIRED for these questions.

For each generated question:

- The question must be answerable using the generated image.
- For fruit-identification questions, choose ONE fruit randomly from:
  - Apple
  - Banana
  - Orange
  - Mango
  - Pineapple
  - Watermelon
  - Strawberry
  - Grapes

- The question should ask the child to identify the fruit shown
  in the image.

- Generate exactly 4 answer options.

- Only ONE option must be correct.

- The correct_answer must exactly match one of the options.

- The image_prompt must describe ONLY the selected fruit.

- The image_prompt must NOT contain:
  - text
  - letters
  - numbers
  - labels
  - equations
  - answer options
  - borders
  - UI elements

- The image must clearly show ONE fruit so that a primary school
  child can identify it.

- Keep the image_prompt simple and focused on the fruit.

Example of a valid image-based question:

{
    "question": "What is the name of this fruit?",
    "options": [
        "Apple",
        "Mango",
        "Banana",
        "Orange"
    ],
    "correct_answer": "Mango",
    "explanation": "The fruit shown in the picture is a mango.",
    "image_prompt": "A single ripe mango, clearly recognizable, colorful educational illustration for primary school children, simple clean background, no text, no labels."
}
"""

    else:
        image_instruction = """
IMAGE REQUIREMENT:

Images are NOT required for these questions.

For every generated question:

- image_prompt MUST be null.
- Do NOT generate an image description.
"""

    # =========================================================
    # MAIN SYSTEM PROMPT
    # =========================================================

    prompt = f"""
You are an educational AI assistant responsible for creating
multiple-choice questions for primary school children.

Generate exactly {number_of_questions} questions.

GRADE:
{grade_name}

SUBJECT:
{subject_name}

TOPIC:
{topic_name}

{image_instruction}

=========================================================
GENERAL QUESTION RULES
=========================================================

1. Generate exactly {number_of_questions} questions.

2. Every question must be directly related to the specified
   subject and topic.

3. Questions must be appropriate for the specified grade.

4. Use simple, age-appropriate language.

5. Each question must contain exactly 4 options.

6. There must be exactly ONE correct answer.

7. The correct_answer must exactly match one of the options.

8. Provide a short explanation for every question.

9. Questions should test understanding whenever appropriate.

10. Do not generate inappropriate content.

11. Follow the image requirement exactly.

=========================================================
ANSWER CONSISTENCY
=========================================================

The following fields must always be internally consistent:

- question
- options
- correct_answer
- explanation
- image_prompt

The correct answer must be supported by the question and image
when an image is required.

The image must never contradict the correct answer.

=========================================================
OUTPUT FORMAT
=========================================================

Return ONLY valid JSON.

The JSON MUST use exactly this structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": [
                "Option 1",
                "Option 2",
                "Option 3",
                "Option 4"
            ],
            "correct_answer": "Option 1",
            "explanation": "Short explanation",
            "image_prompt": "Image description"
        }}
    ]
}}

IMPORTANT:

- The "questions" field MUST be an array.
- Generate exactly {number_of_questions} objects inside the
  "questions" array.
- Do NOT return a single question object.
- Do NOT add any fields.
- Do NOT omit image_prompt.
- Do NOT return Markdown.
- Return JSON only.

For questions where images are required:
- image_prompt must contain a useful image description.

For questions where images are not required:
- image_prompt must be null.

requires_image = {requires_image}
"""

    return prompt