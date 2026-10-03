from functools import lru_cache
from typing import Optional
import asyncio

from config import settings


class GeminiServiceError(RuntimeError):
    """Raised when the Gemini service cannot be used successfully."""
    pass


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
        return genai.Client(api_key=settings.gemini_api_key)
    except Exception as exc:
        raise GeminiServiceError(
            "Failed to create Gemini client: " + str(exc)
        ) from exc


async def generate_text(
    prompt: str,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
) -> str:
    """
    Generate text using Gemini 3.8 Flash.

    Uses Google's current Interactions API.
    """

    if not prompt or not prompt.strip():
        raise GeminiServiceError("The prompt cannot be empty.")

    client = get_client()

    if temperature is None:
        temperature = settings.temperature

    if max_output_tokens is None:
        max_output_tokens = settings.max_output_tokens

    max_attempts = 3
    last_error = None

    for attempt in range(max_attempts):
        try:
            interaction = client.interactions.create(
                model=settings.gemini_model,
                input=prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                },
            )

            response_text = getattr(
                interaction,
                "output_text",
                None
            )

            if response_text is None:
                raise GeminiServiceError(
                    "Gemini returned an empty response."
                )

            response_text = str(response_text).strip()

            if not response_text:
                raise GeminiServiceError(
                    "Gemini returned an empty response."
                )

            return response_text

        except Exception as exc:
            last_error = exc
            error_message = str(exc)

            temporary_error = (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
                or "503" in error_message
                or "UNAVAILABLE" in error_message
                or "500" in error_message
                or "INTERNAL" in error_message
            )

            if temporary_error and attempt < max_attempts - 1:
                await asyncio.sleep(3 * (attempt + 1))
                continue

            raise GeminiServiceError(
                "Gemini API request failed: " + error_message
            ) from exc

    raise GeminiServiceError(
        "Gemini API request failed after "
        f"{max_attempts} attempts: {last_error}"
    )