"""Utilities for validating generated Markdown study guides."""

from typing import TypedDict


REQUIRED_HEADINGS = [
    "# Topic",
    "## Simple Explanation",
    "## Key Concepts",
    "## Example",
    "## Practice Exercise",
    "## Common Mistakes",
    "## Review Comments",
    "## Final Summary",
]


class ValidationResult(TypedDict):
    """Result returned by the deterministic Markdown validator."""

    valid: bool
    missing_sections: list[str]


def validate_required_sections(markdown: str) -> ValidationResult:
    """Check whether Markdown contains every required heading."""
    headings = set()
    active_fence = None

    for line in markdown.splitlines():
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

        if (
            active_fence is None
            and stripped_line.startswith("#")
        ):
            headings.add(stripped_line)

    missing_sections = [
        heading
        for heading in REQUIRED_HEADINGS
        if heading not in headings
    ]

    return {
        "valid": not missing_sections,
        "missing_sections": missing_sections,
    }
