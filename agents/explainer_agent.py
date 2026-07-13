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
        "Creates structured programming study guides for beginners."
    ),
    instruction=(
        "Create a beginner-friendly Markdown study guide for the "
        "programming topic supplied by the user.\n\n"
        "You must copy the following structure exactly.\n"
        "Replace only the instructional text beneath each heading.\n"
        "Do not rename, remove or reorder any heading.\n"
        "Every heading must begin with exactly two hash characters.\n"
        "Never use three hash characters.\n"
        "Return Markdown only.\n\n"
        "## Topic\n"
        "Repeat the programming topic supplied by the user.\n\n"
        "## Simple Explanation\n"
        "Explain the topic in two to four short sentences.\n\n"
        "## Key Concepts\n"
        "Give three to five bullet points.\n\n"
        "## Example\n"
        "Provide one simple example with a short code block when useful.\n\n"
        "## Practice Exercise\n"
        "Give one small exercise for the learner to complete.\n\n"
        "## Common Mistakes\n"
        "Describe two or three common beginner mistakes.\n\n"
        "## Review Comments\n"
        "Briefly review the clarity and consistency of the guide.\n\n"
        "## Final Summary\n"
        "Summarise the main lesson in a short paragraph.\n\n"
        "Before responding, verify that the response contains exactly "
        "these eight headings and that every heading starts with ##."
    ),
)