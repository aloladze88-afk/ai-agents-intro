"""Create and configure the Explainer Agent."""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def create_explainer_agent(model_name: str) -> Agent:
    """Return an Explainer Agent configured with the selected model."""
    if not model_name.strip():
        raise ValueError("The Explainer Agent requires a model name.")

    return Agent(
        name="explainer_agent",
        model=LiteLlm(model=model_name),
        description=(
            "Explains programming topics clearly for beginner students."
        ),
        instruction=(
            "You are an Explainer Agent.\n\n"
            "Explain the supplied programming topic clearly for a beginner. "
            "Focus only on explanation, key concepts, a small example, "
            "common mistakes and a final summary.\n\n"
            "Do not create a practice exercise or review comments because "
            "other agents handle those sections.\n\n"
            "Use the exact Markdown headings requested in the user's "
            "prompt. Keep examples small and close every Markdown code "
            "block with three backticks."
        ),
    )
