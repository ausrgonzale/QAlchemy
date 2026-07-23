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

import logging
from pathlib import Path

from services.app_configuration_service import AppConfigurationService

logger = logging.getLogger(__name__)


class PromptLoaderService:
    """
    Utility class for loading AI prompt templates.
    """

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    _configuration = AppConfigurationService()

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
            Exception:
                Re-raises any unexpected exception encountered while
                loading the prompt file after logging the error.
        """

        logger.info("Starting prompt load.")

        try:
            prompt_file = cls.PROMPTS_DIRECTORY / filename

            logger.debug("Loading prompt file: %s", prompt_file)

            prompt_text = prompt_file.read_text(encoding="utf-8")

            logger.info("Prompt load completed successfully.")

            return prompt_text

        except Exception:
            logger.exception("Prompt load failed for '%s'.", filename)
            raise
