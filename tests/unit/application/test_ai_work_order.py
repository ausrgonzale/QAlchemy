"""
Unit tests for AIWorkOrder.
"""

from __future__ import annotations

from scripts.core.ai_work_order import AIWorkOrder

# =============================================================================
# Construction
# =============================================================================


def test_create_valid_ai_work_order() -> None:
    """Create a valid AI Work Order."""

    work_order = AIWorkOrder(
        who="You are a senior Python engineer.",
        what="Implement LoggerService.",
        why="Add centralized logging.",
    )

    assert work_order.who == "You are a senior Python engineer."
    assert work_order.what == "Implement LoggerService."
    assert work_order.why == "Add centralized logging."


def test_context_defaults_to_empty_string() -> None:
    """Context defaults to an empty string."""

    work_order = AIWorkOrder(
        who="Engineer",
        what="Generate code",
        why="Implement feature",
    )

    assert work_order.context == ""


def test_preserves_context() -> None:
    """Preserve supplied context."""

    work_order = AIWorkOrder(
        who="Engineer",
        what="Generate code",
        why="Implement feature",
        context="Existing implementation attached.",
    )

    assert work_order.context == "Existing implementation attached."


def test_preserves_all_values() -> None:
    """Preserve all supplied values."""

    work_order = AIWorkOrder(
        who="Architect",
        what="Review PromptBuilderService.",
        why="Validate architecture.",
        context="Framework v1.1",
    )

    assert work_order.who == "Architect"
    assert work_order.what == "Review PromptBuilderService."
    assert work_order.why == "Validate architecture."
    assert work_order.context == "Framework v1.1"
