"""Utilities for saving generated Markdown content."""

from pathlib import Path


class FileWriteError(OSError):
    """Raised when generated Markdown cannot be written to disk."""


def save_markdown_file(
    file_path: str | Path,
    content: str,
) -> Path:
    """Save Markdown content and return the absolute saved path."""
    path = Path(file_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        raise FileWriteError(
            f"Could not save Markdown file to `{path}`: {error}"
        ) from error

    return path.resolve()
