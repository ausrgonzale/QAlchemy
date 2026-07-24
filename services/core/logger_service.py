"""
Application logging service.

LoggerService creates structured LogEntry objects and delegates
output to the Logger.
"""

from datetime import UTC, datetime

from scripts.core.log_entry import LogEntry
from scripts.core.logger import Logger


class LoggerService:
    """Provides structured application logging."""

    def __init__(
        self,
        logger: Logger,
        component: str,
    ) -> None:
        """Initialize the logger service."""
        self._logger = logger
        self._component = component

    def log(
        self,
        level: str,
        message: str,
        operation: str | None = None,
        exception: Exception | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Create and write a structured log entry."""

        entry = LogEntry(
            timestamp=datetime.now(UTC),
            level=level,
            component=self._component,
            operation=operation,
            message=message,
            exception=exception,
            metadata=metadata or {},
        )

        self._logger.append(self._render(entry))

    def _render(self, entry: LogEntry) -> str:
        """Render a LogEntry into a plain text log record."""

        parts = [
            f"[{entry.timestamp:%Y-%m-%d %H:%M:%S}]",
            f"[{entry.level}]",
            f"[{entry.component}]",
        ]

        if entry.operation:
            parts.append(f"[{entry.operation}]")

        parts.append(entry.message)

        if entry.exception:
            parts.append(f"Exception: {entry.exception}")

        return " ".join(parts)
