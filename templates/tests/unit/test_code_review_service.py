"""Unit tests for CodeReviewService."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType, SimpleNamespace

import pytest

from services.framework_configuration_service import FrameworkConfigurationService


def _import_review_service_or_skip(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Import code review service module with test-safe configuration stubs."""

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

    sys.modules.pop("services.prompt_loader_service", None)
    sys.modules.pop("services.prompt_builder_service", None)
    sys.modules.pop("services.code_review_service", None)

    return importlib.import_module("services.code_review_service")


def test_execute_sets_runtime_context_and_returns_review(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Populate runtime context and return AI review output."""
    module = _import_review_service_or_skip(monkeypatch)

    class FakeClient:
        provider = "ollama"
        model = "m-review"

        def generate(self, system_prompt: str, user_prompt: str) -> str:
            assert system_prompt == "SYSTEM"
            assert "BEGIN SOURCE CODE" in user_prompt
            return "REVIEW"

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

    runtime_context = SimpleNamespace(provider=None, model=None, lines_reviewed=0)

    service = module.CodeReviewService()
    out = service.execute("a\nb\n", runtime_context)

    assert out == "REVIEW"
    assert runtime_context.provider == "ollama"
    assert runtime_context.model == "m-review"
    assert runtime_context.lines_reviewed == 2


def test_execute_returns_error_message_when_failure_occurs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return formatted failure message when review workflow raises error."""
    module = _import_review_service_or_skip(monkeypatch)

    monkeypatch.setattr(
        module.PromptBuilderService,
        "build_prompt",
        staticmethod(
            lambda task_prompt, user_prompt: (_ for _ in ()).throw(RuntimeError("boom"))
        ),
    )

    runtime_context = SimpleNamespace(provider=None, model=None, lines_reviewed=0)

    service = module.CodeReviewService()
    out = service.execute("print('x')", runtime_context)

    assert "AI code review failed:" in out
    assert "boom" in out
