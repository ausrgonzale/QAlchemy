"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    application_bootstrap_service.py

Purpose:
    Bootstraps the QAlchemy application.

Description:
    The ApplicationBootstrapService serves as the Composition Root for the
    QAlchemy application. Its responsibility is to initialize the application's
    public services and provide a single entry point for host applications.

Current Consumers:
    - tests/e2e/test_e2e_qalchemy.py

Future Consumers:
    - generate_code.py
    - review_source_code.py
    - demo.py
    - CLI
    - REST
    - MCP

===============================================================================
"""

from __future__ import annotations

from scripts.core.logger import Logger
from scripts.core.logger_config import LoggerConfig
from services.core.app_configuration_service import AppConfigurationService
from services.core.logger_service import LoggerService
from services.feature.code_generation_service import CodeGenerationService
from services.feature.code_review_service import CodeReviewService


class ApplicationBootstrapService:
    """
    Composition Root for the QAlchemy application.

    Responsibilities:
        - Load application configuration.
        - Initialize shared application infrastructure.
        - Initialize application feature services.
        - Expose application-facing services to host applications.

    Version 1.1 intentionally keeps the bootstrap lightweight.
    Feature services continue to manage their own internal dependencies.
    """

    def __init__(self) -> None:
        """Initialize the bootstrap service."""

        self._configuration: AppConfigurationService | None = None
        self._logger_service: LoggerService | None = None

        self._code_generation_service: CodeGenerationService | None = None
        self._code_review_service: CodeReviewService | None = None

    @property
    def configuration(self) -> AppConfigurationService:
        """Return the application configuration."""

        assert self._configuration is not None
        return self._configuration

    @property
    def logger_service(self) -> LoggerService:
        """Return the application logger service."""

        assert self._logger_service is not None
        return self._logger_service

    @property
    def code_generation_service(self) -> CodeGenerationService:
        """Return the code generation service."""

        assert self._code_generation_service is not None
        return self._code_generation_service

    @property
    def code_review_service(self) -> CodeReviewService:
        """Return the code review service."""

        assert self._code_review_service is not None
        return self._code_review_service

    def bootstrap(self) -> ApplicationBootstrapService:
        """
        Bootstrap the application.

        Returns:
            The initialized ApplicationBootstrapService instance.
        """

        #
        # Load application configuration.
        #
        self._configuration = AppConfigurationService().load()

        #
        # Initialize application logging.
        #
        logger = Logger(LoggerConfig(self._configuration.logging))

        self._logger_service = LoggerService(
            logger=logger,
            component="Application",
        )

        #
        # Initialize feature services.
        #
        self._code_generation_service = CodeGenerationService()
        self._code_review_service = CodeReviewService()

        return self
