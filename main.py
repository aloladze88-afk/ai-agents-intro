"""Run the sequential AI study-guide workflow."""

import asyncio
import re
import sys
from pathlib import Path
from typing import Any

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.explainer_agent import create_explainer_agent
from agents.practice_designer_agent import (
    create_practice_designer_agent,
)
from agents.reviewer_agent import create_reviewer_agent
from config import ConfigurationError, Settings, load_settings
from tools.file_writer import FileWriteError, save_markdown_file
from tools.ollama import (
    ModelNotAvailableError,
    OllamaConnectionError,
    check_ollama,
)
from tools.validation import validate_required_sections


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_ROOT / "output" / "study_guide.md"

APP_NAME = "ai_study_guide_generator"
USER_ID = "student"


def get_topic_from_user() -> str:
    """Return a topic from command-line arguments or interactive input."""
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:]).strip()
    else:
        try:
            topic = input("Enter a programming topic: ").strip()
        except EOFError as error:
            raise ValueError(
                "Topic cannot be empty. Pass a topic as a command-line "
                "argument or enter one at the prompt."
            ) from error

    if not topic:
        raise ValueError(
            "Topic cannot be empty. Example: "
            '`python main.py "Python list comprehensions"`.'
        )

    return topic


def run_preflight_checks() -> Settings:
    """Validate configuration and confirm Ollama is ready."""
    print("[1/9] Checking configuration...")
    settings = load_settings()
    print(
        "Configuration loaded: "
        f"provider={settings.model_provider}, "
        f"model={settings.model_name}"
    )

    print("\n[2/9] Checking Ollama server and model...")
    check_ollama(
        ollama_api_base=settings.ollama_api_base,
        required_model=settings.ollama_model_name,
    )
    print(
        "Ollama is available and model "
        f"`{settings.ollama_model_name}` is installed."
    )

    return settings


async def run_agent(
    agent: Any,
    prompt: str,
    session_id: str,
) -> str:
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

        response_parts = []

        for part in event.content.parts:
            text = getattr(part, "text", None)

            if text:
                response_parts.append(text)

        final_response = "".join(response_parts).strip()

    if not final_response:
        raise RuntimeError(
            f"{agent.name} did not return a final text response."
        )

    return final_response


def create_explainer_prompt(topic: str) -> str:
    """Create the prompt sent to the Explainer Agent."""
    return f"""Explain this programming topic for a beginner:

{topic}

Return these exact Markdown sections:

## Simple Explanation

Give a short and clear beginner-friendly explanation.

## Key Concepts

Describe the most important concepts.

## Example

Give one small practical example. Close every Markdown code block with
three backticks.

## Common Mistakes

Describe common beginner mistakes.

## Final Summary

Give a short summary of the topic.

Do not generate the Practice Exercise or Review Comments sections. Other
agents are responsible for those sections.
"""


def create_practice_prompt(
    topic: str,
    explanation: str,
) -> str:
    """Create the prompt sent to the Practice Designer Agent."""
    return f"""Original topic:

{topic}

Explanation produced by the Explainer Agent:

--- START OF EXPLANATION ---

{explanation}

--- END OF EXPLANATION ---

Create one small beginner-friendly practice exercise based on the topic and
the explanation.

Return only this Markdown structure:

## Practice Exercise

Describe one clear and practical exercise.

### Expected Input

State the expected input, or write `Not applicable.`

### Expected Output

State the expected output, or write `Not applicable.`

### Hints

Give one or two short hints.

Close every Markdown code block with three backticks.

Do not rewrite the explanation.
"""


def create_reviewer_prompt(
    topic: str,
    draft: str,
) -> str:
    """Create the prompt sent to the Reviewer Agent."""
    return f"""Original topic:

{topic}

Current draft study guide:

--- START OF DRAFT ---

{draft}

--- END OF DRAFT ---

Review the existing draft for clarity, completeness, structure and usefulness
for a beginner.

The current Review Comments content is only a placeholder. Ignore it while
reviewing.

Return only this Markdown structure:

## Review Comments

### Missing Information

Identify important missing information, or write `None identified.`

### Ambiguous or Unclear Explanations

Identify unclear explanations, or write `None identified.`

### Suggestions for Improvement

Give short and specific suggestions, or write `No changes required.`

### Recommendation

Give a short approval or revision recommendation.

Do not rewrite the study guide.
"""


