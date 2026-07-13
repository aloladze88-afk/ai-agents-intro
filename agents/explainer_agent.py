"""Create and configure the Explainer Agent."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL_NAME = os.getenv("MODEL_NAME")

if not MODEL_NAME:
    raise RuntimeError(
        "MODEL_NAME is missing from the project's .env file."
    )


explainer_agent = Agent(
    name="explainer_agent",
    model=LiteLlm(model=MODEL_NAME),
    description=(
        "Explains programming topics clearly for beginner students."
    ),
    instruction=(
        "You are a beginner-friendly programming tutor.\n\n"
        "The user will provide one programming topic.\n"
        "Return a concise Markdown answer using exactly these sections:\n\n"
        "## Explanation\n"
        "Explain the topic in two to four short sentences.\n\n"
        "## Key concepts\n"
        "Give three to five bullet points.\n\n"
        "## Example\n"
        "Give one simple example. Use a short code block when useful.\n\n"
        "Do not add any other sections."
    ),
)
