"""
===============================================================================
File Descriptor Header
===============================================================================
File:
    generation_instructions_service.py

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

from services.ai_client_builder_service import AIClientBuilderService
from services.app_configuration_service import (
    AppConfigurationService,
)
from services.prompt_builder_service import PromptBuilderService
from services.source_code_preprocessing_service import (
    SourceCodePreprocessingService,
)


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
            requirement:
                Description of the requested development task.

            source_code:
                Optional existing source code used for context.

        Returns:
            Generated source code.
        """

        if source_code is not None:
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

        system_prompt, user_prompt = PromptBuilderService.build_prompt(
            task_prompt=configuration.prompts.generation_instructions,
            user_prompt=user_prompt,
        )

        client = AIClientBuilderService.build(
            model_override=model_override,
        )

        response = client.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        return response
