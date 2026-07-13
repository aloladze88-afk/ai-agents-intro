"""Create and configure the Reviewer Agent."""

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


reviewer_agent = Agent(
    name="reviewer_agent",
    model=LiteLlm(model=MODEL_NAME),
    description=(
        "Reviews draft programming study guides and provides short, "
        "actionable quality-control comments."
    ),
    instruction=(
        "You are a Reviewer Agent.\n\n"
        "You will receive an existing draft of a programming study guide.\n\n"
        "Review the draft for clarity, completeness, structure and "
        "usefulness for a beginner.\n\n"
        "Identify:\n"
        "- important information that is missing;\n"
        "- explanations that are ambiguous or unclear;\n"
        "- specific improvements that should be made;\n"
        "- whether the draft should be approved or revised.\n\n"
        "Be critical but constructive. Keep the review short and "
        "actionable.\n\n"
        "Do not rewrite the study guide. Do not create a replacement "
        "explanation, example or exercise. Comment only on the existing "
        "draft.\n\n"
        "Avoid vague comments such as `Improve the explanation`. Give "
        "specific comments such as `The example creates a function but "
        "does not show how to call it`.\n\n"
        "If a category has no meaningful problems, write "
        "`None identified.`\n\n"
        "Return only this Markdown structure:\n\n"
        "## Review Comments\n\n"
        "### Missing Information\n"
        "List missing information or write `None identified.`\n\n"
        "### Ambiguous or Unclear Explanations\n"
        "List unclear points or write `None identified.`\n\n"
        "### Suggestions for Improvement\n"
        "Give short and specific suggestions or write "
        "`No changes required.`\n\n"
        "### Recommendation\n"
        "Write a short approval or revision recommendation."
    ),
)