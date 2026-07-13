#!/usr/bin/env python3
"""Run the AI study guide workflow from the command line."""

import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.explainer_agent import explainer_agent
from agents.practice_designer_agent import practice_designer_agent
from tools.file_writer import save_markdown_file
from tools.validation import validate_required_sections


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

APP_NAME = "ai_study_guide_generator"
USER_ID = "local_user"
OUTPUT_FILE = PROJECT_ROOT / "output" / "study_guide.md"


def get_topic() -> str:
    """Read the programming topic from the command line."""
    parser = argparse.ArgumentParser(
        description="Generate a beginner-friendly programming study guide."
    )
    parser.add_argument(
        "topic",
        help='Programming topic, for example "Python list comprehensions".',
    )

    return parser.parse_args().topic.strip()


async def run_agent(agent, prompt: str, session_id: str) -> str:
    """Run one ADK agent and return its final text response."""
    session_service = InMemorySessionService()

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

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_response = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content:
            final_response = "".join(
                part.text or ""
                for part in event.content.parts
            )

    if not final_response.strip():
        raise RuntimeError(
            f"{agent.name} did not return a final text response."
        )

    return final_response.strip()


def replace_practice_section(
    study_guide: str,
    practice: str,
) -> str:
    """Replace the existing Practice Exercise section with agent output."""
    lines = study_guide.splitlines()
    target_heading = "## Practice Exercise"
    start_index = None
    end_index = len(lines)

    for index, line in enumerate(lines):
        if line.strip() == target_heading:
            start_index = index
            break

    if start_index is None:
        return study_guide

    for index in range(start_index + 1, len(lines)):
        if lines[index].strip().startswith("## "):
            end_index = index
            break

    practice_lines = practice.strip().splitlines()

    if (
        practice_lines
        and practice_lines[0].strip() == target_heading
    ):
        practice_lines = practice_lines[1:]

    combined_lines = (
        lines[:start_index + 1]
        + [""]
        + practice_lines
        + [""]
        + lines[end_index:]
    )

    return "\n".join(combined_lines).strip() + "\n"


async def main() -> None:
    """Generate, validate and save a study guide."""
    topic = get_topic()

    explainer_prompt = f"""Create a beginner-friendly Markdown study guide
about:
{topic}

Use exactly these level-two headings and do not rename them:

## Topic
## Simple Explanation
## Key Concepts
## Example
## Practice Exercise
## Common Mistakes
## Review Comments
## Final Summary

Do not add text before the first heading.
"""

    explanation = await run_agent(
        explainer_agent,
        explainer_prompt,
        "explainer_session",
    )

    practice_prompt = f"""Original topic:
{topic}

Explanation produced by the Explainer Agent:
{explanation}

Create one short beginner-friendly practice exercise based on this topic
and explanation.
"""

    practice = await run_agent(
        practice_designer_agent,
        practice_prompt,
        "practice_designer_session",
    )

    study_guide = replace_practice_section(
        explanation,
        practice,
    )

    print(study_guide)

    validation_result = validate_required_sections(study_guide)

    if not validation_result["valid"]:
        missing_sections = ", ".join(
            validation_result["missing_sections"]
        )

        print("\nValidation failed.")
        print(f"Missing sections: {missing_sections}")
        print("The study guide was not saved.")
        raise SystemExit(1)

    print("\nValidation passed: all required sections are present.")

    save_result = save_markdown_file(
        str(OUTPUT_FILE),
        study_guide,
    )

    print(save_result)


if __name__ == "__main__":
    asyncio.run(main())