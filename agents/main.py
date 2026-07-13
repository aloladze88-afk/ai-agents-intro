#!/usr/bin/env python3
"""Run the Explainer Agent from the command line."""

import argparse
import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.explainer_agent import explainer_agent


APP_NAME = "ai_agents_intro"
USER_ID = "local_user"
SESSION_ID = "explainer_session"


def get_topic() -> str:
    """Read the programming topic from the command line."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate a beginner-friendly explanation of a programming "
            "topic."
        )
    )

    parser.add_argument(
        "topic",
        nargs="+",
        help='Topic to explain, for example: "Python decorators"',
    )

    arguments = parser.parse_args()
    return " ".join(arguments.topic).strip()


async def run_explainer(topic: str) -> str:
    """Send a topic to the Explainer Agent and return its response."""
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
        if not event.is_final_response():
            continue

        if not event.content or not event.content.parts:
            continue

        text_parts = [
            part.text
            for part in event.content.parts
            if part.text
        ]

        final_response = "\n".join(text_parts).strip()

    if not final_response:
        raise RuntimeError(
            "The agent completed without returning a text response."
        )

    return final_response


async def main() -> None:
    """Read the topic, run the agent and display the result."""
    topic = get_topic()
    response = await run_explainer(topic)
    print(response)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecution stopped.")
    except Exception as error:
        raise SystemExit(f"Error: {error}") from error