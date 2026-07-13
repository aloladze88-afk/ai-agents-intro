"""Utilities for validating generated Markdown study guides."""


REQUIRED_SECTIONS = [
    "Topic",
    "Simple Explanation",
    "Key Concepts",
    "Example",
    "Practice Exercise",
    "Common Mistakes",
    "Review Comments",
    "Final Summary",
]


def validate_required_sections(markdown: str) -> dict:
    """Check whether Markdown contains all required level-two headings."""
    headings = {
        line.strip()
        for line in markdown.splitlines()
        if line.strip().startswith("## ")
    }

    missing_sections = [
        section
        for section in REQUIRED_SECTIONS
        if f"## {section}" not in headings
    ]

    return {
        "valid": not missing_sections,
        "missing_sections": missing_sections,
    }