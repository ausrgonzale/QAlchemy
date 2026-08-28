"""
QAlchemy OrchestrationService

Purpose
-------
Coordinates execution of AI engineering workflows.

The OrchestrationService receives a RuntimeRequest, coordinates construction
of the canonical WorkOrder, prepares the Work Order workspace, persists
workflow artifacts, and routes execution to the appropriate feature service.

Responsibilities
----------------
- Coordinate WorkOrder construction.
- Create Work Order identifiers.
- Create Work Order workspaces.
- Persist Work Orders.
- Route requests to feature workflows.
- Persist orchestration-level workflow artifacts.

Out of Scope
------------
- Command-line argument parsing.
- RuntimeRequest construction.
- WorkOrder construction implementation.
- Client communication.
- Feature-specific business logic.
- Report rendering.

Bootstrap
---------
Invoked by the AppBootstrapService.

Handoffs
--------
Input
    RuntimeRequest

Output
    Workflow artifacts
"""

from pathlib import Path

from scripts.core.runtime_request import RuntimeRequest
from scripts.core.work_order import WorkOrder
from scripts.core.work_order_writer import WorkOrderWriter
from scripts.utils.feature_target_mapper import map_feature_code
from scripts.utils.file_writer import FileWriter
from scripts.utils.source_code_resolver import SourceCodeResolver
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
    - Coordinate WorkOrder construction.
    - Create Work Order workspaces.
    - Persist Work Orders.
    - Route requests to feature workflows.
    - Persist workflow artifacts.
    """

    def __init__(
        self,
        execution_service: AppExecutionService,
        generate_code_service: GenerateCodeService,
        review_code_service: ReviewCodeService,
    ) -> None:
        """
        Initialize the orchestration service.
        """

        self._execution_service = execution_service

        self._work_order_builder = WorkOrderBuilderService()
        self._work_order_writer = WorkOrderWriter()
        self._work_order_number_generator = WorkOrderNumberGenerator()
        self._source_code_resolver = SourceCodeResolver()
        self._file_writer = FileWriter()

        #
        # Feature Services
        #
        self._generate_code_service = generate_code_service
        self._review_code_service = review_code_service

        #
        # Route Table
        #
        self._routes = {
            "generate_code": self._generate_code_service.execute,
        }

    def _route(
        self,
        runtime_request: RuntimeRequest,
        work_order: WorkOrder,
        workspace: WorkSpace,
        work_order_name: str,
    ) -> None:
        """
        Route the Work Order to the appropriate workflow.
        """

        if runtime_request.target == "review_code":

            source_files = self._source_code_resolver.resolve(
                runtime_request.source_code,
            )

            rendered_report = self._review_code_service.execute(
                work_order,
                workspace,
                source_files,
            )

            self._persist_review_report(
                rendered_report=rendered_report,
                workspace=workspace,
                work_order_name=work_order_name,
            )

            return

        handler = self._routes.get(
            runtime_request.target,
        )

        if handler is None:
            raise ValueError(
                f"Unsupported target: {runtime_request.target}",
            )

        handler(
            work_order,
            workspace,
        )

    def _persist_review_report(
        self,
        rendered_report: str,
        workspace: WorkSpace,
        work_order_name: str,
    ) -> None:
        """
        Persist the rendered code review report.

        The report is always written to the Work Order workspace.

        When Work Order persistence is enabled, a second copy is written
        to the configured persistent review report location.
        """

        workspace_report_path = (
            workspace.output_root / f"{work_order_name}_code_review.md"
        )

        self._file_writer.write(
            path=workspace_report_path,
            content=rendered_report,
        )

        reports_configuration = self._execution_service.configuration.reports

        runtime = self._execution_service.configuration.work_order.runtime

        if runtime.persist_to_disk:

            persistent_report_path = (
                Path(
                    reports_configuration.review.output_directory,
                )
                / f"{work_order_name}_code_review.md"
            )

            self._file_writer.write(
                path=persistent_report_path,
                content=rendered_report,
            )

    def execute(
        self,
        runtime_request: RuntimeRequest,
    ) -> None:
        """
        Execute the requested target.
        """

        work_order = self._work_order_builder.build(
            runtime_request,
        )

        feature_code = map_feature_code(
            work_order.target,
        )

        work_order_id = self._work_order_number_generator.generate(
            feature=feature_code,
        )

        #
        # Normalize filesystem naming.
        #
        work_order_name = work_order_id.lower()

        runtime = self._execution_service.configuration.work_order.runtime

        workspace_root = self._execution_service.configuration.workspace.root

        workspace = WorkSpace(
            root=Path(workspace_root),
            work_order_id=work_order_name,
        )

        workspace.create()

        #
        # Always persist the Work Order inside its workspace.
        #
        self._work_order_writer.write(
            work_order=work_order,
            path=workspace.work_order_path,
        )

        role_path = workspace.workspace_root / runtime_request.role.name

        role_path.write_text(
            work_order.role,
            encoding="utf-8",
        )

        deliverable_path = workspace.workspace_root / runtime_request.deliverable.name

        deliverable_path.write_text(
            work_order.deliverable,
            encoding="utf-8",
        )

        #
        # Persist a canonical Work Order copy when enabled.
        #
        if runtime.persist_to_disk:

            persistent_work_order_path = (
                Path(runtime.directory) / f"{work_order_name}.md"
            )

            self._work_order_writer.write(
                work_order=work_order,
                path=persistent_work_order_path,
            )

        self._route(
            runtime_request=runtime_request,
            work_order=work_order,
            workspace=workspace,
            work_order_name=work_order_name,
        )
