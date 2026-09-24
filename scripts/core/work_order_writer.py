"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    work_order_writer.py

Purpose:
    Persists Work Orders for inspection and traceability.

Description:
    The WorkOrderWriter is responsible for transforming a WorkOrder into its
    canonical textual representation and writing it to persistent storage.

    The writer serves as the presentation layer for the canonical
    WorkOrder, allowing engineering work to be inspected, reviewed,
    archived, and compared independently of the services that produce or
    consume the work order.

Responsibilities
----------------
- Delegate rendering to the WorkOrderTransformer.
- Persist rendered work orders to disk.
- Produce human-readable engineering artifacts.
- Render WorkOrders.

Non-Responsibilities
--------------------
The WorkOrderWriter does NOT:

- Build WorkOrders.
- Modify WorkOrders.
- Read engineering input documents.
- Coordinate application workflows.
- Invoke models.
- Render model-specific requests.
- Perform logging.
- Perform exception handling.

Design Principles
-----------------
The WorkOrderWriter operates exclusively on the immutable WorkOrder.

It is intentionally independent of application services, feature services,
and model providers. The writer's responsibility is limited to producing a
persistent representation of the canonical engineering artifact.

Future versions may support additional rendering formats including JSON,
YAML, XML, or other structured representations without affecting the
AIWorkOrder or its consumers.

Current Consumers:
    - OrchestrationService (temporary)

Future Consumers:
    - Engineering Workflow Services
    - Debugging Utilities
    - Audit and Traceability Services

===============================================================================
"""

from pathlib import Path

from scripts.utils.file_writer import FileWriter


class WorkOrderWriter:
    """
    Persists rendered Work Orders.
    """

    def __init__(self) -> None:
        """Initialize the Work Order Writer."""
        self._file_writer = FileWriter()

    def write(
        self,
        content: str,
        path: Path,
    ) -> None:
        """
        Render and persist an Work Order.

        Args:
            work_order:
                Work order to persist.

            path:
                Destination markdown file.
        """

        self._file_writer.write(
            path=path,
            content=content,
        )