def find_markdown_headings(
    lines: list[str],
) -> list[tuple[int, int, str]]:
    """Return Markdown headings outside fenced code blocks."""
    headings = []
    active_fence = None

    for index, line in enumerate(lines):
        stripped_line = line.strip()

        if stripped_line.startswith("```"):
            if active_fence == "```":
                active_fence = None
            elif active_fence is None:
                active_fence = "```"

            continue

        if stripped_line.startswith("~~~"):
            if active_fence == "~~~":
                active_fence = None
            elif active_fence is None:
                active_fence = "~~~"

            continue

        if active_fence is not None:
            continue

        match = re.match(
            r"^(#{1,6})\s+(.+?)\s*$",
            stripped_line,
        )

        if match:
            headings.append(
                (
                    index,
                    len(match.group(1)),
                    match.group(2).strip(),
                )
            )

    return headings


def extract_named_section(
    markdown: str,
    section_name: str,
) -> str:
    """Extract a named Markdown section regardless of heading level."""
    lines = markdown.strip().splitlines()
    headings = find_markdown_headings(lines)

    for position, heading in enumerate(headings):
        start_index, start_level, title = heading

        if title.casefold() != section_name.casefold():
            continue

        end_index = len(lines)

        for next_heading in headings[position + 1:]:
            next_index, next_level, _ = next_heading

            if next_level <= start_level:
                end_index = next_index
                break

        return "\n".join(
            lines[start_index + 1:end_index]
        ).strip()

    return ""


def close_unmatched_code_fence(content: str) -> str:
    """Close an unmatched Markdown code fence in generated content."""
    lines = content.strip().splitlines()
    active_fence = None

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith("```"):
            if active_fence == "```":
                active_fence = None
            elif active_fence is None:
                active_fence = "```"

        elif stripped_line.startswith("~~~"):
            if active_fence == "~~~":
                active_fence = None
            elif active_fence is None:
                active_fence = "~~~"

    cleaned_content = "\n".join(lines).strip()

    if active_fence is not None:
        cleaned_content = f"{cleaned_content}\n{active_fence}"

    return cleaned_content


def get_agent_section(
    generated_content: str,
    section_name: str,
) -> str:
    """Extract an agent section or use its complete response."""
    section_body = extract_named_section(
        generated_content,
        section_name,
    )

    if not section_body:
        section_body = generated_content.strip()

    return close_unmatched_code_fence(section_body)


def add_section(
    document_parts: list[str],
    heading: str,
    body: str,
    fallback: str,
) -> None:
    """Append one required Markdown section."""
    cleaned_body = close_unmatched_code_fence(body.strip())

    if not cleaned_body:
        cleaned_body = fallback

    document_parts.extend(
        [
            heading,
            "",
            cleaned_body,
            "",
        ]
    )


def assemble_markdown(
    topic: str,
    explanation: str,
    practice: str,
    review: str | None = None,
) -> str:
    """Assemble the draft or final Markdown study guide."""
    simple_explanation = extract_named_section(
        explanation,
        "Simple Explanation",
    )
    key_concepts = extract_named_section(
        explanation,
        "Key Concepts",
    )
    example = extract_named_section(
        explanation,
        "Example",
    )
    common_mistakes = extract_named_section(
        explanation,
        "Common Mistakes",
    )
    final_summary = extract_named_section(
        explanation,
        "Final Summary",
    )
    practice_body = get_agent_section(
        practice,
        "Practice Exercise",
    )

    if review is None:
        review_body = (
            "The Reviewer Agent has not reviewed the draft yet."
        )
    else:
        review_body = get_agent_section(
            review,
            "Review Comments",
        )

    document_parts = [
        "# Topic",
        "",
        topic,
        "",
    ]

    add_section(
        document_parts,
        "## Simple Explanation",
        simple_explanation,
        "No simple explanation was generated.",
    )
    add_section(
        document_parts,
        "## Key Concepts",
        key_concepts,
        "No key concepts were generated.",
    )
    add_section(
        document_parts,
        "## Example",
        example,
        "No example was generated.",
    )
    add_section(
        document_parts,
        "## Practice Exercise",
        practice_body,
        "No practice exercise was generated.",
    )
    add_section(
        document_parts,
        "## Common Mistakes",
        common_mistakes,
        "No common mistakes were generated.",
    )
    add_section(
        document_parts,
        "## Review Comments",
        review_body,
        "No review comments were generated.",
    )
    add_section(
        document_parts,
        "## Final Summary",
        final_summary,
        "No final summary was generated.",
    )

    return "\n".join(document_parts).strip() + "\n"


