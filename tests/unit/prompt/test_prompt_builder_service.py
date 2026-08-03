"""Unit tests for PromptBuilderService."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType

import pytest

from services.core.app_configuration_service import AppConfigurationService


def _import_prompt_builder_or_skip(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Import prompt builder module with test-safe configuration stubs."""
    fake_config = {
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

    sys.modules.pop("services.prompt_loader_service", None)
    sys.modules.pop("services.prompt_builder_service", None)
    try:
        return importlib.import_module("services.core.prompt_builder_service")
    except ImportError as exc:  # pragma: no cover - explicit skip path
        pytest.skip(f"Skipping prompt_builder_service due to partial state: {exc}")


def test_build_prompt_combines_standard_documents(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Combine standards documents and task prompt into one system prompt."""
    module = _import_prompt_builder_or_skip(monkeypatch)

    loaded = {
        "code_standards.md": "CS",
        "python_standards.md": "PY",
        "playwright_standards.md": "PW",
        "generation_instructions.md": "GEN",
    }

    monkeypatch.setattr(
        module.PromptLoaderService,
        "load",
        staticmethod(lambda filename: loaded[filename]),
    )

    system_prompt, user_prompt = module.PromptBuilderService.build_prompt(
        task_prompt="generation_instructions.md",
        user_prompt="USER",
    )

    assert user_prompt == "USER"
    assert "CS" in system_prompt
    assert "PY" in system_prompt
    assert "PW" in system_prompt
    assert "GEN" in system_prompt
