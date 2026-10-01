from ai_client import generate_text
from prompts import LEARNING_PATH_PROMPT


async def get_learning_recommendations(
    topic: str,
    level: str = "beginner",
    goals: str = ""
) -> str:

    prompt = LEARNING_PATH_PROMPT.format(

        topic=topic.strip(),

        level=(
            level.strip()
            if level.strip()
            else "beginner"
        ),

        goals=(
            goals.strip()
            if goals.strip()
            else "Build a strong practical foundation."
        ),
    )

    return await generate_text(
        prompt,
        temperature=0.5,
        max_output_tokens=2200
    )