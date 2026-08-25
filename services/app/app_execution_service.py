"""
Application execution service.

Provides the common runtime support environment for all QAlchemy
Feature Services.

Responsibilities
----------------
- Hold the initialized application runtime.
- Expose Core Services to the Orchestration Service.
- Expose Core Services to Feature Services.
- Provide a shared runtime context during execution.

Business logic intentionally does not belong here.
"""

from __future__ import annotations

from services.app.app_configuration_service import AppConfigurationService
from services.core.client_service import ClientService
from services.core.exception_handling_service import ExceptionHandlingService
from services.core.logger_service import LoggerService


class AppExecutionService:
    """
    Represents the initialized runtime environment for the QAlchemy application.

    The AppExecutionService receives the Core Services constructed by the
    AppBootstrapService and exposes them to the Orchestration Service and
    Feature Services during application execution.
    """

    def __init__(
        self,
        configuration: AppConfigurationService,
        client_service: ClientService,
        logger_service: LoggerService,
        exception_handling_service: ExceptionHandlingService,
    ) -> None:

        self._configuration: AppConfigurationService = configuration
        self._client_service: ClientService = client_service
        self._logger_service: LoggerService = logger_service
        self._exception_handling_service: ExceptionHandlingService = (
            exception_handling_service
        )

    @property
    def configuration(self) -> AppConfigurationService:
        """
        Return the application configuration.
        """
        return self._configuration

    @property
    def logger_service(self) -> LoggerService:
        """
        Returns the application logger.
        """
        return self._logger_service

    @property
    def exception_handling_service(self) -> ExceptionHandlingService:
        """
        Returns the application exception handler.
        """
        return self._exception_handling_service

    @property
    def client_service(self) -> ClientService:
        """
        Returns the application client service.
        """
        return self._client_service
