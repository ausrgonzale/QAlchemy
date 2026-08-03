"""
Application Configuration Service

Loads and provides strongly typed, read-only access to the application
configuration stored in config/app.yaml.

Version 1.1 Responsibilities
----------------------------
- Load the YAML configuration file.
- Perform basic configuration validation.
- Cache the configuration in memory.
- Provide strongly typed access to configuration values.

Future Enhancements
-------------------
- ConfigurationValidationService
- Environment variable overrides
- Schema validation
- Configuration hot reload
"""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ConfigurationError(RuntimeError):
    """Raised when the application configuration is invalid."""


class ConfigurationSection:
    """
    Base class for all configuration sections.

    Provides a common implementation for retrieving required configuration
    values while producing consistent error messages.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    def _get(self, key: str, default: Any | None = None) -> Any:
        """
        Return a configuration value.

        If a default value is provided, it is returned when the configuration
        key does not exist. Otherwise, a ConfigurationError is raised.
        """
        if key in self._config:
            return self._config[key]

        if default is not None:
            return default

        raise ConfigurationError(f"Missing required configuration value: '{key}'.")


class AppConfiguration(ConfigurationSection):
    """Application metadata."""

    @property
    def name(self) -> str:
        return self._get("name")

    @property
    def version(self) -> str:
        return self._get("version")

    @property
    def edition(self) -> str:
        return self._get("edition")


class AIConfiguration(ConfigurationSection):
    """AI provider configuration."""

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


class PromptConfiguration(ConfigurationSection):
    """Prompt configuration."""

    @property
    def root(self) -> str:
        return self._get("root")

    @property
    def code_standards(self) -> str:
        return self._get("code_standards")

    @property
    def python_standards(self) -> str:
        return self._get("python_standards")

    @property
    def playwright_standards(self) -> str:
        return self._get("playwright_standards")

    @property
    def generation_instructions(self) -> str:
        return self._get("generation_instructions")

    @property
    def review_instructions(self) -> str:
        return self._get("review_instructions")

    @property
    def markdown_contract(self) -> str:
        return self._get("markdown_contract")


class PromptBuilderValidationConfiguration(ConfigurationSection):
    """Prompt builder validation configuration."""

    @property
    def enabled(self) -> bool:
        return self._get("enabled")

    @property
    def fail_on_missing_artifact(self) -> bool:
        return self._get("fail_on_missing_artifact")

    @property
    def fail_on_invalid_work_order(self) -> bool:
        return self._get("fail_on_invalid_work_order")


class PromptBuilderArtifactsConfiguration(ConfigurationSection):
    """Prompt builder artifact configuration."""

    @property
    def preprocess(self) -> bool:
        return self._get("preprocess")

    @property
    def compression(self) -> dict[str, Any]:
        return self._get("compression")


class PromptBuilderRenderingConfiguration(ConfigurationSection):
    """Prompt builder rendering configuration."""

    @property
    def provider(self) -> str:
        return self._get("provider")


class PromptBuilderOutputConfiguration(ConfigurationSection):
    """Prompt builder output configuration."""

    @property
    def write_prompt_to_disk(self) -> bool:
        return self._get("write_prompt_to_disk")

    @property
    def output_directory(self) -> str:
        return self._get("output_directory")

    @property
    def include_metadata(self) -> bool:
        return self._get("include_metadata")


class PromptBuilderConfiguration(ConfigurationSection):
    """Prompt builder configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

        self.validation = PromptBuilderValidationConfiguration(self._get("validation"))

        self.artifacts = PromptBuilderArtifactsConfiguration(self._get("artifacts"))

        self.rendering = PromptBuilderRenderingConfiguration(self._get("rendering"))

        self.output = PromptBuilderOutputConfiguration(self._get("output"))


class TemplateConfiguration(ConfigurationSection):
    """Template configuration."""

    @property
    def root(self) -> str:
        return self._get("root")

    @property
    def code_review_report(self) -> str:
        return self._get("code_review_report")


