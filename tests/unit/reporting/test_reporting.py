"""Unit tests for ReportWriter in reporting.py (v2)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

import scripts.core.reporting as reporting_module
from scripts.core.reporting import ReportWriter
from scripts.core.runtime_context import RuntimeContext
from services.core.app_configuration_service import AppConfigurationService


class _Fields:
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
    """Build a real AppConfigurationService backed by fake config data."""
    fake_config = {
        "app": {
            "name": "Automation Framework",
            "version": "1.0.0",
            "edition": "Community",
        },
        "ai": {
            "provider": "ollama",
            "default_model": "qwen3-coder:480b-cloud",
            "request_timeout": 120,
            "stream": False,
        },
        "prompts": {
            "root": "prompts",
            "code_standards": "code_standards.md",
            "python_standards": "python_standards.md",
            "playwright_standards": "playwright_standards.md",
            "generation_instructions": "generation_instructions.md",
            "review_instructions": "review_instructions.md",
            "markdown_contract": "markdown_contract.md",
        },
        "prompt_builder": {
            "validation": {
                "enabled": True,
                "fail_on_missing_artifact": True,
                "fail_on_invalid_work_order": True,
            },
            "artifacts": {
                "preprocess": True,
                "compression": {
                    "enabled": True,
                    "mode": "summary",
                    "max_tokens": 3000,
                },
            },
            "rendering": {
                "provider": "markdown",
            },
            "output": {
                "write_prompt_to_disk": True,
                "output_directory": "reports/debug/prompts",
                "include_metadata": True,
            },
        },
        "templates": {
            "root": template_root,
            "code_review_report": template_name,
        },
        "reports": {
            "output_root": "reports",
            "debug_output_root": "reports/debug",
            "review": {
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
            "debug": {
                "enabled": True,
                "save_prompt": True,
                "save_response": True,
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
) -> ReportWriter:
    """Build ReportWriter configured to load templates from temporary test directory."""
    #
    # Build a fake project layout.
    #
    # tmp_path/
    # ├── scripts/
    # │   └── core/
    # │       └── reporting.py
    # └── templates/
    #     └── template.md
    #

    project_root = tmp_path

    template_directory = project_root / "templates"
    template_directory.mkdir(parents=True, exist_ok=True)

    template_name = "template.md"
    (template_directory / template_name).write_text(
        template_text,
        encoding="utf-8",
    )

    fake_reporting = project_root / "scripts" / "core" / "reporting.py"

    fake_reporting.parent.mkdir(parents=True, exist_ok=True)
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

    return ReportWriter(configuration)


def _build_runtime_context(tmp_path: Path) -> RuntimeContext:
    """Build a runtime context with common metadata used by ReportWriter tests."""
    runtime_context = RuntimeContext()
    runtime_context.source_file = Path("services/review_instructions_service.py")
    runtime_context.destination_file = tmp_path / "reports" / "review.md"
    runtime_context.provider = "ollama"
    runtime_context.model = "qwen3-coder:480b-cloud"
    runtime_context.execution_time = 3.456
    runtime_context.lines_reviewed = 42
    runtime_context.review_date = datetime(2026, 7, 13, 10, 15, 30, tzinfo=UTC)
    return runtime_context


def test_load_template_reads_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read template contents from configured template path."""
    writer = _build_writer(
        tmp_path,
        monkeypatch,
        template_text="{{ review_information }}\n{{ review }}",
    )

    assert writer._load_template() == "{{ review_information }}\n{{ review }}"


def test_render_markdown_template_replaces_both_placeholders(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Render markdown by replacing review placeholders with runtime values."""
    writer = _build_writer(
        tmp_path,
        monkeypatch,
        template_text="Header\n\n{{ review_information }}\n\nBody:\n{{ review }}\n",
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


def test_write_creates_parent_directory_and_writes_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Create parent directory and write rendered markdown to destination."""
    writer = _build_writer(
        tmp_path,
        monkeypatch,
        template_text="{{ review_information }}\n\n{{ review }}",
    )

    runtime_context = _build_runtime_context(tmp_path)

    output = writer.write(review="Final review", runtime_context=runtime_context)

    assert output == runtime_context.destination_file
    assert output.exists()

    written = output.read_text(encoding="utf-8")
    assert "Final review" in written
    assert "| Execution Time | 3.46 seconds |" in written


def test_build_review_information_respects_field_toggles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Include only enabled metadata fields in review information table."""
    runtime_context = _build_runtime_context(tmp_path)
    fields = _Fields(
        source_file=True,
        provider=False,
        model=True,
        execution_time=False,
        lines_reviewed=True,
        review_date=False,
    )
    writer = _build_writer(
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
    """Skip optional rows when fields are disabled or values are unavailable."""
    runtime_context = _build_runtime_context(tmp_path)
    runtime_context.lines_reviewed = None
    writer = _build_writer(
        tmp_path,
        monkeypatch,
        template_text="{{ review_information }}\n{{ review }}",
        fields=_Fields(review_date=False),
    )

    table = writer._build_review_information(runtime_context)

    assert "| Lines Reviewed |" not in table
    assert "AM" not in table and "PM" not in table
