"""Unit tests for FrameworkConfigurationService."""

from __future__ import annotations

import pytest

from services.framework_configuration_service import FrameworkConfigurationService


def test_configuration_properties_are_exposed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Expose typed accessors for all supported configuration sections."""

    fake_config = {
        "framework": {
            "name": "Automation Framework",
            "version": "1.0.0",
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
            "debug": {
                "enabled": True,
                "save_prompt": True,
                "save_response": True,
                "overwrite_files": True,
            },
        },
    }

    monkeypatch.setattr(
        FrameworkConfigurationService,
        "_load_configuration",
        lambda self: fake_config,
    )

    service = FrameworkConfigurationService()

    # Framework
    assert service.framework.name == "Automation Framework"
    assert service.framework.version == "1.0.0"

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

    # Debug
    assert service.logging.debug.save_prompt is True
    assert service.logging.debug.save_response is True
    assert service.logging.debug.overwrite_files is True
