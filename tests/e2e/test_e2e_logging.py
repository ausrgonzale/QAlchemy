"""Validation test for LoggerService against live AppConfigurationService."""

from __future__ import annotations

from datetime import UTC, datetime

from scripts.core.logger import Logger
from scripts.core.logger_config import LoggerConfig
from services.app.app_configuration_service import AppConfigurationService
from services.core.logger_service import LoggerService

# When True, keep logs/qalchemy.log updates for manual review.
KEEP_LOG_FILE_FOR_REVIEW = True


def test_logger_service_writes_configured_log_file() -> None:
    """Write a real log entry using AppConfigurationService-driven settings."""

    configuration = AppConfigurationService()
    logger_config = LoggerConfig(configuration.logging)
    log_file = logger_config.log_file

    existing_content: str | None = None
    if log_file.exists():
        existing_content = log_file.read_text(encoding="utf-8")

    message = (
        "Validation logger write at "
        f"{datetime.now(UTC).isoformat(timespec='seconds')}"
    )

    logger = Logger(logger_config)
    logger_service = LoggerService(
        logger=logger,
        component="ValidationLoggerService",
    )

    logger_service.log(
        level="INFO",
        operation="validation",
        message=message,
    )

    assert log_file.parent.name == "logs"
    assert log_file.name == "qalchemy.log"
    assert log_file.exists()

    current_content = log_file.read_text(encoding="utf-8")
    assert message in current_content

    if not KEEP_LOG_FILE_FOR_REVIEW:
        if existing_content is None:
            log_file.unlink(missing_ok=True)
        else:
            log_file.write_text(existing_content, encoding="utf-8")