def report_validation_failure(
    final_markdown: str,
    missing_sections: list[str],
) -> None:
    """Print a detailed validation failure without saving the file."""
    print(
        "Validation failed: the final Markdown is missing required "
        "headings."
    )
    print("Missing headings:")

    for section in missing_sections:
        print(f"- {section}")

    print("\nGenerated Markdown for debugging:")
    print("--------------------------------")
    print(final_markdown)
    print("--------------------------------")
    print("The Markdown file was not saved.")


async def run_workflow(
    topic: str,
    settings: Settings,
) -> int:
    """Run the complete sequential study-guide workflow."""
    explainer_agent = create_explainer_agent(
        settings.model_name
    )
    practice_designer_agent = create_practice_designer_agent(
        settings.model_name
    )
    reviewer_agent = create_reviewer_agent(
        settings.model_name
    )

    print(f"\nTopic: {topic}")

    print("\n[3/9] Running Explainer Agent...")
    explanation = await run_agent(
        explainer_agent,
        create_explainer_prompt(topic),
        "explainer_session",
    )
    print("Explainer Agent completed.")

    print("\n[4/9] Running Practice Designer Agent...")
    practice = await run_agent(
        practice_designer_agent,
        create_practice_prompt(topic, explanation),
        "practice_designer_session",
    )
    print("Practice Designer Agent completed.")

    print("\n[5/9] Assembling the draft study guide...")
    draft = assemble_markdown(
        topic=topic,
        explanation=explanation,
        practice=practice,
    )
    print("Draft study guide assembled.")

    print("\n[6/9] Running Reviewer Agent...")
    review = await run_agent(
        reviewer_agent,
        create_reviewer_prompt(topic, draft),
        "reviewer_session",
    )
    print("Reviewer Agent completed.")

    print("\n[7/9] Assembling the final Markdown...")
    final_markdown = assemble_markdown(
        topic=topic,
        explanation=explanation,
        practice=practice,
        review=review,
    )
    print("Final Markdown assembled.")

    print("\n[8/9] Validating required sections...")
    validation_result = validate_required_sections(
        final_markdown
    )

    if not validation_result["valid"]:
        report_validation_failure(
            final_markdown,
            validation_result["missing_sections"],
        )
        return 1

    print(
        "Validation passed: all required sections are present."
    )

    print("\n[9/9] Saving the Markdown file...")
    saved_path = save_markdown_file(
        OUTPUT_FILE,
        final_markdown,
    )
    print(f"Markdown file saved successfully: {saved_path}")

    print("\nWorkflow completed successfully.")
    print(f"Final file: {saved_path}")

    return 0


def main() -> None:
    """Read input, run preflight checks and start the workflow."""
    try:
        topic = get_topic_from_user()
        settings = run_preflight_checks()
        exit_code = asyncio.run(
            run_workflow(topic, settings)
        )
    except ValueError as error:
        print(f"Input error: {error}")
        exit_code = 1
    except ConfigurationError as error:
        print(f"Configuration error: {error}")
        exit_code = 1
    except OllamaConnectionError as error:
        print(f"Ollama connection error: {error}")
        exit_code = 1
    except ModelNotAvailableError as error:
        print(f"Model error: {error}")
        exit_code = 1
    except FileWriteError as error:
        print(f"File-writing error: {error}")
        print(
            "Check the output path, directory permissions and available "
            "disk space."
        )
        exit_code = 1
    except KeyboardInterrupt:
        print("\nWorkflow cancelled.")
        exit_code = 130

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
