"""
prompt_loader_service.py

Purpose:
    Loads AI prompt templates from the project's prompts directory.

Responsibilities:
    - Load prompt template files.
    - Return prompt text as a string.
    - Centralize prompt loading for all services.

Author:
    Ron Gonzalez

Created:
    June 2026
"""

from pathlib import Path

from services.framework_configuration_service import FrameworkConfigurationService


class PromptLoaderService:
    """
    Utility class for loading AI prompt templates.
    """

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    _configuration = FrameworkConfigurationService()

    PROMPTS_DIRECTORY = PROJECT_ROOT / _configuration.prompts.root

    @classmethod
    def load(cls, filename: str) -> str:
        """
        Load a prompt template.

        Args:
            filename:
                Name of the prompt template file.

        Returns:
            Prompt template as a string.

        Raises:
            FileNotFoundError:
                If the prompt template cannot be found.
        """

        prompt_file = cls.PROMPTS_DIRECTORY / filename

        return prompt_file.read_text(encoding="utf-8")
