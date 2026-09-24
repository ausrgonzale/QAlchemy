"""
Client implementation for the configured AI provider.

Version 1.2 supports Ollama only.

Future providers (OpenAI, Anthropic, Gemini, etc.)
will introduce provider-specific client implementations
behind the same public interface.
"""

from types import SimpleNamespace

from agents.contracts.res_agent_response import AgentResponse
from agents.tools.tool_call import ToolCall
from agents.tools.tool_definition import ToolDefinition

try:
    import ollama
except ModuleNotFoundError:
    ollama = SimpleNamespace(Client=None)


class Client:
    """Communicates with the configured AI provider."""

    def __init__(
        self,
        provider: str,
        model: str,
        request_timeout: int,
        stream: bool,
    ) -> None:
        """
        Initialize the client.

        Args:
            provider:
                Configured AI provider.

            model:
                Model name.

            request_timeout:
                Request timeout in seconds.

            stream:
                Enable streaming responses.
        """

        self._provider = provider
        self._model = model
        self._stream = stream
        self._request_timeout = request_timeout

        if provider.lower() != "ollama":
            raise ValueError(f"Unsupported provider: {provider}")

        if ollama.Client is None:
            raise ModuleNotFoundError("The 'ollama' package is not installed.")

        self._client = ollama.Client(
            timeout=self._request_timeout,
        )

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Submit a rendered prompt to the configured provider.

        Args:
            prompt:
                Fully rendered engineering prompt.

        Returns:
            Provider response.
        """

        if self._stream:
            return self._generate_stream(prompt)

        return self._generate_bulk(prompt)

    def agent_turn(
        self,
        messages: list[dict[str, object]],
        tools: tuple[ToolDefinition, ...],
    ) -> AgentResponse:
        """
        Submit an Agent turn to the configured provider.

        Args:
            messages:
                Agent conversation messages.

            tools:
                Tools available to the Agent.

        Returns:
            Provider-neutral Agent response.
        """

        provider_messages = self._build_agent_messages(messages)

        response = self._client.chat(
            model=self._model,
            messages=provider_messages,
            tools=self._build_tools(tools),
            stream=False,
        )

        tool_calls = tuple(
            ToolCall(
                name=tool_call.function.name,
                arguments=dict(tool_call.function.arguments),
            )
            for tool_call in (response.message.tool_calls or ())
        )

        return AgentResponse(
            content=response.message.content or "",
            tool_calls=tool_calls,
        )

    def _build_tools(
        self,
        tools: tuple[ToolDefinition, ...],
    ) -> list[dict[str, object]]:
        """
        Convert provider-neutral tool definitions into the provider format.
        """

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in tools
        ]

    def _build_messages(
        self,
        prompt: str,
    ) -> list[dict[str, str]]:
        """
        Build the provider message payload.
        """

        return [
            {
                "role": "user",
                "content": prompt,
            }
        ]

    def _generate_stream(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a streamed response.
        """

        response = self._client.chat(
            model=self._model,
            messages=self._build_messages(prompt),
            stream=True,
        )

        chunks: list[str] = []

        for chunk in response:
            if chunk.message.content:
                chunks.append(chunk.message.content)

        return "".join(chunks)

    def _generate_bulk(
        self,
        prompt: str,
    ) -> str:
        """
        Generate a non-streamed response.
        """

        response = self._client.chat(
            model=self._model,
            messages=self._build_messages(prompt),
            stream=False,
        )

        return response.message.content or ""

    def _build_agent_messages(
        self,
        messages: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        """
        Convert provider-neutral Agent messages into provider-specific messages.
        """
        converted_messages: list[dict[str, object]] = []

        for message in messages:
            converted_message = dict(message)
            tool_calls = converted_message.get("tool_calls")

            if isinstance(tool_calls, tuple):
                converted_message["tool_calls"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": tool_call.arguments,
                        },
                    }
                    for tool_call in tool_calls
                ]

            converted_messages.append(converted_message)

        return converted_messages
