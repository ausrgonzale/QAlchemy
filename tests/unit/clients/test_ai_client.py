"""Unit tests for clients.ai_client.AIClient."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType, SimpleNamespace

import pytest


def _import_ai_client_module() -> ModuleType:
    """Import the AI client module."""

    sys.modules.pop("clients.ai_client", None)
    return importlib.import_module("clients.ai_client")


class _FakeChunk:
    def __init__(self, content: str | None) -> None:
        self.message = SimpleNamespace(content=content)


class _FakeResponse:
    def __init__(self, content: str | None) -> None:
        self.message = SimpleNamespace(content=content)


def test_init_sets_fields_and_ollama_client_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Initialize AI client with expected fields and configured timeout."""

    module = _import_ai_client_module()
    captured: dict[str, int] = {}

    class FakeOllamaClient:
        def __init__(self, timeout: int) -> None:
            captured["timeout"] = timeout

    monkeypatch.setattr(module.ollama, "Client", FakeOllamaClient)

    client = module.AIClient(
        provider="ollama",
        model="qwen3-coder:480b-cloud",
        request_timeout=120,
        stream=False,
    )

    assert client.provider == "ollama"
    assert client.model == "qwen3-coder:480b-cloud"
    assert client.request_timeout == 120
    assert client.stream is False
    assert captured["timeout"] == 120


def test_build_messages_returns_expected_payload() -> None:
    """Build message payload with expected system and user roles."""

    module = _import_ai_client_module()
    client = module.AIClient.__new__(module.AIClient)

    messages = client._build_messages("system text", "user text")

    assert messages == [
        {"role": "system", "content": "system text"},
        {"role": "user", "content": "user text"},
    ]


def test_build_messages_supports_empty_prompts() -> None:
    """Build message payload when prompts are empty."""

    module = _import_ai_client_module()
    client = module.AIClient.__new__(module.AIClient)

    messages = client._build_messages("", "")

    assert messages == [
        {"role": "system", "content": ""},
        {"role": "user", "content": ""},
    ]


def test_generate_routes_to_stream_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Route generate calls to stream implementation."""

    module = _import_ai_client_module()
    client = module.AIClient.__new__(module.AIClient)
    client.stream = True

    monkeypatch.setattr(client, "_generate_stream", lambda s, u: "stream-result")
    monkeypatch.setattr(client, "_generate_bulk", lambda s, u: "bulk-result")

    assert client.generate("system", "user") == "stream-result"


def test_generate_routes_to_bulk_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Route generate calls to bulk implementation."""

    module = _import_ai_client_module()
    client = module.AIClient.__new__(module.AIClient)
    client.stream = False

    monkeypatch.setattr(client, "_generate_stream", lambda s, u: "stream-result")
    monkeypatch.setattr(client, "_generate_bulk", lambda s, u: "bulk-result")

    assert client.generate("system", "user") == "bulk-result"


def test_generate_stream_joins_non_empty_chunks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Join streamed response chunks."""

    module = _import_ai_client_module()

    class FakeOllamaClient:
        def __init__(self, timeout: int) -> None:
            self.timeout = timeout

        def chat(
            self,
            *,
            model: str,
            messages: list[dict[str, str]],
            stream: bool,
        ):
            assert model == "qwen3-coder:480b-cloud"
            assert stream is True
            assert messages == [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "usr"},
            ]

            return [
                _FakeChunk("Hello"),
                _FakeChunk(" "),
                _FakeChunk("world"),
                _FakeChunk(""),
                _FakeChunk(None),
            ]

    monkeypatch.setattr(module.ollama, "Client", FakeOllamaClient)

    client = module.AIClient(
        "ollama",
        "qwen3-coder:480b-cloud",
        30,
        True,
    )

    assert client._generate_stream("sys", "usr") == "Hello world"


def test_generate_stream_returns_empty_string_when_no_chunks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return empty string when stream produces no content."""

    module = _import_ai_client_module()

    class FakeOllamaClient:
        def __init__(self, timeout: int) -> None:
            self.timeout = timeout

        def chat(self, **kwargs):
            return []

    monkeypatch.setattr(module.ollama, "Client", FakeOllamaClient)

    client = module.AIClient(
        "ollama",
        "model",
        30,
        True,
    )

    assert client._generate_stream("sys", "usr") == ""


def test_generate_stream_propagates_provider_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Propagate provider exceptions during streaming."""

    module = _import_ai_client_module()

    class FakeOllamaClient:
        def __init__(self, timeout: int) -> None:
            self.timeout = timeout

        def chat(self, **kwargs):
            raise RuntimeError("provider failure")

    monkeypatch.setattr(module.ollama, "Client", FakeOllamaClient)

    client = module.AIClient(
        "ollama",
        "model",
        30,
        True,
    )

    with pytest.raises(RuntimeError, match="provider failure"):
        client._generate_stream("sys", "usr")


def test_generate_bulk_returns_response_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return bulk response content."""

    module = _import_ai_client_module()

    class FakeOllamaClient:
        def __init__(self, timeout: int) -> None:
            self.timeout = timeout

        def chat(
            self,
            *,
            model: str,
            messages: list[dict[str, str]],
            stream: bool,
        ):
            assert model == "qwen3-coder:480b-cloud"
            assert stream is False
            assert messages == [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "usr"},
            ]

            return _FakeResponse("Generated response")

    monkeypatch.setattr(module.ollama, "Client", FakeOllamaClient)

    client = module.AIClient(
        "ollama",
        "qwen3-coder:480b-cloud",
        30,
        False,
    )

    assert client._generate_bulk("sys", "usr") == "Generated response"


def test_generate_bulk_returns_empty_string_when_content_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return empty string when bulk response content is missing."""

    module = _import_ai_client_module()

    class FakeOllamaClient:
        def __init__(self, timeout: int) -> None:
            self.timeout = timeout

        def chat(self, **kwargs):
            return _FakeResponse(None)

    monkeypatch.setattr(module.ollama, "Client", FakeOllamaClient)

    client = module.AIClient(
        "ollama",
        "qwen3-coder:480b-cloud",
        30,
        False,
    )

    assert client._generate_bulk("sys", "usr") == ""


def test_generate_bulk_propagates_provider_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Propagate provider exceptions during bulk requests."""

    module = _import_ai_client_module()

    class FakeOllamaClient:
        def __init__(self, timeout: int) -> None:
            self.timeout = timeout

        def chat(self, **kwargs):
            raise RuntimeError("provider failure")

    monkeypatch.setattr(module.ollama, "Client", FakeOllamaClient)

    client = module.AIClient(
        "ollama",
        "model",
        30,
        False,
    )

    with pytest.raises(RuntimeError, match="provider failure"):
        client._generate_bulk("sys", "usr")
