"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_review_code_service.py

Purpose:
    Provides unit tests for the ReviewCodeService.

Description:
    Validates the Review Code feature workflow from the canonical WorkOrder
    through source-code processing, LLM execution, and report rendering.

Current V1.2 Coverage
---------------------
- Accepts a WorkOrder, WorkSpace, and resolved source files.
- Reads multiple source files.
- Preprocesses source code.
- Transforms the WorkOrder and source code into an LLM request.
- Creates the configured AI client.
- Executes the review.
- Renders the review report.
- Returns the rendered review report.

Non-Responsibilities
--------------------
These tests do NOT:

- Determine report destinations.
- Write report files.
- Create report directories.
- Coordinate dual report persistence.
- Perform orchestration.

===============================================================================
"""

from pathlib import Path
from unittest.mock import Mock, patch

from scripts.core.work_order import WorkOrder
from scripts.core.work_order_transformer import WorkOrderTransformer
from scripts.utils.work_space import WorkSpace
from services.feature.review_code_service import ReviewCodeService


class TestReviewCodeService:
    """Unit tests for ReviewCodeService."""

    def _create_service(
        self,
    ) -> tuple[
        ReviewCodeService,
        Mock,
        Mock,
    ]:
        """
        Create a ReviewCodeService with mocked application dependencies.
        """

        execution_service = Mock()

        execution_service.logger_service = Mock()
        execution_service.exception_handling_service = Mock()
        execution_service.client_service = Mock()
        execution_service.configuration = Mock()

        transformer = Mock(
            spec=WorkOrderTransformer,
        )

        service = ReviewCodeService(
            execution_service=execution_service,
            work_order_transformer=transformer,
        )

        return (
            service,
            execution_service,
            transformer,
        )

    def _create_work_order(
        self,
    ) -> WorkOrder:
        """Create a representative WorkOrder."""

        return WorkOrder(
            task="Review the requested source code.",
            role="Python Engineer",
            target="review_code",
            deliverable="Produce an engineering code review.",
            references="",
        )

    def test_execute_reads_multiple_source_files(
        self,
        tmp_path: Path,
    ) -> None:
        """Read all resolved source files supplied to the service."""

        first_file = tmp_path / "calculator.py"
        second_file = tmp_path / "helpers.py"

        first_file.write_text(
            "class Calculator:\n    pass",
            encoding="utf-8",
        )

        second_file.write_text(
            "def helper():\n    pass",
            encoding="utf-8",
        )

        service, execution_service, transformer = self._create_service()

        transformer.transform.return_value = "review request"

        client = Mock()
        client.generate.return_value = "review result"

        execution_service.client_service.create.return_value = client

        workspace = WorkSpace(
            root=tmp_path,
            work_order_id="worcs202608250001",
        )

        workspace.create()

        with patch(
            "services.feature.review_code_service.ReportWriter",
        ) as report_writer_class:

            report_writer = report_writer_class.return_value

            report_writer.render.return_value = "rendered review report"

            service.execute(
                work_order=self._create_work_order(),
                workspace=workspace,
                source_files=[
                    first_file,
                    second_file,
                ],
            )

        request_source = transformer.transform.call_args.kwargs["source_code"]

        assert "calculator.py" in request_source
        assert "class Calculator:" in request_source
        assert "helpers.py" in request_source
        assert "def helper():" in request_source

    def test_execute_preprocesses_source_code(
        self,
        tmp_path: Path,
    ) -> None:
        """Preprocess each source file before combining source."""

        source_file = tmp_path / "calculator.py"

        source_file.write_text(
            "class Calculator:\n    pass",
            encoding="utf-8",
        )

        service, execution_service, transformer = self._create_service()

        transformer.transform.return_value = "review request"

        client = Mock()
        client.generate.return_value = "review result"

        execution_service.client_service.create.return_value = client

        workspace = WorkSpace(
            root=tmp_path,
            work_order_id="worcs202608250002",
        )

        workspace.create()

        with (
            patch.object(
                service._source_code_preprocessor,
                "preprocess",
                return_value="preprocessed source",
            ) as mock_preprocess,
            patch(
                "services.feature.review_code_service.ReportWriter",
            ) as report_writer_class,
        ):

            report_writer = report_writer_class.return_value

            report_writer.render.return_value = "rendered review report"

            service.execute(
                work_order=self._create_work_order(),
                workspace=workspace,
                source_files=[
                    source_file,
                ],
            )

        mock_preprocess.assert_called_once_with(
            "class Calculator:\n    pass",
        )

    def test_execute_transforms_work_order_and_source_code(
        self,
        tmp_path: Path,
    ) -> None:
        """Transform the WorkOrder and resolved source code."""

        source_file = tmp_path / "calculator.py"

        source_file.write_text(
            "class Calculator:\n    pass",
            encoding="utf-8",
        )

        service, execution_service, transformer = self._create_service()

        transformer.transform.return_value = "review request"

        client = Mock()
        client.generate.return_value = "review result"

        execution_service.client_service.create.return_value = client

        workspace = WorkSpace(
            root=tmp_path,
            work_order_id="worcs202608250003",
        )

        workspace.create()

        work_order = self._create_work_order()

        with patch(
            "services.feature.review_code_service.ReportWriter",
        ) as report_writer_class:

            report_writer = report_writer_class.return_value

            report_writer.render.return_value = "rendered review report"

            service.execute(
                work_order=work_order,
                workspace=workspace,
                source_files=[
                    source_file,
                ],
            )

        transformer.transform.assert_called_once()

        call = transformer.transform.call_args

        assert call.args[0] is work_order

        assert "calculator.py" in call.kwargs["source_code"]

    def test_execute_calls_ai_client(
        self,
        tmp_path: Path,
    ) -> None:
        """Submit the transformed request to the AI client."""

        source_file = tmp_path / "calculator.py"

        source_file.write_text(
            "class Calculator:\n    pass",
            encoding="utf-8",
        )

        service, execution_service, transformer = self._create_service()

        transformer.transform.return_value = "review request"

        client = Mock()
        client.generate.return_value = "review result"

        execution_service.client_service.create.return_value = client

        workspace = WorkSpace(
            root=tmp_path,
            work_order_id="worcs202608250004",
        )

        workspace.create()

        with patch(
            "services.feature.review_code_service.ReportWriter",
        ) as report_writer_class:

            report_writer = report_writer_class.return_value

            report_writer.render.return_value = "rendered review report"

            service.execute(
                work_order=self._create_work_order(),
                workspace=workspace,
                source_files=[
                    source_file,
                ],
            )

        execution_service.client_service.create.assert_called_once()

        client.generate.assert_called_once_with(
            "review request",
        )

    def test_execute_renders_review_report(
        self,
        tmp_path: Path,
    ) -> None:
        """Render the AI review into a Markdown report."""

        source_file = tmp_path / "calculator.py"

        source_file.write_text(
            "class Calculator:\n    pass",
            encoding="utf-8",
        )

        service, execution_service, transformer = self._create_service()

        transformer.transform.return_value = "review request"

        client = Mock()
        client.generate.return_value = "review result"

        execution_service.client_service.create.return_value = client

        workspace = WorkSpace(
            root=tmp_path,
            work_order_id="worcs202608250005",
        )

        workspace.create()

        with patch(
            "services.feature.review_code_service.ReportWriter",
        ) as report_writer_class:

            report_writer = report_writer_class.return_value

            report_writer.render.return_value = "rendered review report"

            service.execute(
                work_order=self._create_work_order(),
                workspace=workspace,
                source_files=[
                    source_file,
                ],
            )

        report_writer.render.assert_called_once()

        assert report_writer.render.call_args.kwargs["review"] == "review result"

    def test_execute_returns_rendered_report(
        self,
        tmp_path: Path,
    ) -> None:
        """Return the rendered Markdown review report."""

        source_file = tmp_path / "calculator.py"

        source_file.write_text(
            "class Calculator:\n    pass",
            encoding="utf-8",
        )

        service, execution_service, transformer = self._create_service()

        transformer.transform.return_value = "review request"

        client = Mock()
        client.generate.return_value = "review result"

        execution_service.client_service.create.return_value = client

        workspace = WorkSpace(
            root=tmp_path,
            work_order_id="worcs202608250006",
        )

        workspace.create()

        expected_report = "rendered review report"

        with patch(
            "services.feature.review_code_service.ReportWriter",
        ) as report_writer_class:

            report_writer = report_writer_class.return_value

            report_writer.render.return_value = expected_report

            result = service.execute(
                work_order=self._create_work_order(),
                workspace=workspace,
                source_files=[
                    source_file,
                ],
            )

        assert result == expected_report