class ReportFieldsConfiguration(ConfigurationSection):
    """Report field configuration."""

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

        return self.output_path / f"{self.base_filename}{extension}"


class ExceptionCatalogConfiguration(ConfigurationSection):
    """Exception catalog location configuration."""

    @property
    def root(self) -> str:
        return self._get("root")

    @property
    def filename(self) -> str:
        return self._get("filename")


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


# ============================================================================
# App Configuration Service
# ============================================================================


class AppConfigurationService:
    """
    Loads and provides strongly typed access to the application
    configuration.

    The configuration is loaded once during construction and exposed
    through strongly typed configuration objects.
    """

    _CONFIGURATION_DIRECTORY = "config"
    _CONFIGURATION_FILE = "app.yaml"

    _REQUIRED_SECTIONS = (
        "app",
        "ai",
        "prompts",
        "prompt_builder",
        "templates",
        "reports",
        "logging",
        "exceptions",
    )

    def __init__(
        self,
        configuration_file: Path | None = None,
    ) -> None:
        logger.info("Starting application configuration load.")

        self._configuration_file = configuration_file

        self._config = self._load_configuration()

        self.app = AppConfiguration(self._section("app"))
        self.ai = AIConfiguration(self._section("ai"))
        self.prompts = PromptConfiguration(self._section("prompts"))
        self.prompt_builder = PromptBuilderConfiguration(
            self._section("prompt_builder")
        )
        self.templates = TemplateConfiguration(self._section("templates"))
        self.reports = ReportsConfiguration(self._section("reports"))
        self.logging = LoggingConfiguration(self._section("logging"))
        self.exceptions = ExceptionsConfiguration(self._section("exceptions"))

        logger.info("Application configuration load completed successfully.")

    def load(self) -> "AppConfigurationService":
        """
        Return the loaded configuration.

        Retained for backward compatibility with Version 1 code that
        called AppConfigurationService().load().
        """
        return self

    def _section(self, name: str) -> dict[str, Any]:
        """
        Return a required top-level configuration section.

        Raises:
            ConfigurationError:
                If the requested section is missing.
        """
        try:
            return self._config[name]
        except KeyError as ex:
            logger.exception("Missing required configuration section: '%s'.", name)
            raise ConfigurationError(
                f"Missing required configuration section: '{name}'."
            ) from ex

    def _load_configuration(self) -> dict[str, Any]:
        """
        Load the application configuration from disk.

        Raises:
            ConfigurationError:
                If the configuration file cannot be found, parsed,
                or is missing required sections.
        """
        if self._configuration_file is not None:

            configuration_file = self._configuration_file

        else:

            configuration_file = (
                Path(__file__).resolve().parents[2]
                / self._CONFIGURATION_DIRECTORY
                / self._CONFIGURATION_FILE
            )

        logger.debug("Loading configuration file: %s", configuration_file)

        if not configuration_file.exists():
            logger.error("Configuration file not found: %s", configuration_file)
            raise ConfigurationError(
                "Configuration file not found:\n" f"  {configuration_file}"
            )

        try:
            with configuration_file.open(mode="r", encoding="utf-8") as file:
                configuration = yaml.safe_load(file) or {}

        except OSError as ex:
            logger.exception(
                "Unable to read configuration file: %s", configuration_file
            )
            raise ConfigurationError(
                f"Unable to read configuration file '{configuration_file}'."
            ) from ex

        except yaml.YAMLError as ex:
            logger.exception(
                "Unable to parse configuration file: %s", configuration_file
            )
            raise ConfigurationError(
                f"Unable to parse configuration file '{configuration_file}'."
            ) from ex

        if not isinstance(configuration, dict):
            logger.error("Configuration file does not contain a top-level mapping.")
            raise ConfigurationError(
                "The application configuration must contain a " "top-level mapping."
            )

        for section in self._REQUIRED_SECTIONS:
            if section not in configuration:
                logger.error("Missing required configuration section: %s", section)
                raise ConfigurationError(
                    "Missing required configuration section:\n" f"  {section}"
                )

        logger.debug("Configuration file loaded and validated successfully.")

        return configuration
