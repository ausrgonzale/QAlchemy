"""
File: services/ai_client_builder_service.py

Description:
    Provides a centralized factory for constructing configured AI client
    instances used throughout the Automation Framework.

    The AIClientBuilderService retrieves AI configuration from the
    AppConfigurationService and returns a fully configured AIClient.
    This centralizes client creation and ensures all framework components
    use a consistent configuration.

Responsibilities:
    - Load AI configuration from the framework configuration.
    - Resolve model overrides.
    - Create configured AIClient instances.
    - Serve as the single entry point for AI client construction.

Does Not:
    - Perform AI requests.
    - Validate prompts or responses.
    - Contain business logic.
    - Orchestrate agents or services.

Author: Ron Gonzalez
Framework: Automation Framework
License: MIT
"""

from typing import TYPE_CHECKING

from services.app_configuration_service import (
    AppConfigurationService,
)

if TYPE_CHECKING:
    from clients.ai_client import AIClient

AIClient = None


class AIClientBuilderService:
    """
    Builds configured AI client instances.
    """

    @staticmethod
    def build(
        model_override: str | None = None,
    ) -> "AIClient":
        """
        Build a configured AIClient.

        Args:
            model_override:
                Optional model supplied by the caller. When provided,
                it overrides the default model configured in the
                framework configuration.

        Returns:
            A fully configured AIClient.
        """
        config = AppConfigurationService()

        provider = config.ai.provider
        model = model_override or config.ai.default_model
        request_timeout = config.ai.request_timeout
        stream = config.ai.stream

        client_class = AIClient

        if client_class is None:
            from clients.ai_client import AIClient as client_class

        return client_class(
            provider=provider,
            model=model,
            request_timeout=request_timeout,
            stream=stream,
        )
