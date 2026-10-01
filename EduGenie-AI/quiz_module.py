import json
import re
from typing import Any

from ai_client import generate_text
from prompts import QUIZ_PROMPT


def clean_json_block(
    text: str
) -> str:

    cleaned = text.strip()

    # Remove ```json
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    # Remove ```
    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned
    )

    return cleaned.strip()


def validate_quiz(
    data: Any,
    expected_count: int
) -> dict:

    if not isinstance(
        data,
        dict
    ):

        raise ValueError(
            "Quiz response must be a JSON object."
        )

    if not isinstance(
        data.get("questions"),
        list
    ):

        raise ValueError(
            "Quiz response does not contain a questions list."
        )

    questions = data["questions"]

    if len(questions) != expected_count:

        raise ValueError(
            f"Expected {expected_count} questions, "
            f"received {len(questions)}."
        )

    for index, question in enumerate(
        questions,
        start=1
    ):

        if not isinstance(
            question,
            dict
        ):

            raise ValueError(
                f"Question {index} is invalid."
            )

        required_fields = {
            "question",
            "options",
            "correct_answer",
            "explanation"
        }

        missing_fields = (
            required_fields
            - set(question.keys())
        )

        if missing_fields:

            raise ValueError(
                f"Question {index} is missing: "
                + ", ".join(
                    sorted(missing_fields)
                )
            )

        options = question["options"]

        if not isinstance(
            options,
            list
        ):

            raise ValueError(
                f"Question {index} options must be a list."
            )

        if len(options) != 4:

            raise ValueError(
                f"Question {index} must have exactly 4 options."
            )

        if (
            question["correct_answer"]
            not in options
        ):

            raise ValueError(
                f"Question {index} has an invalid "
                "correct answer."
            )

    return data


async def generate_quiz(
    text: str,
    count: int = 3
) -> dict:

    prompt = QUIZ_PROMPT.format(
        text=text.strip(),
        count=count
    )

    raw_response = await generate_text(
        prompt,
        temperature=0.2,
        max_output_tokens=2400
    )

    cleaned_response = clean_json_block(
        raw_response
    )

    try:

        data = json.loads(
            cleaned_response
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            f"Gemini returned invalid quiz JSON: {exc}"
        ) from exc

    try:

        return validate_quiz(
            data,
            count
        )

    except ValueError as exc:

        raise RuntimeError(
            f"Quiz validation failed: {exc}"
        ) from exc