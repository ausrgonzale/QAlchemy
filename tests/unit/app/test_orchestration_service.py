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

from pathlib import Path
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
        runtime_request.role = Path(
            "resources/role/playwright_engineer.md",
        )
        runtime_request.deliverable = Path(
            "resources/deliverable/playwright_google.md",
        )

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
        runtime_request.role = Path(
            "resources/role/playwright_engineer.md",
        )
        runtime_request.deliverable = Path(
            "resources/deliverable/playwright_google.md",
        )

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

            assert mock_write.call_count == 2

    def test_writes_work_order_to_workspace_when_persistence_is_disabled(
        self,
    ) -> None:

        runtime_request = Mock()
        runtime_request.target = "generate_code"
        runtime_request.role = Path(
            "resources/role/playwright_engineer.md",
        )
        runtime_request.deliverable = Path(
            "resources/deliverable/playwright_google.md",
        )

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

            mock_write.assert_called_once()

    def test_creates_workspace_before_writing_work_order(self) -> None:

        runtime_request = Mock()
        runtime_request.target = "generate_code"
        runtime_request.role = Path(
            "resources/role/playwright_engineer.md",
        )
        runtime_request.deliverable = Path(
            "resources/deliverable/playwright_google.md",
        )

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
            events.append(
                f"work_order:{kwargs['path']}",
            )

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
            assert mock_write.call_count == 2

            assert events[0] == "workspace"

            assert events[1].startswith(
                "work_order:work_space/",
            )

            assert events[2].startswith(
                "work_order:work_order/",
            )

    def test_writes_same_work_order_to_both_locations(self) -> None:

        runtime_request = Mock()
        runtime_request.target = "generate_code"
        runtime_request.role = Path(
            "resources/role/playwright_engineer.md",
        )
        runtime_request.deliverable = Path(
            "resources/deliverable/playwright_google.md",
        )

        execution_service = create_execution_service(
            persist_to_disk=True,
        )

        generate_code_service = Mock()
        review_code_service = Mock()

        work_order = Mock()
        work_order.target = "generate_code"
        work_order.role = "Software Engineer"
        work_order.deliverable = "Generate the requested Python implementation."

        work_order_id = "WOGCS20260823155841-7690"

        with (
            patch(
                "services.app.orchestration_service.WorkOrderBuilderService.build",
                return_value=work_order,
            ),
            patch(
                "services.app.orchestration_service.WorkOrderNumberGenerator.generate",
                return_value=work_order_id,
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

            assert mock_write.call_count == 2

            first_call = mock_write.call_args_list[0]
            second_call = mock_write.call_args_list[1]

            assert first_call.kwargs["work_order"] is work_order
            assert second_call.kwargs["work_order"] is work_order

            expected_filename = f"{work_order_id.lower()}.md"

            assert first_call.kwargs["path"].name == expected_filename
            assert second_call.kwargs["path"].name == expected_filename

    def test_preserves_original_input_filenames_in_workspace(self) -> None:
        runtime_request = Mock()
        runtime_request.target = "generate_code"
        runtime_request.role = Path(
            "resources/role/playwright_engineer.md",
        )
        runtime_request.deliverable = Path(
            "resources/deliverable/playwright_google.md",
        )

        execution_service = create_execution_service(
            persist_to_disk=False,
        )

        generate_code_service = Mock()
        review_code_service = Mock()

        work_order = Mock()
        work_order.target = "generate_code"
        work_order.role = "Senior Playwright Automation Architect"
        work_order.deliverable = "Playwright Google Search requirements."

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

    def test_writes_review_report_to_workspace(
        self,
        tmp_path: Path,
    ) -> None:
        """Write the rendered review report to the WorkSpace output."""

        runtime_request = Mock()
        runtime_request.target = "review_code"
        runtime_request.role = Path(
            "resources/role/python_engineer.md",
        )
        runtime_request.deliverable = Path(
            "resources/deliverable/code_review.md",
        )
        runtime_request.source_code = [
            tmp_path / "calculator.py",
        ]

        source_file = runtime_request.source_code[0]

        source_file.write_text(
            "class Calculator:\n    pass",
            encoding="utf-8",
        )

        execution_service = create_execution_service(
            persist_to_disk=False,
        )

        generate_code_service = Mock()
        review_code_service = Mock()

        review_code_service.execute.return_value = "# Code Review\n\nReview content"

        work_order = Mock()
        work_order.target = "review_code"
        work_order.role = "Python Engineer"
        work_order.deliverable = "Review the requested source code."

        work_order_id = "WORCS202608270001"

        with (
            patch(
                "services.app.orchestration_service.WorkOrderBuilderService.build",
                return_value=work_order,
            ),
            patch(
                "services.app.orchestration_service.WorkOrderNumberGenerator.generate",
                return_value=work_order_id,
            ),
            patch(
                "services.app.orchestration_service.WorkOrderWriter.write",
            ),
            patch(
                "services.app.orchestration_service.FileWriter.write",
            ) as mock_file_write,
        ):

            service = OrchestrationService(
                execution_service=execution_service,
                generate_code_service=generate_code_service,
                review_code_service=review_code_service,
            )

            service.execute(
                runtime_request,
            )

        expected_path = (
            Path("work_space")
            / work_order_id.lower()
            / "output"
            / f"{work_order_id.lower()}_code_review.md"
        )

        mock_file_write.assert_called_once_with(
            path=expected_path,
            content="# Code Review\n\nReview content",
        )

    def test_writes_review_report_to_both_locations_when_persistence_is_enabled(
        self,
        tmp_path: Path,
    ) -> None:
        """Write the rendered review report to both configured locations."""

        runtime_request = Mock()
        runtime_request.target = "review_code"
        runtime_request.role = Path(
            "resources/role/python_engineer.md",
        )
        runtime_request.deliverable = Path(
            "resources/deliverable/code_review.md",
        )
        runtime_request.source_code = [
            tmp_path / "calculator.py",
        ]

        source_file = runtime_request.source_code[0]

        source_file.write_text(
            "class Calculator:\n    pass",
            encoding="utf-8",
        )

        execution_service = create_execution_service(
            persist_to_disk=True,
        )

        execution_service.configuration.reports.review.output_directory = (
            "reports/reviews/code_reviews"
        )

        generate_code_service = Mock()
        review_code_service = Mock()

        review_report = "# Code Review\n\nReview content"

        review_code_service.execute.return_value = review_report

        work_order = Mock()
        work_order.target = "review_code"
        work_order.role = "Python Engineer"
        work_order.deliverable = "Review the requested source code."

        work_order_id = "WORCS202608270002"
        work_order_name = work_order_id.lower()

        with (
            patch(
                "services.app.orchestration_service.WorkOrderBuilderService.build",
                return_value=work_order,
            ),
            patch(
                "services.app.orchestration_service.WorkOrderNumberGenerator.generate",
                return_value=work_order_id,
            ),
            patch(
                "services.app.orchestration_service.WorkOrderWriter.write",
            ),
            patch(
                "services.app.orchestration_service.FileWriter.write",
            ) as mock_file_write,
        ):

            service = OrchestrationService(
                execution_service=execution_service,
                generate_code_service=generate_code_service,
                review_code_service=review_code_service,
            )

            service.execute(
                runtime_request,
            )

        expected_workspace_path = (
            Path("work_space")
            / work_order_name
            / "output"
            / f"{work_order_name}_code_review.md"
        )

        expected_report_path = (
            Path("reports/reviews/code_reviews") / f"{work_order_name}_code_review.md"
        )

        assert mock_file_write.call_count == 2

        mock_file_write.assert_any_call(
            path=expected_workspace_path,
            content=review_report,
        )

        mock_file_write.assert_any_call(
            path=expected_report_path,
            content=review_report,
        )
