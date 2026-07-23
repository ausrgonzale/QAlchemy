"""
===============================================================================
File Descriptor Header
===============================================================================
File: prompt_builder_service.py

Purpose:
    Provides a centralized service for assembling AI prompts used throughout
    the automation framework.

    This service is responsible for combining the framework standards,
    task-specific prompt templates, and user-supplied source code into a
    single prompt that is ready to be submitted to an AI model.

Responsibilities:
    - Load the framework standards prompt.
    - Load the requested task prompt.
    - Assemble the complete AI prompt.
    - Return the completed prompt.

Design Notes:
    PromptBuilderService is responsible only for prompt composition.
    It delegates prompt loading to PromptLoaderService and does not
    communicate directly with AI clients or perform file I/O.

Dependencies:
    - services.prompt_loader_service.PromptLoaderService

Author:
    Ron Gonzalez

Created:
    July 2026
===============================================================================
"""

import logging

from services.app_configuration_service import (
    AppConfigurationService,
)
from services.prompt_loader_service import PromptLoaderService

logger = logging.getLogger(__name__)


class PromptBuilderService:
    """
    Builds complete AI prompts from reusable prompt templates.

    This service combines the framework standards with a task-specific
    prompt and user prompt to produce a prompt suitable
    for submission to an AI model.
    """

    @staticmethod
    def build_prompt(
        task_prompt: str,
        user_prompt: str,
    ) -> tuple[str, str]:
        """
        Build the system and user prompts for an AI workflow.

        Args:
            task_prompt:
                Task-specific prompt document filename.

            user_prompt:
                Caller-provided user prompt content.

        Returns:
            A tuple containing:
                - system_prompt
                - user_prompt

        Raises:
            Exception:
                Re-raises any unexpected exception encountered during prompt
                assembly after logging the error.
        """

        logger.info("Starting prompt assembly.")

        try:
            configuration = AppConfigurationService()

            documents = [
                configuration.prompts.code_standards,
                configuration.prompts.python_standards,
                configuration.prompts.playwright_standards,
                task_prompt,
            ]

            logger.debug("Loading %d prompt documents.", len(documents))

            system_prompt = "\n\n------------------------------------------------------------\n\n".join(
                PromptLoaderService.load(document) for document in documents
            )

            logger.info("Prompt assembly completed successfully.")

            return system_prompt, user_prompt

        except Exception:
            logger.exception("Prompt assembly failed.")
            raise
