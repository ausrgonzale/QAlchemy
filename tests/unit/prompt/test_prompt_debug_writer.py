"""
Unit tests for PromptDebugWriter.
"""

from __future__ import annotations

from pathlib import Path

from scripts.core.prompt_debug_writer import PromptDebugWriter

# =============================================================================
# Construction
# =============================================================================


def test_create_prompt_debug_writer() -> None:
    """Create a PromptDebugWriter."""

    writer = PromptDebugWriter()

    assert writer is not None


# =============================================================================
# Writing
# =============================================================================


def test_write_creates_output_directory(tmp_path: Path) -> None:
    """Create the output directory when it does not exist."""

    writer = PromptDebugWriter()

    output_directory = tmp_path / "debug"

    writer.write(
        prompt_model=[],
        rendered_prompt="Prompt",
        output_directory=str(output_directory),
    )

    assert output_directory.exists()
    assert output_directory.is_dir()


def test_write_returns_output_path(tmp_path: Path) -> None:
    """Return the generated output path."""

    writer = PromptDebugWriter()

    file_path = writer.write(
        prompt_model=[],
        rendered_prompt="Prompt",
        output_directory=str(tmp_path),
    )

    assert isinstance(file_path, Path)
    assert file_path.exists()


def test_write_contains_prompt_model(tmp_path: Path) -> None:
    """Write the prompt model."""

    writer = PromptDebugWriter()

    file_path = writer.write(
        prompt_model=[
            (
                "Objective",
                "Generate LoggerService.",
            ),
        ],
        rendered_prompt="Prompt",
        output_directory=str(tmp_path),
    )

    contents = file_path.read_text(encoding="utf-8")

    assert "# Prompt Debug Output" in contents
    assert "## Prompt Model" in contents
    assert "- Objective: Generate LoggerService." in contents


def test_write_contains_rendered_prompt(tmp_path: Path) -> None:
    """Write the rendered prompt."""

    writer = PromptDebugWriter()

    file_path = writer.write(
        prompt_model=[],
        rendered_prompt="Rendered Prompt",
        output_directory=str(tmp_path),
    )

    contents = file_path.read_text(encoding="utf-8")

    assert "## Rendered Prompt" in contents
    assert "Rendered Prompt" in contents


def test_write_generates_markdown_file(tmp_path: Path) -> None:
    """Generate a Markdown file."""

    writer = PromptDebugWriter()

    file_path = writer.write(
        prompt_model=[],
        rendered_prompt="Prompt",
        output_directory=str(tmp_path),
    )

    assert file_path.suffix == ".md"
