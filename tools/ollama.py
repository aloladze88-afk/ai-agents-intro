"""Preflight checks for the local Ollama server and model."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaConnectionError(RuntimeError):
    """Raised when the Ollama server cannot be reached."""


class ModelNotAvailableError(RuntimeError):
    """Raised when the configured model is not installed in Ollama."""


def _model_aliases(model_name: str) -> set[str]:
    """Return equivalent names for an Ollama model."""
    aliases = {model_name}

    if model_name.endswith(":latest"):
        aliases.add(model_name.removesuffix(":latest"))
    elif ":" not in model_name:
        aliases.add(f"{model_name}:latest")

    return aliases


def check_ollama(
    ollama_api_base: str,
    required_model: str,
    timeout: float = 3.0,
) -> list[str]:
    """Confirm that Ollama is reachable and the required model exists."""
    tags_url = f"{ollama_api_base.rstrip('/')}/api/tags"
    request = Request(
        tags_url,
        headers={"Accept": "application/json"},
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except HTTPError as error:
        raise OllamaConnectionError(
            "Ollama responded with HTTP status "
            f"{error.code} at {tags_url}. Check OLLAMA_API_BASE."
        ) from error
    except URLError as error:
        reason = getattr(error, "reason", error)
        raise OllamaConnectionError(
            f"Could not connect to Ollama at {ollama_api_base}: "
            f"{reason}. Start it with `ollama serve`."
        ) from error
    except TimeoutError as error:
        raise OllamaConnectionError(
            f"Timed out while connecting to Ollama at {ollama_api_base}. "
            "Check that `ollama serve` is running."
        ) from error
    except OSError as error:
        raise OllamaConnectionError(
            f"Could not communicate with Ollama at {ollama_api_base}: "
            f"{error}."
        ) from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise OllamaConnectionError(
            "Ollama returned an unreadable response from "
            f"{tags_url}. Check that OLLAMA_API_BASE points to Ollama."
        ) from error

    models = payload.get("models")

    if not isinstance(models, list):
        raise OllamaConnectionError(
            "Ollama returned an unexpected response from `/api/tags`."
        )

    available_models = set()

    for model in models:
        if not isinstance(model, dict):
            continue

        for key in ("name", "model"):
            value = model.get(key)

            if isinstance(value, str) and value.strip():
                available_models.add(value.strip())

    required_aliases = _model_aliases(required_model)
    available_aliases = set()

    for available_model in available_models:
        available_aliases.update(_model_aliases(available_model))

    if required_aliases.isdisjoint(available_aliases):
        available_text = (
            ", ".join(sorted(available_models))
            if available_models
            else "none"
        )
        raise ModelNotAvailableError(
            f'Ollama is running, but model "{required_model}" is not '
            "available.\n"
            f"Install it with: ollama pull {required_model}\n"
            f"Available models: {available_text}"
        )

    return sorted(available_models)
