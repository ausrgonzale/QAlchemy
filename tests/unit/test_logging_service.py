"""
===============================================================================
File Descriptor Header
===============================================================================

File:
    test_entire_logger_service.py

Purpose:
    Provides consolidated unit test coverage for the QAlchemy logging feature.

Description:
    Verifies the components that support structured application logging,
    including runtime logging configuration, low-level log file persistence,
    structured log entries, and the logging service.

Test Organization:
    Tests are organized by component using pytest marks in the following order:

        1. LoggerConfig
        2. Logger
        3. LogEntry
        4. LoggerService

Pytest Marks:
    logging
        Identifies tests belonging to the QAlchemy logging feature.

    logger_config
        Identifies tests for LoggerConfig.

    logger
        Identifies tests for Logger.

    log_entry
        Identifies tests for LogEntry.

    logger_service
        Identifies tests for LoggerService.

===============================================================================
"""

import re
from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from scripts.core.log_entry import LogEntry
from scripts.core.logger import Logger
from scripts.core.logger_config import LoggerConfig
from scripts.utils.relative_path import relative_path
from services.core.logger_service import LoggerService


@pytest.mark.logging
@pytest.mark.logger_config
class TestLoggerConfig:
    def test_logger_config_returns_directory(
        self,
        logging_configuration,
    ) -> None:
        """Verify the logger configuration exposes the configured directory."""

        config = LoggerConfig(logging_configuration)

        assert config.directory == logging_configuration.output_path

    def test_logger_config_returns_filename(
        self,
        logging_configuration,
    ) -> None:
        """Verify the logger configuration exposes the configured filename."""

        config = LoggerConfig(logging_configuration)

        assert config.filename == logging_configuration.log_file.name

    def test_logger_config_returns_log_file(
        self,
        logging_configuration,
    ) -> None:
        """Verify the logger configuration exposes the configured log file."""

        config = LoggerConfig(logging_configuration)

        assert config.log_file == logging_configuration.log_file


@pytest.mark.logging
@pytest.mark.logger
class TestLogger:
    KEEP_TEST_ARTIFACTS = True

    def test_logger_appends_message(
        self,
        logging_configuration,
    ) -> None:
        """Verify the logger writes to the configured application log."""

        log_file = logging_configuration.log_file

        print(f"Log file: {relative_path(log_file)}")

        if log_file.exists():
            log_file.unlink()

        logger = Logger(LoggerConfig(logging_configuration))

        logger.append("Hello QAlchemy")

        print(f"Created: {relative_path(log_file)}")

        assert log_file.parent.exists()
        assert log_file.exists()
        assert log_file.read_text(encoding="utf-8") == "Hello QAlchemy\n"

        if not self.KEEP_TEST_ARTIFACTS:
            log_file.unlink()


@pytest.mark.logging
@pytest.mark.log_entry
class TestLogEntry:
    def test_log_entry_stores_required_fields(self) -> None:
        """Verify LogEntry stores all required structured logging fields."""

        timestamp = datetime(
            2026,
            8,
            28,
            12,
            0,
            0,
            tzinfo=UTC,
        )

        entry = LogEntry(
            timestamp=timestamp,
            level="INFO",
            component="ReviewCodeService",
            operation="review_code",
            message="Review completed.",
        )

        assert entry.timestamp == timestamp
        assert entry.level == "INFO"
        assert entry.component == "ReviewCodeService"
        assert entry.operation == "review_code"
        assert entry.message == "Review completed."

    def test_log_entry_defaults_exception_to_none(self) -> None:
        """Verify LogEntry defaults exception to None."""

        entry = LogEntry(
            timestamp=datetime.now(UTC),
            level="INFO",
            component="ReviewCodeService",
            operation=None,
            message="Review completed.",
        )

        assert entry.exception is None

    def test_log_entry_defaults_metadata_to_empty_dictionary(self) -> None:
        """Verify LogEntry defaults metadata to an empty dictionary."""

        entry = LogEntry(
            timestamp=datetime.now(UTC),
            level="INFO",
            component="ReviewCodeService",
            operation=None,
            message="Review completed.",
        )

        assert entry.metadata == {}

    def test_log_entry_stores_exception(self) -> None:
        """Verify LogEntry stores an optional exception."""

        exception = ValueError(
            "Invalid source file",
        )

        entry = LogEntry(
            timestamp=datetime.now(UTC),
            level="ERROR",
            component="ReviewCodeService",
            operation="review_code",
            message="Review failed.",
            exception=exception,
        )

        assert entry.exception is exception

    def test_log_entry_stores_metadata(self) -> None:
        """Verify LogEntry stores optional metadata."""

        metadata = {
            "work_order_id": "WO-001",
            "source_files": 3,
        }

        entry = LogEntry(
            timestamp=datetime.now(UTC),
            level="INFO",
            component="ReviewCodeService",
            operation="review_code",
            message="Review completed.",
            metadata=metadata,
        )

        assert entry.metadata == metadata

    def test_log_entry_instances_have_independent_metadata(self) -> None:
        """Verify LogEntry instances do not share default metadata."""

        first_entry = LogEntry(
            timestamp=datetime.now(UTC),
            level="INFO",
            component="GenerateCodeService",
            operation=None,
            message="Generation started.",
        )
        second_entry = LogEntry(
            timestamp=datetime.now(UTC),
            level="INFO",
            component="ReviewCodeService",
            operation=None,
            message="Review started.",
        )

        first_entry.metadata["key"] = "value"

        assert second_entry.metadata == {}


@pytest.mark.logging
@pytest.mark.logger_service
class TestLoggerService:
    def setup_method(self) -> None:
        """Create a mocked Logger for each test."""

        self.logger = Mock()
        self.logger.append = Mock()
        self.logger_service = LoggerService(
            logger=self.logger,
            component="CodeReviewService",
        )

    def test_log_appends_complete_record(self) -> None:
        """Verify LoggerService appends a complete rendered log record."""

        self.logger_service.log(
            level="INFO",
            operation="review_source_code",
            message="Review completed.",
        )

        self.logger.append.assert_called_once()

        rendered = self.logger.append.call_args.args[0]

        assert re.search(
            r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]",
            rendered,
        )
        assert "[INFO]" in rendered
        assert "[CodeReviewService]" in rendered
        assert "[review_source_code]" in rendered
        assert "Review completed." in rendered

    def test_log_omits_operation_when_not_provided(self) -> None:
        """Verify LoggerService omits the operation when not provided."""

        self.logger_service.log(
            level="INFO",
            message="Review completed.",
        )

        rendered = self.logger.append.call_args.args[0]

        assert "[INFO]" in rendered
        assert "[CodeReviewService]" in rendered
        assert "Review completed." in rendered
        assert "None" not in rendered

    def test_log_includes_exception_when_provided(self) -> None:
        """Verify LoggerService includes exception details when provided."""

        exception = ValueError(
            "Invalid source file",
        )

        self.logger_service.log(
            level="ERROR",
            operation="review_source_code",
            message="Review failed.",
            exception=exception,
        )

        rendered = self.logger.append.call_args.args[0]

        assert "Exception: Invalid source file" in rendered
