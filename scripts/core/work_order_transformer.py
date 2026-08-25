"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    work_order_transformer.py

Purpose:
    Transforms the canonical WorkOrder into the request format required by the target LLM.

Description:
    The WorkOrderTransformer is responsible for transforming the immutable
    WorkOrder into a consistent, human-readable representation suitable for presentation, inspection, debugging, logging, persistence, and model consumption.

    The transformer is the single authoritative component that defines how an engineering work order is represented outside of the application's object model. By centralizing transformer logic, all consumers receive an identical representation of the same canonical engineering artifact.

Architecture
------------
The WorkOrderTransformer forms the transformation boundary between the
canonical WorkOrder and the target LLM.

Within QAlchemy, engineering information is represented as strongly typed
domain objects. At application boundaries, those objects are transformed into textual representations appropriate for their consumers.

Responsibilities
----------------
- Transforms WorkOrders into the request format required by an LLM.
- Produce consistent output for all application consumers.
- Preserve the complete semantic content of an WorkOrder.
- Improve readability without modifying engineering intent.

Non-Responsibilities
--------------------
The WorkOrderTransformer does NOT:

- Build WorkOrders.
- Modify WorkOrders.
- Read engineering documents.
- Write files.
- Perform logging.
- Perform debugging.
- Execute LLM models.
- Coordinate application workflows.

Design Principles
-----------------
The WorkOrderTransformer is deterministic and stateless.

Given the same WorkOrder, the transformer will always produce the same LLM request.

The transformer owns presentation only. It never changes the engineering content contained within the WorkOrder.

Future Evolution
----------------
Future versions may support multiple rendering formats including Markdown,
JSON, YAML, XML, or other structured representations while preserving the
WorkOrder as the canonical engineering object.

Current Consumers:
    - GenerateCodeService

Future Consumers:
    - ReviewCodeService
    - RequirementEvalService
    - Model Clients
    - Audit and Traceability Services

===============================================================================
"""

from scripts.core.work_order import WorkOrder


class WorkOrderTransformer:
    """
    Transforms a WorkOrder into a request format required by the target
    LLM.
    """

    _HEADER_DIVIDER = "=" * 79
    _SECTION_DIVIDER = "-" * 79

    def transform(
        self,
        work_order: WorkOrder,
    ) -> str:
        """
        Transforms a WorkOrder into an LLM request.
        """

        sections = [
            self._render_banner(),
            self._render_section("TASK", work_order.task),
            self._render_section("ROLE", work_order.role),
            self._render_section("TARGET", work_order.target),
            self._render_section("DELIVERABLE", work_order.deliverable),
            self._render_section("REFERENCES", work_order.references),
        ]

        return "\n\n".join(sections)

    def _render_banner(self) -> str:
        """
        Render the Work Order banner.
        """

        title = "QALCHEMY WORK ORDER"
        width = len(self._HEADER_DIVIDER)

        return (
            f"{self._HEADER_DIVIDER}\n"
            f"{title.center(width)}\n"
            f"{self._HEADER_DIVIDER}"
        )

    def _render_section(
        self,
        title: str,
        content: str,
    ) -> str:
        """
        Render a Work Order section.
        """

        content = self._normalize_content(content)

        return f"{title}\n" f"{self._SECTION_DIVIDER}\n\n" f"{content}"

    def _normalize_content(
        self,
        content: str,
    ) -> str:
        """
        Normalize Work Order content for presentation.

        Removes duplicated Markdown section headings while preserving the
        engineering content.
        """

        lines = content.splitlines()

        #
        # Remove the leading Markdown heading.
        #
        if lines and lines[0].startswith("#"):
            lines = lines[1:]

        #
        # Remove a single blank line following the heading.
        #
        if lines and not lines[0].strip():
            lines = lines[1:]

        return "\n".join(lines)
