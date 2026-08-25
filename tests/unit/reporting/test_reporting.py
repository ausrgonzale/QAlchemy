"""
===============================================================================
Unit Tests

ReportWriter

Validates Markdown report rendering and delegation of persistence.

Responsibilities Tested
-----------------------
- Template loading.
- Markdown rendering.
- Report metadata generation.
- Destination path resolution.
- Delegation to FileWriter.
- RuntimeContext destination preservation.

Non-Responsibilities
--------------------
These tests do NOT:

- Test FileWriter.
- Test AppConfigurationService.
- Invoke AI providers.
- Execute CodeReviewService.
- Build WorkOrders.
- Perform orchestration.
===============================================================================
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

import scripts.core.report_writer as reporting_module
from scripts.core.report_writer import ReportWriter
from scripts.utils.runtime_context import RuntimeContext
from services.app.app_configuration_service import AppConfigurationService


class _Fields:
    """Test configuration for report metadata fields."""

    def __init__(
        self,
        *,
        source_file: bool = True,
        lines_reviewed: bool = True,
        provider: bool = True,
        model: bool = True,
        execution_time: bool = True,
        review_date: bool = True,
    ) -> None:
        self.source_file = source_file
        self.lines_reviewed = lines_reviewed
        self.provider = provider
        self.model = model
        self.execution_time = execution_time
        self.review_date = review_date


def _build_configuration(
    monkeypatch: pytest.MonkeyPatch,
    *,
    template_root: str,
    template_name: str,
    fields: _Fields,
) -> AppConfigurationService:
    """Build an AppConfigurationService using test configuration."""

    fake_config = {
        "app": {
            "name": "QAlchemy",
            "version": "1.2.0",
            "edition": "Community",
        },
        "client": {
            "provider": "ollama",
            "default_model": "qwen3-coder:480b-cloud",
            "request_timeout": 120,
            "stream": False,
        },
        "work_order": {
            "validation": {
                "enabled": True,
                "fail_on_missing_required_field": True,
                "fail_on_invalid_definition": True,
            },
            "runtime": {
                "allow_multiple_units_of_work": False,
                "stop_on_validation_failure": True,
                "persist_to_disk": True,
                "directory": "work_orders",
                "filename": "work_order.md",
            },
        },
        "workspace": {
            "root": "work_space",
        },
        "templates": {
            "root": template_root,
            "code_review_report": template_name,
        },
        "reports": {
            "output_root": "reports",
            "debug_output_root": "reports/debug",
            "review": {
                "output_directory": "reports/reviews",
                "fields": {
                    "source_file": fields.source_file,
                    "lines_reviewed": fields.lines_reviewed,
                    "provider": fields.provider,
                    "model": fields.model,
                    "execution_time": fields.execution_time,
                    "review_date": fields.review_date,
                },
            },
        },
        "logging": {
            "level": "INFO",
            "output_root": "logs",
            "base_filename": "qalchemy",
            "extension": ".log",
            "debug": {
                "enabled": True,
                "save_prompt": False,
                "save_response": False,
                "overwrite_files": True,
            },
        },
        "exceptions": {
            "enabled": True,
            "catalog": {
                "root": "config",
                "filename": "exceptions.yaml",
            },
            "defaults": {
                "unknown_exception_code": "SYS-0001",
                "validation_exception_code": "VAL-0001",
                "internal_exception_code": "SYS-9999",
            },
            "logging": {
                "log_exceptions": True,
                "include_stack_trace": True,
            },
            "user_messages": {
                "expose_internal_errors": False,
            },
        },
    }

    monkeypatch.setattr(
        AppConfigurationService,
        "_load_configuration",
        lambda self: fake_config,
    )

    return AppConfigurationService()


def _build_writer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    template_text: str,
    fields: _Fields | None = None,
) -> tuple[ReportWriter, Mock]:
    """Build a ReportWriter with a mocked FileWriter."""

    template_directory = tmp_path / "templates"
    template_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    template_name = "template.md"

    (template_directory / template_name).write_text(
        template_text,
        encoding="utf-8",
    )

    fake_reporting = tmp_path / "scripts" / "core" / "reporting.py"

    fake_reporting.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fake_reporting.touch()

    monkeypatch.setattr(
        reporting_module,
        "__file__",
        str(fake_reporting),
    )

    configuration = _build_configuration(
        monkeypatch,
        template_root="templates",
        template_name=template_name,
        fields=fields or _Fields(),
    )

    file_writer = Mock()

    writer = ReportWriter(
        configuration=configuration,
        file_writer=file_writer,
    )

    return writer, file_writer


def _build_runtime_context(
    tmp_path: Path,
) -> RuntimeContext:
    """Build RuntimeContext with common report metadata."""

    runtime_context = RuntimeContext()

    runtime_context.source_file = Path(
        "services/review_instructions_service.py",
    )
    runtime_context.destination_file = tmp_path / "reports" / "review.md"
    runtime_context.provider = "ollama"
    runtime_context.model = "qwen3-coder:480b-cloud"
    runtime_context.execution_time = 3.456
    runtime_context.lines_reviewed = 42
    runtime_context.review_date = datetime(
        2026,
        7,
        13,
        10,
        15,
        30,
        tzinfo=UTC,
    )

    return runtime_context


def test_load_template_reads_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read template contents from the configured template path."""

    writer, _ = _build_writer(
        tmp_path,
        monkeypatch,
        template_text="{{ review_information }}\n{{ review }}",
    )

    assert writer._load_template() == ("{{ review_information }}\n{{ review }}")


