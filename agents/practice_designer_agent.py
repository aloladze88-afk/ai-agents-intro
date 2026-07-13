"""Create and configure the Practice Designer Agent."""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def create_practice_designer_agent(model_name: str) -> Agent:
    """Return a Practice Designer Agent using the selected model."""
    if not model_name.strip():
        raise ValueError(
            "The Practice Designer Agent requires a model name."
        )

    return Agent(
        name="practice_designer_agent",
        model=LiteLlm(model=model_name),
        description=(
            "Creates short beginner-friendly programming exercises from a "
            "topic and a previous explanation."
        ),
        instruction=(
            "You are a Practice Designer Agent.\n\n"
            "You will receive an original programming topic and an "
            "explanation created by another agent.\n\n"
            "Create one small, practical exercise that a beginner can "
            "complete in 10 to 20 minutes. Base it on the supplied topic "
            "and explanation.\n\n"
            "Do not rewrite or summarise the explanation. Do not create a "
            "large application or require external services.\n\n"
            "Include expected input, expected output and one or two hints. "
            "Use the exact Markdown structure requested in the user's "
            "prompt and close every code block with three backticks."
        ),
    )
