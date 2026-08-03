"""
Shared pytest fixtures for unit tests.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml

from scripts.core.exception_catalog import ExceptionCatalog
from services.core.app_configuration_service import (
    AppConfigurationService,
    LoggingConfiguration,
)
from services.core.exception_handling_service import (
    ExceptionHandlingService,
)

# =============================================================================
# Test Resources
# =============================================================================

TEST_RESOURCES = Path(__file__).parent.parent / "resources"

TEST_APP_CONFIGURATION = TEST_RESOURCES / "app" / "app.yaml"

TEST_EXCEPTION_CATALOG = TEST_RESOURCES / "exceptions" / "exception_catalog.yaml"


# =============================================================================
# Application Configuration Fixtures
# =============================================================================


@pytest.fixture
def test_configuration() -> dict[str, Any]:
    """
    Load the canonical application configuration dictionary.
    """

    with TEST_APP_CONFIGURATION.open(
        mode="r",
        encoding="utf-8",
    ) as stream:
        return yaml.safe_load(stream)


@pytest.fixture
def configuration() -> AppConfigurationService:
    """
    Create an AppConfigurationService using the shared test configuration.
    """

    return AppConfigurationService(
        TEST_APP_CONFIGURATION,
    )


# =============================================================================
# Logging Fixtures
# =============================================================================


@pytest.fixture
def logging_configuration(
    tmp_path: Path,
) -> LoggingConfiguration:
    """
    Create a temporary logging configuration.
    """

    return LoggingConfiguration(
        {
            "level": "INFO",
            "output_root": str(tmp_path),
            "base_filename": "alchemy",
            "extension": ".log",
            "debug": {
                "enabled": False,
                "save_prompt": False,
                "save_response": False,
                "overwrite_files": True,
            },
        }
    )


# =============================================================================
# Exception Fixtures
# =============================================================================


@pytest.fixture
def exception_catalog_yaml() -> Path:
    """
    Return the shared exception catalog.
    """

    return TEST_EXCEPTION_CATALOG


@pytest.fixture
def exception_catalog(
    exception_catalog_yaml: Path,
) -> ExceptionCatalog:
    """
    Create an ExceptionCatalog.
    """

    return ExceptionCatalog(
        exception_catalog_yaml,
    )


@pytest.fixture
def exception_handling_service(
    exception_catalog: ExceptionCatalog,
) -> ExceptionHandlingService:
    """
    Create an ExceptionHandlingService.
    """

    return ExceptionHandlingService(
        catalog=exception_catalog,
    )


@pytest.fixture
def sample_exception_code() -> str:
    """
    Standard exception code used throughout unit tests.
    """

    return "CFG001"
