"""Generate, review, validate and save a Markdown study guide."""

import asyncio
import sys
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.explainer_agent import explainer_agent
from agents.practice_designer_agent import practice_designer_agent
from agents.reviewer_agent import reviewer_agent
from tools.file_writer import save_markdown_file
from tools.validation import validate_required_sections


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_ROOT / "output" / "study_guide.md"

APP_NAME = "ai_study_guide_generator"
USER_ID = "local_user"

session_service = InMemorySessionService()


async def run_agent(
    agent,
    prompt: str,
    session_id: str,
) -> str:
    """Run one ADK agent and return its final text response."""
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_response = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message,
    ):
        if not event.is_final_response():
            continue

        if not event.content or not event.content.parts:
            continue

        text_parts = [
            part.text
            for part in event.content.parts
            if getattr(part, "text", None)
        ]

        final_response = "\n".join(text_parts).strip()

    if not final_response:
        raise RuntimeError(
            f"The {agent.name} did not return a text response."
        )

    return final_response


def extract_section_body(
    generated_content: str,
    section_heading: str,
) -> list[str]:
    """Extract content beneath a generated level-two heading."""
    lines = generated_content.strip().splitlines()
    heading_index = None

    for index, line in enumerate(lines):
        if line.strip() == section_heading:
            heading_index = index
            break

    if heading_index is None:
        return lines

    section_lines = []

    for line in lines[heading_index + 1:]:
        if line.strip().startswith("## "):
            break

        section_lines.append(line)

    return section_lines


def replace_markdown_section(
    document: str,
    section_heading: str,
    generated_content: str,
) -> str:
    """Replace one level-two Markdown section with generated content."""
    lines = document.splitlines()
    start_index = None
    end_index = len(lines)

    for index, line in enumerate(lines):
        if line.strip() == section_heading:
            start_index = index
            break

    if start_index is None:
        return document

    for index in range(start_index + 1, len(lines)):
        if lines[index].strip().startswith("## "):
            end_index = index
            break

    section_body = extract_section_body(
        generated_content,
        section_heading,
    )

    while section_body and not section_body[0].strip():
        section_body.pop(0)

    while section_body and not section_body[-1].strip():
        section_body.pop()

    combined_lines = (
        lines[:start_index + 1]
        + [""]
        + section_body
        + [""]
        + lines[end_index:]
    )

    return "\n".join(combined_lines).strip() + "\n"


def create_explainer_prompt(topic: str) -> str:
    """Create the prompt sent to the Explainer Agent."""
    return f"""Create a beginner-friendly Markdown study guide about:

{topic}

Use exactly these level-two headings:

## Topic
## Simple Explanation
## Key Concepts
## Example
## Practice Exercise
## Common Mistakes
## Review Comments
## Final Summary

Requirements:

- Put the original topic under `## Topic`.
- Explain the topic clearly and simply.
- Include important key concepts.
- Include one small practical example.
- Create a temporary practice exercise.
- Include common beginner mistakes.
- Under `## Review Comments`, write `Pending reviewer feedback.`
- End with a short final summary.
- Do not rename, remove or change the level of any required heading.
"""


def create_practice_prompt(
    topic: str,
    explanation: str,
) -> str:
    """Create the prompt sent to the Practice Designer Agent."""
    return f"""Original topic:

{topic}

Draft produced by the Explainer Agent:

{explanation}

Create one short beginner-friendly practice exercise based on the original
topic and the explanation.

Return only the requested Practice Exercise Markdown section. Do not rewrite
the complete study guide.
"""


def create_reviewer_prompt(
    topic: str,
    study_guide: str,
) -> str:
    """Create the prompt sent to the Reviewer Agent."""
    return f"""Original topic:

{topic}

Current draft study guide:

--- START OF DRAFT ---

{study_guide}

--- END OF DRAFT ---

Review this existing draft for clarity, completeness, structure and usefulness
for a beginner.

The current content under `## Review Comments` is only a placeholder. Ignore
that placeholder when reviewing the draft.

Return only the requested Review Comments Markdown section. Do not rewrite the
study guide.
"""


async def generate_study_guide(topic: str) -> str:
    """Run the agents and return the completed study guide."""
    explanation = await run_agent(
        explainer_agent,
        create_explainer_prompt(topic),
        "explainer_session",
    )

    practice = await run_agent(
        practice_designer_agent,
        create_practice_prompt(topic, explanation),
        "practice_designer_session",
    )

    draft_with_practice = replace_markdown_section(
        explanation,
        "## Practice Exercise",
        practice,
    )

    review = await run_agent(
        reviewer_agent,
        create_reviewer_prompt(
            topic,
            draft_with_practice,
        ),
        "reviewer_session",
    )

    completed_guide = replace_markdown_section(
        draft_with_practice,
        "## Review Comments",
        review,
    )

    return completed_guide


async def main() -> None:
    """Read the topic, generate the guide and save valid Markdown."""
    if len(sys.argv) < 2:
        raise SystemExit(
            'Usage: python main.py "programming topic"'
        )

    topic = " ".join(sys.argv[1:]).strip()

    if not topic:
        raise SystemExit("The programming topic cannot be empty.")

    try:
        study_guide = await generate_study_guide(topic)
    except Exception as error:
        raise SystemExit(
            f"Study guide generation failed: {error}"
        ) from error

    validation_result = validate_required_sections(study_guide)

    if not validation_result["valid"]:
        missing_sections = ", ".join(
            validation_result["missing_sections"]
        )

        print("\nValidation failed.")
        print(f"Missing sections: {missing_sections}")
        print("The study guide was not saved.")
        raise SystemExit(1)

    print(study_guide)
    print("Validation passed: all required sections are present.")

    save_result = save_markdown_file(
        str(OUTPUT_FILE),
        study_guide,
    )

    print(save_result)


if __name__ == "__main__":
    asyncio.run(main())