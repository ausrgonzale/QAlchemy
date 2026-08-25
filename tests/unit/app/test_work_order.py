"""
===============================================================================
Unit Tests

WorkOrder

Validates the canonical Work Order exchanged between the WorkOrderBuilderService
and QAlchemy Feature Services.

Responsibilities Tested
-----------------------
- Construction
- Required field preservation
- Optional reference defaults
- Reference preservation
- Full value preservation
===============================================================================
"""

from __future__ import annotations

from scripts.core.work_order import WorkOrder

# =============================================================================
# Construction
# =============================================================================


def test_create_valid_work_order() -> None:
    """Create a valid Work Order."""

    work_order = WorkOrder(
        task="Implement LoggerService.",
        role="senior_python_engineer",
        target="generate-code",
        deliverable=(
            "Produce one Python source file with type hints, "
            "docstrings, and no markdown."
        ),
    )

    assert work_order.task == "Implement LoggerService."
    assert work_order.role == "senior_python_engineer"
    assert work_order.target == "generate-code"
    assert (
        work_order.deliverable == "Produce one Python source file with type hints, "
        "docstrings, and no markdown."
    )


# =============================================================================
# Default Values
# =============================================================================


def test_references_default_to_empty_string() -> None:
    """References default to an empty string."""

    work_order = WorkOrder(
        task="Generate code.",
        role="python_engineer",
        target="generate-code",
        deliverable="Produce one Python source file.",
    )

    assert work_order.references == ""


# =============================================================================
# References
# =============================================================================


def test_preserves_references() -> None:
    """Preserve supplied reference material."""

    references = (
        "Follow Python engineering guidance.\n"
        "Use the project's existing logging patterns."
    )

    work_order = WorkOrder(
        task="Generate LoggerService.",
        role="python_engineer",
        target="generate-code",
        deliverable="Produce one Python source file.",
        references=references,
    )

    assert work_order.references == references


# =============================================================================
# Preservation
# =============================================================================


def test_preserves_all_values() -> None:
    """Preserve all supplied values."""

    references = "Python reference material.\n" "QAlchemy reference material."

    work_order = WorkOrder(
        task="Review PromptBuilderService.",
        role="senior_python_engineer",
        target="review-code",
        deliverable="Produce a code review report.",
        references=references,
    )

    assert work_order.task == "Review PromptBuilderService."
    assert work_order.role == "senior_python_engineer"
    assert work_order.target == "review-code"
    assert work_order.deliverable == "Produce a code review report."
    assert work_order.references == references
