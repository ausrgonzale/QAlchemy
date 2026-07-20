"""
AI client for interacting with a local Ollama server.

Responsibilities:
- Send prompts to Ollama
- Return model responses

This client is intentionally simple and supports a single
provider (Ollama) for the Toolshop project.
"""

from types import SimpleNamespace

try:
    import ollama
except ModuleNotFoundError:
    ollama = SimpleNamespace(Client=None)


class AIClient:
    """Simple Ollama client."""

    def __init__(
        self,
        provider: str,
        model: str,
        request_timeout: int,
        stream: bool,
    ):
        """
        Initialize the AI client.

        Args:
            provider:
                The AI provider to use for requests.

            model:
                The AI model to use for requests.

            request_timeout:
                Maximum time, in seconds, to wait for an AI response.

            stream:
                Whether to use streaming responses.
        """
        self.provider = provider
        self.model = model
        self.stream = stream
        self.request_timeout = request_timeout

        if ollama.Client is None:
            raise ModuleNotFoundError(
                "No module named 'ollama'. Install the ollama package to use AIClient."
            )

        self._client = ollama.Client(
            timeout=self.request_timeout,
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Send a prompt to Ollama and return the response.
        """

        if self.stream:
            return self._generate_stream(
                system_prompt,
                user_prompt,
            )

        return self._generate_bulk(
            system_prompt,
            user_prompt,
        )

    def _build_messages(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> list[dict[str, str]]:
        """
        Build the message payload for an AI request.
        """

        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

    def _generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Send a prompt to Ollama using streamed responses.

        Collects streamed response chunks and returns the
        assembled response text.
        """

        messages = self._build_messages(
            system_prompt,
            user_prompt,
        )

        response = self._client.chat(
            model=self.model,
            messages=messages,
            stream=True,
        )

        response_chunks: list[str] = []

        for chunk in response:
            content = chunk.message.content

            if content:
                response_chunks.append(content)

        return "".join(response_chunks)

    def _generate_bulk(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Send a prompt to Ollama and return the complete response.
        """

        messages = self._build_messages(
            system_prompt,
            user_prompt,
        )

        response = self._client.chat(
            model=self.model,
            messages=messages,
            stream=False,
        )

        return response.message.content or ""
