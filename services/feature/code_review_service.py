"""
===============================================================================
File Descriptor Header
===============================================================================
File:
    code_review_service.py

Purpose:
    Provides AI-assisted source code review services for the
    Toolshop automation framework.

Architecture:
    This service orchestrates the AI code review workflow. It is
    responsible for constructing the review-specific user prompt,
    delegating prompt assembly to PromptBuilderService, submitting
    the completed prompts to the AI client, and returning the
    AI-generated review.

Responsibilities:
    - Accept source code for review.
    - Construct the review-specific user prompt.
    - Delegate prompt assembly to PromptBuilderService.
    - Submit prompts to the AI client.
    - Return AI-generated review feedback.

Workflow:
    Source Code
        ↓
    Review User Prompt
        ↓
    PromptBuilderService
        ↓
    AIClient
        ↓
    Ollama
        ↓
    Review Results

Dependencies:
    - clients.ai_client.AIClient
    - services.prompt_builder_service.PromptBuilderService
    - pathlib.Path

Notes:
    Review-specific prompt construction remains within this service.
    Framework standards and task prompt composition are delegated to
    PromptBuilderService, allowing prompt assembly logic to be reused
    across multiple services.

Author:
    Ron Gonzalez

Created:
    June 2026
===============================================================================
"""

import logging

from scripts.core.runtime_context import RuntimeContext
from services.core.ai_client_builder_service import AIClientBuilderService
from services.core.app_configuration_service import (
    AppConfigurationService,
)
from services.core.prompt_builder_service import PromptBuilderService

logger = logging.getLogger(__name__)


class CodeReviewService:
    """
    Service responsible for AI-assisted code reviews.

    This service accepts source code, submits it to an AI model
    using a predefined review prompt, and returns the review
    results to the caller.
    """

    def execute(
        self,
        source_code: str,
        runtime_context: RuntimeContext,
        model_override: str | None = None,
    ) -> str:
        """
        Execute an AI code review.

        Args:
            source_code: Python source code to be reviewed.

        Returns:
            AI-generated review feedback.

        Raises:
            Exception:
                Re-raises any unexpected exception encountered during the code review workflow after logging the error.
        """

        logger.info("Starting code review.")

        try:

            user_prompt = (
                "Review the supplied source code.\n\n"
                "============================================================\n"
                "BEGIN SOURCE CODE\n"
                "============================================================\n\n"
                f"{source_code}\n\n"
                "============================================================\n"
                "END SOURCE CODE\n"
                "============================================================\n"
            )

            configuration = AppConfigurationService()

            logger.info("Building AI prompts.")

            system_prompt, user_prompt = PromptBuilderService.build_prompt(
                task_prompt=configuration.prompts.review_instructions,
                user_prompt=user_prompt,
            )

            # Create a new AI client instance for this review operation.

            if model_override is not None:
                logger.debug(f"Using model override: {model_override}")

            client = AIClientBuilderService.build(
                model_override=model_override,
            )

            runtime_context.provider = client.provider
            runtime_context.model = client.model

            runtime_context.lines_reviewed = len(source_code.splitlines())

            # Send the formatted prompt to the model and return the generated review.

            logger.info("Invoking AI provider.")

            response = client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            logger.info("Code review completed successfully.")

            return response

        except Exception:
            logger.exception("Code review failed.")
            raise
