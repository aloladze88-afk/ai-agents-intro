"""Run the Explainer Agent, validate the response and save it."""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.explainer_agent import explainer_agent
from tools.file_writer import save_markdown_file
from tools.validation import validate_required_sections


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

APP_NAME = "ai_study_guide_generator"
USER_ID = "local_user"
SESSION_ID = "local_session"

OUTPUT_FILE = PROJECT_ROOT / "output" / "study_guide.md"


async def run_agent(topic: str) -> str:
    """Run the Explainer Agent and return its final response."""
    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    runner = Runner(
        agent=explainer_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    user_message = types.Content(
        role="user",
        parts=[types.Part(text=topic)],
    )

    final_response = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_message,
    ):
        if (
            event.is_final_response()
            and event.content
            and event.content.parts
        ):
            final_response = "\n".join(
                part.text
                for part in event.content.parts
                if part.text
            )

    return final_response


async def main() -> None:
    """Run, validate and save the generated study guide."""
    if len(sys.argv) < 2:
        print('Usage: python main.py "programming topic"')
        raise SystemExit(1)

    topic = " ".join(sys.argv[1:])
    response = await run_agent(topic)

    if not response:
        print("The Explainer Agent did not return any content.")
        raise SystemExit(1)

    print(response)

    validation_result = validate_required_sections(response)

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
        response,
    )

    print(save_result)


if __name__ == "__main__":
    asyncio.run(main())