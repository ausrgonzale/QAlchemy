"""Unit tests for PromptLoaderService."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest

from services.app_configuration_service import AppConfigurationService


def _import_prompt_loader(
    monkeypatch: pytest.MonkeyPatch,
) -> ModuleType:
    """Import PromptLoaderService with test configuration."""

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
            "review_instructions_report": "review_instructions_report_template.md",
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
                }
            },
        },
        "logging": {
            "level": "INFO",
            "debug": {
                "save_prompt": False,
                "save_response": False,
                "overwrite_debug_files": True,
            },
        },
    }

    monkeypatch.setattr(
        AppConfigurationService,
        "_load_configuration",
        lambda self: fake_config,
    )

    sys.modules.pop("services.prompt_loader_service", None)

    return importlib.import_module(
        "services.prompt_loader_service",
    )


def test_load_reads_prompt_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Load prompt text from the configured prompt directory."""

    module = _import_prompt_loader(monkeypatch)

    prompt_file = tmp_path / "sample.md"
    prompt_file.write_text(
        "hello prompt",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        module.PromptLoaderService,
        "PROMPTS_DIRECTORY",
        tmp_path,
    )

    text = module.PromptLoaderService.load("sample.md")

    assert text == "hello prompt"


def test_load_raises_when_prompt_file_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise FileNotFoundError when the prompt file does not exist."""

    module = _import_prompt_loader(monkeypatch)

    monkeypatch.setattr(
        module.PromptLoaderService,
        "PROMPTS_DIRECTORY",
        tmp_path,
    )

    with pytest.raises(FileNotFoundError):
        module.PromptLoaderService.load("missing.md")
