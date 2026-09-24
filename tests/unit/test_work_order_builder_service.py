"""
===============================================================================
Unit Tests

WorkOrderBuilderService

Validates construction of the canonical WorkOrder from a RuntimeRequest.

Responsibilities Tested
-----------------------
- WorkOrder construction
- Task preservation
- Role resolution
- Target preservation
- Deliverable resolution
- Optional reference resolution
===============================================================================
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.core.runtime_request import RuntimeRequest
from scripts.utils.route_resolver import Route
from services.app.work_order_builder_service import WorkOrderBuilderService

pytestmark = [
    pytest.mark.application,
    pytest.mark.work_order,
]

# =============================================================================
# Construction
# =============================================================================


def test_builds_work_order(tmp_path: Path) -> None:
    """Build a WorkOrder from a RuntimeRequest."""

    role = tmp_path / "role.md"
    deliverable = tmp_path / "deliverable.md"

    role.write_text(
        "Act as a Playwright automation architect.",
        encoding="utf-8",
    )

    deliverable.write_text(
        "Produce a Playwright/Pytest project.",
        encoding="utf-8",
    )

    runtime_request = RuntimeRequest(
        task="Create a Playwright test.",
        role=role,
        target="generate-code",
        deliverable=deliverable,
    )

    route = Route(
        target="generate-code",
        capability="generate",
        role="playwright_engineer",
    )

    work_order = WorkOrderBuilderService().build(runtime_request, route)

    assert work_order.task == "Create a Playwright test."
    assert work_order.role == "playwright_engineer"
    assert work_order.target == "generate-code"
    assert work_order.deliverable == "Produce a Playwright/Pytest project."
    assert work_order.references == ""


# =============================================================================
# References
# =============================================================================


def test_reads_reference_material(tmp_path: Path) -> None:
    """Read optional reference material into the WorkOrder."""

    role = tmp_path / "role.md"
    deliverable = tmp_path / "deliverable.md"
    reference_one = tmp_path / "playwright.md"
    reference_two = tmp_path / "python.md"

    role.write_text(
        "Act as a Playwright automation architect.",
        encoding="utf-8",
    )

    deliverable.write_text(
        "Produce a Playwright/Pytest project.",
        encoding="utf-8",
    )

    reference_one.write_text(
        "Use Playwright best practices.",
        encoding="utf-8",
    )

    reference_two.write_text(
        "Use Python best practices.",
        encoding="utf-8",
    )

    runtime_request = RuntimeRequest(
        task="Create a Playwright test.",
        role=role,
        target="generate-code",
        deliverable=deliverable,
        references=[
            reference_one,
            reference_two,
        ],
    )

    route = Route(
        target="generate-code",
        capability="generate",
        role="playwright_engineer",
    )

    work_order = WorkOrderBuilderService().build(runtime_request, route)

    assert (
        work_order.references
        == "Use Playwright best practices.\n\nUse Python best practices."
    )
