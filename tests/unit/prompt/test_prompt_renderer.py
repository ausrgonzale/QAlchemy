"""
Unit tests for PromptRenderer.
"""

from __future__ import annotations

from scripts.core.prompt_renderer import PromptRenderer

# =============================================================================
# Construction
# =============================================================================


def test_create_prompt_renderer() -> None:
    """Create a PromptRenderer."""

    renderer = PromptRenderer()

    assert renderer is not None


# =============================================================================
# Rendering
# =============================================================================


def test_render_single_section() -> None:
    """Render a single prompt section."""

    renderer = PromptRenderer()

    prompt = renderer.render(
        [
            (
                "Objective",
                "Generate LoggerService.",
            ),
        ]
    )

    expected = "## Objective\n" "Generate LoggerService."

    assert prompt == expected


def test_render_multiple_sections() -> None:
    """Render multiple sections."""

    renderer = PromptRenderer()

    prompt = renderer.render(
        [
            (
                "Objective",
                "Generate code.",
            ),
            (
                "Instructions",
                "Follow project standards.",
            ),
        ]
    )

    assert "## Objective" in prompt
    assert "Generate code." in prompt

    assert "## Instructions" in prompt
    assert "Follow project standards." in prompt


def test_skip_empty_sections() -> None:
    """Skip empty prompt sections."""

    renderer = PromptRenderer()

    prompt = renderer.render(
        [
            (
                "Objective",
                "Generate code.",
            ),
            (
                "Context",
                "",
            ),
        ]
    )

    assert "## Objective" in prompt
    assert "Generate code." in prompt

    assert "## Context" not in prompt


def test_preserve_section_order() -> None:
    """Render sections in supplied order."""

    renderer = PromptRenderer()

    prompt = renderer.render(
        [
            (
                "System Prompt",
                "You are a senior engineer.",
            ),
            (
                "Objective",
                "Generate code.",
            ),
            (
                "Instructions",
                "Follow standards.",
            ),
        ]
    )

    assert (
        prompt.index("System Prompt")
        < prompt.index("Objective")
        < prompt.index("Instructions")
    )


def test_trim_surrounding_whitespace() -> None:
    """Trim surrounding whitespace from content."""

    renderer = PromptRenderer()

    prompt = renderer.render(
        [
            (
                "Objective",
                "   Generate code.   ",
            ),
        ]
    )

    expected = "## Objective\n" "Generate code."

    assert prompt == expected
