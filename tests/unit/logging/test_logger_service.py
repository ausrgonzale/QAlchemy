"""
Unit tests for LoggerService.

These tests verify that LoggerService correctly:
- Creates LogEntry objects
- Renders log entries
- Delegates output to Logger.append()
- Handles optional exception and metadata values
"""

import re
from unittest.mock import Mock

from services.core.logger_service import LoggerService


class TestLoggerService:
    """Unit tests for LoggerService."""

    def setup_method(self):
        """Create a mocked Logger for each test."""

        self.logger = Mock()
        self.logger.append = Mock()

        self.logger_service = LoggerService(
            logger=self.logger,
            component="CodeReviewService",
        )

    def test_log_calls_logger_append_once(self):
        """Logger.append() should be called exactly once."""

        self.logger_service.log(
            level="INFO",
            operation="review_source_code",
            message="Review completed.",
        )

        self.logger.append.assert_called_once()

    def test_log_contains_level(self):
        """Rendered output should contain the log level."""

        self.logger_service.log(
            level="INFO",
            operation="review_source_code",
            message="Review completed.",
        )

        rendered = self.logger.append.call_args.args[0]

        assert "INFO" in rendered

    def test_log_contains_component(self):
        """Rendered output should contain the configured component."""

        self.logger_service.log(
            level="INFO",
            operation="review_source_code",
            message="Review completed.",
        )

        rendered = self.logger.append.call_args.args[0]

        assert "CodeReviewService" in rendered

    def test_log_contains_operation(self):
        """Rendered output should contain the operation."""

        self.logger_service.log(
            level="INFO",
            operation="review_source_code",
            message="Review completed.",
        )

        rendered = self.logger.append.call_args.args[0]

        assert "review_source_code" in rendered

    def test_log_contains_message(self):
        """Rendered output should contain the message."""

        self.logger_service.log(
            level="INFO",
            operation="review_source_code",
            message="Review completed.",
        )

        rendered = self.logger.append.call_args.args[0]

        assert "Review completed." in rendered

    def test_log_with_exception(self):
        """Exception text should appear in the rendered output."""

        exception = ValueError("Invalid source file")

        self.logger_service.log(
            level="ERROR",
            operation="review_source_code",
            message="Review failed.",
            exception=exception,
        )

        rendered = self.logger.append.call_args.args[0]

        assert "Invalid source file" in rendered

    def test_log_without_exception(self):
        """Logging without an exception should succeed."""

        self.logger_service.log(
            level="INFO",
            operation="review_source_code",
            message="Review completed.",
        )

        self.logger.append.assert_called_once()

    def test_multiple_logs(self):
        """Multiple log calls should each invoke Logger.append()."""

        self.logger_service.log(
            level="INFO",
            operation="start",
            message="Started",
        )

        self.logger_service.log(
            level="INFO",
            operation="finish",
            message="Finished",
        )

        assert self.logger.append.call_count == 2

    def test_log_without_operation(self):
        """Operation should be omitted when None."""

        self.logger_service.log(
            level="INFO",
            message="Review completed.",
        )

        rendered = self.logger.append.call_args.args[0]

        assert "[INFO]" in rendered
        assert "Review completed." in rendered
        assert "None" not in rendered

    def test_log_formats_exception(self):
        """Exception should be appended to the log message."""

        exception = ValueError("Boom")

        self.logger_service.log(
            level="ERROR",
            message="Failure",
            exception=exception,
        )

        rendered = self.logger.append.call_args.args[0]

        assert "Exception: Boom" in rendered

    def test_log_timestamp_format(self):
        """Rendered output should contain a correctly formatted timestamp."""

        self.logger_service.log(
            level="INFO",
            operation="review_source_code",
            message="Review completed.",
        )

        rendered = self.logger.append.call_args.args[0]

        assert re.search(
            r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]",
            rendered,
        )

        assert "[INFO]" in rendered
        assert "CodeReviewService" in rendered
        assert "review_source_code" in rendered
        assert "Review completed." in rendered
