"""
Unit tests for LoggerConfig.
"""

from scripts.core.logger_config import LoggerConfig


def test_logger_config_returns_directory(logging_configuration):
    """Verify the logger configuration exposes the configured directory."""

    config = LoggerConfig(logging_configuration)

    assert config.directory == logging_configuration.output_path


def test_logger_config_returns_filename(logging_configuration):
    """Verify the logger configuration exposes the configured filename."""

    config = LoggerConfig(logging_configuration)

    assert config.filename == logging_configuration.log_file.name


def test_logger_config_returns_log_file(logging_configuration):
    """Verify the logger configuration exposes the configured log file."""

    config = LoggerConfig(logging_configuration)

    assert config.log_file == logging_configuration.log_file
