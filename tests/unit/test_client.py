"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_client.py

Purpose:
    Provides unit tests for the QAlchemy AI Client.

Description:
    Validates the provider-facing behavior of the Client and its translation
    between provider-neutral Agent schemas and the configured AI provider.

    These tests focus on deterministic Client behavior and do not require a
    live AI provider or model.

Responsibilities:
    - Validate Client initialization.
    - Validate provider configuration.
    - Validate standard text generation behavior.
    - Validate Agent turn message handling.
    - Validate Agent tool definition translation.
    - Validate provider tool-call translation.
    - Validate provider-neutral AgentResponse creation.

Non-Responsibilities:
    - Testing LLM reasoning.
    - Testing Agent decision-making.
    - Testing tool execution.
    - Testing Agent workflow orchestration.
    - Testing live provider/model behavior.

Test Strategy:
    - Mock the Ollama client.
    - Verify provider calls and arguments.
    - Verify provider responses are translated into QAlchemy schemas.
    - Keep tests deterministic and independent of a live model.

Version 1.3
-----------
- Introduces Client unit-test coverage for Agent workflows.

===============================================================================
"""

from unittest.mock import Mock

import pytest

from agents.tools.tool_call import ToolCall
from agents.tools.tool_definition import ToolDefinition
from clients.client import Client

pytestmark = pytest.mark.client


@pytest.mark.agent
def test_agent_turn_sends_messages_and_tools_to_provider() -> None:
    """Send Agent messages and translated tools to the provider."""

    client = Client.__new__(Client)

    client._model = "test-model"
    client._client = Mock()

    client._client.chat.return_value.message.content = "done"
    client._client.chat.return_value.message.tool_calls = []

    messages: list[dict[str, object]] = [
        {
            "role": "user",
            "content": "Evaluate this requirement.",
        },
    ]

    tools = (
        ToolDefinition(
            name="read_file",
            description="Read the contents of a file.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                    },
                },
                "required": ["path"],
            },
        ),
    )

    client.agent_turn(messages, tools)

    client._client.chat.assert_called_once_with(
        model="test-model",
        messages=messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of " "a file.",
                    "parameters": tools[0].parameters,
                },
            },
        ],
        stream=False,
    )


@pytest.mark.agent
def test_agent_turn_sends_assistant_tool_call_history() -> None:
    """Send provider-neutral assistant tool-call history to the provider."""

    client = Client.__new__(Client)

    client._model = "test-model"
    client._client = Mock()

    client._client.chat.return_value.message.content = "done"
    client._client.chat.return_value.message.tool_calls = []

    tool_call = ToolCall(
        name="read_file",
        arguments={
            "path": "/resources/requirements/requirement.json",
        },
    )

    messages: list[dict[str, object]] = [
        {
            "role": "user",
            "content": "Evaluate this requirement.",
        },
        {
            "role": "assistant",
            "tool_calls": (tool_call,),
        },
        {
            "role": "tool",
            "content": '{"summary": "Password Reset"}',
        },
    ]

    client.agent_turn(
        messages=messages,
        tools=(
            ToolDefinition(
                name="read_file",
                description="Read the contents of a file.",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                        },
                    },
                    "required": ["path"],
                },
            ),
        ),
    )

    expected_messages: list[dict[str, object]] = [
        {
            "role": "user",
            "content": "Evaluate this requirement.",
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "arguments": {
                            "path": "/resources/requirements/requirement.json",
                        },
                    },
                },
            ],
        },
        {
            "role": "tool",
            "content": '{"summary": "Password Reset"}',
        },
    ]

    client._client.chat.assert_called_once_with(
        model="test-model",
        messages=expected_messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                            },
                        },
                        "required": ["path"],
                    },
                },
            },
        ],
        stream=False,
    )


def test_agent_turn_translates_tool_call_history_for_provider():
    """Translate provider-neutral ToolCall history into provider format."""
    client = Client(
        provider="ollama",
        model="test-model",
        request_timeout=30,
        stream=False,
    )

    tool_call = ToolCall(
        name="read_file",
        arguments={"path": "/templates/template1"},
    )

    messages: list[dict[str, object]] = [
        {"role": "user", "content": "Evaluate this requirement."},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": (tool_call,),
        },
        {
            "role": "tool",
            "content": '{"summary": "Password Reset"}',
        },
    ]

    mock_response = Mock()
    mock_response.message.content = '{"summary": "complete"}'
    mock_response.message.tool_calls = None

    client._client.chat = Mock(return_value=mock_response)

    client.agent_turn(messages, ())

    client._client.chat.assert_called_once()

    provider_messages = client._client.chat.call_args.kwargs["messages"]

    assert provider_messages[1]["tool_calls"] == [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "arguments": {
                    "path": "/templates/template1",
                },
            },
        }
    ]