def test_render_markdown_template_replaces_both_placeholders(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Render Markdown using runtime review values."""

    writer, _ = _build_writer(
        tmp_path,
        monkeypatch,
        template_text=(
            "Header\n\n" "{{ review_information }}\n\n" "Body:\n" "{{ review }}\n"
        ),
    )

    runtime_context = _build_runtime_context(tmp_path)

    rendered = writer._render_markdown_template(
        review="Looks good",
        runtime_context=runtime_context,
    )

    assert "{{ review_information }}" not in rendered
    assert "{{ review }}" not in rendered
    assert "Looks good" in rendered
    assert "| Source File | services/review_instructions_service.py |" in rendered


def test_write_delegates_persistence_to_file_writer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Delegate rendered report persistence to FileWriter."""

    writer, file_writer = _build_writer(
        tmp_path,
        monkeypatch,
        template_text="{{ review_information }}\n\n{{ review }}",
    )

    runtime_context = _build_runtime_context(tmp_path)

    output = writer.write(
        review="Final review",
        runtime_context=runtime_context,
    )

    assert output == runtime_context.destination_file

    file_writer.write.assert_called_once()

    call = file_writer.write.call_args

    assert call.kwargs["path"] == runtime_context.destination_file
    assert "Final review" in call.kwargs["content"]


def test_build_review_information_respects_field_toggles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Include only enabled metadata fields."""

    runtime_context = _build_runtime_context(tmp_path)

    fields = _Fields(
        source_file=True,
        provider=False,
        model=True,
        execution_time=False,
        lines_reviewed=True,
        review_date=False,
    )

    writer, _ = _build_writer(
        tmp_path,
        monkeypatch,
        template_text="{{ review_information }}\n{{ review }}",
        fields=fields,
    )

    table = writer._build_review_information(runtime_context)

    assert "| Source File | services/review_instructions_service.py |" in table
    assert "| Provider |" not in table
    assert "| Model | qwen3-coder:480b-cloud |" in table
    assert "| Execution Time |" not in table
    assert "| Lines Reviewed | 42 |" in table


def test_build_review_information_skips_optional_values_when_none(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skip metadata rows when values are unavailable."""

    runtime_context = _build_runtime_context(tmp_path)
    runtime_context.lines_reviewed = None

    writer, _ = _build_writer(
        tmp_path,
        monkeypatch,
        template_text="{{ review_information }}\n{{ review }}",
        fields=_Fields(review_date=False),
    )

    table = writer._build_review_information(runtime_context)

    assert "| Lines Reviewed |" not in table
    assert "AM" not in table
    assert "PM" not in table
