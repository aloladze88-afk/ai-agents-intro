"""Create and configure the Reviewer Agent."""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm


def create_reviewer_agent(model_name: str) -> Agent:
    """Return a Reviewer Agent configured with the selected model."""
    if not model_name.strip():
        raise ValueError("The Reviewer Agent requires a model name.")

    return Agent(
        name="reviewer_agent",
        model=LiteLlm(model=model_name),
        description=(
            "Reviews draft programming study guides and provides short, "
            "actionable quality-control comments."
        ),
        instruction=(
            "You are a Reviewer Agent.\n\n"
            "Review the supplied draft for clarity, completeness, structure "
            "and usefulness for a beginner.\n\n"
            "Identify missing information, ambiguous explanations, specific "
            "improvements and whether the draft should be approved or "
            "revised.\n\n"
            "Be critical but constructive. Do not rewrite the study guide. "
            "Return only the exact Review Comments Markdown structure "
            "requested in the user's prompt."
        ),
    )
