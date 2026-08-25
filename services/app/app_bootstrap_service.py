"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    app_bootstrap_service.py

Purpose:
    Bootstraps the QAlchemy application.

Description:
    The AppBootstrapService serves as the Composition Root for the QAlchemy application. Its responsibility is to initialize the application's public services and provide a single entry point for host applications.

Current Consumers:
    - tests/e2e/test_e2e_qalchemy.py

Future Consumers:
    - generate_code.py
    - review_code.py
    - demo.py
    - CLI
    - REST
    - MCP

===============================================================================
"""

import logging
from pathlib import Path
from typing import Self

from scripts.app.bootstrap_logging import configure_bootstrap_logging
from scripts.core.logger import Logger
from scripts.core.logger_config import LoggerConfig
from scripts.core.work_order_transformer import WorkOrderTransformer
from services.app.app_configuration_service import AppConfigurationService
from services.app.app_execution_service import AppExecutionService
from services.app.orchestration_service import OrchestrationService
from services.core.client_service import ClientService
from services.core.exception_handling_service import ExceptionHandlingService
from services.core.logger_service import LoggerService
from services.feature.generate_code_service import GenerateCodeService
from services.feature.review_code_service import ReviewCodeService

logger = logging.getLogger(__name__)


class AppBootstrapService:
    """
    Composition Root for the QAlchemy application.

    Responsibilities:
        - Initialize the application.
        - Construct shared application services.
        - Construct Core Services.
        - Construct Feature Services.
        - Wire application dependencies.
        - Expose the application runtime.

    The AppBootstrapService is the application's entry point and is responsible for preparing the application for execution.
    """

    def __init__(self) -> None:
        """Initialize the bootstrap service."""

        self._configuration: AppConfigurationService | None = None

        #
        # Core Services
        #
        self._logger_service: LoggerService | None = None
        self._exception_handling_service: ExceptionHandlingService | None = None
        self._client_service: ClientService | None = None

        #
        # Application Services
        #
        self._execution_service: AppExecutionService | None = None
        self._orchestration_service: OrchestrationService | None = None

        #
        # Feature Services
        #
        self._generate_code_service: GenerateCodeService | None = None
        self._review_code_service: ReviewCodeService | None = None

    @property
    def configuration(self) -> AppConfigurationService:
        """Return the application configuration."""

        assert self._configuration is not None
        return self._configuration

    @property
    def client_service(self) -> ClientService:
        """Return the application client service."""

        assert self._client_service is not None
        return self._client_service

    @property
    def logger_service(self) -> LoggerService:
        """Return the application logger service."""

        assert self._logger_service is not None
        return self._logger_service

    @property
    def generate_code_service(self) -> GenerateCodeService:
        """Return the generate code service."""

        assert self._generate_code_service is not None
        return self._generate_code_service

    @property
    def review_code_service(self) -> ReviewCodeService:
        """Return the review code service."""

        assert self._review_code_service is not None
        return self._review_code_service

    @property
    def exception_handling_service(self) -> ExceptionHandlingService:
        assert self._exception_handling_service is not None
        return self._exception_handling_service

    @property
    def execution_service(self) -> AppExecutionService:
        assert self._execution_service is not None
        return self._execution_service

    @property
    def orchestration_service(self) -> OrchestrationService:
        assert self._orchestration_service is not None
        return self._orchestration_service

    def bootstrap(self) -> Self:
        """
        Bootstrap the application.
        """

        configure_bootstrap_logging()

        logger.info("Starting QAlchemy bootstrap.")

        try:

            #
            # Load application configuration.
            #
            self._configuration = AppConfigurationService().load()

            logger.info("Application configuration loaded.")

            #
            # Initialize Core Services
            #

            #
            # Client
            #
            self._client_service = ClientService(
                configuration=self._configuration.client,
            )

            logger.info("Client service initialized.")

            #
            # Logger
            #
            logger_instance = Logger(
                LoggerConfig(
                    self._configuration.logging,
                )
            )

            self._logger_service = LoggerService(
                logger=logger_instance,
                component="Application",
            )

            logger.info("Logger service initialized.")

            #
            # Exception Handling
            #
            self._exception_handling_service = ExceptionHandlingService(
                catalog_path=(
                    Path(self._configuration.exceptions.catalog.root)
                    / self._configuration.exceptions.catalog.filename
                )
            )

            logger.info("Exception handling service initialized.")

            self._execution_service = AppExecutionService(
                configuration=self.configuration,
                client_service=self.client_service,
                logger_service=self.logger_service,
                exception_handling_service=self.exception_handling_service,
            )

            logger.info("Application execution service initialized.")

            #
            # Renderers
            #
            work_order_transformer = WorkOrderTransformer()

            logger.info("Work Order renderer initialized.")

            #
            # Initialize Feature Services
            #
            self._generate_code_service = GenerateCodeService(
                execution_service=self.execution_service,
                work_order_transformer=work_order_transformer,
            )
            self._review_code_service = ReviewCodeService(
                execution_service=self.execution_service,
                work_order_transformer=work_order_transformer,
            )

            logger.info("Feature services initialized.")
            logger.info("Application bootstrap completed successfully.")

            #
            # Initialize Application Services
            #
            self._orchestration_service = OrchestrationService(
                execution_service=self._execution_service,
                generate_code_service=self._generate_code_service,
                review_code_service=self._review_code_service,
            )

            logger.info("Orchestration service initialized.")

            return self

        except Exception:
            logger.exception("Application bootstrap failed.")
            raise

    def run(self, runtime_request) -> None:
        """
        Start the QAlchemy application.
        """

        assert self._orchestration_service is not None

        self._orchestration_service.execute(runtime_request)
