from ai_client import generate_text
from prompts import QA_PROMPT


async def answer_question(
    question: str
) -> str:

    prompt = QA_PROMPT.format(
        question=question.strip()
    )

    return await generate_text(
        prompt,
        temperature=0.3,
        max_output_tokens=1200
    )