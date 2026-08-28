"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    review_code_service.py

Purpose:
    Provides the Review Code feature for the QAlchemy application.

Description:
    The ReviewCodeService consumes a canonical WorkOrder and executes the
    Review Code engineering workflow.

Version 1.2
-----------
- Receives the WorkOrder from the OrchestrationService.
- Transforms the WorkOrder into an LLM request.
- Delegates AI execution to the AppExecutionService.
- Produces an engineering code review.
- Renders the engineering review into Markdown.

Architecture
------------
The ReviewCodeService is a Feature Service responsible for coordinating the
Review Code engineering workflow.

The service intentionally delegates engineering responsibilities to reusable
application components and remains focused on workflow coordination.

Responsibilities
----------------
- Receive the canonical WorkOrder.
- Read source files provided for review.
- Preprocess source code.
- Transform the WorkOrder into an LLM request.
- Acquire the configured AI client.
- Submit the review request to the LLM.
- Render the engineering review into Markdown.
- Return the rendered review.

Non-Responsibilities
--------------------
The ReviewCodeService does NOT:

- Build WorkOrders.
- Modify WorkOrders.
- Determine output destinations.
- Write files.
- Create directories.
- Coordinate application workflows.

Dependencies
------------
- AppExecutionService
- WorkOrderTransformer
- SourceCodePreprocessor
- ReportWriter

Current Consumers
-----------------
- OrchestrationService

===============================================================================
"""

from pathlib import Path

from scripts.core.report_writer import ReportWriter
from scripts.core.work_order import WorkOrder
from scripts.core.work_order_transformer import WorkOrderTransformer
from scripts.feature.source_code_preprocessor import SourceCodePreprocessor
from scripts.utils.runtime_context import RuntimeContext
from scripts.utils.work_space import WorkSpace
from services.app.app_execution_service import AppExecutionService


class ReviewCodeService:
    """
    Review Code feature service.
    """

    def __init__(
        self,
        execution_service: AppExecutionService,
        work_order_transformer: WorkOrderTransformer,
    ) -> None:
        """
        Initialize the Review Code service.
        """

        self._execution_service = execution_service
        self._work_order_transformer = work_order_transformer
        self._logger = execution_service.logger_service
        self._exception_handler = execution_service.exception_handling_service

        self._source_code_preprocessor = SourceCodePreprocessor()

    def execute(
        self,
        work_order: WorkOrder,
        workspace: WorkSpace,
        source_files: list[Path],
    ) -> str:
        """
        Execute the Review Code feature.

        Returns:
            Rendered Markdown code review report.
        """

        self._logger.log(
            level="INFO",
            operation="execute",
            message="Entering ReviewCodeService.execute().",
        )

        source_parts: list[str] = []

        for source_file in source_files:
            content = source_file.read_text(
                encoding="utf-8",
            )

            content = self._source_code_preprocessor.preprocess(
                content,
            )

            source_parts.append(
                f"FILE: {source_file}\n\n{content}",
            )

        source_code = "\n\n".join(
            source_parts,
        )

        request = self._work_order_transformer.transform(
            work_order,
            source_code=source_code,
        )

        client = self._execution_service.client_service.create()

        review = client.generate(
            request,
        )

        runtime_context = RuntimeContext()

        runtime_context.source_file = source_files[0] if source_files else None

        runtime_context.provider = self._execution_service.configuration.client.provider

        runtime_context.model = (
            self._execution_service.configuration.client.default_model
        )

        report_writer = ReportWriter(
            configuration=(self._execution_service.configuration),
        )

        rendered_report = report_writer.render(
            review=review,
            runtime_context=runtime_context,
        )

        self._logger.log(
            level="INFO",
            operation="execute",
            message="Review report rendered.",
        )

        return rendered_report
