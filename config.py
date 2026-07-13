"""Load and validate project configuration."""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"
SUPPORTED_MODEL_PROVIDERS = {"ollama"}


class ConfigurationError(RuntimeError):
    """Raised when required project configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    """Validated settings used by the study-guide workflow."""

    model_provider: str
    model_name: str
    ollama_api_base: str
    ollama_model_name: str


def load_settings() -> Settings:
    """Load `.env`, validate required values and return project settings."""
    load_dotenv(ENV_FILE, override=False)

    values = {
        "MODEL_PROVIDER": os.getenv("MODEL_PROVIDER", "").strip(),
        "MODEL_NAME": os.getenv("MODEL_NAME", "").strip(),
        "OLLAMA_API_BASE": os.getenv("OLLAMA_API_BASE", "").strip(),
    }

    missing_variables = [
        name
        for name, value in values.items()
        if not value
    ]

    if missing_variables:
        missing_text = ", ".join(missing_variables)
        raise ConfigurationError(
            "Missing required environment variable(s): "
            f"{missing_text}. Copy `.env.example` to `.env` and fill in "
            "the required values."
        )

    provider = values["MODEL_PROVIDER"].casefold()

    if provider not in SUPPORTED_MODEL_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_MODEL_PROVIDERS))
        raise ConfigurationError(
            f'Unsupported MODEL_PROVIDER "{values["MODEL_PROVIDER"]}". '
            f"Supported provider(s): {supported}."
        )

    model_name = values["MODEL_NAME"]
    valid_prefixes = ("ollama/", "ollama_chat/")

    if not model_name.startswith(valid_prefixes):
        raise ConfigurationError(
            "MODEL_NAME must use a LiteLLM Ollama prefix, for example "
            "`ollama_chat/llama3.2:3b`."
        )

    ollama_model_name = model_name.split("/", 1)[1].strip()

    if not ollama_model_name:
        raise ConfigurationError(
            "MODEL_NAME does not contain an Ollama model name."
        )

    ollama_api_base = values["OLLAMA_API_BASE"].rstrip("/")
    parsed_url = urlparse(ollama_api_base)

    if (
        parsed_url.scheme not in {"http", "https"}
        or not parsed_url.netloc
    ):
        raise ConfigurationError(
            "OLLAMA_API_BASE must be a complete HTTP or HTTPS URL, for "
            "example `http://localhost:11434`."
        )

    return Settings(
        model_provider=provider,
        model_name=model_name,
        ollama_api_base=ollama_api_base,
        ollama_model_name=ollama_model_name,
    )
