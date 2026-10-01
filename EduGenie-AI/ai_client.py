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
        client = genai.Client(
            api_key=settings.gemini_api_key
        )
        return client

    except Exception as exc:
        raise GeminiServiceError(
            "Failed to create Gemini client: " + str(exc)
        ) from exc


async def generate_text(
    prompt: str,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
) -> str:
    """Send a prompt to Gemini and return the generated text."""

    # Check prompt
    if not prompt or not prompt.strip():
        raise GeminiServiceError(
            "The prompt cannot be empty."
        )

    # Import Google GenAI types
    try:
        from google.genai import types
    except ImportError as exc:
        raise GeminiServiceError(
            "Google GenAI SDK is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    # Get Gemini client
    client = get_client()

    # Use default settings if values are not provided
    if temperature is None:
        temperature = settings.temperature

    if max_output_tokens is None:
        max_output_tokens = settings.max_output_tokens

    # Gemini generation configuration
    generation_config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )

    # Try the request multiple times for temporary errors
    max_attempts = 4
    last_error = None

    for attempt in range(max_attempts):

        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=generation_config,
            )

            # Get generated text
            response_text = getattr(
                response,
                "text",
                None,
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

            # Successful response
            return response_text

        except Exception as exc:

            last_error = exc
            error_message = str(exc)

            # Temporary Gemini errors
            temporary_error = (
                "503" in error_message
                or "UNAVAILABLE" in error_message
                or "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
                or "500" in error_message
                or "INTERNAL" in error_message
            )

            if temporary_error and attempt < max_attempts - 1:

                # Exponential backoff:
                # attempt 1 -> 2 seconds
                # attempt 2 -> 4 seconds
                # attempt 3 -> 8 seconds
                wait_time = 2 ** (attempt + 1)

                await asyncio.sleep(wait_time)

                continue

            # Non-temporary error or all retries exhausted
            raise GeminiServiceError(
                "Gemini API request failed: "
                + error_message
            ) from exc

    # Safety fallback
    raise GeminiServiceError(
        "Gemini API request failed after "
        f"{max_attempts} attempts: {last_error}"
    )