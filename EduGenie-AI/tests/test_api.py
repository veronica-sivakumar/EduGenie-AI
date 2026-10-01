import pytest
from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


# =====================================================
# HOME PAGE
# =====================================================

def test_home_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "EduGenie" in response.text


# =====================================================
# HEALTH CHECK
# =====================================================

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# =====================================================
# API ROUTE TESTS
# =====================================================

@pytest.mark.parametrize(
    "path,payload",
    [
        (
            "/qa",
            {
                "question": "What is Artificial Intelligence?"
            },
        ),
        (
            "/explain",
            {
                "text": "Explain recursion."
            },
        ),
        (
            "/summarize",
            {
                "text": "This is educational text."
            },
        ),
        (
            "/quiz",
            {
                "text": "Python is a programming language.",
                "count": 3,
            },
        ),
        (
            "/learn/recommendations",
            {
                "topic": "SQL",
                "level": "beginner",
                "goals": "Learn databases",
            },
        ),
    ],
)
def test_api_routes(path, payload, monkeypatch):

    async def fake_generation(*args, **kwargs):
        return "Mocked AI response"

    # Mock normal AI endpoints
    monkeypatch.setattr(
        main,
        "answer_question",
        fake_generation,
    )

    monkeypatch.setattr(
        main,
        "explain_topic",
        fake_generation,
    )

    monkeypatch.setattr(
        main,
        "summarize_text",
        fake_generation,
    )

    monkeypatch.setattr(
        main,
        "get_learning_recommendations",
        fake_generation,
    )

    # Mock quiz endpoint
    async def fake_quiz(*args, **kwargs):

        count = payload.get("count", 3)

        questions = []

        for index in range(count):
            questions.append(
                {
                    "question": f"Mock Question {index + 1}",
                    "options": [
                        "A",
                        "B",
                        "C",
                        "D",
                    ],
                    "correct_answer": "A",
                    "explanation": "Mock explanation",
                }
            )

        return {
            "questions": questions
        }

    monkeypatch.setattr(
        main,
        "generate_quiz",
        fake_quiz,
    )

    # Send request
    response = client.post(
        path,
        json=payload,
    )

    # All valid requests must return HTTP 200
    assert response.status_code == 200


# =====================================================
# INVALID REQUEST
# =====================================================

def test_bad_payload():

    response = client.post(
        "/qa",
        json={
            "question": ""
        },
    )

    # Empty question should be rejected by Pydantic
    assert response.status_code == 422