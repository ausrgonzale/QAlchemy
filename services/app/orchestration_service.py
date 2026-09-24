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

from agents.contracts.res_agent_results import RequirementsAgentResult
from scripts.core.runtime_request import RuntimeRequest
from scripts.core.work_order import WorkOrder
from scripts.core.work_order_transformer import WorkOrderTransformer
from scripts.core.work_order_writer import WorkOrderWriter
from scripts.utils.feature_target_mapper import (
    map_feature_code,
    map_requirements_capability,
)
from scripts.utils.file_writer import FileWriter
from scripts.utils.relative_path import relative_path
from scripts.utils.route_resolver import RouteResolver
from scripts.utils.source_code_resolver import SourceCodeResolver
from scripts.utils.work_order_number_generator import (
    WorkOrderNumberGenerator,
)
from scripts.utils.work_space import WorkSpace
from services.app.app_execution_service import AppExecutionService
from services.app.work_order_builder_service import (
    WorkOrderBuilderService,
)
from services.core.logger_service import LoggerService
from services.feature.generate_code_service import GenerateCodeService
from services.feature.requirements_eval_service import RequirementsEvalService
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
        requirements_eval_service: RequirementsEvalService,
        route_resolver: RouteResolver,
        logger_service: LoggerService,
    ) -> None:
        """
        Initialize the orchestration service.
        """

        self._execution_service = execution_service

        self._route_resolver = route_resolver
        self._work_order_builder = WorkOrderBuilderService()
        self._work_order_writer = WorkOrderWriter()
        self._work_order_transformer = WorkOrderTransformer()
        self._work_order_number_generator = WorkOrderNumberGenerator()
        self._source_code_resolver = SourceCodeResolver()
        self._file_writer = FileWriter()
        self._logger_service = logger_service

        #
        # Feature Services
        #
        self._generate_code_service = generate_code_service
        self._review_code_service = review_code_service
        self._requirements_eval_service = requirements_eval_service

        #
        # Route Table
        #
        self._routes = {
            "generate_code": self._generate_code_service.execute,
        }

    def _route(
        self,
        capability,
        runtime_request,
        work_order: WorkOrder,
        workspace: WorkSpace,
        work_order_name: str,
    ) -> str | RequirementsAgentResult | None:
        """
        Route the Work Order to the appropriate workflow.
        """

        #
        # Review Code Workflow
        #
        if capability == "review_code":

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

            return rendered_report

        #
        # Requirements Evaluation Workflow
        #
        if capability == "evaluate":

            result = self._requirements_eval_service.execute(
                work_order,
                workspace,
                runtime_request.source_code,
                "evaluate_requirement",
            )

            self._persist_requirements_report(
                result.report,
                workspace=workspace,
                work_order_name=work_order_name,
            )

            return result

        #
        # Registered Feature Workflows
        #
        handler = self._routes.get(
            capability,
        )

        if handler is None:
            raise ValueError(
                f"Unsupported target: {capability}",
            )

        return handler(
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

    def _persist_requirements_report(
        self,
        rendered_report: str,
        workspace: WorkSpace,
        work_order_name: str,
    ) -> None:
        """
        Persist the requirements evaluation report to the WorkSpace.
        """

        workspace_report_path = (
            workspace.output_root / "requirements_evaluation_report.md"
        )

        self._file_writer.write(
            path=workspace_report_path,
            content=rendered_report,
        )

    def execute(
        self,
        runtime_request: RuntimeRequest,
    ) -> RequirementsAgentResult | str | None:
        """
        Execute the requested target.
        """

        route = self._route_resolver.resolve(
            runtime_request,
        )

        capability = route.capability

        work_order = self._work_order_builder.build(
            runtime_request,
            route,
        )

        feature_code = map_feature_code(
            route.target,
        )

        work_order_id = self._work_order_number_generator.generate(
            feature=feature_code,
        )

        self._logger_service.log(
            level="INFO",
            message="Work Order execution started.",
            operation="execution",
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
        # Persist the initial Work Order inside the workspace.
        #
        self._work_order_writer.write(
            content=self._work_order_transformer.work_order_execution(
                work_order=work_order,
                capability=capability,
            ),
            path=workspace.work_order_path,
        )

        #
        # Persist a canonical Work Order copy when enabled.
        #
        if runtime.persist_to_disk:

            persistent_work_order_path = (
                Path(runtime.directory) / f"{work_order_name}.md"
            )

            self._work_order_writer.write(
                content=self._work_order_transformer.work_order_execution(
                    work_order=work_order,
                    capability=capability,
                ),
                path=persistent_work_order_path,
            )

        deliverable_path = workspace.workspace_root / runtime_request.deliverable.name

        deliverable_path.write_text(
            work_order.deliverable,
            encoding="utf-8",
        )

        self._logger_service.log(
            level="INFO",
            message="Feature execution started.",
            operation="execution",
        )

        result = self._route(
            capability=capability,
            runtime_request=runtime_request,
            work_order=work_order,
            workspace=workspace,
            work_order_name=work_order_name,
        )

        self._logger_service.log(
            level="INFO",
            message="Feature execution completed.",
            operation="execution",
        )

        if isinstance(result, RequirementsAgentResult):

            #
            # Assemble Work Order completion context.
            #
            capability = map_requirements_capability(result.capability.value)
            role = result.role

            source_code = "\n".join(
                str(relative_path(path)) for path in runtime_request.source_code
            )

            #
            # Transform the completed Work Order.
            #
            completed_work_order = self._work_order_transformer.work_order_completion(
                work_order=work_order,
                source_code=source_code,
                capability=capability,
                role=role,
            )

            #
            # Persist the completed Work Order inside the workspace.
            #
            self._work_order_writer.write(
                content=completed_work_order,
                path=workspace.work_order_path,
            )

            #
            # Persist a canonical Work Order copy when enabled.
            #
            if runtime.persist_to_disk:

                persistent_work_order_path = (
                    Path(runtime.directory) / f"{work_order_name}.md"
                )

                self._work_order_writer.write(
                    content=completed_work_order,
                    path=persistent_work_order_path,
                )

            #
            # Persist the Agent-selected role.
            #
            role_path = Path("agents") / "roles" / f"{role}.md"
            role_content = role_path.read_text(encoding="utf-8")

            workspace_role_path = workspace.workspace_root / f"{role}.md"

            workspace_role_path.write_text(
                role_content,
                encoding="utf-8",
            )

            #
            # Return the report content to the caller.
            #

        return result
