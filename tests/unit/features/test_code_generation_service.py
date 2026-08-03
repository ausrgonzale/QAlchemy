"""Unit tests for CodeGenerationService."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType

import pytest

from services.core.app_configuration_service import AppConfigurationService


def _import_generation_service(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Import code generation service module with test-safe configuration stubs."""

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

    sys.modules.pop("services.core.prompt_loader_service", None)
    sys.modules.pop("services.core.prompt_builder_service", None)
    sys.modules.pop("services.feature.code_generation_service", None)
    return importlib.import_module("services.feature.code_generation_service")


def test_generate_invokes_builder_client_and_returns_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return generated content from AI client for generation requests."""
    module = _import_generation_service(monkeypatch)

    class FakeClient:
        def generate(self, system_prompt: str, user_prompt: str) -> str:
            assert system_prompt == "SYSTEM"
            assert "User Task" in user_prompt
            return "GENERATED"

    monkeypatch.setattr(
        module.PromptBuilderService,
        "build_prompt",
        staticmethod(lambda task_prompt, user_prompt: ("SYSTEM", user_prompt)),
    )
    monkeypatch.setattr(
        module.AIClientBuilderService,
        "build",
        staticmethod(lambda model_override=None: FakeClient()),
    )

    service = module.CodeGenerationService()
    result = service.generate(task="Create helper", source_code=None)

    assert result == "GENERATED"


def test_generate_preprocesses_existing_source_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Include preprocessed source in prompt when existing source is supplied."""
    module = _import_generation_service(monkeypatch)
    captured = {}

    class FakeClient:
        def generate(self, system_prompt: str, user_prompt: str) -> str:
            captured["system_prompt"] = system_prompt
            captured["user_prompt"] = user_prompt
            return "OK"

    monkeypatch.setattr(
        module.SourceCodePreprocessingService,
        "preprocess",
        staticmethod(lambda src: "PREPROCESSED:" + src),
    )
    monkeypatch.setattr(
        module.PromptBuilderService,
        "build_prompt",
        staticmethod(lambda task_prompt, user_prompt: ("SYSTEM", user_prompt)),
    )
    monkeypatch.setattr(
        module.AIClientBuilderService,
        "build",
        staticmethod(lambda model_override=None: FakeClient()),
    )

    service = module.CodeGenerationService()
    service.generate(task="Task", source_code="print('x')")

    assert "Existing Source Code" in captured["user_prompt"]
    assert "PREPROCESSED:print('x')" in captured["user_prompt"]


def test_generate_reraises_ai_client_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Re-raise AI client exceptions after logging."""

    module = _import_generation_service(monkeypatch)

    class FakeClient:
        def generate(self, system_prompt: str, user_prompt: str) -> str:
            raise RuntimeError("AI provider unavailable")

    monkeypatch.setattr(
        module.PromptBuilderService,
        "build_prompt",
        staticmethod(lambda task_prompt, user_prompt: ("SYSTEM", user_prompt)),
    )

    monkeypatch.setattr(
        module.AIClientBuilderService,
        "build",
        staticmethod(lambda model_override=None: FakeClient()),
    )

    service = module.CodeGenerationService()

    with pytest.raises(RuntimeError, match="AI provider unavailable"):
        service.generate(task="Create helper")
