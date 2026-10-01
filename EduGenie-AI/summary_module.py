from ai_client import generate_text
from prompts import SUMMARY_PROMPT


async def summarize_text(
    text: str
) -> str:

    prompt = SUMMARY_PROMPT.format(
        text=text.strip()
    )

    return await generate_text(
        prompt,
        temperature=0.25,
        max_output_tokens=1600
    )