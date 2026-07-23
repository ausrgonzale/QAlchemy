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

import logging
from typing import TYPE_CHECKING

from services.app_configuration_service import (
    AppConfigurationService,
)

if TYPE_CHECKING:
    from clients.ai_client import AIClient

AIClient = None

logger = logging.getLogger(__name__)


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

        Raises:
            Exception:
                Re-raises any unexpected exception encountered while
                constructing the AI client after logging the error.
        """
        logger.info("Starting AI client construction.")

        try:
            config = AppConfigurationService()

            provider = config.ai.provider
            model = model_override or config.ai.default_model
            request_timeout = config.ai.request_timeout
            stream = config.ai.stream

            if model_override is not None:
                logger.debug("Using model override: %s", model_override)

            client_class = AIClient

            if client_class is None:
                from clients.ai_client import AIClient as client_class

            logger.info("AI client construction completed successfully.")

            return client_class(
                provider=provider,
                model=model,
                request_timeout=request_timeout,
                stream=stream,
            )

        except Exception:
            logger.exception("AI client construction failed.")
            raise
