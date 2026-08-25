# =============================================================================
# test_app_execution_service.py
#
# QAlchemy Community Edition
#
# Copyright (c) 2026
#
# =============================================================================
# Purpose
# -----------------------------------------------------------------------------
# Unit tests for AppExecutionService.
#
# These tests verify that AppExecutionService correctly composes the common
# runtime environment required by all QAlchemy Feature Services.
#
# The behavior of the individual runtime services is intentionally NOT tested
# here. Those services have their own dedicated unit test suites.
#
# Responsibilities Verified
# -----------------------------------------------------------------------------
# • AppConfigurationService is initialized.
# • LoggerService is initialized.
# • ExceptionHandlingService is initialized.
# • Public properties return the expected runtime services.
#
# =============================================================================

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from services.app.app_configuration_service import AppConfigurationService
from services.app.app_execution_service import AppExecutionService
from services.core.exception_handling_service import ExceptionHandlingService
from services.core.logger_service import LoggerService


@pytest.fixture
def app_execution_service() -> AppExecutionService:
    """Returns a fully initialized AppExecutionService."""

    configuration = MagicMock(spec=AppConfigurationService)
    client_service = MagicMock()
    logger_service = MagicMock(spec=LoggerService)
    exception_handling_service = MagicMock(spec=ExceptionHandlingService)

    return AppExecutionService(
        configuration=configuration,
        client_service=client_service,
        logger_service=logger_service,
        exception_handling_service=exception_handling_service,
    )


# =============================================================================
# Construction
# =============================================================================


def test_configuration_is_initialized(
    app_execution_service: AppExecutionService,
) -> None:
    """Verify the application configuration is initialized."""

    assert app_execution_service.configuration is not None
    assert isinstance(
        app_execution_service.configuration,
        AppConfigurationService,
    )


def test_logger_is_initialized(
    app_execution_service: AppExecutionService,
) -> None:
    """Verify the logger service is initialized."""

    assert app_execution_service.logger_service is not None
    assert isinstance(
        app_execution_service.logger_service,
        LoggerService,
    )


def test_exception_handler_is_initialized(
    app_execution_service: AppExecutionService,
) -> None:
    """Verify the exception handling service is initialized."""

    assert app_execution_service.exception_handling_service is not None
    assert isinstance(
        app_execution_service.exception_handling_service,
        ExceptionHandlingService,
    )


# =============================================================================
# Properties
# =============================================================================


def test_configuration_property_returns_configuration(
    app_execution_service: AppExecutionService,
) -> None:
    """Verify the configuration property returns the same instance."""

    assert app_execution_service.configuration is app_execution_service._configuration


def test_logger_property_returns_logger(
    app_execution_service: AppExecutionService,
) -> None:
    """Verify the logger property returns the same instance."""

    assert app_execution_service.logger_service is app_execution_service._logger_service


def test_exception_handler_property_returns_exception_handler(
    app_execution_service: AppExecutionService,
) -> None:
    """Verify the exception handler property returns the same instance."""

    assert (
        app_execution_service.exception_handling_service
        is app_execution_service._exception_handling_service
    )


def test_runtime_services_are_initialized(
    app_execution_service: AppExecutionService,
) -> None:
    """Verify all runtime services are initialized."""

    assert app_execution_service.configuration is not None
    assert app_execution_service.logger_service is not None
    assert app_execution_service.exception_handling_service is not None
