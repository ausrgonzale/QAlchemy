"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_work_order_writer.py

Purpose:
    Validates persistence of rendered Work Orders.

Description:
    These tests verify that WorkOrderWriter transforms a canonical WorkOrder
    and persists the resulting representation to the supplied destination.

Responsibilities
----------------
- Verify WorkOrders are rendered before persistence.
- Verify rendered WorkOrders are written to the supplied path.
- Verify the persisted content matches the transformed WorkOrder.

Non-Responsibilities
--------------------
These tests do NOT:

- Build WorkOrders.
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

from scripts.core.work_order import WorkOrder
from scripts.core.work_order_writer import WorkOrderWriter


def test_writes_work_order_to_supplied_path(
    tmp_path: Path,
) -> None:
    """Render and persist a WorkOrder to the supplied path."""

    work_order = WorkOrder(
        task="Create a Playwright automation solution.",
        role="Act as a Senior Playwright Automation Architect.",
        target="generate_code",
        deliverable="""## Required Artifact

Generate exactly one file:

pages/google_search_page.py
""",
    )

    output_path = tmp_path / "work_orders" / "WOGCS20260823151130-4827.md"

    writer = WorkOrderWriter()

    writer.write(
        work_order=work_order,
        path=output_path,
    )

    assert output_path.exists()

    content = output_path.read_text(
        encoding="utf-8",
    )

    assert "QALCHEMY WORK ORDER" in content
    assert "Create a Playwright automation solution." in content
    assert "Act as a Senior Playwright Automation Architect." in content
    assert "generate_code" in content
    assert "pages/google_search_page.py" in content
