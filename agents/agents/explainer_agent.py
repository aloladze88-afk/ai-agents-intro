"""Create and configure the Explainer Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


# Locate the project directory regardless of where Python is started.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load OLLAMA_API_BASE and MODEL_NAME from the project's .env file.
load_dotenv(PROJECT_ROOT / ".env")

MODEL_NAME = os.getenv("MODEL_NAME")

if not MODEL_NAME:
    raise RuntimeError(
        "MODEL_NAME is missing. Add it to the project's .env file."
    )


explainer_agent = Agent(
    name="explainer_agent",
    model=LiteLlm(model=MODEL_NAME),
    description=(
        "Explains one programming topic clearly for a beginner student."
    ),
    instruction=(
        "You are a beginner-friendly programming tutor.\n\n"
        "The user's message contains one programming topic.\n"
        "Return a concise Markdown answer using exactly these sections:\n\n"
        "## Explanation\n"
        "Explain the topic in two to four short sentences.\n\n"
        "## Key concepts\n"
        "Give three to five bullet points containing the most important "
        "ideas.\n\n"
        "## Example\n"
        "Give one simple example. Use a short code block when useful.\n\n"
        "Do not add an introduction, conclusion, or extra sections."
    ),
)