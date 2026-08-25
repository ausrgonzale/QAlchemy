"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    reporting.py

Purpose:
    Provides Markdown report rendering services for QAlchemy.

Description:
    ReportWriter transforms engineering review results into Markdown using
    configurable report templates.

    ReportWriter is responsible for rendering report content only.
    Persistence is delegated to FileWriter.

Responsibilities:
    - Load report templates.
    - Render Markdown reports.
    - Build report metadata.
    - Determine default report names.

Non-Responsibilities:
    - Write files.
    - Create directories.
    - Perform AI operations.
    - Build WorkOrders.
    - Determine workflow execution.

Workflow:
    Review Content
        ↓
    Configuration Driven Metadata
        ↓
    Markdown Report
        ↓
    FileWriter
        ↓
    Report File

Dependencies:
    - AppConfigurationService
    - FileWriter

===============================================================================
"""

from pathlib import Path

from scripts.utils.file_writer import FileWriter
from scripts.utils.runtime_context import RuntimeContext
from services.app.app_configuration_service import (
    AppConfigurationService,
)


class ReportWriter:
    """
    Generates Markdown engineering reports.

    ReportWriter transforms AI-generated review results into Markdown
    using the configured report template.

    This class performs no filesystem operations.
    """

    def __init__(
        self,
        configuration: AppConfigurationService,
        file_writer: FileWriter,
    ) -> None:
        """
        Initialize the ReportWriter.
        """

        self._configuration = configuration
        self._file_writer = file_writer

    def _load_template(self) -> str:
        """
        Load the configured Markdown report template.
        """

        project_root = Path(__file__).resolve().parents[2]

        template_path = (
            project_root
            / self._configuration.templates.root
            / self._configuration.templates.code_review_report
        )

        return template_path.read_text(
            encoding="utf-8",
        )

    def _render_markdown_template(
        self,
        review: str,
        runtime_context: RuntimeContext,
    ) -> str:
        """
        Render the configured Markdown report template.
        """

        template = self._load_template()

        review_information = self._build_review_information(
            runtime_context,
        )

        return template.replace(
            "{{ review_information }}",
            review_information,
        ).replace(
            "{{ review }}",
            review,
        )

    # -------------------------------------------------------------------------
    # Temporary Implementation
    #
    # Destination paths are currently determined by ReportWriter.
    # Future versions will obtain report destinations from the
    # Runtime Object (RTO).
    # -------------------------------------------------------------------------

    def _build_destination_path(
        self,
        runtime_context: RuntimeContext,
    ) -> Path:
        """
        Build the default destination report path.
        """

        if runtime_context.source_file is None:
            raise ValueError("RuntimeContext.source_file has not been set.")

        report_directory = Path(
            self._configuration.reports.review.output_directory,
        )

        report_name = f"{runtime_context.source_file.stem}_review.md"

        return report_directory / report_name

    def write(
        self,
        review: str,
        runtime_context: RuntimeContext,
    ) -> Path:
        """
        Generate and persist a Markdown report.

        Returns:
            Path to the generated report.
        """

        destination = runtime_context.destination_file

        if destination is None:
            destination = self._build_destination_path(
                runtime_context,
            )
            runtime_context.destination_file = destination

        markdown = self._render_markdown_template(
            review=review,
            runtime_context=runtime_context,
        )

        self._file_writer.write(
            path=destination,
            content=markdown,
        )

        return destination

    def _build_review_information(
        self,
        runtime_context: RuntimeContext,
    ) -> str:
        """
        Build the report metadata table.
        """

        fields = self._configuration.reports.review.fields

        rows = [
            "| Property | Value |",
            "|----------|-------|",
        ]

        if fields.source_file and runtime_context.source_file is not None:
            rows.append(f"| Source File | {runtime_context.source_file} |")

        if fields.provider and runtime_context.provider is not None:

            rows.append(f"| Provider | {runtime_context.provider} |")

        if fields.model and runtime_context.model is not None:

            rows.append(f"| Model | {runtime_context.model} |")

        if fields.execution_time and runtime_context.execution_time is not None:

            rows.append(
                f"| Execution Time | " f"{runtime_context.execution_time:.2f} seconds |"
            )

        if fields.lines_reviewed and runtime_context.lines_reviewed is not None:

            rows.append(f"| Lines Reviewed | " f"{runtime_context.lines_reviewed} |")

        if fields.review_date and runtime_context.review_date is not None:
            review_date = runtime_context.review_date.strftime("%B %d, %Y %I:%M:%S %p")

            rows.append(f"| Review Date | {review_date} |")

        return "\n".join(rows)
