from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from config import settings
from explanation_module import explain_topic
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text


BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title="EduGenie - Google Gemini Powered Learning Assistant",
    description="AI-powered educational assistant for students.",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=30000
    )


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=10000
    )


class QuizRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=30000
    )

    count: int = Field(
        default=3,
        ge=1,
        le=10
    )


class LearningPathRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        max_length=500
    )

    level: str = Field(
        default="beginner",
        max_length=50
    )

    goals: str = Field(
        default="",
        max_length=2000
    )


# =====================================================
# HOME PAGE
# =====================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
            "model": settings.gemini_model,
        },
    )


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "gemini_configured": settings.gemini_configured,
        "model": settings.gemini_model,
    }


# =====================================================
# QUESTION & ANSWER
# =====================================================

@app.post("/qa")
async def qa(payload: QuestionRequest):

    try:
        answer = await answer_question(
            payload.question
        )

        return {
            "answer": answer
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )


# =====================================================
# EXPLAIN TOPIC
# =====================================================

@app.post("/explain")
async def explain(payload: TextRequest):

    try:
        answer = await explain_topic(
            payload.text
        )

        return {
            "answer": answer
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )


# =====================================================
# GENERATE QUIZ
# =====================================================

@app.post("/quiz")
async def quiz(payload: QuizRequest):

    try:
        quiz_data = await generate_quiz(
            payload.text,
            payload.count
        )

        return {
            "quiz": quiz_data
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )


# =====================================================
# SUMMARIZE TEXT
# =====================================================

@app.post("/summarize")
async def summarize(payload: TextRequest):

    try:
        summary = await summarize_text(
            payload.text
        )

        return {
            "summary": summary
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )


# =====================================================
# LEARNING PATH
# =====================================================

@app.post("/learn/recommendations")
async def learning_recommendations(
    payload: LearningPathRequest
):

    try:

        recommendations = (
            await get_learning_recommendations(
                payload.topic,
                payload.level,
                payload.goals
            )
        )

        return {
            "recommendations": recommendations
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc)
        )