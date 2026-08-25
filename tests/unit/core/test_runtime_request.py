"""
===============================================================================
Unit Tests

RuntimeRequest

Validates the runtime request created by QAlchemy from command-line
arguments and passed into the orchestration layer.

Responsibilities Tested
-----------------------
- Construction
- Required field preservation
- Deliverable path preservation
- Optional reference defaults
- Reference path preservation
- Full value preservation
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from scripts.core.runtime_request import RuntimeRequest

# =============================================================================
# Construction
# =============================================================================


def test_create_valid_runtime_request() -> None:
    """Create a valid Runtime Request."""

    deliverable = Path("resources/deliverables/code.md")

    runtime_request = RuntimeRequest(
        task="Create a Playwright/Pytest test.",
        role="playwright_generate",
        target="generate-code",
        deliverable=deliverable,
    )

    assert runtime_request.task == "Create a Playwright/Pytest test."

    assert runtime_request.role == "playwright_generate"

    assert runtime_request.target == "generate-code"

    assert runtime_request.deliverable == deliverable


# =============================================================================
# Default Values
# =============================================================================


def test_references_default_to_empty_list() -> None:
    """References default to an empty list."""

    runtime_request = RuntimeRequest(
        task="Generate code.",
        role="python_generate",
        target="generate-code",
        deliverable=Path("deliverable.md"),
    )

    assert runtime_request.references == []


# =============================================================================
# References
# =============================================================================


def test_preserves_reference_paths() -> None:
    """Preserve supplied reference paths."""

    references = [
        Path("resources/reference/playwright.md"),
        Path("resources/reference/python.md"),
    ]

    runtime_request = RuntimeRequest(
        task="Generate Playwright code.",
        role="playwright_generate",
        target="generate-code",
        deliverable=Path("deliverable.md"),
        references=references,
    )

    assert runtime_request.references == references


# =============================================================================
# Preservation
# =============================================================================


def test_preserves_all_values() -> None:
    """Preserve all supplied values."""

    deliverable = Path("resources/deliverables/review.md")

    references = [
        Path("resources/reference/playwright.md"),
        Path("resources/reference/testing.md"),
    ]

    runtime_request = RuntimeRequest(
        task="Review Playwright tests.",
        role="playwright_review",
        target="review-code",
        deliverable=deliverable,
        references=references,
    )

    assert runtime_request.task == "Review Playwright tests."

    assert runtime_request.role == "playwright_review"

    assert runtime_request.target == "review-code"

    assert runtime_request.deliverable == deliverable

    assert runtime_request.references == references
