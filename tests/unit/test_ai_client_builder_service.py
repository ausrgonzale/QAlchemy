"""Unit tests for AIClientBuilderService."""

from __future__ import annotations

import importlib
import sys

import pytest


def _import_builder_service() -> type:
    """Import AIClientBuilderService."""

    sys.modules.pop("services.ai_client_builder_service", None)
    module = importlib.import_module("services.ai_client_builder_service")
    return module.AIClientBuilderService


def test_build_uses_default_model_when_no_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Build AI client using the configured default model."""

    AIClientBuilderService = _import_builder_service()

    class FakeConfig:
        class ai:
            provider = "ollama"
            default_model = "default-model"
            request_timeout = 120
            stream = False

    captured: dict[str, object] = {}

    class FakeClient:
        def __init__(
            self,
            provider: str,
            model: str,
            request_timeout: int,
            stream: bool,
        ) -> None:
            captured["provider"] = provider
            captured["model"] = model
            captured["request_timeout"] = request_timeout
            captured["stream"] = stream

    monkeypatch.setattr(
        "services.ai_client_builder_service.FrameworkConfigurationService",
        FakeConfig,
    )
    monkeypatch.setattr(
        "services.ai_client_builder_service.AIClient",
        FakeClient,
    )

    client = AIClientBuilderService.build()

    assert isinstance(client, FakeClient)
    assert captured == {
        "provider": "ollama",
        "model": "default-model",
        "request_timeout": 120,
        "stream": False,
    }


def test_build_uses_model_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Build AI client using the supplied model override."""

    AIClientBuilderService = _import_builder_service()

    class FakeConfig:
        class ai:
            provider = "ollama"
            default_model = "default-model"
            request_timeout = 45
            stream = True

    captured: dict[str, object] = {}

    class FakeClient:
        def __init__(
            self,
            provider: str,
            model: str,
            request_timeout: int,
            stream: bool,
        ) -> None:
            captured["provider"] = provider
            captured["model"] = model
            captured["request_timeout"] = request_timeout
            captured["stream"] = stream

    monkeypatch.setattr(
        "services.ai_client_builder_service.FrameworkConfigurationService",
        FakeConfig,
    )
    monkeypatch.setattr(
        "services.ai_client_builder_service.AIClient",
        FakeClient,
    )

    client = AIClientBuilderService.build(
        model_override="override-model",
    )

    assert isinstance(client, FakeClient)
    assert captured == {
        "provider": "ollama",
        "model": "override-model",
        "request_timeout": 45,
        "stream": True,
    }
