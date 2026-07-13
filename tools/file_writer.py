"""Utilities for saving generated Markdown content."""

from pathlib import Path


def save_markdown_file(file_path: str, content: str) -> str:
    """Save Markdown content to a file and return a useful result."""
    path = Path(file_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        return f"Could not save Markdown file: {error}"

    return f"Markdown file saved successfully: {path.resolve()}"