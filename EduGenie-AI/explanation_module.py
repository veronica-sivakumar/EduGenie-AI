from config import settings
from ai_client import generate_text
from prompts import EXPLAIN_PROMPT


def local_explain(topic: str) -> str:
    """
    Optional local LaMini-Flan-T5 explanation.

    This is only used when:

    EXPLANATION_PROVIDER=local

    in .env
    """

    from transformers import pipeline

    generator = pipeline(
        "text2text-generation",
        model=settings.local_explanation_model
    )

    prompt = (
        "Explain this topic simply for a beginner. "
        "Include definition, working, key points and "
        "one example: "
        + topic.strip()
    )

    result = generator(
        prompt,
        max_new_tokens=350,
        do_sample=False
    )

    return result[0][
        "generated_text"
    ].strip()


async def explain_topic(
    topic: str
) -> str:

    if settings.explanation_provider == "local":

        try:

            return local_explain(
                topic
            )

        except ImportError as exc:

            raise RuntimeError(
                "Local explanation requires the optional "
                "dependencies. Run: "
                "pip install -r requirements-local.txt"
            ) from exc

        except Exception as exc:

            raise RuntimeError(
                f"Local explanation failed: {exc}"
            ) from exc

    prompt = EXPLAIN_PROMPT.format(
        topic=topic.strip()
    )

    return await generate_text(
        prompt,
        temperature=0.35,
        max_output_tokens=1400
    )