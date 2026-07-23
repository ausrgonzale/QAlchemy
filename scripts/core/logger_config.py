"""
Logger configuration.

Adapts the application's LoggingConfiguration into a runtime
configuration that can be consumed by Logger.
"""

from pathlib import Path

from services.app_configuration_service import LoggingConfiguration


class LoggerConfig:
    """Runtime logger configuration."""

    def __init__(self, configuration: LoggingConfiguration) -> None:
        self._configuration = configuration

    @property
    def directory(self) -> Path:
        """Return the log directory."""
        return self._configuration.output_path

    @property
    def filename(self) -> str:
        """Return the log filename."""
        return self.log_file.name

    @property
    def log_file(self) -> Path:
        """Return the configured log file."""
        return self._configuration.log_file
