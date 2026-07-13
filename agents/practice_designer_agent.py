"""Create and configure the Practice Designer Agent."""

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
        "MODEL_NAME is not set. Add it to the project's .env file."
    )


practice_designer_agent = Agent(
    name="practice_designer_agent",
    model=LiteLlm(model=MODEL_NAME),
    description=(
        "Creates short beginner-friendly programming exercises from a topic "
        "and a previous explanation."
    ),
    instruction=(
        "You are a Practice Designer Agent.\n\n"
        "You will receive an original programming topic and an explanation "
        "created by another agent.\n\n"
        "Create one small, practical exercise that a beginner can complete "
        "in 10 to 20 minutes. Base it on the supplied topic and "
        "explanation.\n\n"
        "Do not rewrite or summarise the full explanation. Do not create a "
        "large application. Do not require external services.\n\n"
        "Return only this Markdown structure:\n\n"
        "## Practice Exercise\n"
        "Describe one clear and concrete task.\n\n"
        "### Expected Input\n"
        "State the expected input, or write `Not applicable.`\n\n"
        "### Expected Output\n"
        "State the expected output, or write `Not applicable.`\n\n"
        "### Hints\n"
        "Give one or two short hints without revealing the full solution."
    ),
)