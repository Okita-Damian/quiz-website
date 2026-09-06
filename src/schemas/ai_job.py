from pydantic import BaseModel


# -------------------------
# AI Job Status Response
# -------------------------

class AIJobResponse(BaseModel):
    job_id: str

    status: str

    total: int

    completed: int

    failed: int

    question_ids: list[str]

    error: str | None = None


# -------------------------
# Generated Question Response
# -------------------------

class AIJobQuestionResponse(BaseModel):
    id: str

    question: str

    options: list[str]

    correct_answer: str

    explanation: str | None = None

    grade_id: str

    subject_id: str

    topic_id: str

    question_type: str

    source: str

    image_url: str | None = None


# -------------------------
# AI Job Questions Response
# -------------------------

class AIJobQuestionsResponse(BaseModel):
    job_id: str

    status: str

    questions: list[AIJobQuestionResponse]