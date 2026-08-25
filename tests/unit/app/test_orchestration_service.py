"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_orchestration_service.py

Purpose:
    Unit tests for the OrchestrationService.

Description:
    Verifies that the OrchestrationService validates runtime requests,
    coordinates WorkOrder construction, and persists Work Orders according
    to the configured runtime policy.

Responsibilities Tested
-----------------------
- WorkOrder construction
- WorkOrder persistence
- Runtime configuration behavior

===============================================================================
"""

from unittest.mock import Mock, patch

from services.app.orchestration_service import OrchestrationService


def create_execution_service(
    *,
    persist_to_disk: bool,
) -> Mock:
    """
    Create a mocked AppExecutionService.
    """

    runtime = Mock()
    runtime.persist_to_disk = persist_to_disk
    runtime.directory = "work_order"

    work_order = Mock()
    work_order.runtime = runtime

    workspace = Mock()
    workspace.root = "work_space"

    configuration = Mock()
    configuration.work_order = work_order
    configuration.workspace = workspace

    execution_service = Mock()
    execution_service.configuration = configuration

    return execution_service


class TestOrchestrationService:
    """
    Unit tests for the OrchestrationService.
    """

    def test_builds_work_order(self) -> None:

        runtime_request = Mock()
        runtime_request.target = "generate_code"

        work_order = Mock()
        work_order.target = "generate_code"
        work_order.role = "Software Engineer"
        work_order.deliverable = "Generate the requested Python implementation."

        execution_service = create_execution_service(
            persist_to_disk=False,
        )

        generate_code_service = Mock()
        review_code_service = Mock()

        with (
            patch(
                "services.app.orchestration_service.WorkOrderBuilderService.build",
                return_value=work_order,
            ) as mock_build,
            patch(
                "services.app.orchestration_service.WorkOrderNumberGenerator.generate",
                return_value="WOGCS20260823155841-7690",
            ),
            patch(
                "services.app.orchestration_service.WorkOrderWriter.write",
            ),
        ):

            service = OrchestrationService(
                execution_service=execution_service,
                generate_code_service=generate_code_service,
                review_code_service=review_code_service,
            )

            service.execute(runtime_request)

            mock_build.assert_called_once_with(runtime_request)

    def test_writes_work_order_when_persistence_is_enabled(self) -> None:

        runtime_request = Mock()
        runtime_request.target = "generate_code"

        execution_service = create_execution_service(
            persist_to_disk=True,
        )

        generate_code_service = Mock()
        review_code_service = Mock()

        work_order = Mock()
        work_order.target = "generate_code"
        work_order.role = "Software Engineer"
        work_order.deliverable = "Generate the requested Python implementation."

        with (
            patch(
                "services.app.orchestration_service.WorkOrderBuilderService.build",
                return_value=work_order,
            ),
            patch(
                "services.app.orchestration_service.WorkOrderWriter.write",
            ) as mock_write,
        ):

            service = OrchestrationService(
                execution_service=execution_service,
                generate_code_service=generate_code_service,
                review_code_service=review_code_service,
            )

            service.execute(runtime_request)

            mock_write.assert_called_once()

    def test_does_not_write_work_order_when_persistence_is_disabled(self) -> None:

        runtime_request = Mock()
        runtime_request.target = "generate_code"

        execution_service = create_execution_service(
            persist_to_disk=False,
        )

        generate_code_service = Mock()
        review_code_service = Mock()

        work_order = Mock()
        work_order.target = "generate_code"
        work_order.role = "Software Engineer"
        work_order.deliverable = "Generate the requested Python implementation."

        with (
            patch(
                "services.app.orchestration_service.WorkOrderBuilderService.build",
                return_value=work_order,
            ),
            patch(
                "services.app.orchestration_service.WorkOrderWriter.write",
            ) as mock_write,
        ):

            service = OrchestrationService(
                execution_service=execution_service,
                generate_code_service=generate_code_service,
                review_code_service=review_code_service,
            )

            service.execute(runtime_request)

            mock_write.assert_not_called()

    def test_creates_workspace_before_writing_work_order(self) -> None:
        runtime_request = Mock()
        runtime_request.target = "generate_code"

        execution_service = create_execution_service(
            persist_to_disk=True,
        )

        generate_code_service = Mock()
        review_code_service = Mock()

        work_order = Mock()
        work_order.target = "generate_code"
        work_order.role = "Software Engineer"
        work_order.deliverable = "Generate the requested Python implementation."

        events: list[str] = []

        def workspace_created() -> None:
            events.append("workspace")

        def work_order_written(*args, **kwargs) -> None:
            events.append("work_order")

        with (
            patch(
                "services.app.orchestration_service.WorkOrderBuilderService.build",
                return_value=work_order,
            ),
            patch(
                "services.app.orchestration_service.WorkOrderNumberGenerator.generate",
                return_value="WOGCS20260823155841-7690",
            ),
            patch(
                "services.app.orchestration_service.WorkSpace.create",
                side_effect=workspace_created,
            ) as mock_workspace_create,
            patch(
                "services.app.orchestration_service.WorkOrderWriter.write",
                side_effect=work_order_written,
            ) as mock_write,
        ):

            service = OrchestrationService(
                execution_service=execution_service,
                generate_code_service=generate_code_service,
                review_code_service=review_code_service,
            )

            service.execute(runtime_request)

            mock_workspace_create.assert_called_once()
            mock_write.assert_called_once()

            assert events == ["workspace", "work_order"]
