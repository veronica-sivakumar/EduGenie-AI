from functools import lru_cache
from typing import Optional
import asyncio

from config import settings


class GeminiServiceError(RuntimeError):
    """Raised when Gemini or the local AI service cannot be used."""
    pass


# ---------------------------------------------------------
# GEMINI CLIENT
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_client():
    """Create and cache the Gemini API client."""

    if not settings.gemini_api_key:
        raise GeminiServiceError(
            "GEMINI_API_KEY is not configured. "
            "Add your Gemini API key to the .env file."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise GeminiServiceError(
            "Google GenAI SDK is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    try:
        return genai.Client(
            api_key=settings.gemini_api_key
        )

    except Exception as exc:
        raise GeminiServiceError(
            f"Failed to create Gemini client: {exc}"
        ) from exc


# ---------------------------------------------------------
# LOCAL AI MODEL
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_local_generator():
    """
    Load and cache the local LaMini-Flan-T5 model.
    """

    try:
        from transformers import pipeline
    except ImportError as exc:
        raise GeminiServiceError(
            "Local AI dependencies are not installed. "
            "Run: pip install -r requirements-local.txt"
        ) from exc

    try:
        generator = pipeline(
            "text2text-generation",
            model=settings.local_explanation_model
        )

        return generator

    except Exception as exc:
        raise GeminiServiceError(
            f"Failed to load local AI model: {exc}"
        ) from exc


def generate_local_text(
    prompt: str,
    max_output_tokens: Optional[int] = None,
) -> str:
    """
    Generate text using the local LaMini-Flan-T5 model.
    """

    if not prompt or not prompt.strip():
        raise GeminiServiceError(
            "The local AI prompt cannot be empty."
        )

    generator = get_local_generator()

    output_tokens = min(
        max_output_tokens or 350,
        512
    )

    try:
        result = generator(
            prompt,
            max_new_tokens=output_tokens,
            do_sample=False
        )

    except Exception as exc:
        raise GeminiServiceError(
            f"Local AI generation failed: {exc}"
        ) from exc

    if not result:
        raise GeminiServiceError(
            "Local AI returned an empty response."
        )

    response_text = result[0].get(
        "generated_text",
        ""
    )

    response_text = str(
        response_text
    ).strip()

    if not response_text:
        raise GeminiServiceError(
            "Local AI returned an empty response."
        )

    return response_text


# ---------------------------------------------------------
# GEMINI GENERATION
# ---------------------------------------------------------

async def generate_gemini_text(
    prompt: str,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
) -> str:
    """
    Generate text using Google Gemini.
    """

    if not prompt or not prompt.strip():
        raise GeminiServiceError(
            "The prompt cannot be empty."
        )

    try:
        from google.genai import types
    except ImportError as exc:
        raise GeminiServiceError(
            "Google GenAI SDK is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    client = get_client()

    if temperature is None:
        temperature = settings.temperature

    if max_output_tokens is None:
        max_output_tokens = settings.max_output_tokens

    generation_config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=generation_config,
        )

    except Exception as exc:
        raise GeminiServiceError(
            f"Gemini API request failed: {exc}"
        ) from exc

    response_text = getattr(
        response,
        "text",
        None
    )

    if not response_text:
        raise GeminiServiceError(
            "Gemini returned an empty response."
        )

    response_text = str(
        response_text
    ).strip()

    if not response_text:
        raise GeminiServiceError(
            "Gemini returned an empty response."
        )

    return response_text


# ---------------------------------------------------------
# GEMINI ERROR CHECK
# ---------------------------------------------------------

def is_quota_error(error: Exception) -> bool:
    """
    Detect Gemini quota/rate-limit errors.
    """

    error_message = str(
        error
    ).upper()

    quota_errors = [
        "429",
        "RESOURCE_EXHAUSTED",
        "QUOTA",
        "RATE LIMIT",
        "RATE_LIMIT",
        "GENERATE_CONTENT_FREE_TIER_REQUESTS",
    ]

    return any(
        error_text in error_message
        for error_text in quota_errors
    )


# ---------------------------------------------------------
# MAIN AI FUNCTION
# ---------------------------------------------------------

async def generate_text(
    prompt: str,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
) -> str:
    """
    Main AI generation function.

    1. Try Gemini first.
    2. If Gemini quota is exhausted, use local AI.
    """

    if not prompt or not prompt.strip():
        raise GeminiServiceError(
            "The prompt cannot be empty."
        )

    # -----------------------------------------------------
    # STEP 1: Try Gemini
    # -----------------------------------------------------

    try:

        return await generate_gemini_text(
            prompt=prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

    except Exception as gemini_error:

        # -------------------------------------------------
        # STEP 2: Gemini quota exceeded
        # -------------------------------------------------

        if not is_quota_error(
            gemini_error
        ):
            raise

        # -------------------------------------------------
        # STEP 3: Use local AI
        # -------------------------------------------------

        try:

            local_result = await asyncio.to_thread(
                generate_local_text,
                prompt,
                max_output_tokens,
            )

            return local_result

        except Exception as local_error:

            raise GeminiServiceError(
                "Gemini quota is exhausted and "
                "the local AI fallback could not generate "
                "a response.\n\n"
                f"Gemini error: {gemini_error}\n"
                f"Local AI error: {local_error}"
            ) from local_error
