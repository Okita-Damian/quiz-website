from routes.student_routes import router as student_router
from routes.subject_routes import router as subject_router
from routes.topic_routes import router as topic_router
from routes.question_routes import router as question_router

from routes.auth_routes import (
    router as auth_router,
)

from routes.grade_routes import (
    router as grade_router,
)

from routes.parent_routes import router as parent_router

from routes.teacher_routes import router as teacher_router

from routes.ai_routes import router as ai_router

from routes.ai_job_router import router as ai_job_router

from errorHandlers.exceptions import AppError
from errorHandlers.exception_handlers import app_exception_handler



from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.db import (
    connect_to_database,
    close_database_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_database()

    yield

    await close_database_connection()


app = FastAPI(
    title="Primary School Quiz API",
    description="AI-powered quiz platform for primary school students",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(grade_router)
app.include_router(subject_router)
app.include_router(topic_router)
app.include_router(student_router)
app.include_router(auth_router)
app.include_router(parent_router)
app.include_router(teacher_router)
app.include_router(question_router)
app.include_router(ai_job_router)


app.include_router(ai_router)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Primary Quiz API",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "success",
        "message": "Quiz API is running",
    }


app.add_exception_handler(
    AppError,
    app_exception_handler,
)