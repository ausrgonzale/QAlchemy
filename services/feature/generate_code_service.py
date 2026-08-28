"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    generate_code_service.py

Purpose:
    Provides the Generate Code feature for the QAlchemy application.

Description:
    The GenerateCodeService consumes a canonical WorkOrder and executes the
    Generate Code engineering workflow.

Version 1.2
-----------
- Receives the WorkOrder from the OrchestrationService.
- Transforms the WorkOrder into an LLM request.
- Delegates AI execution to the AppExecutionService.
- Displays the generated response.

Future versions will:
- Normalize response.
- Persist prompts.
- Persist response.
- Move output location to application configuration.

===============================================================================
"""

from scripts.core.work_order import WorkOrder
from scripts.core.work_order_transformer import WorkOrderTransformer
from scripts.utils.create_generated_artifacts import (
    create_generated_artifacts,
)
from scripts.utils.normalize_provider_response import (
    normalize_provider_response,
)
from scripts.utils.work_space import WorkSpace
from services.app.app_execution_service import AppExecutionService


class GenerateCodeService:
    """
    Generate Code feature service.
    """

    def __init__(
        self,
        execution_service: AppExecutionService,
        work_order_transformer: WorkOrderTransformer,
    ) -> None:
        """
        Initialize the Generate Code service.
        """

        self._execution_service = execution_service
        self._work_order_transformer = work_order_transformer
        self._logger = execution_service.logger_service
        self._exception_handler = execution_service.exception_handling_service

    def execute(
        self,
        work_order: WorkOrder,
        workspace: WorkSpace,
    ) -> None:
        """
        Execute the Generate Code feature.
        """

        self._logger.log(
            level="INFO",
            message="Entering GenerateCodeService.execute().",
            operation="execute",
        )

        request = self._work_order_transformer.transform(work_order)

        client = self._execution_service.client_service.create()

        response = client.generate(request)

        normalized_response = normalize_provider_response(
            response,
        )

        print(">>> NORMALIZED RESPONSE:")
        print(normalized_response)

        artifacts = create_generated_artifacts(
            work_order,
            normalized_response,
        )

        for artifact in artifacts:
            output_path = workspace.output_root / artifact.relative_path

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path.write_text(
                artifact.content,
                encoding="utf-8",
            )

        self._logger.log(
            level="INFO",
            message=f"Created {len(artifacts)} generated artifact(s).",
            operation="execute",
        )

        #
        # Future:
        #   Normalize response.
        #   Persist prompt.
        #   Persist response.
        #   Persist generated source files.
        #
