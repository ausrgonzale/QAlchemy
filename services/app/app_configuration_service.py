"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    app_configuration_service.py

Purpose:
    Provides strongly typed, read-only access to QAlchemy application
    configuration.

Description:
    AppConfigurationService loads config/app.yaml, validates the required
    top-level configuration sections, and exposes the configuration through
    strongly typed configuration objects.

Responsibilities
----------------
- Load app.yaml.
- Validate required top-level configuration sections.
- Expose strongly typed configuration objects.
- Provide a single configuration authority for the application.

Non-Responsibilities
--------------------
This service does NOT:

- Execute application workflows.
- Construct application services.
- Read prompt or standards files.
- Persist Work Orders.
- Perform AI operations.
- Perform logging persistence.
- Perform exception processing.

===============================================================================
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ConfigurationError(RuntimeError):
    """Raised when application configuration is invalid."""


class ConfigurationSection:
    """
    Base class for strongly typed configuration sections.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    def _get(
        self,
        key: str,
        default: Any | None = None,
    ) -> Any:
        """
        Return a configuration value.

        Raises:
            ConfigurationError:
                If the requested value is missing and no default is provided.
        """

        if key in self._config:
            return self._config[key]

        if default is not None:
            return default

        raise ConfigurationError(f"Missing required configuration value: '{key}'.")


# =============================================================================
# Application
# =============================================================================


class AppConfiguration(ConfigurationSection):
    """Application metadata configuration."""

    @property
    def name(self) -> str:
        return self._get("name")

    @property
    def version(self) -> str:
        return self._get("version")

    @property
    def edition(self) -> str:
        return self._get("edition")


# =============================================================================
# Client
# =============================================================================


class ClientConfiguration(ConfigurationSection):
    """AI client configuration."""

    @property
    def provider(self) -> str:
        return self._get("provider")

    @property
    def default_model(self) -> str:
        return self._get("default_model")

    @property
    def request_timeout(self) -> int:
        return self._get("request_timeout")

    @property
    def stream(self) -> bool:
        return self._get("stream")


# =============================================================================
# Work Order
# =============================================================================


class WorkOrderValidationConfiguration(ConfigurationSection):
    """Work Order validation configuration."""

    @property
    def enabled(self) -> bool:
        return self._get("enabled")

    @property
    def fail_on_missing_required_field(self) -> bool:
        return self._get("fail_on_missing_required_field")

    @property
    def fail_on_invalid_definition(self) -> bool:
        return self._get("fail_on_invalid_definition")


class WorkOrderRuntimeConfiguration(ConfigurationSection):
    """Work Order runtime configuration."""

    @property
    def allow_multiple_units_of_work(self) -> bool:
        return self._get("allow_multiple_units_of_work")

    @property
    def stop_on_validation_failure(self) -> bool:
        return self._get("stop_on_validation_failure")

    @property
    def persist_to_disk(self) -> bool:
        return self._get("persist_to_disk")

    @property
    def directory(self) -> str:
        return self._get("directory")


class WorkOrderConfiguration(ConfigurationSection):
    """Work Order configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

        self.validation = WorkOrderValidationConfiguration(self._get("validation"))

        self.runtime = WorkOrderRuntimeConfiguration(self._get("runtime"))


# =============================================================================
# WorkSpace
# =============================================================================


class WorkspaceConfiguration(ConfigurationSection):
    """WorkSpace configuration."""

    @property
    def root(self) -> str:
        return self._get("root")


# =============================================================================
# Templates
# =============================================================================


class TemplateConfiguration(ConfigurationSection):
    """Template configuration."""

    @property
    def root(self) -> str:
        return self._get("root")

    @property
    def code_review_report(self) -> str:
        return self._get("code_review_report")

    @property
    def requirement_reports(self) -> str:
        return self._get("requirement_reports")

    @property
    def test_cases_reports(self) -> str:
        return self._get("test_cases_reports")


# =============================================================================
# Reports
# =============================================================================


