import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent


# Load .env
load_dotenv(
    BASE_DIR / ".env"
)


@dataclass(frozen=True)
class Settings:

    app_name: str = os.getenv(
        "APP_NAME",
        "EduGenie - Google Gemini Powered Learning Assistant"
    )

    gemini_api_key: str = os.getenv(
        "GEMINI_API_KEY",
        ""
    )

    gemini_model: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash"
    )

    explanation_provider: str = os.getenv(
        "EXPLANATION_PROVIDER",
        "gemini"
    ).lower()

    local_explanation_model: str = os.getenv(
        "LOCAL_EXPLANATION_MODEL",
        "MBZUAI/LaMini-Flan-T5-783M"
    )

    temperature: float = float(
        os.getenv(
            "GEMINI_TEMPERATURE",
            "0.4"
        )
    )

    max_output_tokens: int = int(
        os.getenv(
            "GEMINI_MAX_OUTPUT_TOKENS",
            "2048"
        )
    )

    @property
    def gemini_configured(self) -> bool:

        return bool(
            self.gemini_api_key
        )


settings = Settings()