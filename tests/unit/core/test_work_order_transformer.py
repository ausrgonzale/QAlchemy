"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_work_order_transformer.py

Purpose:
    Unit tests for the WorkOrderTransformer.

Description:
    Verifies that the WorkOrderTransformer produces the canonical textual
    representation of a WorkOrder. The tests validate banner rendering,
    section rendering, content normalization, and preservation of engineering
    content.

===============================================================================
"""

from scripts.core.work_order import WorkOrder
from scripts.core.work_order_transformer import WorkOrderTransformer


class TestWorkOrderTransformer:
    """
    Unit tests for the WorkOrderTransformer.
    """

    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------
    #

    def _create_work_order(self) -> WorkOrder:
        """
        Create a sample WorkOrder for testing.
        """

        return WorkOrder(
            task="Implement LoggerService.",
            role="senior_python_engineer",
            target="generate-code",
            deliverable="# Deliverable\n\nDeliverable content.",
            references="# Reference Material\n\nReference content.",
        )

    #
    # -------------------------------------------------------------------------
    # Test Cases
    # -------------------------------------------------------------------------
    #

    def test_renders_banner(self) -> None:
        """
        Should render the WorkOrder banner.
        """

        transformer = WorkOrderTransformer()

        work_order = self._create_work_order()

        transformed = transformer.transform(work_order)

        assert "QALCHEMY WORK ORDER" in transformed

    def test_renders_all_sections(self) -> None:
        """
        Should render all WorkOrder sections.
        """

        transformer = WorkOrderTransformer()

        work_order = self._create_work_order()

        transformed = transformer.transform(work_order)

        assert "TASK" in transformed
        assert "ROLE" in transformed
        assert "TARGET" in transformed
        assert "DELIVERABLE" in transformed
        assert "REFERENCES" in transformed

    def test_normalizes_markdown_headings(self) -> None:
        """
        Should remove duplicated Markdown section headings.
        """

        transformer = WorkOrderTransformer()

        work_order = self._create_work_order()

        transformed = transformer.transform(work_order)

        assert "# Deliverable" not in transformed
        assert "# Reference Material" not in transformed

    def test_preserves_engineering_content(self) -> None:
        """
        Should preserve engineering content during transformation.
        """

        transformer = WorkOrderTransformer()

        work_order = self._create_work_order()

        transformed = transformer.transform(work_order)

        assert "Implement LoggerService." in transformed
        assert "senior_python_engineer" in transformed
        assert "generate-code" in transformed
        assert "Deliverable content." in transformed
        assert "Reference content." in transformed

    def test_returns_string(self) -> None:
        """
        Should return a transformed string.
        """

        transformer = WorkOrderTransformer()

        work_order = self._create_work_order()

        transformed = transformer.transform(work_order)

        assert isinstance(transformed, str)