class ReportFieldsConfiguration(ConfigurationSection):
    """Review report field configuration."""

    @property
    def source_file(self) -> bool:
        return self._get("source_file")

    @property
    def lines_reviewed(self) -> bool:
        return self._get("lines_reviewed")

    @property
    def provider(self) -> bool:
        return self._get("provider")

    @property
    def model(self) -> bool:
        return self._get("model")

    @property
    def execution_time(self) -> bool:
        return self._get("execution_time")

    @property
    def review_date(self) -> bool:
        return self._get("review_date")


class ReportConfiguration(ConfigurationSection):
    """Review report configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

        self.fields = ReportFieldsConfiguration(self._get("fields"))

    @property
    def output_directory(self) -> str:
        return self._get("output_directory")


class ReportsConfiguration(ConfigurationSection):
    """Reports configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

        self.review = ReportConfiguration(self._get("review"))

    @property
    def output_root(self) -> str:
        return self._get("output_root")

    @property
    def debug_output_root(self) -> str:
        return self._get("debug_output_root")


# =============================================================================
# Logging
# =============================================================================


class DebugConfiguration(ConfigurationSection):
    """Debug logging configuration."""

    @property
    def enabled(self) -> bool:
        return self._get("enabled")

    @property
    def save_prompt(self) -> bool:
        return self._get("save_prompt")

    @property
    def save_response(self) -> bool:
        return self._get("save_response")

    @property
    def overwrite_files(self) -> bool:
        return self._get("overwrite_files")


class LoggingConfiguration(ConfigurationSection):
    """Application logging configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

        self.debug = DebugConfiguration(self._get("debug"))

    @property
    def level(self) -> str:
        return self._get("level")

    @property
    def output_root(self) -> str:
        return self._get("output_root")

    @property
    def output_path(self) -> Path:
        return Path(self.output_root)

    @property
    def base_filename(self) -> str:
        return self._get("base_filename")

    @property
    def extension(self) -> str:
        return self._get("extension", "")

    @property
    def log_file(self) -> Path:
        extension = self.extension or ".log"

        if not extension.startswith("."):
            extension = f".{extension}"

        return self.output_path / (f"{self.base_filename}{extension}")


# =============================================================================
# Exceptions
# =============================================================================


class ExceptionCatalogConfiguration(ConfigurationSection):
    """Exception catalog location configuration."""

    @property
    def root(self) -> Path:
        return Path(self._get("root"))

    @property
    def filename(self) -> str:
        return self._get("filename")

    @property
    def catalog_file(self) -> Path:
        return self.root / self.filename


class ExceptionDefaultsConfiguration(ConfigurationSection):
    """Exception default code configuration."""

    @property
    def unknown_exception_code(self) -> str:
        return self._get("unknown_exception_code")

    @property
    def validation_exception_code(self) -> str:
        return self._get("validation_exception_code")

    @property
    def internal_exception_code(self) -> str:
        return self._get("internal_exception_code")


class ExceptionLoggingConfiguration(ConfigurationSection):
    """Exception logging behavior configuration."""

    @property
    def log_exceptions(self) -> bool:
        return self._get("log_exceptions")

    @property
    def include_stack_trace(self) -> bool:
        return self._get("include_stack_trace")


class ExceptionUserMessagesConfiguration(ConfigurationSection):
    """Exception user message behavior configuration."""

    @property
    def expose_internal_errors(self) -> bool:
        return self._get("expose_internal_errors")


class ExceptionsConfiguration(ConfigurationSection):
    """Application exception subsystem configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

        self.catalog = ExceptionCatalogConfiguration(self._get("catalog"))

        self.defaults = ExceptionDefaultsConfiguration(self._get("defaults"))

        self.logging = ExceptionLoggingConfiguration(self._get("logging"))

        self.user_messages = ExceptionUserMessagesConfiguration(
            self._get("user_messages")
        )

    @property
    def enabled(self) -> bool:
        return self._get("enabled")


