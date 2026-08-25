"""
Client implementation for the configured AI provider.

Version 1.2 supports Ollama only.

Future providers (OpenAI, Anthropic, Gemini, etc.)
will introduce provider-specific client implementations
behind the same public interface.
"""

from types import SimpleNamespace

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
