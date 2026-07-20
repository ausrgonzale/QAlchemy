"""
reporting.py

Purpose:
    Provides report generation and persistence services for the
    Toolshop automation framework.

Architecture:
    This module is responsible for transforming framework output
    into persistent report artifacts. ReportWriter formats report
    content, writes reports to disk, and returns the generated
    report location to the caller.

Responsibilities:
    - Generate Markdown report content.
    - Write reports to disk.
    - Create destination directories when necessary.
    - Return the generated report path.

Workflow:
    Review Content
        ↓
    Configuration Driven Metadata
        ↓
    Markdown Report
        ↓
    File System
        ↓
    Report Path

Dependencies:
    - pathlib.Path

Notes:
    ReportWriter is an infrastructure component and is not
    responsible for AI operations, prompt construction, source
    code analysis, or report naming conventions. Those
    responsibilities remain with the calling service.

Author:
    Ron Gonzalez

Created:
    July 2026
"""

from pathlib import Path

from runtime_context import RuntimeContext
from services.app_configuration_service import (
    AppConfigurationService,
)


class ReportWriter:
    """
    Generates and writes Markdown reports.

    ReportWriter transforms AI-generated review results into
    persistent Markdown report files. The caller supplies the
    report content, metadata, and destination path.

    This class is responsible only for formatting and writing
    reports. It does not perform AI operations or determine
    report naming conventions.

    """

    def __init__(
        self,
        configuration: AppConfigurationService,
    ) -> None:
        self._configuration = configuration

    def _load_template(self) -> str:
        """Load the configured report template."""

        template_path = (
            Path(__file__).resolve().parent
            / self._configuration.templates.root
            / self._configuration.templates.code_review_report
        )

        return Path(template_path).read_text(encoding="utf-8")

    def _render_markdown_template(
        self,
        review: str,
        runtime_context: RuntimeContext,
    ) -> str:
        """Render the configured Markdown report template."""

        template = self._load_template()

        review_information = self._build_review_information(runtime_context)

        return template.replace(
            "{{ review_information }}",
            review_information,
        ).replace(
            "{{ review }}",
            review,
        )

    def _build_destination_path(
        self,
        runtime_context: RuntimeContext,
    ) -> Path:
        if runtime_context.source_file is None:
            raise ValueError("RuntimeContext.source_file has not been set.")

        output_root = Path(self._configuration.reports.output_root)

        report_directory = output_root / "code_reviews"

        report_name = f"{runtime_context.source_file.stem}_review.md"

        return report_directory / report_name

    def write(
        self,
        review: str,
        runtime_context: RuntimeContext,
    ) -> Path:
        """
        Generate and write a Markdown report.

        Args:
            review: AI-generated review content.
            runtime_context: Runtime execution metadata.

        Returns:
            Path to the generated report.
        """

        destination = runtime_context.destination_file

        if destination is None:
            destination = self._build_destination_path(runtime_context)
            runtime_context.destination_file = destination

        destination.parent.mkdir(parents=True, exist_ok=True)

        markdown = self._render_markdown_template(
            review=review,
            runtime_context=runtime_context,
        )

        destination.write_text(markdown, encoding="utf-8")

        return destination

    def _build_review_information(
        self,
        runtime_context: RuntimeContext,
    ) -> str:
        """Build the review information table."""

        fields = self._configuration.reports.review.fields

        rows = [
            "| Property | Value |",
            "|----------|-------|",
        ]

        if fields.source_file:
            rows.append(f"| Source File | {runtime_context.source_file} |")

        if fields.provider:
            rows.append(f"| Provider | {runtime_context.provider} |")

        if fields.model:
            rows.append(f"| Model | {runtime_context.model} |")

        if fields.execution_time:
            rows.append(
                f"| Execution Time | {runtime_context.execution_time:.2f} seconds |"
            )

        if fields.lines_reviewed and runtime_context.lines_reviewed is not None:
            rows.append(f"| Lines Reviewed | {runtime_context.lines_reviewed} |")

        if fields.review_date and runtime_context.review_date is not None:
            review_date = runtime_context.review_date.strftime("%B %d, %Y %I:%M:%S %p")
            rows.append(f"| Review Date | {review_date} |")

        return "\n".join(rows)
