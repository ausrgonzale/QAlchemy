"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_work_order_writer.py

Purpose:
    Validates persistence of rendered Work Orders.

Description:
    These tests verify that WorkOrderWriter persists already-rendered
    Work Order content to the supplied destination.

Responsibilities
----------------
- Verify rendered Work Order content is written to the supplied path.
- Verify the persisted content matches the supplied content.

Non-Responsibilities
--------------------
These tests do NOT:

- Build WorkOrders.
- Transform WorkOrders.
- Generate Work Order identifiers.
- Create WorkSpaces.
- Invoke AI providers.
- Execute Feature Services.
- Perform orchestration.
- Test WorkOrderTransformer implementation.
- Test FileWriter implementation.

===============================================================================
"""

from pathlib import Path

from scripts.core.work_order_writer import WorkOrderWriter


def test_writes_work_order_to_supplied_path(
    tmp_path: Path,
) -> None:
    """Persist rendered Work Order content to the supplied path."""

    output_path = tmp_path / "work_orders" / "WOGCS20260823151130-4827.md"

    content = """QALCHEMY WORK ORDER

TASK
Create a Playwright automation solution.

ROLE
Act as a Senior Playwright Automation Architect.

TARGET
generate_code

DELIVERABLE
## Required Artifact

Generate exactly one file:

pages/google_search_page.py
"""

    writer = WorkOrderWriter()

    writer.write(
        content=content,
        path=output_path,
    )

    assert output_path.exists()

    persisted_content = output_path.read_text(
        encoding="utf-8",
    )

    assert "QALCHEMY WORK ORDER" in persisted_content
    assert "Create a Playwright automation solution." in persisted_content
    assert "Act as a Senior Playwright Automation Architect." in persisted_content
    assert "generate_code" in persisted_content
    assert "pages/google_search_page.py" in persisted_content
