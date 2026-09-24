"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_report_writer.py

Purpose:
    Unit tests for the ReportWriter.

Description:
    Verifies that ReportWriter loads templates, renders review content, and
    builds review metadata according to application configuration.

Responsibilities
----------------
- Verify template loading.
- Verify Markdown rendering.
- Verify review metadata rendering.
- Verify configured metadata field toggles.
- Verify optional runtime metadata handling.

Non-Responsibilities
--------------------
These tests do NOT:

- Write files.
- Determine report destinations.
- Invoke AI providers.
- Execute ReviewCodeService.
- Perform orchestration.

===============================================================================
"""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scripts.core.report_writer import ReportWriter
from scripts.utils.runtime_context import RuntimeContext

pytestmark = pytest.mark.reporting


def _build_configuration() -> Mock:
    """Build a mocked application configuration."""

    fields = Mock()

    fields.source_file = True
    fields.provider = True
    fields.model = True
    fields.execution_time = True
    fields.lines_reviewed = True
    fields.review_date = True

    configuration = Mock()

    configuration.reports.review.fields = fields

    return configuration


def _build_writer() -> ReportWriter:
    """Build a ReportWriter with mocked configuration."""

    return ReportWriter(
        configuration=_build_configuration(),
    )


def _build_runtime_context(
    tmp_path: Path,
) -> RuntimeContext:
    """Build a populated RuntimeContext for testing."""

    runtime_context = RuntimeContext()

    runtime_context.source_file = tmp_path / "google_search_page.py"
    runtime_context.provider = "ollama"
    runtime_context.model = "gpt-oss:120b-cloud"
    runtime_context.execution_time = 1.25
    runtime_context.lines_reviewed = 42
    runtime_context.review_date = datetime(
        2026,
        8,
        26,
        17,
        30,
        0,
        tzinfo=UTC,
    )

    return runtime_context


def test_load_template_reads_configured_file() -> None:
    """Load the configured Markdown report template."""

    configuration = _build_configuration()

    configuration.templates.root = "templates"
    configuration.templates.code_review_report = "code_review_report_template.md"

    writer = ReportWriter(
        configuration=configuration,
    )

    expected_template = "{{ review_information }}\n\n" "{{ review }}"

    with patch.object(
        Path,
        "read_text",
        return_value=expected_template,
    ):

        result = writer._load_template()

    assert result == expected_template


def test_render_markdown_template_replaces_both_placeholders(
    tmp_path: Path,
) -> None:
    """Replace review and review-information placeholders."""

    writer = _build_writer()

    runtime_context = _build_runtime_context(
        tmp_path,
    )

    template = "# Code Review\n\n" "{{ review_information }}\n\n" "{{ review }}"

    with patch.object(
        writer,
        "_load_template",
        return_value=template,
    ):

        result = writer._render_markdown_template(
            review="Review content",
            runtime_context=runtime_context,
        )

    assert "# Code Review" in result
    assert "Review content" in result
    assert "Source File" in result
    assert "{{ review_information }}" not in result
    assert "{{ review }}" not in result


def test_render_returns_rendered_markdown(
    tmp_path: Path,
) -> None:
    """Render Markdown without performing filesystem persistence."""

    writer = _build_writer()

    runtime_context = _build_runtime_context(
        tmp_path,
    )

    template = "{{ review_information }}\n\n" "{{ review }}"

    with patch.object(
        writer,
        "_load_template",
        return_value=template,
    ):

        result = writer.render(
            review="Review content",
            runtime_context=runtime_context,
        )

    assert "Review content" in result
    assert "Source File" in result
    assert "Provider" in result
    assert "Model" in result
    assert "Execution Time" in result
    assert "Lines Reviewed" in result
    assert "Review Date" in result


def test_build_review_information_respects_field_toggles(
    tmp_path: Path,
) -> None:
    """Include only metadata fields enabled by configuration."""

    configuration = _build_configuration()

    fields = configuration.reports.review.fields

    fields.source_file = True
    fields.provider = False
    fields.model = True
    fields.execution_time = False
    fields.lines_reviewed = True
    fields.review_date = False

    writer = ReportWriter(
        configuration=configuration,
    )

    runtime_context = _build_runtime_context(
        tmp_path,
    )

    result = writer._build_review_information(
        runtime_context,
    )

    assert "Source File" in result
    assert "Model" in result
    assert "Lines Reviewed" in result

    assert "Provider" not in result
    assert "Execution Time" not in result
    assert "Review Date" not in result


def test_build_review_information_skips_unset_optional_values(
    tmp_path: Path,
) -> None:
    """Skip metadata rows when optional runtime values are not set."""

    writer = _build_writer()

    runtime_context = RuntimeContext()

    runtime_context.source_file = tmp_path / "google_search_page.py"

    result = writer._build_review_information(
        runtime_context,
    )

    assert "Source File" in result
    assert "Provider" not in result
    assert "Model" not in result
    assert "Execution Time" not in result
    assert "Lines Reviewed" not in result

    # RuntimeContext always initializes review_date.
    assert "Review Date" in result
