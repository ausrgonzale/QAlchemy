"""
QAlchemy OrchestrationService

Purpose
-------
Coordinates execution of AI engineering workflows.

The OrchestrationService receives a RuntimeRequest, validates the requested
target, coordinates construction of the canonical WorkOrder, and routes
execution to the appropriate feature service.

Responsibilities
----------------
- Validate the requested target.
- Coordinate AIWorkOrder construction.
- Route the request to the appropriate workflow.

Out of Scope
------------
- Command-line argument parsing.
- RuntimeRequest construction.
- WorkOrder construction.
- Client communication.
- Feature-specific business logic.

Compliance
----------
BLEH

Bootstrap
---------
Invoked by the AppBootstrapService.

Handoffs
--------
Input
    RuntimeRequest

Output
    WorkOrder
"""

from pathlib import Path

from scripts.core.work_order import WorkOrder
from scripts.core.work_order_writer import WorkOrderWriter
from scripts.utils.feature_target_mapper import map_feature_code
from scripts.utils.work_order_number_generator import (
    WorkOrderNumberGenerator,
)
from scripts.utils.work_space import WorkSpace
from services.app.app_execution_service import AppExecutionService
from services.app.work_order_builder_service import (
    WorkOrderBuilderService,
)
from services.feature.generate_code_service import GenerateCodeService
from services.feature.review_code_service import ReviewCodeService


class OrchestrationService:
    """
    Coordinates application execution.

    Responsibilities:
    - Validate the requested target.
    - Coordinate AIWorkOrder construction.
    - Route the request to the appropriate workflow.
    """

    def __init__(
        self,
        execution_service: AppExecutionService,
        generate_code_service: GenerateCodeService,
        review_code_service: ReviewCodeService,
    ) -> None:

        self._execution_service = execution_service
        self._work_order_builder = WorkOrderBuilderService()
        self._work_order_writer = WorkOrderWriter()
        self._work_order_number_generator = WorkOrderNumberGenerator()

        # Feature Services
        self._generate_code_service = generate_code_service
        self._review_code_service = review_code_service

        # Route Table
        self._routes = {
            "generate_code": self._generate_code_service.execute,
            "review_code": self._review_code_service.execute,
        }

    def _route(
        self,
        target: str,
        work_order: WorkOrder,
        work_space: WorkSpace,
    ) -> None:
        """Route the Work Order to the appropriate feature service."""

        handler = self._routes.get(target)

        if handler is None:
            raise ValueError(f"Unsupported target: {target}")

        handler(
            work_order,
            work_space,
        )

        print(">>> OrchestrationService.execute()")

    def execute(self, runtime_request) -> None:
        """
        Execute the requested target.
        """

        work_order = self._work_order_builder.build(
            runtime_request,
        )

        print(">>> WorkOrder built")

        feature_code = map_feature_code(
            work_order.target,
        )

        work_order_id = self._work_order_number_generator.generate(
            feature=feature_code,
        )

        runtime = self._execution_service.configuration.work_order.runtime
        workspace_root = self._execution_service.configuration.workspace.root

        workspace = WorkSpace(
            root=Path(workspace_root),
            work_order_id=work_order_id,
        )

        workspace.create()

        workspace.role_path.write_text(
            work_order.role,
            encoding="utf-8",
        )

        workspace.deliverable_path.write_text(
            work_order.deliverable,
            encoding="utf-8",
        )

        if runtime.persist_to_disk:

            output_path = Path(runtime.directory) / f"{work_order_id}.md"

            self._work_order_writer.write(
                work_order=work_order,
                path=output_path,
            )

        self._route(
            runtime_request.target,
            work_order,
            workspace,
        )
