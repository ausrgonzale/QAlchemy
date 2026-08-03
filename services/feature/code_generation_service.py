"""
===============================================================================
File Descriptor Header
===============================================================================
File:
    code_generation_service.py

Purpose:
    Provides AI-assisted source code generation services for the
    Toolshop automation framework.

Architecture:
    This service is responsible for orchestrating the AI code
    generation workflow. It constructs the generation-specific
    user prompt, delegates prompt assembly to PromptBuilderService,
    submits the completed prompts to the AI client, and returns
    the AI-generated source code.

Responsibilities:
    - Accept code generation requests.
    - Construct the generation-specific user prompt.
    - Optionally preprocess existing source code.
    - Delegate prompt assembly to PromptBuilderService.
    - Submit prompts to the AI client.
    - Return AI-generated source code.

Workflow:
    User Task
        ↓
    Optional Existing Source Code
        ↓
    Generation User Prompt
        ↓
    PromptBuilderService
        ↓
    AIClient
        ↓
    Ollama
        ↓
    Generated Source Code

Dependencies:
    - clients.ai_client.AIClient
    - services.prompt_builder_service.PromptBuilderService
    - services.source_code_preprocessing_service.SourceCodePreprocessingService

Notes:
    This service is responsible only for generation-specific
    prompt construction and workflow orchestration. Framework
    standards and task prompt composition are delegated to
    PromptBuilderService.

Author:
    Ron Gonzalez

Created:
    June 2026
===============================================================================
"""

import logging

from services.core.ai_client_builder_service import AIClientBuilderService
from services.core.app_configuration_service import (
    AppConfigurationService,
)
from services.core.prompt_builder_service import PromptBuilderService
from services.core.source_code_preprocessing_service import (
    SourceCodePreprocessingService,
)

logger = logging.getLogger(__name__)


class CodeGenerationService:
    """
    Service responsible for generating source code from user input tasks.
    """

    def generate(
        self,
        task: str,
        source_code: str | None = None,
        model_override: str | None = None,
    ) -> str:
        """
        Generate source code using the configured AI provider.

        Args:
            task:
                Description of the requested development task.

            source_code:
                Optional existing source code that is preprocessed and included as context for the AI.

        Returns:
            Generated source code.
        """

        logger.info("Starting code generation.")

        try:

            if source_code is not None:
                logger.debug("Preprocessing existing source code.")
                source_code = SourceCodePreprocessingService.preprocess(source_code)

            user_prompt = "User Task\n\n" f"{task}"

            if source_code is not None:
                user_prompt += (
                    "\n\n"
                    "------------------------------------------------------------\n\n"
                    "Existing Source Code\n\n"
                    f"{source_code}"
                )

            configuration = AppConfigurationService()

            logger.info("Building AI prompts.")

            system_prompt, user_prompt = PromptBuilderService.build_prompt(
                task_prompt=configuration.prompts.generation_instructions,
                user_prompt=user_prompt,
            )

            if model_override is not None:
                logger.debug(f"Using model override: {model_override}")

            client = AIClientBuilderService.build(
                model_override=model_override,
            )

            logger.info("Invoking AI provider.")

            response = client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            logger.info("Code generation completed successfully.")

            return response

        except Exception:
            logger.exception("An unexpected error occurred during code generation.")
            raise
