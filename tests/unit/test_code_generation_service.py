"""Unit tests for CodeGenerationService."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType

import pytest

from services.app_configuration_service import AppConfigurationService


def _import_generation_service_or_skip(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
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
        AppConfigurationService,
        "_load_configuration",
        lambda self: fake_config,
    )

    print(AppConfigurationService()._config.keys())

    sys.modules.pop("services.prompt_loader_service", None)
    sys.modules.pop("services.prompt_builder_service", None)
    sys.modules.pop("services.code_generation_service", None)
    return importlib.import_module("services.code_generation_service")


def test_generate_invokes_builder_client_and_returns_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return generated content from AI client for generation requests."""
    module = _import_generation_service_or_skip(monkeypatch)

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
    module = _import_generation_service_or_skip(monkeypatch)
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