# =============================================================================
# App Configuration Service
# =============================================================================


class AppConfigurationService:
    """
    Loads and provides strongly typed access to application configuration.

    Configuration is loaded once during construction and exposed through
    strongly typed configuration objects.
    """

    _CONFIGURATION_DIRECTORY = "config"
    _CONFIGURATION_FILE = "app.yaml"

    _REQUIRED_SECTIONS = (
        "app",
        "client",
        "work_order",
        "workspace",
        "templates",
        "reports",
        "logging",
        "exceptions",
    )

    def __init__(
        self,
        configuration_file: Path | None = None,
    ) -> None:
        """Load and initialize application configuration."""

        logger.info("Starting application configuration load.")

        self._configuration_file = configuration_file
        self._config = self._load_configuration()

        self.app = AppConfiguration(self._section("app"))

        self.client = ClientConfiguration(self._section("client"))

        self.work_order = WorkOrderConfiguration(self._section("work_order"))

        self.workspace = WorkspaceConfiguration(self._section("workspace"))

        self.templates = TemplateConfiguration(self._section("templates"))

        self.reports = ReportsConfiguration(self._section("reports"))

        self.logging = LoggingConfiguration(self._section("logging"))

        self.exceptions = ExceptionsConfiguration(self._section("exceptions"))

        logger.info("Application configuration load completed successfully.")

    def load(self) -> AppConfigurationService:
        """
        Return the loaded configuration.

        This method remains because the current AppBootstrapService calls
        AppConfigurationService().load().
        """

        return self

    def _section(
        self,
        name: str,
    ) -> dict[str, Any]:
        """
        Return a required top-level configuration section.

        Raises:
            ConfigurationError:
                If the requested section is missing.
        """

        try:
            return self._config[name]

        except KeyError as ex:
            logger.exception(
                "Missing required configuration section: '%s'.",
                name,
            )

            raise ConfigurationError(
                f"Missing required configuration section: '{name}'."
            ) from ex

    def _load_configuration(self) -> dict[str, Any]:
        """
        Load and validate app.yaml.

        Raises:
            ConfigurationError:
                If the configuration file cannot be found, read, parsed,
                or is missing required top-level sections.
        """

        if self._configuration_file is not None:
            configuration_file = self._configuration_file

        else:
            configuration_file = (
                Path(__file__).resolve().parents[2]
                / self._CONFIGURATION_DIRECTORY
                / self._CONFIGURATION_FILE
            )

        logger.debug(
            "Loading configuration file: %s",
            configuration_file,
        )

        if not configuration_file.exists():
            logger.error(
                "Configuration file not found: %s",
                configuration_file,
            )

            raise ConfigurationError(
                "Configuration file not found:\n" f"  {configuration_file}"
            )

        try:
            with configuration_file.open(
                mode="r",
                encoding="utf-8",
            ) as file:
                configuration = yaml.safe_load(file) or {}

        except OSError as ex:
            logger.exception(
                "Unable to read configuration file: %s",
                configuration_file,
            )

            raise ConfigurationError(
                f"Unable to read configuration file " f"'{configuration_file}'."
            ) from ex

        except yaml.YAMLError as ex:
            logger.exception(
                "Unable to parse configuration file: %s",
                configuration_file,
            )

            raise ConfigurationError(
                f"Unable to parse configuration file " f"'{configuration_file}'."
            ) from ex

        if not isinstance(configuration, dict):
            logger.error("Configuration file does not contain a " "top-level mapping.")

            raise ConfigurationError(
                "The application configuration must contain " "a top-level mapping."
            )

        for section in self._REQUIRED_SECTIONS:
            if section not in configuration:
                logger.error(
                    "Missing required configuration section: %s",
                    section,
                )

                raise ConfigurationError(
                    "Missing required configuration section:\n" f"  {section}"
                )

        logger.debug("Configuration file loaded and validated successfully.")

        return configuration
