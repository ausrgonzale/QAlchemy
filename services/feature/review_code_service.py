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

Future Versions
---------------
Future versions will:

- Normalize AI responses.
- Persist engineering review artifacts.
- Return structured review results.
- Support orchestration result processing.

Architecture
------------
The ReviewCodeService is a Feature Service responsible for coordinating the
Review Code engineering workflow.

The service intentionally delegates engineering responsibilities to reusable
application components and remains focused on workflow coordination.

Responsibilities
----------------
- Receive the canonical WorkOrder.
- Transform the WorkOrder into an LLM request.
- Acquire the configured AI client.
- Submit the review request to the LLM.
- Produce the engineering review.

Non-Responsibilities
--------------------
The ReviewCodeService does NOT:

- Build WorkOrders.
- Modify WorkOrders.
- Load engineering documents.
- Transform engineering artifacts.
- Write files.
- Perform logging implementation.
- Translate runtime exceptions.
- Coordinate application workflows.

Dependencies
------------
- AppExecutionService
- WorkOrderTransformer

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
from scripts.utils.file_writer import FileWriter
from scripts.utils.runtime_context import RuntimeContext
from services.app.app_execution_service import AppExecutionService

REVIEW_INPUT_FILE = Path("working/output/calculator.py")
REVIEW_OUTPUT_FILE = Path("working/output/review.md")


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
    ) -> None:

        self._logger.log(
            level="INFO",
            operation="execute",
            message="Entering ReviewCodeService.execute().",
        )

        source_code = REVIEW_INPUT_FILE.read_text(
            encoding="utf-8",
        )

        source_code = self._source_code_preprocessor.preprocess(
            source_code,
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

        runtime_context.source_file = REVIEW_INPUT_FILE

        # Future - Inject self._report_write from AppBootStrapService

        report_writer = ReportWriter(
            configuration=self._execution_service.configuration,
            file_writer=FileWriter(),
        )

        output_path = report_writer.write(
            review=review,
            runtime_context=runtime_context,
        )

        self._logger.log(
            level="INFO",
            operation="execute",
            message=f"Review written to {output_path}",
        )
