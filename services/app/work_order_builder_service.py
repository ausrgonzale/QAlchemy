"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    work_order_builder_service.py

Purpose:
    Builds the canonical Work Order.

Description:
    The WorkOrderBuilderService transforms a RuntimeRequest into a canonical WorkOrder.

    It is responsible for reading the requested engineering artifacts and
    assembling the canonical WorkOrder.

Current Consumers:
    - OrchestrationService

Future Consumers:
    - GenerateCodeService
    - ReviewCodeService
    - EvaluateRequirementService
    - GenerateTestCaseService
    - AnalyzeDefectService

===============================================================================
"""

from scripts.core.runtime_request import RuntimeRequest
from scripts.core.work_order import WorkOrder
from scripts.utils.file_reader import FileReader


class WorkOrderBuilderService:
    """
    Builds the canonical Work Order.

    Responsibilities:
        - Read engineering input documents.
        - Assemble the canonical WorkOrder.
        - Return the completed WorkOrder.

    Out of Scope:
        - AI provider communication.
        - Feature execution.
        - Runtime orchestration.
        - Logging.
        - Exception handling.
    """

    def __init__(self) -> None:
        """Initialize the Work Order Builder."""

        self._file_reader = FileReader()

    def build(self, runtime_request: RuntimeRequest) -> WorkOrder:
        """
        Build an AI Work Order from a RuntimeRequest.
        """

        role = self._read_role(runtime_request)

        deliverable = self._read_deliverable(runtime_request)

        references = self._read_references(runtime_request)

        return WorkOrder(
            task=runtime_request.task,
            role=role,
            target=runtime_request.target,
            deliverable=deliverable,
            references=references,
        )

    #
    # -------------------------------------------------------------------------
    # Private Methods
    # -------------------------------------------------------------------------
    #

    def _read_role(self, runtime_request: RuntimeRequest) -> str:
        """
        Read the role definition.
        """

        return self._file_reader.read(
            runtime_request.role,
        )

    def _read_deliverable(self, runtime_request: RuntimeRequest) -> str:
        """
        Read all deliverable input documents.
        """
        return self._file_reader.read_many(
            [runtime_request.deliverable],
        )

    def _read_references(
        self,
        runtime_request: RuntimeRequest,
    ) -> str:
        """
        Read optional reference material.
        """

        return self._file_reader.read_many(
            runtime_request.references,
        )
