"""
===============================================================================
Unit Tests

RuntimeRequest

Validates the runtime request transport contract between the QAlchemy
application entry point and the orchestration layer.

Responsibilities Tested
-----------------------
- Construction
- Required field preservation
- Source code input defaults
- Source code input preservation
- Reference input defaults
- Reference input preservation
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

from scripts.core.runtime_request import RuntimeRequest

# =============================================================================
# Construction
# =============================================================================


def test_create_valid_runtime_request() -> None:
    """Create a valid RuntimeRequest."""

    role = Path("resources/role/playwright_engineer.md")
    deliverable = Path("resources/deliverable/review_code.md")
    source_code = [
        Path("/project/src/calculator.py"),
    ]
    references = [
        Path("resources/standards/python_standards.md"),
    ]

    request = RuntimeRequest(
        task="Review the calculator implementation.",
        role=role,
        target="review-code",
        deliverable=deliverable,
        source_code=source_code,
        references=references,
    )

    assert request.task == "Review the calculator implementation."
    assert request.role == role
    assert request.target == "review-code"
    assert request.deliverable == deliverable
    assert request.source_code == source_code
    assert request.references == references


# =============================================================================
# Defaults
# =============================================================================


def test_source_code_defaults_to_empty_list() -> None:
    """Source code defaults to an empty list."""

    request = RuntimeRequest(
        task="Generate a Playwright page.",
        role=Path("resources/role/playwright_engineer.md"),
        target="generate-code",
        deliverable=Path("resources/deliverable/generate_code.md"),
    )

    assert request.source_code == []


def test_references_default_to_empty_list() -> None:
    """References default to an empty list."""

    request = RuntimeRequest(
        task="Generate a Playwright page.",
        role=Path("resources/role/playwright_engineer.md"),
        target="generate-code",
        deliverable=Path("resources/deliverable/generate_code.md"),
    )

    assert request.references == []


# =============================================================================
# Source Code
# =============================================================================


def test_preserves_multiple_source_code_paths() -> None:
    """Preserve multiple source code input paths."""

    source_code = [
        Path("/project/src/calculator.py"),
        Path("/project/src/helpers.py"),
        Path("/project/src/pages/login.py"),
    ]

    request = RuntimeRequest(
        task="Review the application source.",
        role=Path("resources/role/python_reviewer.md"),
        target="review-code",
        deliverable=Path("resources/deliverable/review_code.md"),
        source_code=source_code,
    )

    assert request.source_code == source_code


# =============================================================================
# References
# =============================================================================


def test_preserves_multiple_reference_paths() -> None:
    """Preserve multiple reference material paths."""

    references = [
        Path("resources/standards/python_standards.md"),
        Path("resources/standards/playwright_standards.md"),
    ]

    request = RuntimeRequest(
        task="Review the application source.",
        role=Path("resources/role/python_reviewer.md"),
        target="review-code",
        deliverable=Path("resources/deliverable/review_code.md"),
        references=references,
    )

    assert request.references == references
