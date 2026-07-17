"""
Framework Configuration Service

Loads and provides access to the framework configuration stored in
framework.yaml.

Version 1 Responsibilities:
- Load the YAML configuration file.
- Cache the configuration in memory.
- Provide read-only access to configuration values.

Future enhancements:
- Configuration validation
- Environment variable overrides
- Default values
- Singleton implementation
"""

from pathlib import Path
from typing import Any

import yaml


class FrameworkConfiguration:
    """Provides access to framework configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    @property
    def name(self) -> str:
        return self._config["name"]

    @property
    def version(self) -> str:
        return self._config["version"]


class AIConfiguration:
    """Provides access to AI configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    @property
    def provider(self) -> str:
        return self._config["provider"]

    @property
    def default_model(self) -> str:
        return self._config["default_model"]

    @property
    def request_timeout(self) -> int:
        return self._config["request_timeout"]

    @property
    def stream(self) -> bool:
        return self._config["stream"]


class PromptConfiguration:
    """Provides access to prompt configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    @property
    def root(self) -> str:
        return self._config["root"]

    @property
    def code_standards(self) -> str:
        return self._config["code_standards"]

    @property
    def python_standards(self) -> str:
        return self._config["python_standards"]

    @property
    def playwright_standards(self) -> str:
        return self._config["playwright_standards"]

    @property
    def generation_instructions(self) -> str:
        return self._config["generation_instructions"]

    @property
    def review_instructions(self) -> str:
        return self._config["review_instructions"]

    @property
    def markdown_contract(self) -> str:
        return self._config["markdown_contract"]


class TemplateConfiguration:
    """Provides access to template configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    @property
    def root(self) -> str:
        return self._config["root"]

    @property
    def code_review_report(self) -> str:
        return self._config["code_review_report"]


class ReportFieldsConfiguration:
    """Provides access to report field configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    @property
    def source_file(self) -> bool:
        return self._config["source_file"]

    @property
    def lines_reviewed(self) -> bool:
        return self._config["lines_reviewed"]

    @property
    def provider(self) -> bool:
        return self._config["provider"]

    @property
    def model(self) -> bool:
        return self._config["model"]

    @property
    def execution_time(self) -> bool:
        return self._config["execution_time"]

    @property
    def review_date(self) -> bool:
        return self._config["review_date"]


class ReportConfiguration:
    """Provides access to report configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self.fields = ReportFieldsConfiguration(config["fields"])


class ReportsConfiguration:
    """Provides access to reports configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self.review = ReportConfiguration(config["review"])

    @property
    def output_root(self) -> str:
        return self._config["output_root"]

    @property
    def debug_output_root(self) -> str:
        return self._config["debug_output_root"]


class LoggingConfiguration:
    """Provides access to logging configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self.debug = DebugConfiguration(config["debug"])

    @property
    def level(self) -> str:
        return self._config["level"]


class DebugConfiguration:
    """Provides access to debug configuration."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    @property
    def enabled(self) -> bool:
        return self._config["enabled"]

    @property
    def save_prompt(self) -> bool:
        return self._config["save_prompt"]

    @property
    def save_response(self) -> bool:
        return self._config["save_response"]

    @property
    def overwrite_files(self) -> bool:
        return self._config["overwrite_files"]


class FrameworkConfigurationService:
    """Loads and provides access to the framework configuration."""

    _CONFIGURATION_FILE = "framework.yaml"

    def __init__(self) -> None:
        self._config = self._load_configuration()

        self.framework = FrameworkConfiguration(self._config["framework"])

        self.ai = AIConfiguration(self._config["ai"])

        self.prompts = PromptConfiguration(self._config["prompts"])

        self.templates = TemplateConfiguration(self._config["templates"])

        self.reports = ReportsConfiguration(self._config["reports"])

        self.logging = LoggingConfiguration(self._config["logging"])

    def _load_configuration(self) -> dict[str, Any]:
        """Load the framework configuration."""

        current_file = Path(__file__).resolve()

        project_root = current_file.parent.parent

        configuration_file = project_root / self._CONFIGURATION_FILE

        with configuration_file.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            return yaml.safe_load(file)
