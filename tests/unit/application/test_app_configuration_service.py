"""Unit tests for AppConfigurationService."""

from __future__ import annotations

from typing import Any

import pytest

from services.core.app_configuration_service import AppConfigurationService


@pytest.fixture
def fake_configuration() -> dict[str, Any]:
    """Return a valid application configuration for unit tests."""

    return {
        "app": {
            "name": "Automation Framework",
            "version": "1.0.0",
            "edition": "Community",
        },
        "ai": {
            "provider": "ollama",
            "default_model": "m1",
            "request_timeout": 30,
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
            "root": "templates",
            "code_review_report": "code_review_report_template.md",
        },
        "reports": {
            "output_root": "reports",
            "debug_output_root": "reports/debug",
            "review": {
                "fields": {
                    "source_file": True,
                    "lines_reviewed": True,
                    "provider": True,
                    "model": True,
                    "execution_time": True,
                    "review_date": True,
                },
            },
        },
        "logging": {
            "level": "INFO",
            "output_root": "logs",
            "base_filename": "qalchemy",
            "extension": "log",
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


def test_configuration_properties_are_exposed(
    monkeypatch: pytest.MonkeyPatch,
    fake_configuration: dict[str, Any],
) -> None:
    """Expose typed accessors for all supported configuration sections."""

    monkeypatch.setattr(
        AppConfigurationService,
        "_load_configuration",
        lambda self: fake_configuration,
    )

    service = AppConfigurationService()

    # App
    assert service.app.name == "Automation Framework"
    assert service.app.version == "1.0.0"
    assert service.app.edition == "Community"

    # AI
    assert service.ai.provider == "ollama"
    assert service.ai.default_model == "m1"
    assert service.ai.request_timeout == 30
    assert service.ai.stream is False

    # Prompts
    assert service.prompts.root == "prompts"
    assert service.prompts.code_standards == "code_standards.md"
    assert service.prompts.python_standards == "python_standards.md"
    assert service.prompts.playwright_standards == "playwright_standards.md"
    assert service.prompts.generation_instructions == "generation_instructions.md"
    assert service.prompts.review_instructions == "review_instructions.md"
    assert service.prompts.markdown_contract == "markdown_contract.md"

    # Prompt Builder
    assert service.prompt_builder.validation.enabled is True
    assert service.prompt_builder.validation.fail_on_missing_artifact is True
    assert service.prompt_builder.validation.fail_on_invalid_work_order is True

    assert service.prompt_builder.artifacts.preprocess is True
    assert service.prompt_builder.artifacts.compression["enabled"] is True
    assert service.prompt_builder.artifacts.compression["mode"] == "summary"
    assert service.prompt_builder.artifacts.compression["max_tokens"] == 3000

    assert service.prompt_builder.rendering.provider == "markdown"

    assert service.prompt_builder.output.write_prompt_to_disk is True
    assert service.prompt_builder.output.output_directory == "reports/debug/prompts"
    assert service.prompt_builder.output.include_metadata is True

    # Templates
    assert service.templates.root == "templates"
    assert service.templates.code_review_report == "code_review_report_template.md"

    # Reports
    assert service.reports.output_root == "reports"
    assert service.reports.debug_output_root == "reports/debug"

    assert service.reports.review.fields.source_file is True
    assert service.reports.review.fields.lines_reviewed is True
    assert service.reports.review.fields.provider is True
    assert service.reports.review.fields.model is True
    assert service.reports.review.fields.execution_time is True
    assert service.reports.review.fields.review_date is True

    # Logging
    assert service.logging.level == "INFO"
    assert service.logging.output_root == "logs"
    assert service.logging.base_filename == "qalchemy"
    assert service.logging.extension == "log"
    assert service.logging.log_file.name == "qalchemy.log"

    # Debug
    assert service.logging.debug.enabled is True
    assert service.logging.debug.save_prompt is True
    assert service.logging.debug.save_response is True
    assert service.logging.debug.overwrite_files is True

    # Exceptions
    assert service.exceptions.enabled is True
    assert service.exceptions.catalog.root == "config"
    assert service.exceptions.catalog.filename == "exceptions.yaml"
    assert service.exceptions.defaults.unknown_exception_code == "SYS-0001"
    assert service.exceptions.defaults.validation_exception_code == "VAL-0001"
    assert service.exceptions.defaults.internal_exception_code == "SYS-9999"
    assert service.exceptions.logging.log_exceptions is True
    assert service.exceptions.logging.include_stack_trace is True
    assert service.exceptions.user_messages.expose_internal_errors is False


def test_live_configuration_exposes_required_app_metadata() -> None:
    """Load the repository configuration from its production location."""

    service = AppConfigurationService()

    assert service.app.name == "QAlchemy"
    assert service.app.version == "1.1.0"
    assert service.app.edition == "Community"
